#!/usr/bin/env python3
"""
Import Scraped Data into GrapplingWiki
=======================================
Reads the merged glossary JSON from the scrapers and creates
article stubs in the wiki database.

Usage:
    python scripts/import_scraped_data.py
    python scripts/import_scraped_data.py --input content/scraped/glossary_master.json
    python scripts/import_scraped_data.py --dry-run          # preview without writing to DB
    python scripts/import_scraped_data.py --categories person # only import persons
    python scripts/import_scraped_data.py --limit 50         # import first 50 entries
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slugify import slugify
from app import create_app, db
from app.models import User, Article, ArticleRevision, Tag


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / "content" / "scraped" / "glossary_master.json"

# Template for auto-generated article stubs
PERSON_TEMPLATE = """## Overview

{short_definition}

{metadata_section}

## Career Highlights

*This article is a stub. Help GrapplingWiki by expanding it with competition results, notable matches, and contributions to the art.*

## Technique Contributions

*Add information about signature techniques, instructionals, and teaching style.*

## Related

{related_section}

---
*Auto-generated from {source}. [Edit this article to expand it.]*
"""

TECHNIQUE_TEMPLATE = """## Overview

{short_definition}

## Mechanics

*This article is a stub. Help GrapplingWiki by adding a detailed description of how this technique works.*

## Variations

*Describe known variations and setups.*

{instructional_section}

## Related

{related_section}

---
*Auto-generated from {source}. [Edit this article to expand it.]*
"""

INSTRUCTIONAL_TEMPLATE = """## Overview

{short_definition}

**Instructor:** {instructor}

## Technique List

{technique_list}

## Related

{related_section}

