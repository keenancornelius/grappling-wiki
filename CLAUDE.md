# GrapplingWiki — Project Architecture & Vision

## Mission

Build the definitive free, open-source, community-driven wiki covering **all of jiu-jitsu and grappling** — Brazilian Jiu-Jitsu, submission grappling, judo, wrestling, sambo, catch wrestling, and every related discipline. Modeled on the depth and rigor of Wikipedia but laser-focused on the grappling arts.

## Project Overview

- **Stack:** Python 3.11+ / Flask / SQLAlchemy / SQLite (dev) → PostgreSQL (prod)
- **Frontend:** Server-rendered Jinja2 templates, vanilla JS, responsive CSS
- **Content format:** Markdown (stored in DB, rendered to sanitized HTML)
- **Auth:** Flask-Login with password hashing (Werkzeug)
- **SEO:** XML sitemap, Open Graph, JSON-LD structured data, semantic HTML5
- **Hosting:** TBD (GitHub Pages for static export, or Vercel/Railway/VPS for full server)
- **License:** Open source (choose during Stream A)
- **Repo:** GitHub — collaborative via pull requests

## Architecture

```
grappling-wiki/
├── run.py                  # Flask entry point
├── config.py               # Environment-based configuration
├── requirements.txt        # Python dependencies
├── .gitignore
├── CLAUDE.md               # This file — project vision & task streams
├── CONTRIBUTING.md          # Git collaboration guide for contributors
├── content/
│   └── glossary/           # Glossary seed data (YAML/Markdown)
├── app/
│   ├── __init__.py         # App factory (create_app)
│   ├── forms.py            # WTForms (login, register, article, edit, search)
│   ├── models/
│   │   ├── user.py         # User model (auth, roles, contributions)
│   │   ├── article.py      # Article, ArticleRevision, Tag models
│   │   └── discussion.py   # Talk page / discussion thread models
│   ├── routes/
│   │   ├── main.py         # Homepage, search, categories, sitemap, random
│   │   ├── wiki.py         # Article CRUD, history, diffs, talk pages
│   │   ├── auth.py         # Register, login, logout, profiles
│   │   ├── api.py          # JSON API (search autocomplete, article data)
│   │   └── errors.py       # Error handlers (404, 403, 500)
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── base.html       # Master layout (nav, footer, SEO meta)
│   │   ├── index.html      # Homepage
│   │   ├── search.html, categories.html, category.html, recent_changes.html
│   │   ├── wiki/           # view, edit, create, history, diff, talk
│   │   ├── auth/           # login, register, profile
│   │   └── errors/         # 404, 403, 500
│   ├── static/
│   │   ├── css/style.css   # Full responsive stylesheet
│   │   ├── js/wiki.js      # Client-side interactivity
│   │   └── images/         # Logo, icons, default images
│   └── utils/
│       ├── filters.py      # Jinja2 filters (markdown_to_html, timeago)
│       ├── seo.py          # Sitemap, meta tags, JSON-LD generators
│       └── wiki_helpers.py # Slug gen, TOC gen, HTML sanitization, diffs
├── migrations/             # Flask-Migrate / Alembic
└── tests/                  # Test suite
```

## Core Wiki Feature Set

These are the features that make this a real wiki, not just a blog:

1. **Article creation & editing** — Any registered user can create or edit articles in Markdown
2. **Full revision history** — Every edit is stored as a numbered revision with edit summary
3. **Diff comparison** — Compare any two revisions side-by-side
4. **Talk/discussion pages** — Each article has a threaded discussion page
5. **Categories & tags** — Articles organized by: technique, position, concept, person, competition, glossary, style
6. **Full-text search** — Search across all articles with autocomplete
7. **User accounts & profiles** — Registration, login, contribution history
8. **Role-based permissions** — Admin, Editor, regular user tiers
9. **Recent changes feed** — See all edits across the wiki chronologically
10. **Random article** — Discover content serendipitously
11. **SEO optimization** — Sitemap, structured data, semantic markup
12. **JSON API** — Programmatic access to articles and search
13. **Protected articles** — Lock critical articles to editor-only editing

---

## Task Streams A–G

Each stream is an independent work surface with its own scope, context, and deliverables. Contributors should claim a stream and work within it. Streams can run in parallel.

---

### Stream A — Project Foundation & DevOps
**Status:** ✅ Scaffolded | 🔧 Needs polish
**Owner:** Unassigned
**Code context:** `config.py`, `run.py`, `requirements.txt`, `.gitignore`, `CONTRIBUTING.md`

