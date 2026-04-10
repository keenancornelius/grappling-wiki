"""
Upgrade existing articles with deep, SEO-grade content from markdown files.

Reads content/articles/*.md — each file has YAML frontmatter (title, slug,
summary, category, meta_description) and a markdown body. For every file,
this script finds the matching Article by slug and updates its content,
summary, and title. If no article with that slug exists, one is created.

Run from project root:
    python scripts/upgrade_articles.py

Safe to re-run — it's idempotent. Only updates fields that changed.
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Article, ArticleRevision, User

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "articles"


def parse_markdown_file(path: Path):
    """Return (frontmatter_dict, body_markdown) from a .md file."""
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ValueError(f"{path.name}: missing YAML frontmatter")
    # Split frontmatter from body
    _, fm, body = raw.split("---", 2)
    frontmatter = {}
    for line in fm.strip().splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return frontmatter, body.lstrip("\n")


def word_count(text: str) -> int:
    return len(re.sub(r"[^a-zA-Z ]", " ", text).split())


def upgrade_articles():
    app = create_app(os.environ.get("FLASK_CONFIG", "default"))
    with app.app_context():
        # Ensure we have an author for any new articles
        author = User.query.filter_by(username="admin").first()
        if not author:
            author = User.query.first()
        if not author:
            print("ERROR: No users in database. Run seed_articles.py first to create admin.")
            return

        files = sorted(CONTENT_DIR.glob("*.md"))
        print(f"Found {len(files)} markdown articles in {CONTENT_DIR}")

        created = updated = unchanged = 0

        for path in files:
            try:
                fm, body = parse_markdown_file(path)
            except Exception as e:
                print(f"  SKIP {path.name}: {e}")
                continue

            slug = fm.get("slug") or path.stem
            title = fm.get("title") or slug.replace("-", " ").title()
            summary = fm.get("summary", "")
            category = fm.get("category", "technique").lower()

            article = Article.query.filter_by(slug=slug).first()

            if article is None:
                article = Article(
                    title=title,
                    slug=slug,
                    content=body,
                    summary=summary,
                    category=category,
                    author_id=author.id,
                    is_published=True,
                )
                db.session.add(article)
                db.session.flush()
                rev = ArticleRevision(
                    article_id=article.id,
                    editor_id=author.id,
                    content=body,
                    edit_summary="Initial weapon-grade content",
                    revision_number=1,
                )
                db.session.add(rev)
                created += 1
                print(f"  NEW  {slug}  ({word_count(body)} words)")
            else:
                changed = False
                if article.content != body:
                    article.content = body
                    changed = True
                if summary and article.summary != summary:
                    article.summary = summary
                    changed = True
                if title and article.title != title:
                    article.title = title
                    changed = True
                if not article.is_published:
                    article.is_published = True
                    changed = True

                if changed:
                    latest_rev_num = (
                        db.session.query(db.func.max(ArticleRevision.revision_number))
                        .filter_by(article_id=article.id)
                        .scalar()
                        or 0
                    )
                    rev = ArticleRevision(
                        article_id=article.id,
                        editor_id=author.id,
                        content=body,
                        edit_summary="Upgrade to weapon-grade SEO content",
                        revision_number=latest_rev_num + 1,
                    )
                    db.session.add(rev)
                    updated += 1
                    print(f"  UPD  {slug}  ({word_count(body)} words)")
                else:
                    unchanged += 1

        db.session.commit()
        print(f"\nDone. created={created} updated={updated} unchanged={unchanged}")


if __name__ == "__main__":
    upgrade_articles()
