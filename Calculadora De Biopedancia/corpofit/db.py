from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(trim(name)) BETWEEN 1 AND 80),
    sex TEXT NOT NULL CHECK(sex IN ('male', 'female')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    assessed_at TEXT NOT NULL,
    method TEXT NOT NULL CHECK(method IN ('navy', 'jp3', 'jp7')),
    age INTEGER NOT NULL CHECK(age BETWEEN 18 AND 100),
    weight_kg REAL NOT NULL,
    height_cm REAL NOT NULL,
    waist_cm REAL,
    neck_cm REAL,
    hip_cm REAL,
    skinfold_chest_mm REAL,
    skinfold_abdomen_mm REAL,
    skinfold_thigh_mm REAL,
    skinfold_triceps_mm REAL,
    skinfold_suprailiac_mm REAL,
    skinfold_midaxillary_mm REAL,
    skinfold_subscapular_mm REAL,
    body_density REAL NOT NULL,
    body_fat_pct REAL NOT NULL,
    fat_mass_kg REAL NOT NULL,
    lean_mass_kg REAL NOT NULL,
    bmi REAL NOT NULL,
    waist_height_ratio REAL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_evaluations_profile_date
    ON evaluations(profile_id, assessed_at DESC, id DESC);
"""

NEW_SKINFOLD_COLUMNS = {
    "skinfold_midaxillary_mm": "REAL",
    "skinfold_subscapular_mm": "REAL",
}
EVALUATION_COLUMNS = (
    "id", "profile_id", "assessed_at", "method", "age", "weight_kg", "height_cm",
    "waist_cm", "neck_cm", "hip_cm", "skinfold_chest_mm", "skinfold_abdomen_mm",
    "skinfold_thigh_mm", "skinfold_triceps_mm", "skinfold_suprailiac_mm",
    "skinfold_midaxillary_mm", "skinfold_subscapular_mm", "body_density", "body_fat_pct",
    "fat_mass_kg", "lean_mass_kg", "bmi", "waist_height_ratio", "created_at", "updated_at",
)
CREATE_EVALUATIONS_TABLE = """
CREATE TABLE evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    assessed_at TEXT NOT NULL,
    method TEXT NOT NULL CHECK(method IN ('navy', 'jp3', 'jp7')),
    age INTEGER NOT NULL CHECK(age BETWEEN 18 AND 100),
    weight_kg REAL NOT NULL,
    height_cm REAL NOT NULL,
    waist_cm REAL,
    neck_cm REAL,
    hip_cm REAL,
    skinfold_chest_mm REAL,
    skinfold_abdomen_mm REAL,
    skinfold_thigh_mm REAL,
    skinfold_triceps_mm REAL,
    skinfold_suprailiac_mm REAL,
    skinfold_midaxillary_mm REAL,
    skinfold_subscapular_mm REAL,
    body_density REAL NOT NULL,
    body_fat_pct REAL NOT NULL,
    fat_mass_kg REAL NOT NULL,
    lean_mass_kg REAL NOT NULL,
    bmi REAL NOT NULL,
    waist_height_ratio REAL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        database = current_app.config["DATABASE"]
        if database != ":memory:":
            Path(database).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def _upgrade_evaluations(connection: sqlite3.Connection) -> None:
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(evaluations)")}
    for name, sql_type in NEW_SKINFOLD_COLUMNS.items():
        if name not in columns:
            connection.execute(f"ALTER TABLE evaluations ADD COLUMN {name} {sql_type}")
    connection.commit()

    table_row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'evaluations'"
    ).fetchone()
    table_sql = (table_row["sql"] or "").lower() if table_row else ""
    if "'jp7'" in table_sql:
        return

    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")
    try:
        connection.execute("DROP INDEX IF EXISTS idx_evaluations_profile_date")
        connection.execute("ALTER TABLE evaluations RENAME TO evaluations_legacy")
        connection.execute(CREATE_EVALUATIONS_TABLE)
        names = ", ".join(EVALUATION_COLUMNS)
        connection.execute(
            f"INSERT INTO evaluations ({names}) SELECT {names} FROM evaluations_legacy"
        )
        connection.execute("DROP TABLE evaluations_legacy")
        connection.execute(
            "CREATE INDEX idx_evaluations_profile_date "
            "ON evaluations(profile_id, assessed_at DESC, id DESC)"
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.execute("PRAGMA foreign_keys = ON")


def close_db(_error: BaseException | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db(app) -> None:
    with app.app_context():
        connection = get_db()
        connection.executescript(SCHEMA)
        _upgrade_evaluations(connection)
        connection.commit()
