#!/usr/bin/env python3
"""
BJJ Fanatics Scraper for GrapplingWiki
=======================================
Scrapes bjjfanatics.com for instructional titles, instructor names,
technique/chapter names, descriptions, and categories.

BJJ Fanatics runs on Shopify, so we can use the /products.json API
for the catalog, then scrape individual product pages for technique lists.

Usage:
    python scripts/scrape_bjj_fanatics.py
    python scripts/scrape_bjj_fanatics.py --output content/scraped/bjj_fanatics.json
    python scripts/scrape_bjj_fanatics.py --index-only      # just catalog, no detail pages
    python scripts/scrape_bjj_fanatics.py --delay 2.0       # seconds between requests
    python scripts/scrape_bjj_fanatics.py --limit 50        # only first 50 products
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, quote

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
BASE_URL = "https://www.bjjfanatics.com"
PRODUCTS_JSON_URL = f"{BASE_URL}/products.json"
COLLECTIONS_URL = f"{BASE_URL}/collections/all"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

DEFAULT_OUTPUT = "content/scraped/bjj_fanatics.json"
DEFAULT_DELAY = 1.5
PRODUCTS_PER_PAGE = 250  # Shopify max per page


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def clean_text(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_instructor_from_title(title: str) -> tuple[str, str]:
    """
    BJJ Fanatics titles often follow the pattern:
      "Technique Name by Instructor Name"
      "Instructor Name - Technique Name"
      "Technique Name with Instructor Name"

    Returns (cleaned_title, instructor_name).
    """
    # Pattern: "Something by Someone"
    by_match = re.match(r"^(.+?)\s+by\s+(.+)$", title, re.IGNORECASE)
    if by_match:
        return clean_text(by_match.group(1)), clean_text(by_match.group(2))

    # Pattern: "Someone - Something"
    dash_match = re.match(r"^(.+?)\s*[-–—]\s*(.+)$", title)
    if dash_match:
        # The instructor is usually the shorter part
        part1 = clean_text(dash_match.group(1))
        part2 = clean_text(dash_match.group(2))
        # Heuristic: if part1 looks like a name (2-4 words, capitalized),
        # it's likely the instructor
        words1 = part1.split()
        if 1 <= len(words1) <= 4 and all(w[0].isupper() for w in words1 if w):
            return part2, part1
        return part1, part2

    # Pattern: "Something with Someone"
    with_match = re.match(r"^(.+?)\s+with\s+(.+)$", title, re.IGNORECASE)
    if with_match:
        return clean_text(with_match.group(1)), clean_text(with_match.group(2))

    return title, ""


def extract_techniques_from_html(html_content: str) -> list[str]:
    """
    Parse the product description HTML for technique/chapter names.
    BJJ Fanatics descriptions often contain structured lists of techniques
    in various formats: ordered lists, bullet lists, bold headings, etc.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "lxml")
    techniques = []

    # Strategy 1: Look for list items (ol/ul > li)
    for li in soup.find_all("li"):
        text = clean_text(li.get_text())
        if text and len(text) > 3 and len(text) < 200:
            # Filter out generic marketing text
            lower = text.lower()
            if not any(skip in lower for skip in [
                "free shipping", "money back", "digital access",
                "lifetime access", "instant access", "buy now",
                "add to cart", "customer review", "satisfaction",
                "download", "streaming", "dvd", "sale", "discount",
                "subscribe", "newsletter", "copyright"
            ]):
                techniques.append(text)

    # Strategy 2: Look for bold or strong elements that might be chapter titles
    if not techniques:
        for strong in soup.find_all(["strong", "b"]):
            text = clean_text(strong.get_text())
            if text and len(text) > 3 and len(text) < 150:
                lower = text.lower()
                # Look for things that sound like technique names
                if any(kw in lower for kw in [
                    "part", "chapter", "volume", "section", "disc",
                    "guard", "mount", "pass", "sweep", "choke",
                    "lock", "escape", "takedown", "submission",
                    "half", "open", "closed", "side", "back",
                    "arm", "leg", "knee", "ankle", "neck",
                    "intro", "overview", "fundamentals", "advanced",
                ]) or re.match(r"^(part|chapter|volume|section|disc)\s*\d", lower):
                    techniques.append(text)

    # Strategy 3: Look for heading-like elements inside the description
    if not techniques:
        for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            text = clean_text(heading.get_text())
            if text and len(text) > 3:
                techniques.append(text)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for t in techniques:
        normalized = t.lower()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(t)

    return unique


