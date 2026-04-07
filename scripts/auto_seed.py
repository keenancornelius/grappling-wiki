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
from app.models import Article, Category, User

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))

with app.app_context():
    db.create_all()

    # ── Add missing columns to existing tables ──
    # db.create_all() only creates NEW tables, not new columns on existing ones.
    # This block handles schema migrations without Flask-Migrate.
    COLUMN_MIGRATIONS = [
        # (table, column, SQL type + constraints)
        ('users', 'is_banned', 'BOOLEAN NOT NULL DEFAULT FALSE'),
        ('users', 'ban_reason', 'VARCHAR(500)'),
        ('users', 'banned_at', 'TIMESTAMP'),
        ('users', 'banned_by_id', 'INTEGER REFERENCES users(id)'),
        ('users', 'is_suspended', 'BOOLEAN NOT NULL DEFAULT FALSE'),
        ('users', 'suspended_until', 'TIMESTAMP'),
        ('users', 'suspend_reason', 'VARCHAR(500)'),
        ('users', 'registration_ip', 'VARCHAR(45)'),
        ('users', 'last_login_at', 'TIMESTAMP'),
        ('article_revisions', 'is_minor', 'BOOLEAN NOT NULL DEFAULT FALSE'),
    ]

    for table, column, col_type in COLUMN_MIGRATIONS:
        try:
            result = db.session.execute(db.text(
                f"SELECT column_name FROM information_schema.columns "
                f"WHERE table_name = '{table}' AND column_name = '{column}'"
            ))
            if not result.fetchone():
                db.session.execute(db.text(
                    f'ALTER TABLE {table} ADD COLUMN {column} {col_type}'
                ))
                db.session.commit()
                print(f"[auto_seed] Added column: {table}.{column}")
        except Exception as e:
            db.session.rollback()
            print(f"[auto_seed] Migration note ({table}.{column}): {e}")

    # ── Ensure admin user exists (survives ephemeral DB wipes) ──
    admin = User.query.filter_by(username='keenan').first()
    if not admin:
        admin = User(
            username='keenan',
            email='keenan@legionajj.com',
            is_admin=True,
        )
        admin.set_password(os.environ.get('ADMIN_PASSWORD', 'LegionAJJ2024!'))
        db.session.add(admin)
        db.session.commit()
        print("[auto_seed] Created admin user: keenan")
    else:
        print("[auto_seed] Admin user 'keenan' already exists.")

    # ── Ensure category_id column exists on articles (safe on fresh + existing DBs) ──
    try:
        existing_cols = set()
        result = db.session.execute(db.text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'articles'"
        ))
        existing_cols = {row[0] for row in result}
        if 'category_id' not in existing_cols:
            db.session.execute(db.text(
                'ALTER TABLE articles ADD COLUMN category_id INTEGER REFERENCES categories(id)'
            ))
            print("[auto_seed] Added column: category_id")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[auto_seed] Migration note: {e}")

    # ── Seed default categories if categories table is empty ──
    cat_count = Category.query.count()
    if cat_count == 0:
        print("[auto_seed] Seeding default categories...")
        default_cats = [
            ('Technique', 'technique', 'Submissions, sweeps, passes, escapes, and takedowns.'),
            ('Position', 'position', 'Guards, pins, dominant positions, and transitional states.'),
            ('Concept', 'concept', 'Principles, strategies, and mental models.'),
            ('Person', 'person', 'Practitioners, instructors, competitors, and pioneers.'),
            ('Competition', 'competition', 'Tournaments, rulesets, and organizations.'),
            ('Style', 'style', 'Martial arts disciplines and grappling systems.'),
            ('Glossary', 'glossary', 'Terminology, Japanese and Portuguese terms, and slang.'),
        ]
        for name, slug, desc in default_cats:
            cat = Category(name=name, slug=slug, description=desc)
            db.session.add(cat)
        db.session.commit()
        print(f"[auto_seed] Created {len(default_cats)} default categories.")

    # ── Migrate legacy string categories to category_id FK ──
    try:
        unmigrated = Article.query.filter(
            Article.category_id.is_(None),
            Article.category.isnot(None)
        ).all()
        if unmigrated:
            print(f"[auto_seed] Migrating {len(unmigrated)} articles to category FK...")
            for article in unmigrated:
                cat = Category.query.filter_by(slug=article.category).first()
                if cat:
                    article.category_id = cat.id
            db.session.commit()
            print("[auto_seed] Category migration complete.")
    except Exception as e:
        db.session.rollback()
        print(f"[auto_seed] Category migration note: {e}")

    # ── Reset admin password on every deploy so dashboard env var works ──
    if admin:
        new_pw = os.environ.get('ADMIN_PASSWORD', 'LegionAJJ2024!')
        admin.set_password(new_pw)
        db.session.commit()
        print(f"[auto_seed] Admin password set from ADMIN_PASSWORD env var.")

    # ── Always run individual article seeds (they skip if already present) ──
    always_run = ['seed_miha.py', 'seed_comprehensive.py']
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    for seed_file in always_run:
        seed_path = os.path.join(scripts_dir, seed_file)
        if os.path.exists(seed_path):
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

        final_count = Article.query.count()
        print(f"[auto_seed] Seeding complete. {final_count} articles.")
    else:
        print(f"[auto_seed] Database has {count} articles — skipping seed.")
