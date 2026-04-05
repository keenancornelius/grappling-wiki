#!/usr/bin/env python3
"""
BJJ Heroes Scraper for GrapplingWiki
=====================================
Scrapes bjjheroes.com for fighter/practitioner names, bios, and metadata.
Outputs JSON files compatible with GrapplingWiki's seed pipeline.

Usage:
    python scripts/scrape_bjj_heroes.py
    python scripts/scrape_bjj_heroes.py --output content/scraped/bjj_heroes.json
    python scripts/scrape_bjj_heroes.py --delay 2.0  # be polite, seconds between requests
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install requests beautifulsoup4 lxml")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "https://www.bjjheroes.com"
FIGHTERS_LIST_URL = f"{BASE_URL}/a-z-bjj-fighters-list"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

DEFAULT_OUTPUT = "content/scraped/bjj_heroes.json"
DEFAULT_DELAY = 1.5  # seconds between detail-page requests


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_soup(url: str, session: requests.Session) -> BeautifulSoup:
    """Fetch a page and return a BeautifulSoup object."""
    resp = session.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def clean_text(text: str | None) -> str:
    """Strip and normalize whitespace."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# Stage 1: Scrape the A-Z fighter list
# ---------------------------------------------------------------------------
def scrape_fighter_index(session: requests.Session) -> list[dict]:
    """
    Scrape the main A-Z fighters list page.
    Returns a list of dicts with at minimum: name, url, and any table metadata.
    """
    print(f"[1/2] Fetching fighter index: {FIGHTERS_LIST_URL}")
    soup = get_soup(FIGHTERS_LIST_URL, session)

    fighters = []

    # BJJ Heroes lists fighters in an HTML table or in <a> tags inside a
    # sortable table. Try multiple selectors for resilience.

    # Strategy A: look for a <table> with fighter rows
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue

            # Try to find a link in the first cell (fighter name)
            link = cells[0].find("a")
            if not link:
                continue

            href = link.get("href", "")
            if not href or "bjj-fighters" not in href and "a-z" not in href:
                # Not a fighter link — might still be valid, keep if it's
                # on bjjheroes.com
                if BASE_URL not in href and not href.startswith("/"):
                    continue

            name = clean_text(link.get_text())
            if not name:
                continue

            url = urljoin(BASE_URL, href)

            fighter = {"name": name, "url": url}

            # Some versions of the table have extra columns:
            # nickname, team, nationality, weight class
            if len(cells) >= 2:
                fighter["nickname"] = clean_text(cells[1].get_text())
            if len(cells) >= 3:
                fighter["team"] = clean_text(cells[2].get_text())

            fighters.append(fighter)

    # Strategy B: if no table found, look for list-style layout
    if not fighters:
        print("  No table found, trying list/link-based extraction...")
        # Look for links inside the main content area
        content_area = (
            soup.find("div", class_="entry-content")
            or soup.find("article")
            or soup.find("main")
            or soup
        )
        for link in content_area.find_all("a", href=True):
            href = link["href"]
            if "bjj-fighters" in href or "bjj-fighter" in href:
                name = clean_text(link.get_text())
                if name and len(name) > 2:
                    fighters.append({
                        "name": name,
                        "url": urljoin(BASE_URL, href),
                    })

    # Deduplicate by URL
    seen = set()
    unique = []
    for f in fighters:
        if f["url"] not in seen:
            seen.add(f["url"])
            unique.append(f)

    print(f"  Found {len(unique)} fighters on index page.")
    return unique