**Scope:**
- [ ] Choose and add an open-source license (MIT or Apache 2.0 recommended)
- [ ] Set up Flask-Migrate for proper database migrations (not just create_all)
- [ ] Create a `.env.example` file documenting all environment variables
- [ ] Write a `Makefile` or `scripts/` with common commands (run, test, migrate, seed)
- [ ] Set up GitHub Actions CI pipeline (lint with flake8, run tests with pytest)
- [ ] Configure production deployment (Dockerfile, or Railway/Render config)
- [ ] Add pre-commit hooks (black, isort, flake8)
- [ ] Set up logging configuration

**Key files to touch:**
```
config.py, run.py, requirements.txt, Makefile, Dockerfile,
.github/workflows/ci.yml, .env.example, .pre-commit-config.yaml
```

---

### Stream B — Data Models & Database
**Status:** ✅ Models defined | 🔧 Needs migrations & seed data
**Owner:** Unassigned
**Code context:** `app/models/`, `migrations/`

**Scope:**
- [ ] Review and refine all SQLAlchemy models (User, Article, ArticleRevision, Tag, Discussion)
- [ ] Initialize Flask-Migrate and generate initial migration
- [ ] Add database indexes for performance (slug lookups, full-text search)
- [ ] Create a seed script (`scripts/seed_db.py`) that populates:
  - Default admin user
  - Initial categories/tags
  - A few sample articles from the glossary
- [ ] Add model-level validation beyond what WTForms provides
- [ ] Consider adding: Watchlist model (users watch articles for changes), UserContribution summary table
- [ ] Write model unit tests

**Key files to touch:**
```
app/models/*.py, migrations/, scripts/seed_db.py, tests/test_models.py
```

---

### Stream C — Routes, Views & Business Logic
**Status:** ✅ Routes scaffolded | 🔧 Needs testing & edge cases
**Owner:** Unassigned
**Code context:** `app/routes/`, `app/forms.py`

**Scope:**
- [ ] Test all routes end-to-end (create article → edit → view history → diff)
- [ ] Implement edit conflict detection (warn if article changed since user started editing)
- [ ] Add article watchlist functionality (email or in-app notifications)
- [ ] Implement article locking/protection for admins
- [ ] Add bulk operations for admins (delete, merge, move articles)
- [ ] Implement redirect system (when article titles change, old slug redirects)
- [ ] Add rate limiting on edits and account creation
- [ ] Add CAPTCHA or honeypot on registration to prevent spam
- [ ] Improve search with ranking/relevance scoring
- [ ] Write integration tests for all routes

**Key files to touch:**
```
app/routes/*.py, app/forms.py, tests/test_routes.py
```

---

### Stream D — Frontend, Templates & UX
**Status:** ✅ Templates created | 🔧 Needs visual polish & JS features
**Owner:** Unassigned
**Code context:** `app/templates/`, `app/static/`

**Scope:**
- [ ] Design and create a logo / favicon for GrapplingWiki
- [ ] Polish responsive design — test on mobile, tablet, desktop
- [ ] Enhance the Markdown editor: add toolbar buttons (bold, italic, link, heading, list)
- [ ] Implement live Markdown preview (side-by-side or tabbed)
- [ ] Add syntax highlighting for any code blocks (Pygments or highlight.js)
- [ ] Build a proper table of contents component (collapsible, tracks scroll position)
- [ ] Add dark mode toggle
- [ ] Improve diff display (word-level highlighting, toggle inline vs side-by-side)
- [ ] Add image upload support for articles
- [ ] Create print-friendly article styles
- [ ] Add keyboard shortcuts (Ctrl+S to save, Ctrl+B for bold in editor, etc.)
- [ ] Accessibility audit (ARIA labels, focus management, screen reader testing)

**Key files to touch:**
```
app/templates/*.html, app/static/css/style.css, app/static/js/wiki.js,
app/static/images/
```

---

### Stream E — SEO & Content Discovery
**Status:** ✅ Basic SEO in place | 🔧 Needs expansion
**Owner:** Unassigned
**Code context:** `app/utils/seo.py`, `app/templates/base.html`, `app/routes/main.py`

**Scope:**
- [ ] Validate XML sitemap output and test with Google Search Console
- [ ] Add `robots.txt` route
- [ ] Implement canonical URLs consistently across all pages
- [ ] Add breadcrumb navigation with BreadcrumbList schema markup
- [ ] Create a "Related Articles" section on each article page
- [ ] Implement internal linking suggestions (detect mentions of other article titles in content)
- [ ] Add RSS/Atom feed for recent changes
- [ ] Optimize page load speed (minify CSS/JS, lazy-load images, caching headers)
- [ ] Add social sharing buttons (Twitter, Reddit, Facebook)
- [ ] Implement AMP pages for mobile search (optional/stretch)
- [ ] Set up Google Analytics or privacy-friendly alternative (Plausible, Umami)

**Key files to touch:**
```
app/utils/seo.py, app/routes/main.py, app/templates/base.html,
app/templates/wiki/view.html
```

---