def categorize_instructional(title: str, techniques: list[str]) -> list[str]:
    """
    Auto-categorize an instructional into GrapplingWiki categories based
    on keywords in the title and technique list.
    """
    text = (title + " " + " ".join(techniques)).lower()
    categories = set()

    keyword_map = {
        "technique": [
            "submission", "choke", "armbar", "armlock", "leglock",
            "ankle lock", "heel hook", "kimura", "guillotine",
            "triangle", "omoplata", "sweep", "pass", "takedown",
            "throw", "escape", "reversal",
        ],
        "position": [
            "guard", "mount", "side control", "half guard",
            "butterfly", "x-guard", "de la riva", "rubber guard",
            "turtle", "north south", "knee on belly", "back control",
            "50/50", "ashi garami", "saddle", "headquarters",
        ],
        "concept": [
            "fundamentals", "philosophy", "strategy", "game plan",
            "principles", "conceptual", "mindset", "pressure",
            "frames", "grips", "movement",
        ],
        "style": [
            "no-gi", "nogi", "gi", "wrestling", "judo",
            "sambo", "catch wrestling", "luta livre",
        ],
        "competition": [
            "competition", "tournament", "match study",
            "championship", "adcc", "mundials", "worlds",
        ],
    }

    for category, keywords in keyword_map.items():
        for kw in keywords:
            if kw in text:
                categories.add(category)
                break

    return list(categories) if categories else ["technique"]


# ---------------------------------------------------------------------------
# Stage 1: Fetch product catalog via Shopify JSON API
# ---------------------------------------------------------------------------
def scrape_catalog_json(session: requests.Session, limit: int = 0) -> list[dict]:
    """
    Use Shopify's /products.json endpoint to fetch the full catalog.
    This is more reliable than HTML scraping.
    """
    print("[1/3] Fetching product catalog via Shopify JSON API...")
    all_products = []
    page = 1

    while True:
        url = f"{PRODUCTS_JSON_URL}?limit={PRODUCTS_PER_PAGE}&page={page}"
        print(f"  Page {page}...")

        try:
            resp = session.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.JSONDecodeError:
            print(f"  ⚠ Non-JSON response on page {page}, falling back to HTML scraping.")
            return []
        except Exception as e:
            print(f"  ⚠ Error on page {page}: {e}")
            break

        products = data.get("products", [])
        if not products:
            break

        for p in products:
            product = {
                "title": p.get("title", ""),
                "handle": p.get("handle", ""),
                "url": f"{BASE_URL}/products/{p.get('handle', '')}",
                "description_html": p.get("body_html", ""),
                "product_type": p.get("product_type", ""),
                "vendor": p.get("vendor", ""),
                "tags": p.get("tags", []),
                "created_at": p.get("created_at", ""),
                "variants": [
                    {
                        "title": v.get("title", ""),
                        "price": v.get("price", ""),
                    }
                    for v in p.get("variants", [])
                ],
                "images": [img.get("src", "") for img in p.get("images", [])[:1]],
            }
            all_products.append(product)

        if limit and len(all_products) >= limit:
            all_products = all_products[:limit]
            break

        if len(products) < PRODUCTS_PER_PAGE:
            break

        page += 1
        time.sleep(1)  # be polite between pages

    print(f"  Found {len(all_products)} products via JSON API.")
    return all_products