---
*Auto-generated from {source}. [Edit this article to expand it.]*
"""


def get_or_create_tag(name: str, slug_str: str, description: str = "") -> Tag:
    """Get existing tag or create it."""
    tag = Tag.query.filter_by(slug=slug_str).first()
    if not tag:
        tag = Tag(name=name, slug=slug_str, description=description)
        db.session.add(tag)
        db.session.flush()
    return tag


def get_bot_user() -> User:
    """Get or create the bot user for auto-generated articles."""
    user = User.query.filter_by(username="GrapplingWiki").first()
    if not user:
        user = User(
            username="GrapplingWiki",
            email="bot@grapplingwiki.com",
            is_admin=True,
            is_editor=True,
        )
        user.set_password("grapplingwiki2026")
        db.session.add(user)
        db.session.flush()
    return user


def article_exists(slug: str) -> bool:
    """Check if an article with this slug already exists."""
    return Article.query.filter_by(slug=slug).first() is not None


def build_person_content(entry: dict) -> str:
    """Generate markdown content for a person article."""
    metadata = entry.get("metadata", {})
    metadata_lines = []
    if metadata.get("team"):
        metadata_lines.append(f"**Team:** {metadata['team']}")
    if metadata.get("nationality"):
        metadata_lines.append(f"**Nationality:** {metadata['nationality']}")
    if metadata.get("weight_class"):
        metadata_lines.append(f"**Weight Class:** {metadata['weight_class']}")
    if metadata.get("belt_rank"):
        metadata_lines.append(f"**Belt Rank:** {metadata['belt_rank']}")
    if metadata.get("lineage"):
        metadata_lines.append(f"**Lineage:** {metadata['lineage']}")

    metadata_section = "\n".join(metadata_lines) if metadata_lines else ""

    aliases = entry.get("aliases", [])
    related = entry.get("related_terms", [])
    related_items = aliases + related
    related_section = ", ".join(f"[[{t}]]" for t in related_items) if related_items else "*None yet.*"

    return PERSON_TEMPLATE.format(
        short_definition=entry.get("short_definition", "Notable grappling practitioner."),
        metadata_section=metadata_section,
        related_section=related_section,
        source=entry.get("source", "scraped data"),
    )


def build_technique_content(entry: dict) -> str:
    """Generate markdown content for a technique article."""
    instructionals = entry.get("mentioned_in_instructionals", [])
    if instructionals:
        items = "\n".join(f"- {title}" for title in instructionals[:10])
        if len(instructionals) > 10:
            items += f"\n- *...and {len(instructionals) - 10} more*"
        instructional_section = f"## Featured In\n\n{items}"
    else:
        instructional_section = ""

    related = entry.get("related_terms", [])
    related_section = ", ".join(f"[[{t}]]" for t in related) if related else "*None yet.*"

    return TECHNIQUE_TEMPLATE.format(
        short_definition=entry.get("short_definition", "A grappling technique."),
        instructional_section=instructional_section,
        related_section=related_section,
        source=entry.get("source", "scraped data"),
    )


def build_instructional_content(entry: dict) -> str:
    """Generate markdown content for an instructional article."""
    techniques = entry.get("techniques", [])
    if techniques:
        technique_list = "\n".join(f"- {t}" for t in techniques)
    else:
        technique_list = "*Technique list not yet available.*"

    related = entry.get("related_terms", [])
    related_section = ", ".join(f"[[{t}]]" for t in related) if related else "*None yet.*"

    return INSTRUCTIONAL_TEMPLATE.format(
        short_definition=entry.get("short_definition", "BJJ instructional."),
        instructor=entry.get("instructor", "Unknown"),
        technique_list=technique_list,
        related_section=related_section,
        source=entry.get("source", "scraped data"),
    )


def import_entries(entries: list[dict], category: str, dry_run: bool, bot_user, limit: int = 0):
    """Import a list of entries into the wiki as article stubs."""
    created = 0
    skipped = 0
    total = len(entries) if limit == 0 else min(limit, len(entries))

    for entry in entries[:total]:
        term = entry.get("term", "").strip()
        if not term:
            continue

        slug = slugify(term)
        if article_exists(slug):
            skipped += 1
            continue

        # Generate content based on category
        if category == "person":
            content = build_person_content(entry)
            article_category = "person"
        elif category == "instructional":
            content = build_instructional_content(entry)
            article_category = "glossary"
        else:
            content = build_technique_content(entry)
            article_category = entry.get("category", "technique")

        summary = entry.get("short_definition", "")[:300]

        if dry_run:
            print(f"  [DRY RUN] Would create: {term} ({article_category})")
            created += 1
            continue

        # Create the article
        article = Article(
            title=term,
            slug=slug,
            content=content,
            summary=summary,
            author_id=bot_user.id,
            category=article_category,
            is_published=True,
            is_protected=False,
        )
        db.session.add(article)
        db.session.flush()

        # Create initial revision
        revision = ArticleRevision(
            article_id=article.id,
            editor_id=bot_user.id,
            content=content,
            edit_summary=f"Auto-generated stub from {entry.get('source', 'scraped data')}",
            revision_number=1,
        )
        db.session.add(revision)

        # Add appropriate tag
        tag_name = article_category.capitalize()
        tag = get_or_create_tag(tag_name, article_category, f"Articles about {tag_name.lower()}.")
        article.tags.append(tag)

        created += 1
        if created % 50 == 0:
            print(f"    ...{created} created so far")

    return created, skipped


def main():
    parser = argparse.ArgumentParser(description="Import scraped data into GrapplingWiki")
    parser.add_argument(
        "--input", "-i",
        default=str(DEFAULT_INPUT),
        help=f"Input JSON file (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be imported without writing to the database",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["person", "technique", "instructional"],
        default=["person", "technique", "instructional"],
        help="Which categories to import (default: all)",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=0,
        help="Max entries to import per category (0 = all)",
    )
    args = parser.parse_args()

    # Load scraped data
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        print("Run the scrapers first: python scripts/scrape_all.py")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded scraped data from {input_path}")
    print(f"  Persons:        {len(data.get('persons', []))}")
    print(f"  Techniques:     {len(data.get('techniques', []))}")
    print(f"  Instructionals: {len(data.get('instructionals', []))}")

    if args.dry_run:
        print("\n🔍 DRY RUN — no changes will be made to the database\n")

    # Initialize Flask app
    app = create_app()

    with app.app_context():
        bot_user = None if args.dry_run else get_bot_user()

        total_created = 0
        total_skipped = 0

        if "person" in args.categories:
            print(f"\n--- Importing persons ---")
            c, s = import_entries(data.get("persons", []), "person", args.dry_run, bot_user, args.limit)
            total_created += c
            total_skipped += s
            print(f"  Created: {c}, Skipped (already exist): {s}")

        if "technique" in args.categories:
            print(f"\n--- Importing techniques ---")
            c, s = import_entries(data.get("techniques", []), "technique", args.dry_run, bot_user, args.limit)
            total_created += c
            total_skipped += s
            print(f"  Created: {c}, Skipped (already exist): {s}")

        if "instructional" in args.categories:
            print(f"\n--- Importing instructionals ---")
            c, s = import_entries(data.get("instructionals", []), "instructional", args.dry_run, bot_user, args.limit)
            total_created += c
            total_skipped += s
            print(f"  Created: {c}, Skipped (already exist): {s}")

        if not args.dry_run:
            db.session.commit()

        print(f"\n✅ Import complete!")
        print(f"   Total created:  {total_created}")
        print(f"   Total skipped:  {total_skipped}")

        if args.dry_run:
            print("\n   (No changes made — run without --dry-run to apply)")


if __name__ == "__main__":
    main()
