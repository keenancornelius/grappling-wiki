"""
Migration: Add taxonomy columns to articles table.

English-from-Japanese naming convention fields:
  mechanism         — action type (lock, choke, entanglement, throw, reap, sweep, ...)
  target            — body part (arm, leg, neck, hip, shoulder, knee, ankle, wrist, body)
  spatial_qualifier — directional modifier (inner, outer, major, minor, cross, triangle, ...)
  graph_tier        — comma-separated sys_ node IDs from graph-engine.js
  taxonomy_complete — False = needs taxonomy metadata; flagged in editor UI

Run from project root:
  python scripts/migrate_taxonomy.py

Safe to run multiple times (checks for existing columns first).
"""

import sqlite3
import os
import sys

# Resolve DB path — matches Flask's instance/ convention
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'grappling_wiki.db')

if not os.path.exists(DB_PATH):
    print(f"[ERROR] Database not found at {DB_PATH}")
    sys.exit(1)

NEW_COLUMNS = [
    # (column_name, sql_type_and_default)
    ('mechanism',         'TEXT DEFAULT NULL'),
    ('target',            'TEXT DEFAULT NULL'),
    ('spatial_qualifier', 'TEXT DEFAULT NULL'),
    ('graph_tier',        'TEXT DEFAULT NULL'),
    ('taxonomy_complete', 'INTEGER NOT NULL DEFAULT 0'),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Read existing columns
cursor.execute("PRAGMA table_info(articles)")
existing = {row[1] for row in cursor.fetchall()}

added = []
skipped = []

for col_name, col_def in NEW_COLUMNS:
    if col_name in existing:
        skipped.append(col_name)
        continue
    cursor.execute(f"ALTER TABLE articles ADD COLUMN {col_name} {col_def}")
    added.append(col_name)

# For non-graph categories, set taxonomy_complete = 1 retroactively
# (person, competition, style, glossary articles don't need taxonomy)
if 'taxonomy_complete' in [c for c, _ in NEW_COLUMNS]:
    cursor.execute("""
        UPDATE articles
        SET taxonomy_complete = 1
        WHERE category IN ('person', 'competition', 'style', 'glossary')
    """)
    updated = cursor.rowcount
    print(f"[OK] Set taxonomy_complete=1 for {updated} non-graph articles.")

conn.commit()
conn.close()

print(f"[OK] Added columns:   {added if added else 'none (already exist)'}")
print(f"[OK] Skipped columns: {skipped if skipped else 'none'}")
print(f"[DONE] Taxonomy migration complete.")
