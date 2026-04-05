#!/usr/bin/env python3
"""
GrapplingWiki Master Scraper
==============================
Runs all scrapers and merges results into a unified glossary dataset.

Usage:
    python scripts/scrape_all.py                    # run everything
    python scripts/scrape_all.py --sources heroes   # just BJJ Heroes
    python scripts/scrape_all.py --sources fanatics # just BJJ Fanatics
    python scripts/scrape_all.py --index-only       # skip detail pages (fast)
    python scripts/scrape_all.py --limit 10         # limit items per source (testing)
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRAPED_DIR = PROJECT_ROOT / "content" / "scraped"
MERGED_OUTPUT = SCRAPED_DIR / "glossary_master.json"


def run_scraper(script_name: str, extra_args: list[str] = None):
    """Run a scraper script as a subprocess."""
    script_path = PROJECT_ROOT / "scripts" / script_name
    cmd = [sys.executable, str(script_path)] + (extra_args or [])

    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode == 0


def merge_results():
    """
    Merge all scraped JSON files into a single glossary_master.json.
    Deduplicates entries by normalized term name across sources.
    """
    print(f"\n{'='*60}")
    print("Merging all scraped data...")
    print(f"{'='*60}\n")

    all_entries = []  # unified list
    all_persons = {}  # name -> merged entry
    all_techniques = {}  # name -> merged entry
    all_instructionals = []

    # Load BJJ Heroes data
    heroes_path = SCRAPED_DIR / "bjj_heroes.json"
    if heroes_path.exists():
        with open(heroes_path, "r", encoding="utf-8") as f:
            heroes_data = json.load(f)
        print(f"  BJJ Heroes: {heroes_data.get('total_entries', 0)} entries")
        for entry in heroes_data.get("entries", []):
            key = entry["term"].lower().strip()
            if key not in all_persons:
                all_persons[key] = entry
            else:
                # Merge: prefer the one with more data
                existing = all_persons[key]
                if len(entry.get("short_definition", "")) > len(existing.get("short_definition", "")):
                    entry["aliases"] = list(set(
                        existing.get("aliases", []) + entry.get("aliases", [])
                    ))
                    all_persons[key] = entry

    # Load BJJ Fanatics data
    fanatics_path = SCRAPED_DIR / "bjj_fanatics.json"
    if fanatics_path.exists():
        with open(fanatics_path, "r", encoding="utf-8") as f:
            fanatics_data = json.load(f)
        stats = fanatics_data.get("stats", {})
        print(f"  BJJ Fanatics: {stats.get('total_instructionals', 0)} instructionals, "
              f"{stats.get('total_persons', 0)} persons, "
              f"{stats.get('total_techniques', 0)} techniques")

        # Add persons from Fanatics
        for entry in fanatics_data.get("persons", []):
            key = entry["term"].lower().strip()
            if key not in all_persons:
                all_persons[key] = entry
            # If already from Heroes, keep Heroes version (richer data)

        # Add techniques
        for entry in fanatics_data.get("techniques", []):
            key = entry["term"].lower().strip()
            if key not in all_techniques:
                all_techniques[key] = entry

        # Keep instructionals as-is
        all_instructionals = fanatics_data.get("instructionals", [])

    # Build the master glossary
    master = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "stats": {
            "total_persons": len(all_persons),
            "total_techniques": len(all_techniques),
            "total_instructionals": len(all_instructionals),
            "total_glossary_entries": len(all_persons) + len(all_techniques),
        },
        "persons": sorted(all_persons.values(), key=lambda x: x["term"]),
        "techniques": sorted(all_techniques.values(), key=lambda x: x.get("mention_count", 0), reverse=True),
        "instructionals": all_instructionals,
    }

    SCRAPED_DIR.mkdir(parents=True, exist_ok=True)
    with open(MERGED_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(master, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Master glossary saved to {MERGED_OUTPUT}")
    print(f"   Persons:        {master['stats']['total_persons']}")
    print(f"   Techniques:     {master['stats']['total_techniques']}")
    print(f"   Instructionals: {master['stats']['total_instructionals']}")
    print(f"   Total glossary: {master['stats']['total_glossary_entries']}")


def main():
    parser = argparse.ArgumentParser(description="Run all GrapplingWiki scrapers")
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["heroes", "fanatics"],
        default=["heroes", "fanatics"],
        help="Which sources to scrape (default: all)",
    )
    parser.add_argument(
        "--index-only",
        action="store_true",
        help="Only scrape indexes/catalogs, skip detail pages",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=0,
        help="Limit items per source (0 = all, useful for testing)",
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=1.5,
        help="Delay between requests in seconds",
    )
    parser.add_argument(
        "--skip-merge",
        action="store_true",
        help="Skip the merge step",
    )
    args = parser.parse_args()

    SCRAPED_DIR.mkdir(parents=True, exist_ok=True)

    # Build extra args to pass through
    extra = []
    if args.index_only:
        extra.append("--index-only")
    if args.limit:
        extra.extend(["--limit", str(args.limit)])
    if args.delay:
        extra.extend(["--delay", str(args.delay)])

    success = True

    if "heroes" in args.sources:
        if not run_scraper("scrape_bjj_heroes.py", extra):
            print("⚠ BJJ Heroes scraper had errors")
            success = False

    if "fanatics" in args.sources:
        if not run_scraper("scrape_bjj_fanatics.py", extra):
            print("⚠ BJJ Fanatics scraper had errors")
            success = False

    if not args.skip_merge:
        merge_results()

    if success:
        print("\n🎉 All scrapers completed successfully!")
    else:
        print("\n⚠ Some scrapers had errors. Check output above.")

    print("\nNext steps:")
    print("  python scripts/import_scraped_data.py  # seed the wiki database")


if __name__ == "__main__":
    main()
