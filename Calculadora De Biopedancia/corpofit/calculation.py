from __future__ import annotations

import math
from typing import Any

class InputError(ValueError):
    """Erro de entrada que pode ser explicado diretamente ao usuário."""


def parse_number(value: Any, label: str) -> float:
    text = str(value or "").strip().replace(",", ".")
    if not text:
        raise InputError(f"Informe {label.lower()}.")
    try:
        number = float(text)
    except (TypeError, ValueError):
        raise InputError(f"{label} precisa ser um número válido.") from None
    if not math.isfinite(number):
        raise InputError(f"{label} precisa ser um número válido.")
    return number


def _bounded(value: float, label: str, low: float, high: float) -> float:
    if not low <= value <= high:
        raise InputError(f"{label} deve ficar entre {low:g} e {high:g}.")
    return value


def classify_body_fat(percent: float, sex: str) -> str:
    """Faixas gerais adultas ACE, usadas como contexto não diagnóstico."""
    if sex == "male":
        if percent < 6:
            return "Abaixo da faixa de referência"
        if percent <= 13:
            return "Faixa atlética"
        if percent <= 17:
            return "Faixa fitness"
        if percent <= 24:
            return "Faixa média não atleta"
        return "Acima da faixa média"
    if percent < 14:
        return "Abaixo da faixa de referência"
    if percent <= 20:
        return "Faixa atlética"
    if percent <= 24:
        return "Faixa fitness"
    if percent <= 31:
        return "Faixa média não atleta"
    return "Acima da faixa média"


def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "Abaixo da faixa de referência"
    if bmi < 25:
        return "Faixa de referência"
    if bmi < 30:
        return "Acima da faixa de referência"
    return "Faixa de obesidade pelo IMC"


def _skinfold_sum(data: dict[str, Any], names: tuple[tuple[str, str], ...]) -> float:
    return sum(
        _bounded(parse_number(data.get(field), label), label, 2, 100)
        for field, label in names
    )