# ---------------------------------------------------------------------------
# Stage 2: Scrape individual fighter detail pages
# ---------------------------------------------------------------------------
def scrape_fighter_detail(fighter: dict, session: requests.Session) -> dict:
    """
    Fetch a single fighter's page and extract detailed info.
    Returns an enriched copy of the fighter dict.
    """
    url = fighter["url"]
    try:
        soup = get_soup(url, session)
    except Exception as e:
        print(f"    ⚠ Failed to fetch {url}: {e}")
        fighter["scrape_error"] = str(e)
        return fighter

    result = dict(fighter)  # copy

    # --- Bio / main content ---
    content_div = (
        soup.find("div", class_="entry-content")
        or soup.find("article")
        or soup.find("div", {"id": "content"})
    )
    if content_div:
        # Get first paragraph as summary
        first_p = content_div.find("p")
        if first_p:
            result["bio_summary"] = clean_text(first_p.get_text())

        # Get full text for keyword extraction later
        result["full_bio"] = clean_text(content_div.get_text())

    # --- Sidebar / info box ---
    # BJJ Heroes often has a sidebar or info table with structured data
    info_box = soup.find("div", class_=re.compile(r"fighter[-_]?info|sidebar|bio[-_]?box", re.I))
    if not info_box:
        # Try to find a small table that looks like a fighter card
        for tbl in soup.find_all("table"):
            text = tbl.get_text().lower()
            if any(kw in text for kw in ["weight", "team", "lineage", "nationality", "born"]):
                info_box = tbl
                break

    if info_box:
        rows = info_box.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                label = clean_text(cells[0].get_text()).lower().rstrip(":")
                value = clean_text(cells[1].get_text())
                if "weight" in label:
                    result["weight_class"] = value
                elif "team" in label or "affiliation" in label:
                    result["team"] = value
                elif "nation" in label or "country" in label:
                    result["nationality"] = value
                elif "born" in label or "birth" in label:
                    result["birth_year"] = value
                elif "lineage" in label:
                    result["lineage"] = value
                elif "nickname" in label:
                    result["nickname"] = value
                elif "belt" in label or "rank" in label:
                    result["belt_rank"] = value

    # --- Category tags from page ---
    tags = []
    tag_links = soup.find_all("a", rel="tag")
    for t in tag_links:
        tag_text = clean_text(t.get_text())
        if tag_text:
            tags.append(tag_text)
    if tags:
        result["tags"] = tags

    return result


# ---------------------------------------------------------------------------
# Stage 3: Transform to GrapplingWiki format
# ---------------------------------------------------------------------------
def transform_for_wiki(fighters: list[dict]) -> list[dict]:
    """
    Convert scraped fighter data into GrapplingWiki article-seed format.
    """
    wiki_entries = []
    for f in fighters:
        entry = {
            "term": f["name"],
            "source": "bjj_heroes",
            "source_url": f.get("url", ""),
            "category": "person",
            "short_definition": f.get("bio_summary", f"Notable grappling practitioner."),
            "aliases": [],
            "related_terms": [],
            "metadata": {},
        }

        # Add nickname as alias
        nickname = f.get("nickname", "")
        if nickname and nickname.lower() != f["name"].lower():
            entry["aliases"].append(nickname)

        # Pack extra fields into metadata
        for key in ["team", "nationality", "weight_class", "birth_year",
                     "lineage", "belt_rank", "tags"]:
            if key in f and f[key]:
                entry["metadata"][key] = f[key]

        wiki_entries.append(entry)

    return wiki_entries


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Scrape BJJ Heroes for GrapplingWiki")
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT,
        help=f"Output JSON file path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=DEFAULT_DELAY,
        help=f"Delay between detail-page requests in seconds (default: {DEFAULT_DELAY})",
    )
    parser.add_argument(
        "--index-only",
        action="store_true",
        help="Only scrape the index (names + URLs), skip detail pages",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=0,
        help="Limit number of fighters to scrape details for (0 = all)",
    )
    args = parser.parse_args()

    # Resolve output path relative to project root
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()

    # Stage 1: Index
    fighters = scrape_fighter_index(session)
    if not fighters:
        print("ERROR: No fighters found on index page. The site structure may have changed.")
        print("Check the URL manually and update selectors if needed.")
        sys.exit(1)

    # Stage 2: Detail pages (optional)
    if not args.index_only:
        total = len(fighters) if args.limit == 0 else min(args.limit, len(fighters))
        print(f"\n[2/2] Scraping detail pages for {total} fighters (delay: {args.delay}s)...")

        for i, fighter in enumerate(fighters[:total]):
            print(f"  [{i+1}/{total}] {fighter['name']}")
            fighters[i] = scrape_fighter_detail(fighter, session)
            if i < total - 1:
                time.sleep(args.delay)
    else:
        print("\n[2/2] Skipped detail pages (--index-only)")

    # Stage 3: Transform
    wiki_data = transform_for_wiki(fighters)

    # Write output
    output = {
        "source": "bjj_heroes",
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "total_entries": len(wiki_data),
        "entries": wiki_data,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(wiki_data)} entries to {output_path}")
    print(f"   Categories: person")
    print(f"   Ready for: scripts/import_scraped_data.py")


if __name__ == "__main__":
    main()