### Stream F — Content Architecture & Glossary
**Status:** 📋 Planning phase
**Owner:** Unassigned
**Code context:** `content/glossary/`, `scripts/`

**Scope:**
This stream is about planning and organizing the **content** that will populate the wiki. The framework comes first (Streams A–E), then we fill it.

- [ ] Define the master taxonomy of categories and subcategories (see Content Taxonomy below)
- [ ] Build the glossary seed list (see Glossary Plan below)
- [ ] Create article templates/stubs for each category type
- [ ] Write style guide for wiki articles (tone, structure, citation format)
- [ ] Prioritize which articles to write first (high-traffic, foundational)
- [ ] Create a content calendar / pipeline for article creation
- [ ] Identify authoritative sources for each subject area
- [ ] Build import scripts if migrating content from other sources

**Key files to touch:**
```
content/glossary/*.yml, content/templates/, docs/style-guide.md,
scripts/import_glossary.py
```

---

### Stream G — Community, Moderation & Growth
**Status:** 📋 Planning phase
**Owner:** Unassigned
**Code context:** `app/models/`, `app/routes/`, future features

**Scope:**
- [ ] Design user reputation / contribution scoring system
- [ ] Implement article quality ratings or review workflow
- [ ] Add user-to-user messaging or at least @mentions in discussions
- [ ] Create admin dashboard (stats, recent flags, user management)
- [ ] Implement content flagging / reporting system
- [ ] Add email notification system (watchlist changes, replies to discussions)
- [ ] Write community guidelines / code of conduct
- [ ] Plan outreach strategy (BJJ forums, Reddit r/bjj, social media)
- [ ] Consider gamification (badges for contributions, edit milestones)
- [ ] Anti-vandalism tools (auto-revert, IP blocking, edit throttling)

**Key files to touch:**
```
app/models/user.py (reputation), app/routes/admin.py (new),
app/templates/admin/, docs/community-guidelines.md
```

---

## Content Taxonomy

The wiki organizes all grappling knowledge into these top-level categories:

| Category | Description | Examples |
|---|---|---|
| **Technique** | Individual moves, submissions, sweeps, passes, escapes, takedowns | Armbar, Triangle Choke, Berimbolo, Double Leg |
| **Position** | Dominant positions, guards, pins, scramble states | Mount, Closed Guard, Side Control, Turtle |
| **Concept** | Principles, strategies, theories of grappling | Frames, Pressure, Weight Distribution, Grip Fighting |
| **Person** | Notable practitioners, instructors, competitors, pioneers | Helio Gracie, Marcelo Garcia, Gordon Ryan, John Danaher |
| **Competition** | Tournaments, rulesets, organizations, weight classes | ADCC, IBJJF Worlds, EBI, Quintet |
| **Glossary** | Terminology, Japanese/Portuguese terms, slang | Oss, Shrimping, Pulling Guard, Açaí |
| **Style** | Martial arts and grappling disciplines | BJJ, Judo, Wrestling, Sambo, Catch Wrestling, Luta Livre |

Each category will have subcategories. For example, **Technique** branches into:
- Submissions (chokes, joint locks, leg locks, compression)
- Sweeps (from guard, from bottom)
- Guard passes (pressure, speed, leg drag, toreando)
- Takedowns (single leg, double leg, trips, throws)
- Escapes (mount escape, side control escape, back escape)
- Transitions

---

## Glossary Plan

The glossary is the seed content that will populate the wiki at launch. We will build it in phases:

### Phase 1 — Core Terms (Target: 200 entries)
Foundational terms every grappler knows. These become the first articles.

**Sources to compile from:**
- Standard BJJ/judo/wrestling terminology lists
- IBJJF and ADCC rulebooks (official terminology)
- Common instructional vocabulary (Danaher, Lachlan Giles, etc.)

**Structure per glossary entry (YAML format in `content/glossary/`):**
```yaml
term: "Armbar"
aliases: ["Juji Gatame", "Arm Lock", "Cross Armlock"]
category: technique
subcategory: submission
origin_language: English
japanese_term: "十字固め (Juji Gatame)"
portuguese_term: "Chave de Braço"
short_definition: "A joint lock that hyperextends the elbow by controlling the opponent's arm between the legs and hips."
related_terms: ["Kimura", "Americana", "Straight Armlock", "Belly-Down Armbar"]
positions_from: ["Mount", "Closed Guard", "Side Control", "Back"]
priority: high
```

### Phase 2 — Expanded Encyclopedia (Target: 500+ entries)
Deeper dives: competition histories, biographical entries, stylistic analysis.

### Phase 3 — Community Contributions (Ongoing)
Open the wiki for community submissions. Moderation pipeline from Stream G.

### Initial Glossary Categories to Seed:

**Positions (~30 terms):** Mount, Side Control, Back Mount, Closed Guard, Open Guard, Half Guard, Butterfly Guard, De La Riva Guard, Spider Guard, Lasso Guard, X-Guard, Single Leg X, Rubber Guard, Worm Guard, Z-Guard, Knee Shield, Turtle, North-South, Knee on Belly, Headquarters, 50/50, Saddle/Inside Sankaku, Ashi Garami, Outside Ashi, Cross Ashi, Truck, Lockdown, Deep Half Guard, Reverse De La Riva, Octopus Guard

**Submissions (~40 terms):** Armbar, Triangle Choke, Rear Naked Choke, Guillotine, Kimura, Americana, Omoplata, D'Arce Choke, Anaconda Choke, Ezekiel Choke, Baseball Bat Choke, Bow and Arrow Choke, Cross Collar Choke, Loop Choke, North-South Choke, Von Flue Choke, Heel Hook (inside/outside), Toe Hold, Kneebar, Calf Slicer, Bicep Slicer, Wrist Lock, Gogoplata, Twister, Electric Chair, Banana Split, Buggy Choke, Straight Ankle Lock, Estima Lock, Mounted Triangle, Inverted Triangle, Peruvian Necktie, Japanese Necktie, Arm Triangle, Head and Arm Choke, Pace Choke, Suloev Stretch, Tarikoplata, Baratoplata, Monoplata

**Sweeps & Passes (~25 terms):** Scissor Sweep, Hip Bump Sweep, Flower Sweep, Pendulum Sweep, Tripod Sweep, Sickle Sweep, Balloon Sweep, Berimbolo, Kiss of the Dragon, Toreando Pass, Knee Slice, Leg Drag, Over-Under Pass, Stack Pass, Smash Pass, Long Step Pass, Cartwheel Pass, X-Pass, Bull Fighter Pass, Body Lock Pass, Headquarters Pass, Leg Weave, Folding Pass, Double Under Pass

**Takedowns (~20 terms):** Double Leg, Single Leg, High Crotch, Fireman's Carry, Ankle Pick, Snap Down, Arm Drag, Duck Under, Osoto Gari, Ouchi Gari, Kouchi Gari, Seoi Nage, Harai Goshi, Uchi Mata, Tomoe Nage, Sumi Gaeshi, Guard Pull, Imanari Roll, Flying Armbar, Flying Triangle

**Concepts (~20 terms):** Frames, Underhooks, Overhooks, Pummeling, Shrimping (Hip Escape), Bridging, Base, Posture, Pressure, Weight Distribution, Grip Fighting, Guard Retention, Leg Pummeling, Inside Position, Kuzushi (Off-Balancing), Connection, Wedges, Levers, Timing, Chain Wrestling

**People (~25 terms):** Helio Gracie, Carlos Gracie, Rolls Gracie, Rickson Gracie, Royce Gracie, Roger Gracie, Marcelo Garcia, Andre Galvao, Gordon Ryan, John Danaher, Craig Jones, Lachlan Giles, Mikey Musumeci, Keenan Cornelius, Leandro Lo, Buchecha, Bernardo Faria, Demian Maia, BJ Penn, Eddie Bravo, Dean Lister, Garry Tonon, Nicky Ryan, Meregali, Ffion Davies

**Competitions (~15 terms):** ADCC, IBJJF World Championship (Mundials), Pan Americans, European Open, ADCC Trials, EBI (Eddie Bravo Invitational), Quintet, Polaris, Who's Number One (WNO), Fight to Win, Copa Podio, Abu Dhabi Grand Slam, NAGA, Grappling Industries, Submission Underground

**Styles (~10 terms):** Brazilian Jiu-Jitsu, Judo, Freestyle Wrestling, Greco-Roman Wrestling, Sambo, Combat Sambo, Catch Wrestling, Luta Livre, Shoot Wrestling, Submission Wrestling/No-Gi Grappling

---

## Git Workflow

See `CONTRIBUTING.md` for the full contributor guide. Summary:

- `main` branch is protected — no direct pushes
- All work happens on feature branches: `stream-X/description` (e.g., `stream-b/seed-database`)
- Pull requests require at least 1 review before merge
- Commits should reference their stream: `[Stream B] Add initial migration`
- Use conventional commit style when possible

## Getting Started (for new contributors)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/grappling-wiki.git
cd grappling-wiki

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env  # then edit .env with your settings

# Initialize database
flask db upgrade  # or: python run.py (auto-creates tables in dev)

# Run the wiki
python run.py
# Visit http://localhost:5000
```

## Conventions

- **Python style:** PEP 8, enforced by flake8 + black
- **Templates:** Jinja2 with proper escaping, CSRF on all forms
- **Commit messages:** `[Stream X] Short description` format
- **Branch names:** `stream-x/feature-name`
- **Article content:** Markdown with standard heading hierarchy
- **Tests:** pytest, aim for >80% coverage on routes and models