# ---------------------------------------------------------------------------
# Stage 1b: Fallback — scrape catalog from HTML collection pages
# ---------------------------------------------------------------------------
def scrape_catalog_html(session: requests.Session, limit: int = 0) -> list[dict]:
    """
    Fallback: scrape the /collections/all pages if JSON API isn't available.
    """
    print("[1/3] Falling back to HTML catalog scraping...")
    all_products = []
    page = 1

    while True:
        url = f"{COLLECTIONS_URL}?page={page}"
        print(f"  Page {page}...")

        try:
            soup = BeautifulSoup(
                session.get(url, headers=HEADERS, timeout=30).text, "lxml"
            )
        except Exception as e:
            print(f"  ⚠ Error on page {page}: {e}")
            break

        # Look for product cards — Shopify themes vary, try common selectors
        product_cards = (
            soup.select(".product-card")
            or soup.select(".grid-product")
            or soup.select("[data-product-id]")
            or soup.select(".collection-product")
            or soup.select(".product-item")
        )

        if not product_cards:
            # Last resort: find all links to /products/
            product_links = soup.find_all("a", href=re.compile(r"/products/[^/]+$"))
            seen = set()
            for link in product_links:
                href = link.get("href", "")
                if href in seen:
                    continue
                seen.add(href)
                title = clean_text(link.get_text()) or href.split("/")[-1].replace("-", " ").title()
                all_products.append({
                    "title": title,
                    "handle": href.split("/")[-1],
                    "url": urljoin(BASE_URL, href),
                    "description_html": "",
                    "tags": [],
                })

            if not product_links:
                break
        else:
            for card in product_cards:
                link = card.find("a", href=True)
                if not link:
                    continue
                href = link.get("href", "")
                title_el = (
                    card.find(class_=re.compile(r"product.title|product.name", re.I))
                    or card.find(["h2", "h3", "h4"])
                    or link
                )
                title = clean_text(title_el.get_text()) if title_el else ""

                all_products.append({
                    "title": title,
                    "handle": href.split("/")[-1] if "/products/" in href else "",
                    "url": urljoin(BASE_URL, href),
                    "description_html": "",
                    "tags": [],
                })

        if limit and len(all_products) >= limit:
            all_products = all_products[:limit]
            break

        # Check for next page
        next_link = soup.find("a", href=re.compile(r"page=\d+"), string=re.compile(r"next|→|›", re.I))
        if not next_link:
            # Also check for pagination by number
            current_page_links = soup.find_all("a", href=re.compile(rf"page={page + 1}"))
            if not current_page_links:
                break

        page += 1
        time.sleep(1)

    print(f"  Found {len(all_products)} products via HTML scraping.")
    return all_products


# ---------------------------------------------------------------------------
# Stage 2: Scrape individual product pages for technique details
# ---------------------------------------------------------------------------
def scrape_product_detail(product: dict, session: requests.Session) -> dict:
    """
    Fetch a single product page to extract detailed technique/chapter info.
    """
    url = product["url"]
    result = dict(product)

    # If we already have description_html from JSON API, parse techniques from it
    if product.get("description_html"):
        techniques = extract_techniques_from_html(product["description_html"])
        if techniques:
            result["techniques"] = techniques

    # If no techniques found yet, try the product page
    if "techniques" not in result or not result["techniques"]:
        try:
            soup = BeautifulSoup(
                session.get(url, headers=HEADERS, timeout=30).text, "lxml"
            )
        except Exception as e:
            print(f"    ⚠ Failed to fetch {url}: {e}")
            result["scrape_error"] = str(e)
            return result

        # Try multiple selectors for the product description
        desc = (
            soup.find("div", class_=re.compile(r"product.description|product.body", re.I))
            or soup.find("div", {"id": re.compile(r"product.description", re.I)})
            or soup.find("div", class_="rte")  # common Shopify class
            or soup.find("div", class_="product__description")
        )

        if desc:
            result["description_html"] = str(desc)
            result["techniques"] = extract_techniques_from_html(str(desc))

        # Also try to get the instructor from the page
        vendor_el = soup.find(class_=re.compile(r"product.vendor|product.author", re.I))
        if vendor_el:
            result["vendor"] = clean_text(vendor_el.get_text())

    return result


