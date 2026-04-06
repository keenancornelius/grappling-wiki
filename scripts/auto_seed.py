"""
Auto-seed: check if the database is empty and run all seed scripts if so.
Called before gunicorn starts on Render deploys.
Safe to run repeatedly — seed scripts skip existing articles.
"""
import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Article

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))

with app.app_context():
    db.create_all()

    # ── Ensure taxonomy columns exist (safe on fresh + existing DBs) ──
    # db.create_all() doesn't add new columns to existing tables,
    # so we ALTER TABLE for each missing column.
    TAXONOMY_COLUMNS = [
        ('mechanism',         'VARCHAR(50)'),
        ('target',            'VARCHAR(50)'),
        ('spatial_qualifier', 'VARCHAR(50)'),
        ('graph_tier',        'VARCHAR(200)'),
        ('taxonomy_complete', 'BOOLEAN NOT NULL DEFAULT FALSE'),
    ]
    try:
        existing_cols = set()
        result = db.session.execute(db.text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'articles'"
        ))
        existing_cols = {row[0] for row in result}
        for col_name, col_type in TAXONOMY_COLUMNS:
            if col_name not in existing_cols:
                db.session.execute(db.text(
                    f'ALTER TABLE articles ADD COLUMN {col_name} {col_type}'
                ))
                print(f"[auto_seed] Added column: {col_name}")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[auto_seed] Taxonomy migration note: {e}")

    count = Article.query.count()
    print(f"[auto_seed] Current article count: {count}")

    if count == 0:
        print("[auto_seed] Empty database — running seed scripts...")
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        seed_files = sorted([
            f for f in os.listdir(scripts_dir)
            if f.startswith('seed_articles') and f.endswith('.py')
        ])

        for seed_file in seed_files:
            seed_path = os.path.join(scripts_dir, seed_file)
            print(f"[auto_seed] Running {seed_file}...")
            result = subprocess.run(
                [sys.executable, seed_path],
                cwd=os.path.dirname(scripts_dir),
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"[auto_seed] {seed_file} failed:")
                print(result.stderr)
            else:
                print(f"[auto_seed] {seed_file} OK")

        # Recount
        final_count = Article.query.count()
        print(f"[auto_seed] Seeding complete. {final_count} articles.")
    else:
        print(f"[auto_seed] Database has {count} articles — skipping seed.")

    # ── Always run taxonomy backfill (safe to repeat, overwrites taxonomy data) ──
    print("[auto_seed] Running taxonomy backfill...")
    try:
        from scripts.backfill_taxonomy import TAXONOMY
        updated = 0
        for slug, (mechanism, target, spatial, graph_tier) in TAXONOMY.items():
            tc = bool(mechanism and graph_tier)
            db.session.execute(db.text(
                "UPDATE articles SET mechanism = :m, target = :t, "
                "spatial_qualifier = :s, graph_tier = :g, taxonomy_complete = :tc "
                "WHERE slug = :slug"
            ), {'m': mechanism, 't': target, 's': spatial, 'g': graph_tier,
                'tc': tc, 'slug': slug})
            updated += 1
        # Mark non-graph categories as complete
        db.session.execute(db.text(
            "UPDATE articles SET taxonomy_complete = TRUE "
            "WHERE category IN ('person', 'competition', 'style', 'glossary')"
        ))
        db.session.commit()
        print(f"[auto_seed] Taxonomy backfill done ({updated} mappings applied).")
    except Exception as e:
        db.session.rollback()
        print(f"[auto_seed] Taxonomy backfill error: {e}")
