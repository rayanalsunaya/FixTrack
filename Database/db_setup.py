"""
db_setup.py
------------
Run this ONCE to create fixtrack.db from schema.sql, and to seed the
8 usage_patterns rows (the same 8 patterns from the survey / onboarding
questionnaire).

Usage:
    python db_setup.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fixtrack.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

# The 8 usage patterns, with a DEFAULT estimated km/day for each.
# These numbers are starting assumptions (cold start values) — you should
# refine them later using the real averages from your 145 survey
# responses (Q5 + Q6 cross-tabulated) instead of guessing.
USAGE_PATTERNS = [
    # (id, name_ar,                          name_en,                         est_km_per_day)
    (1, "للعمل فقط (مسار ثابت)",              "Work commute only (fixed route)", 35),
    (2, "للعمل + مشاوير يومية",                "Work commute + daily errands",    55),
    (3, "استخدام يومي مكثف (توصيل/عمل حر)",    "Heavy daily use (delivery/freelance)", 120),
    (4, "سفر متكرر بين المدن",                 "Frequent intercity travel",       150),
    (5, "سيارة إضافية / احتياطية",             "Secondary / backup vehicle",      15),
    (6, "سيارة يقودها سائق خاص",               "Vehicle driven by a private driver", 70),
    (7, "استخدام نهاية الأسبوع فقط",           "Weekend-only use",                20),
    (8, "استخدام نادر / مناسبات فقط",          "Rare use / occasions only",       8),
]


def build_database():
    # If the database already exists, don't overwrite it — this script
    # is meant to run once. Delete fixtrack.db manually if you want a
    # clean rebuild during development.
    if os.path.exists(DB_PATH):
        print(f"'{DB_PATH}' already exists. Delete it first if you want a fresh rebuild.")
        return

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # executescript runs multiple ; separated statements at once,
    # which is exactly what schema.sql contains (6 CREATE TABLE statements).
    cursor.executescript(schema_sql)

    # Seed the usage_patterns lookup table.
    cursor.executemany(
        "INSERT INTO usage_patterns (id, pattern_name_ar, pattern_name_en, estimated_km_per_day) "
        "VALUES (?, ?, ?, ?)",
        USAGE_PATTERNS,
    )

    conn.commit()
    conn.close()
    print(f"Database created at '{DB_PATH}' with {len(USAGE_PATTERNS)} usage patterns seeded.")


if __name__ == "__main__":
    build_database()