# ---------------------------------------------------------------------------
# Stage 3: Transform to GrapplingWiki format
# ---------------------------------------------------------------------------
def transform_for_wiki(products: list[dict]) -> dict:
    """
    Convert scraped product data into GrapplingWiki article-seed format.
    Returns a dict with 'instructionals', 'persons', and 'techniques' lists.
    """
    instructionals = []
    persons = set()
    technique_glossary = {}  # technique_name -> {sources, categories}

    for p in products:
        title = p.get("title", "")
        if not title:
            continue

        cleaned_title, instructor = extract_instructor_from_title(title)
        if not instructor:
            instructor = p.get("vendor", "")

        techniques = p.get("techniques", [])
        wiki_categories = categorize_instructional(title, techniques)

        # Build instructional entry
        instructional = {
            "term": cleaned_title,
            "source": "bjj_fanatics",
            "source_url": p.get("url", ""),
            "category": "glossary",
            "short_definition": f"Instructional by {instructor}." if instructor else "BJJ instructional.",
            "instructor": instructor,
            "techniques": techniques,
            "tags": p.get("tags", []),
            "wiki_categories": wiki_categories,
            "metadata": {
                "product_type": p.get("product_type", ""),
                "original_title": title,
            },
        }
        instructionals.append(instructional)

        # Track instructor as a person
        if instructor and len(instructor) > 2:
            persons.add(instructor)

        # Track individual techniques for the glossary
        for tech in techniques:
            key = tech.lower().strip()
            if key not in technique_glossary:
                technique_glossary[key] = {
                    "term": tech,
                    "sources": [],
                    "categories": set(),
                }
            technique_glossary[key]["sources"].append(cleaned_title)
            for cat in wiki_categories:
                technique_glossary[key]["categories"].add(cat)

    # Convert technique glossary to list
    technique_list = []
    for key, data in sorted(technique_glossary.items()):
        entry = {
            "term": data["term"],
            "source": "bjj_fanatics",
            "category": list(data["categories"])[0] if data["categories"] else "technique",
            "short_definition": f"Technique covered in: {', '.join(data['sources'][:3])}{'...' if len(data['sources']) > 3 else ''}",
            "aliases": [],
            "related_terms": [],
            "mentioned_in_instructionals": data["sources"],
            "mention_count": len(data["sources"]),
        }
        technique_list.append(entry)

    # Convert persons set to list
    person_list = [
        {
            "term": name,
            "source": "bjj_fanatics",
            "category": "person",
            "short_definition": f"Grappling instructor featured on BJJ Fanatics.",
            "aliases": [],
            "related_terms": [],
        }
        for name in sorted(persons)
    ]

    return {
        "instructionals": instructionals,
        "persons": person_list,
        "techniques": sorted(technique_list, key=lambda x: x.get("mention_count", 0), reverse=True),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Scrape BJJ Fanatics for GrapplingWiki")
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
        help="Only scrape the catalog, skip individual product detail pages",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=0,
        help="Limit number of products to process (0 = all)",
    )
    args = parser.parse_args()

    # Resolve output path relative to project root
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()

    # Stage 1: Catalog
    products = scrape_catalog_json(session, limit=args.limit)
    if not products:
        products = scrape_catalog_html(session, limit=args.limit)
    if not products:
        print("ERROR: Could not fetch any products. The site structure may have changed.")
        sys.exit(1)

    # Stage 2: Detail pages
    if not args.index_only:
        total = len(products)
        print(f"\n[2/3] Enriching {total} products with technique details (delay: {args.delay}s)...")

        for i, product in enumerate(products):
            print(f"  [{i+1}/{total}] {product['title'][:60]}...")
            products[i] = scrape_product_detail(product, session)
            if i < total - 1:
                time.sleep(args.delay)
    else:
        print("\n[2/3] Skipped detail pages (--index-only)")

    # Stage 3: Transform
    print("\n[3/3] Transforming data for GrapplingWiki...")
    wiki_data = transform_for_wiki(products)

    # Write output
    output = {
        "source": "bjj_fanatics",
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "stats": {
            "total_instructionals": len(wiki_data["instructionals"]),
            "total_persons": len(wiki_data["persons"]),
            "total_techniques": len(wiki_data["techniques"]),
        },
        "instructionals": wiki_data["instructionals"],
        "persons": wiki_data["persons"],
        "techniques": wiki_data["techniques"],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved to {output_path}")
    print(f"   Instructionals: {output['stats']['total_instructionals']}")
    print(f"   Persons:        {output['stats']['total_persons']}")
    print(f"   Techniques:     {output['stats']['total_techniques']}")
    print(f"   Ready for: scripts/import_scraped_data.py")


if __name__ == "__main__":
    main()
