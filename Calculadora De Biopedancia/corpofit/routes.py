from __future__ import annotations

import csv
import io
from datetime import date
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)

from .calculations import InputError, calculate_assessment, parse_number
from .db import get_db

main = Blueprint("main", __name__)

PROFILE_SQL = "SELECT id, name, sex FROM profiles ORDER BY name COLLATE NOCASE"
EVALUATION_SELECT = """
SELECT e.*, p.name AS profile_name, p.sex AS sex
FROM evaluations e JOIN profiles p ON p.id = e.profile_id
"""


def _row_dict(row):
    return dict(row) if row is not None else None


def _get_profiles():
    return [dict(row) for row in get_db().execute(PROFILE_SQL).fetchall()]


def _assessment_query(profile_id: int | None = None, limit: int = 100):
    connection = get_db()
    if profile_id:
        rows = connection.execute(
            EVALUATION_SELECT + " WHERE e.profile_id = ? ORDER BY e.assessed_at DESC, e.id DESC LIMIT ?",
            (profile_id, limit),
        ).fetchall()
    else:
        rows = connection.execute(
            EVALUATION_SELECT + " ORDER BY e.assessed_at DESC, e.id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def _get_evaluation(evaluation_id: int):
    row = get_db().execute(EVALUATION_SELECT + " WHERE e.id = ?", (evaluation_id,)).fetchone()
    evaluation = _row_dict(row)
    if evaluation:
        evaluation.update(calculate_assessment(evaluation, evaluation["sex"]))
    return evaluation


def _form_values(form, sex: str) -> dict:
    if form.get("unit") not in {None, "", "metric"}:
        raise InputError("Este formulário aceita somente unidades métricas: kg, cm e mm.")

    def read_optional(name: str, label: str):
        raw = str(form.get(name, "")).strip()
        return None if not raw else parse_number(raw, label)

    values = {
        "method": form.get("method", "navy"),
        "age": form.get("age", ""),
        "weight_kg": read_optional("weight", "Peso"),
        "height_cm": read_optional("height", "Altura"),
        "waist_cm": read_optional("waist", "Cintura/abdômen"),
        "neck_cm": read_optional("neck", "Pescoço"),
        "hip_cm": read_optional("hip", "Quadril"),
        "skinfold_chest_mm": read_optional("skinfold_chest", "Dobra peitoral"),
        "skinfold_abdomen_mm": read_optional("skinfold_abdomen", "Dobra abdominal"),
        "skinfold_thigh_mm": read_optional("skinfold_thigh", "Dobra da coxa"),
        "skinfold_triceps_mm": read_optional("skinfold_triceps", "Dobra tricipital"),
        "skinfold_suprailiac_mm": read_optional("skinfold_suprailiac", "Dobra supra-ilíaca"),
        "skinfold_midaxillary_mm": read_optional("skinfold_midaxillary", "Dobra axilar média"),
        "skinfold_subscapular_mm": read_optional("skinfold_subscapular", "Dobra subescapular"),
    }
    result = calculate_assessment(values, sex)
    try:
        assessed_at = date.fromisoformat(str(form.get("assessed_at", "")).strip())
    except ValueError:
        raise InputError("Informe uma data de avaliação válida.") from None
    if assessed_at > date.today():
        raise InputError("A data da avaliação não pode estar no futuro.")
    values.update(result)
    values["assessed_at"] = assessed_at.isoformat()
    values["waist_cm"] = _to_db_optional(values["waist_cm"])
    values["neck_cm"] = _to_db_optional(values["neck_cm"])
    values["hip_cm"] = _to_db_optional(values["hip_cm"])
    values["skinfold_chest_mm"] = _to_db_optional(values["skinfold_chest_mm"])
    values["skinfold_abdomen_mm"] = _to_db_optional(values["skinfold_abdomen_mm"])
    values["skinfold_thigh_mm"] = _to_db_optional(values["skinfold_thigh_mm"])
    values["skinfold_triceps_mm"] = _to_db_optional(values["skinfold_triceps_mm"])
    values["skinfold_suprailiac_mm"] = _to_db_optional(values["skinfold_suprailiac_mm"])
    values["skinfold_midaxillary_mm"] = _to_db_optional(values["skinfold_midaxillary_mm"])
    values["skinfold_subscapular_mm"] = _to_db_optional(values["skinfold_subscapular_mm"])
    return values


def _to_db_optional(value):
    return None if value is None else float(value)


def _safe_csv_text(value):
    text = str(value or "")
    if text.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def _persist_evaluation(profile_id: int, values: dict, evaluation_id: int | None = None):
    fields = (
        "assessed_at", "method", "age", "weight_kg", "height_cm", "waist_cm", "neck_cm", "hip_cm",
        "skinfold_chest_mm", "skinfold_abdomen_mm", "skinfold_thigh_mm", "skinfold_triceps_mm",
        "skinfold_suprailiac_mm", "skinfold_midaxillary_mm", "skinfold_subscapular_mm",
        "body_density", "body_fat_pct", "fat_mass_kg", "lean_mass_kg", "bmi",
        "waist_height_ratio",
    )
    connection = get_db()
    if evaluation_id is None:
        placeholders = ", ".join("?" for _ in range(len(fields) + 1))
        columns = ", ".join(("profile_id", *fields))
        parameters = [profile_id, *(values[field] for field in fields)]
        cursor = connection.execute(
            f"INSERT INTO evaluations ({columns}) VALUES ({placeholders})", parameters
        )
        connection.commit()
        return cursor.lastrowid

    assignments = ", ".join(f"{field} = ?" for field in fields)
    parameters = [*(values[field] for field in fields), evaluation_id]
    connection.execute(
        f"UPDATE evaluations SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", parameters
    )
    connection.commit()
    return evaluation_id


def _parse_profile_id(raw: str):
    if not raw or raw == "__new__":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _render_dashboard(*, form_data=None, errors=None, selected_profile_id=None, assessment_id=None, status=200):
    profiles = _get_profiles()
    selected_profile = next((p for p in profiles if p["id"] == selected_profile_id), None)
    evaluations = _assessment_query(selected_profile_id, limit=100)
    latest = evaluations[0] if evaluations else None
    if latest:
        latest.update(calculate_assessment(latest, latest["sex"]))
    comparable = [item for item in evaluations if latest and item["method"] == latest["method"]]
    chart_data = [
        {
            "date": item["assessed_at"], "body_fat": item["body_fat_pct"],
            "weight": item["weight_kg"], "lean_mass": item["lean_mass_kg"],
        }
        for item in reversed(comparable if selected_profile_id else [])
    ]
    selected_assessment = _get_evaluation(assessment_id) if assessment_id else None
    previous = comparable[1] if len(comparable) > 1 else None
    change = None
    if previous and latest and previous["method"] == latest["method"]:
        change = latest["body_fat_pct"] - previous["body_fat_pct"]
    return render_template(
        "index.html",
        profiles=profiles,
        selected_profile=selected_profile,
        evaluations=evaluations,
        chart_data=chart_data,
        selected_assessment=selected_assessment,
        form_data=form_data or {},
        errors=errors or [],
        latest=latest,
        change=change,
        today=date.today().isoformat(),
        form_action=url_for("main.calculate"),
        is_edit=False,
    ), status


@main.get("/")
def index():
    profile_id = request.args.get("profile_id", type=int)
    assessment_id = request.args.get("avaliacao", type=int)
    if assessment_id:
        assessment = _get_evaluation(assessment_id)
        if not assessment:
            abort(404)
        profile_id = assessment["profile_id"]
    return _render_dashboard(selected_profile_id=profile_id, assessment_id=assessment_id)


@main.get("/manus-routes.json")
def routes_manifest():
    static_dir = Path(current_app.root_path).parent / "static"
    return send_from_directory(str(static_dir), "manus-routes.json", mimetype="application/json")


@main.post("/calcular")
def calculate():
    profile_id = _parse_profile_id(request.form.get("profile_id", ""))
    is_new_profile = request.form.get("profile_id") == "__new__"
    profile = None if is_new_profile else next(
        (item for item in _get_profiles() if item["id"] == profile_id), None
    )
    name = ""
    try:
        if is_new_profile:
            name = request.form.get("new_profile_name", "").strip()
            if not name or len(name) > 80:
                raise InputError("Informe um nome ou apelido de até 80 caracteres para o perfil.")
            sex = request.form.get("profile_sex", "")
            if sex not in {"male", "female"}:
                raise InputError("Selecione a equação do perfil.")
        else:
            if profile is None:
                raise InputError("Selecione um perfil válido ou crie um novo.")
            sex = profile["sex"]
        values = _form_values(request.form, sex)
    except InputError as error:
        return _render_dashboard(
            form_data=request.form,
            errors=[str(error)],
            selected_profile_id=profile_id,
            status=400,
        )

    connection = get_db()
    if is_new_profile:
        cursor = connection.execute(
            "INSERT INTO profiles (name, sex) VALUES (?, ?)", (name, sex)
        )
        if cursor.lastrowid is None:
            abort(500)
        target_profile_id = int(cursor.lastrowid)
    else:
        if profile is None:
            abort(400)
        target_profile_id = int(profile["id"])
    evaluation_id = _persist_evaluation(target_profile_id, values)
    flash("Avaliação calculada e salva no histórico local.", "success")
    return redirect(url_for("main.index", profile_id=target_profile_id, avaliacao=evaluation_id) + "#resultado")


@main.route("/avaliacoes/<int:evaluation_id>/editar", methods=["GET", "POST"])
def edit_evaluation(evaluation_id: int):
    evaluation = _get_evaluation(evaluation_id)
    if not evaluation:
        abort(404)
    if request.method == "GET":
        return render_template(
            "edit.html", evaluation=evaluation, form_data={}, errors=[],
            form_action=url_for("main.edit_evaluation", evaluation_id=evaluation_id),
            is_edit=True, today=date.today().isoformat(),
        )

    try:
        values = _form_values(request.form, evaluation["sex"])
    except InputError as error:
        return render_template(
            "edit.html", evaluation=evaluation, form_data=request.form, errors=[str(error)],
            form_action=url_for("main.edit_evaluation", evaluation_id=evaluation_id),
            is_edit=True, today=date.today().isoformat(),
        ), 400
    _persist_evaluation(evaluation["profile_id"], values, evaluation_id=evaluation_id)
    flash("Avaliação atualizada.", "success")
    return redirect(url_for("main.index", profile_id=evaluation["profile_id"], avaliacao=evaluation_id) + "#resultado")


@main.post("/avaliacoes/<int:evaluation_id>/excluir")
def delete_evaluation(evaluation_id: int):
    evaluation = _get_evaluation(evaluation_id)
    if not evaluation:
        abort(404)
    connection = get_db()
    connection.execute("DELETE FROM evaluations WHERE id = ?", (evaluation_id,))
    connection.commit()
    flash("Avaliação excluída do histórico local.", "success")
    return redirect(url_for("main.index", profile_id=evaluation["profile_id"]) + "#historico")


@main.get("/avaliacoes/<int:evaluation_id>/imprimir")
def print_evaluation(evaluation_id: int):
    evaluation = _get_evaluation(evaluation_id)
    if not evaluation:
        abort(404)
    result = calculate_assessment(evaluation, evaluation["sex"])
    evaluation["body_fat_category"] = result["body_fat_category"]
    evaluation["method_label"] = result["method_label"]
    return render_template("print.html", evaluation=evaluation)


@main.get("/exportar.csv")
def export_csv():
    profile_id = request.args.get("profile_id", type=int)
    rows = _assessment_query(profile_id, limit=100000)
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow([
        "Perfil", "Equação", "Data", "Idade", "Peso (kg)", "Altura (cm)", "Densidade (kg/L)",
        "Gordura (%)", "Massa de gordura (kg)", "Massa livre de gordura (kg)", "IMC",
    ])
    for item in rows:
        writer.writerow([
            _safe_csv_text(item["profile_name"]), _safe_csv_text(item["method"]), item["assessed_at"], item["age"], item["weight_kg"],
            item["height_cm"], item["body_density"], item["body_fat_pct"], item["fat_mass_kg"],
            item["lean_mass_kg"], item["bmi"],
        ])
    content = ("\ufeff" + buffer.getvalue()).encode("utf-8")
    return send_file(
        io.BytesIO(content), mimetype="text/csv; charset=utf-8", as_attachment=True,
        download_name="historico-corpo-fit.csv",
    )