def calculate_assessment(data: dict[str, Any], sex: str) -> dict[str, Any]:
    if sex not in {"male", "female"}:
        raise InputError("Selecione a equação masculina ou feminina do protocolo.")

    method = str(data.get("method", "")).strip()
    if method not in {"navy", "jp3", "jp7"}:
        raise InputError("Selecione um método de avaliação.")

    age_value = parse_number(data.get("age"), "Idade")
    age = int(age_value)
    if age != age_value:
        raise InputError("A idade deve ser informada em anos completos.")
    _bounded(age, "Idade", 18, 100)

    weight = _bounded(parse_number(data.get("weight_kg"), "Peso"), "Peso", 25, 350)
    height = _bounded(parse_number(data.get("height_cm"), "Altura"), "Altura", 120, 230)
    height_m = height / 100
    bmi = weight / (height_m * height_m)
    warnings: list[str] = []
    waist_height_ratio: float | None = None

    if method == "navy":
        waist = _bounded(parse_number(data.get("waist_cm"), "Cintura/abdômen"), "Cintura/abdômen", 25, 200)
        neck = _bounded(parse_number(data.get("neck_cm"), "Pescoço"), "Pescoço", 15, 80)
        if sex == "male":
            if waist <= neck:
                raise InputError("A medida de abdômen precisa ser maior que a medida do pescoço.")
            body_fat = 86.010 * math.log10(waist - neck) - 70.041 * math.log10(height) + 30.295210379296204
            method_label = "Circunferências da Marinha dos EUA — equação masculina"
        else:
            waist_height_ratio = waist / height
            hip = _bounded(parse_number(data.get("hip_cm"), "Quadril"), "Quadril", 30, 220)
            if waist + hip <= neck:
                raise InputError("Confira cintura, quadril e pescoço: a combinação informada não é compatível.")
            body_fat = 163.205 * math.log10(waist + hip - neck) - 97.684 * math.log10(height) - 104.91210994665497
            method_label = "Circunferências da Marinha dos EUA — equação feminina"
        # A equação Navy estima BF%; a densidade é recuperada pela relação inversa de Siri.
        if not 0 <= body_fat <= 70:
            raise InputError("O resultado ficou fora da faixa calculável. Confira as medidas e as instruções do protocolo.")
        density = 495 / (body_fat + 450)
        if sex == "male":
            warnings.append("Meça o abdômen na altura do umbigo e mantenha a fita horizontal, sem apertar a pele.")
        else:
            warnings.append("Use sempre o mesmo ponto para a cintura e meça o quadril na maior circunferência dos glúteos.")
    else:
        if (sex == "male" and age > 61) or (sex == "female" and age > 40):
            age_note = "A equação feminina original incluiu mulheres de 18 a 55 anos, e os autores recomendam cautela acima dos 40 anos." if sex == "female" else "A equação masculina original foi desenvolvida com adultos de 18 a 61 anos; este resultado é uma extrapolação da faixa estudada."
            warnings.append(age_note)

        if method == "jp3":
            if sex == "male":
                total = _skinfold_sum(data, (
                    ("skinfold_chest_mm", "Dobra peitoral"),
                    ("skinfold_abdomen_mm", "Dobra abdominal"),
                    ("skinfold_thigh_mm", "Dobra da coxa"),
                ))
                density = 1.10938 - 0.0008267 * total + 0.0000016 * total**2 - 0.0002574 * age
                method_label = "Jackson–Pollock de 3 sítios — equação masculina + Siri"
            else:
                total = _skinfold_sum(data, (
                    ("skinfold_triceps_mm", "Dobra tricipital"),
                    ("skinfold_suprailiac_mm", "Dobra supra-ilíaca"),
                    ("skinfold_thigh_mm", "Dobra da coxa"),
                ))
                density = 1.0994921 - 0.0009929 * total + 0.0000023 * total**2 - 0.0001392 * age
                method_label = "Jackson–Pollock de 3 sítios — equação feminina + Siri"
        else:
            total = _skinfold_sum(data, (
                ("skinfold_chest_mm", "Dobra peitoral"),
                ("skinfold_midaxillary_mm", "Dobra axilar média"),
                ("skinfold_triceps_mm", "Dobra tricipital"),
                ("skinfold_subscapular_mm", "Dobra subescapular"),
                ("skinfold_abdomen_mm", "Dobra abdominal"),
                ("skinfold_suprailiac_mm", "Dobra supra-ilíaca"),
                ("skinfold_thigh_mm", "Dobra da coxa"),
            ))
            if sex == "male":
                density = 1.112 - 0.00043499 * total + 0.00000055 * total**2 - 0.00028826 * age
                method_label = "Jackson–Pollock de 7 sítios — equação masculina + Siri"
            else:
                density = 1.097 - 0.00046971 * total + 0.00000056 * total**2 - 0.00012828 * age
                method_label = "Jackson–Pollock de 7 sítios — equação feminina + Siri"

        if total > 120:
            warnings.append("A soma das dobras é elevada; a equação quadrática pode não representar bem valores fora da amostra original. Confira os pontos e a técnica de medida.")
        if not 0.80 <= density <= 1.20:
            raise InputError("A densidade estimada ficou fora de uma faixa calculável. Confira idade e dobras cutâneas.")
        body_fat = 495 / density - 450
        if not 0 <= body_fat <= 70:
            raise InputError("O percentual calculado ficou fora da faixa calculável. Confira idade e medidas das dobras.")
        warnings.append("As dobras devem ser medidas com adipômetro e técnica padronizada por pessoa treinada.")

    fat_mass = weight * body_fat / 100
    lean_mass = weight - fat_mass
    return {
        "method": method,
        "method_label": method_label,
        "age": age,
        "weight_kg": weight,
        "height_cm": height,
        "body_density": density,
        "body_fat_pct": body_fat,
        "fat_mass_kg": fat_mass,
        "lean_mass_kg": lean_mass,
        "bmi": bmi,
        "bmi_category": classify_bmi(bmi),
        "body_fat_category": classify_body_fat(body_fat, sex),
        "waist_height_ratio": waist_height_ratio,
        "warnings": warnings,
    }
