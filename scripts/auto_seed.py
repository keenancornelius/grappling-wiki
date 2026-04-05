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
