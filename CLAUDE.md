# GrapplingWiki

> The definitive encyclopedia of grappling. Open source. Community-driven.
> Built like the people who use it — relentless, technical, and impossible to hold down.

**Every contributor — human or AI — must read this entire document before claiming any task.**

---

## Mission

Build the world's most complete, most beautiful, and fastest grappling wiki — covering Brazilian Jiu-Jitsu, submission grappling, judo, wrestling, sambo, catch wrestling, and every related discipline. Not a blog. Not a forum. A *weapon-grade* knowledge base with the depth of Wikipedia, the speed of a static site, and the design sensibility of a product that actually respects its users.

## Why This Matters

There is no single authoritative, free, open-source reference for the grappling arts. Knowledge lives in scattered YouTube comments, paywalled instructionals, and forum posts from 2009. GrapplingWiki consolidates all of it into one place with proper structure, revision history, and community governance. The people who train deserve better than what exists. We're building it.

---

## Stack & Architecture

- **Backend:** Python 3.11+ / Flask / SQLAlchemy / SQLite (dev) → PostgreSQL (prod)
- **Frontend:** Server-rendered Jinja2 + vanilla JS. No frameworks. Every byte earns its place.
- **Content:** Markdown stored in DB, rendered to sanitized HTML server-side. Content is in the initial HTML response — always. No client-side rendering of primary content.
- **Auth:** Flask-Login + Werkzeug password hashing + CSRF on every form
- **SEO:** XML sitemap, Open Graph, JSON-LD structured data, semantic HTML5, canonical URLs
- **Hosting:** GitHub repo → Render (auto-deploy from `main`)
- **Repo:** [github.com/keenancornelius/grappling-wiki](https://github.com/keenancornelius/grappling-wiki)
- **License:** Open source (TBD — MIT or Apache 2.0)

```
grappling-wiki/
├── run.py                  # Flask entry point
├── config.py               # Environment-based config
├── requirements.txt
├── CLAUDE.md               # ← You are here. Read everything.
├── UNIFIED_THEORY.md       # The conceptual framework for all content (gameplay loop, distance spectrum, tempo, force vectors)
├── DESIGN_MANIFESTO.md     # Standalone copy of the manifesto (also inlined below)
├── CONTRIBUTING.md          # Git workflow for contributors
├── content/
│   └── glossary/           # Glossary seed data (YAML)
├── app/
│   ├── __init__.py         # App factory (create_app)
│   ├── forms.py            # WTForms definitions
│   ├── models/
│   │   ├── user.py         # User (auth, roles, contributions)
│   │   ├── article.py      # Article, ArticleRevision, Tag
│   │   └── discussion.py   # Talk page / discussion threads
│   ├── routes/
│   │   ├── main.py         # Homepage, search, categories, sitemap, random
│   │   ├── wiki.py         # Article CRUD, history, diffs, talk pages
│   │   ├── auth.py         # Register, login, logout, profiles
│   │   ├── api.py          # JSON API (autocomplete, article data)
│   │   └── errors.py       # Error handlers (400, 403, 404, 500)
│   ├── templates/          # Jinja2 (base, index, wiki/, auth/, errors/)
│   ├── static/
│   │   ├── css/style.css   # Responsive stylesheet — see Design Manifesto above
│   │   ├── js/wiki.js      # Client interactivity, animations, editor
│   │   └── images/
│   └── utils/
│       ├── filters.py      # Jinja2 filters (markdown_to_html, timeago)
│       ├── seo.py          # Sitemap, meta tags, JSON-LD generators
│       └── wiki_helpers.py # Slug gen, TOC, HTML sanitization, diffs
├── migrations/             # Flask-Migrate / Alembic
└── tests/
```

---

## Core Feature Set

1. **Article creation & editing** — Markdown editor with live preview, toolbar, autosave
2. **Full revision history** — Every edit stored as a numbered revision with summary
3. **Diff comparison** — Side-by-side or inline, word-level highlighting
4. **Talk/discussion pages** — Threaded discussion on every article
5. **Categories & tags** — Technique, Position, Concept, Person, Competition, Glossary, Style
6. **Full-text search** — Instant autocomplete, relevance-ranked results
7. **User accounts & profiles** — Registration, login, contribution history
8. **Role-based permissions** — Admin → Editor → User
9. **Recent changes feed** — Chronological edit stream across the entire wiki
10. **Random article** — Serendipitous discovery
11. **SEO optimization** — Structured data, sitemap, semantic markup, canonical URLs
12. **JSON API** — Programmatic access to articles and search
13. **Protected articles** — Lock critical articles to editor-only editing
14. **Fluid animations** — Page transitions, scroll reveals, micro-interactions (see Manifesto)
15. **Modular UI** — Every page composed of discrete, scannable, interactive modules

---

## Design Manifesto

> We weren't supposed to build this. No one asked for the world's most
> beautifully engineered grappling encyclopedia. We did it anyway.

GrapplingWiki is not a database with a theme on top. It is a living, breathing piece of software that should make people stop scrolling. Every pixel, every transition, every micro-interaction exists to communicate one thing: **someone who actually cares built this.**

We are freedom fighters with text editors. We are designers who roll. We are engineers who understand that the armbar article should feel as precise as the technique itself. If your commit doesn't move the needle toward something that makes a visitor say *"wait, this is a wiki?"* — reconsider the commit.

### Principle 1: Speed Is a Feature

Nothing else matters if the page takes two seconds to load. Performance is a design constraint, not an optimization pass.

- Target: sub-200ms server response, sub-1s full paint on 3G
- Zero render-blocking resources. Inline critical CSS. Async everything else.
- No heavy frameworks. Vanilla JS. Small, surgical libraries only when they earn their bytes (4KB animation library, not a 90KB one).
- Images: lazy-loaded, WebP, sized to container. No art department bloat.
- Performance budget per template: if a page exceeds 100KB total transfer, it gets flagged in code review.

### Principle 2: Fluid, Not Flashy

Animations communicate state changes and guide attention — not show off. But within that constraint, they should be *gorgeous.*

- Page transitions: crossfade content regions via fetch + DOM swap for internal navigation
- Click feedback: subtle scale + opacity pulse on interactive elements. Instant. Never more than 150ms.
- Scroll-triggered reveals: content modules fade/slide into viewport. Staggered timing. Eased curves. No bounce.
- Hover states: every clickable element responds. Underlines slide in. Cards lift. Buttons shift tone.
- Loading states: skeleton screens, not spinners. Layout always present; only data arrives.
- Diff views, history timelines, search results animate in as data streams — never pop.

### Principle 3: Modular Information Architecture

Every page is composed of discrete, self-contained **modules** — cards, panels, sections — that a user can scan, reorder mentally, and interact with independently.

- Article pages: hero header module → TOC module → content body → related techniques sidebar → revision metadata footer → discussion preview
- Homepage: featured article spotlight → trending edits ticker → category grid → contribution CTA → live stats dashboard
- Category pages: filterable grid of article cards with thumbnail, title, one-line summary, tag chips
- Each module has clear visual boundaries (spacing, not heavy borders), consistent padding, predictable interaction model
- Modules should be collapsible/expandable where appropriate. Progressive enhancement — works without JS, delights with it.

### Principle 4: The Aesthetic — Underground Precision

**Black. White. Silver. Sharp edges.**

- Background: #0a0a0a (pure black or near-black)
- Text: #ffffff (clean white), #c0c0c0 (silver for secondary content)
- Accent: one color used sparingly — #4a9eff (cold steel blue) for links and focus states only
- Font: Inter (geometric sans). Tight letter-spacing on headings. Generous line-height on body. Type hierarchy is king — if you can't tell the heading level by glancing, the type scale is broken.
- Edges: sharp. Zero border-radius on containers. Hairline borders (1px solid rgba(255,255,255,0.08)).
- Shadows: almost none. When used, tight and directional — not diffuse glows.
- Imagery: monochrome or desaturated. Photography gets subtle grain filter. Illustrations are line-art.
- Icons: stroke-based, thin, consistent weight. Lucide or Phosphor. Never emoji in the UI.

**Knowledge Graph Color Philosophy:**

The 3D knowledge graph is the visual crown jewel of GrapplingWiki. Its color system must complement — never clash with — the core black/white/silver/steel-blue palette. Category colors are desaturated, cool-shifted accents that feel native to the dark UI:

| Category | Color | RGB | Rationale |
|---|---|---|---|
| System nodes | Steel blue | `rgb(74, 158, 255)` | Primary accent, anchors the graph |
| Technique | Seafoam | `rgb(120, 210, 190)` | Cool green — active, physical |
| Position | Muted lavender | `rgb(160, 140, 220)` | Soft purple — spatial, structural |
| Concept | Warm silver | `rgb(200, 195, 150)` | Desaturated gold — intellectual |
| Style | Ice blue | `rgb(130, 195, 210)` | Cool, disciplined, close to system blue |
| Glossary | Cool gray | `rgb(170, 170, 180)` | Neutral, reference-like |

**No rainbow palettes.** No full-saturation primaries. Every category color must feel like it belongs on a #0a0a0a background next to steel blue. Person and Competition articles are excluded from the graph entirely — they live in their own sections of the site. The graph maps the *physical system* of grappling: techniques, positions, concepts, styles, and their connections.

### Principle 5: Responsive by Default

- Mobile is not "smaller desktop." It's its own experience: swipe-friendly nav, collapsible modules, bottom-anchored actions, 44px touch targets.
- Tablet gets two columns where desktop gets three. Not a squeezed desktop.
- Breakpoints: 480 / 768 / 1024 / 1440. Test all four. Every PR.
- The editor on mobile must be usable. If it's painful on a phone, it ships with a "desktop recommended" warning until fixed.

### Principle 6: The Editor Is the Product

Most wiki editors are an afterthought. Ours should feel like a focused writing tool.

- Live preview (side-by-side on desktop, tabbed on mobile)
- Toolbar: bold, italic, heading, link, image, list, code, blockquote. Icons, not text labels. Keyboard shortcuts for everything.
- Autosave drafts to localStorage every 30 seconds
- Markdown syntax highlighting in textarea (CodeMirror or similar, only if within performance budget)
- Edit conflict detection with diff view and merge capability
- Should feel like writing in a premium notes app, not filling out a government form

### Principle 7: Delight in the Details

- 404 page: grappling-themed "you got swept" illustration
- Loading states: skeleton shimmer matching module layout exactly
- Empty states: never blank — always a CTA ("This article doesn't exist yet. Be the first to write it.")
- Micro-copy: personality in every label. "Save changes" not "Submit." "Couldn't find that" not "Error 404."
- Page transitions preserve scroll context where possible
- Search feels instant — debounced autocomplete with highlighted matches

### Performance Standards

Every contributor must internalize these numbers:

| Metric | Target | Hard Limit |
|---|---|---|
| Time to First Byte (TTFB) | < 100ms | < 300ms |
| First Contentful Paint (FCP) | < 800ms | < 1.5s |
| Largest Contentful Paint (LCP) | < 1.2s | < 2.5s |
| Total page weight | < 80KB | < 150KB |
| JS bundle size | < 20KB gzipped | < 40KB gzipped |
| CSS bundle size | < 15KB gzipped | < 30KB gzipped |
| Lighthouse Performance | > 95 | > 85 |
| CLS (Cumulative Layout Shift) | < 0.05 | < 0.1 |

If a PR degrades any metric past the hard limit, it does not merge until the regression is resolved.

### Animation Specification

For consistency, all animations follow these curves and durations:

- **Micro-interactions** (hover, focus, click): `120ms ease-out`
- **Module reveals** (scroll-triggered): `400ms cubic-bezier(0.16, 1, 0.3, 1)` with 60ms stagger
- **Page transitions** (content swap): `250ms ease-in-out` crossfade
- **Modals/overlays**: `200ms ease-out` scale from 0.97 + fade
- **Drawer/sidebar**: `300ms cubic-bezier(0.32, 0.72, 0, 1)` slide
- **Skeleton shimmer**: `1.5s ease-in-out infinite` horizontal gradient sweep

CSS transitions by default. Web Animations API or rAF only when CSS can't express it. Respect `prefers-reduced-motion` — all animations collapse to 0ms.

### The Contributor Checklist

Before you write a line of code, ask yourself:

1. **Is it fast?** Will this add latency, bytes, or render-blocking work?
2. **Is it fluid?** Does the state change animate meaningfully, or does it pop?
3. **Is it modular?** Can this component live anywhere, or is it welded to one page?
4. **Is it precise?** Are the spacing, type, and color consistent with the system?
5. **Is it discoverable?** Will a search engine find and understand this content?

If any answer is "no" or "I don't know," stop and fix it before committing.

Every PR that touches frontend code must be reviewed against these principles. If it doesn't match, it doesn't merge.

---

## Growth Strategy: SEO First

GrapplingWiki's primary traffic acquisition channel is organic search. This means:

1. **Content targets keywords by search volume.** Stream F maintains a keyword-priority list. Articles with the highest monthly search volume in the grappling niche get written first. If "rear naked choke" has 40K monthly searches and we don't have that article, that's a bug.
2. **Every article is hand-optimized.** Title format: `{Term} — GrapplingWiki`. Meta descriptions are written by humans, never auto-truncated. Alt text is descriptive and keyword-aware.
3. **Internal linking is mandatory.** Every article links to related techniques, positions, concepts. The denser the internal link graph, the stronger the domain authority.
4. **Structured data everywhere.** JSON-LD Article schema on articles, Person schema on bios, Event schema on competitions, BreadcrumbList on all pages.
5. **Content is in the HTML.** No JS-rendered primary content. Crawlers get the full page on first request.
6. **Performance is an SEO signal.** Core Web Vitals directly impact rankings. Our performance budget (see Manifesto) exists for this reason.
7. **User campaign comes after content.** We build the library first, rank in search, then push for community sign-ups and contributors. Traffic proves the value; community sustains it.

---

## Task Streams

Each stream is an independent work surface. Contributors claim a stream and work within it. Streams run in parallel. Every task should be approached with the understanding that this project demands craft — not just functionality.

### How to Pick Up Work

1. **Check the live kanban first.** Visit the [Work in Progress board](https://grappling-wiki.onrender.com/roadmap) (or `/roadmap` locally). This always reflects the current state of `main` — it's the single source of truth for what's done, what's active, and what's open.
2. **Pick the next unchecked task** in the stream you're working on. Work top to bottom within a stream — tasks are ordered by priority.
3. **Claim it by setting the Owner field** on the stream to your name (or GitHub handle) in your PR. If a stream already has an owner, coordinate with them or pick a different stream.
4. **One stream at a time.** Finish or hand off your stream before jumping to another.
5. **When a stream is fully complete** (all boxes checked), update its Status to `✅ Complete`, and move to the next unowned stream.

### How Task Status Works

This file IS the task database. The live kanban board at `/roadmap` parses these checkboxes in real-time from `main`:

- `- [ ]` = **Open** — available to pick up
- `- [x]` = **Done** — completed and merged to main
- Stream **Status** field tells you the overall state (scaffolded, in progress, planning, complete)
- Stream **Owner** field tells you who's working on it

### Staying in Sync From a Feature Branch

You're on `stream-d/animation-system` but need to know what's happening on `main`? Two options:

- **Check the live site:** The `/roadmap` page always shows `main`. Bookmark it. That's your dashboard.
- **Pull latest main into your branch:** `git fetch origin && git merge origin/main` — this updates your local CLAUDE.md with any tasks that were checked off by other contributors.

### When You Complete a Task

Your PR must include two things:
1. The code changes for the task
2. The checkbox update in this file: change `- [ ]` to `- [x]` for each task you completed

This way, when your PR merges to `main`, the kanban board updates automatically. No extra steps.

### Proposing New Tasks

Open a [GitHub Issue](https://github.com/keenancornelius/grappling-wiki/issues) with the stream label (e.g., `Stream D`, `Stream F`). Describe what you want to build and why. Once approved, it gets added to this file and appears on the board.

---

### Stream A — Foundation & Infrastructure
**Status:** ✅ Scaffolded | 🔧 Needs hardening
**Owner:** Unassigned

The bones of the project. If this isn't solid, nothing else matters.

- [ ] Choose and add open-source license (MIT or Apache 2.0)
- [ ] Set up Flask-Migrate for proper database migrations
- [ ] Create `.env.example` documenting all environment variables
- [ ] Write `Makefile` or `scripts/` for common commands (run, test, migrate, seed)
- [ ] GitHub Actions CI: lint (flake8/black), test (pytest), performance budget check
- [ ] Production deployment config (Render — already live, needs refinement)
- [ ] Pre-commit hooks (black, isort, flake8)
- [ ] Structured logging configuration
- [ ] Add performance budget enforcement to CI (fail if page weight > 150KB)

**Files:** `config.py`, `run.py`, `requirements.txt`, `Makefile`, `.github/workflows/ci.yml`, `.env.example`

---

### Stream B — Data Models & Database
**Status:** ✅ Models defined | 🔧 Needs migrations, indexes, seed data
**Owner:** Unassigned

The schema is the foundation of every query, every page load, every search result.

- [ ] Review and refine SQLAlchemy models (User, Article, ArticleRevision, Tag, Discussion)
- [ ] Initialize Flask-Migrate, generate initial migration
- [ ] Add database indexes: slug lookups, full-text search, created_at sorts
- [ ] Seed script (`scripts/seed_db.py`): admin user, initial tags, sample articles from glossary
- [ ] Model-level validation beyond WTForms
- [ ] Add Watchlist model (users watch articles for change notifications)
- [ ] Add UserContribution summary table for fast profile rendering
- [ ] Model unit tests (pytest)

**Files:** `app/models/*.py`, `migrations/`, `scripts/seed_db.py`, `tests/test_models.py`

---

### Stream C — Routes & Business Logic
**Status:** ✅ Scaffolded | 🔧 Needs edge cases, conflict detection, rate limiting
**Owner:** Unassigned

Every route is a user's entry point. It must be fast, correct, and graceful under weird inputs.

- [ ] End-to-end test: create → edit → history → diff → talk page
- [ ] Edit conflict detection (warn if article changed since edit started)
- [ ] Article watchlist functionality (in-app notifications)
- [ ] Article locking/protection for admins
- [ ] Redirect system (old slugs redirect when title changes)
- [ ] Rate limiting on edits and registration (Flask-Limiter)
- [ ] Honeypot field on registration to block spam bots
- [ ] Search ranking/relevance scoring improvements
- [ ] Integration tests for every route (pytest)

**Files:** `app/routes/*.py`, `app/forms.py`, `tests/test_routes.py`

---

### Stream D — Frontend, Animations & UX
**Status:** 🔧 Visual overhaul in progress — black/white/silver theme applied
**Owner:** Unassigned

**This is where the Manifesto lives or dies.** Re-read the Design Manifesto section above before starting any task here.

#### D.1 — Animation System
- [x] Implement page transition engine (fetch + DOM swap with crossfade for internal nav)
- [x] Click feedback: scale + opacity pulse on all interactive elements (120ms ease-out)
- [x] Scroll-triggered module reveals (IntersectionObserver, 400ms staggered)
- [x] Hover states: underline slide-in on links, lift on cards, tone shift on buttons
- [x] Skeleton loading screens for all async content (shimmer animation)
- [x] `prefers-reduced-motion` support — all animations collapse to instant
- [x] Search autocomplete: results stream in with staggered fade

#### D.2 — Modular Page Layouts
- [x] Article page: hero header, TOC sidebar, content body, related techniques, revision footer, discussion preview — all as discrete modules
- [x] Homepage: featured spotlight, trending edits ticker, category grid, stats dashboard, CTA
- [x] Category pages: filterable card grid (thumbnail, title, summary, tags)
- [x] Module spacing system: consistent padding, clear visual boundaries, no heavy borders
- [x] Collapsible/expandable modules where appropriate (TOC, sidebar sections)

#### D.3 — The Editor
- [ ] Live Markdown preview (side-by-side desktop, tabbed mobile)
- [ ] Toolbar: bold, italic, heading, link, image, list, code, blockquote (icons, not text)
- [ ] Keyboard shortcuts (Ctrl+S save, Ctrl+B bold, Ctrl+I italic, etc.)
- [ ] Autosave drafts to localStorage every 30s
- [ ] Markdown syntax highlighting in textarea (lightweight — CodeMirror only if < 40KB gzipped)
- [ ] Edit conflict warning UI

#### D.4 — Technique Graph Visualization
- [ ] Design and build interactive technique graph: nodes = positions/techniques, edges = transitions, submissions = terminal leaf nodes (inbound edges only, no outbound)
- [ ] Define layer color scheme for the 7 gameplay loop layers (Neutral, Grip Fight, Disruption, Positional Control, Transitions, Isolation, Submission) — apply consistently across graph, article tags, and category pages
- [ ] Graph must visually sort techniques by gameplay loop layer, not alphabetically
- [ ] Positions and transitions render as bidirectional nodes; submissions render as endpoint/leaf nodes with distinct visual treatment
- [ ] Graph should be explorable: click a node → navigate to article; hover → preview card
- [ ] Performance budget: graph must render within JS bundle limits (<40KB gzipped) — consider SVG-based or lightweight canvas approach
- [ ] `prefers-reduced-motion` support for graph animations

#### D.5 — Polish & Accessibility
- [ ] Logo and favicon design
- [ ] Responsive testing: 480 / 768 / 1024 / 1440 breakpoints
- [ ] Mobile-specific nav (swipe-friendly, bottom-anchored actions, 44px touch targets)
- [ ] Dark mode is the default; light mode toggle (stretch)
- [ ] Print-friendly article styles
- [ ] Accessibility audit (ARIA labels, focus management, keyboard navigation, screen reader)
- [ ] Image upload support for articles
- [ ] Diff view: word-level highlighting, toggle inline vs side-by-side

**Files:** `app/templates/*.html`, `app/static/css/style.css`, `app/static/js/wiki.js`, `app/static/images/`

---

### Stream E — SEO & Performance
**Status:** ✅ Basic SEO in place | 🔧 Needs structured data, performance hardening
**Owner:** Unassigned

Every millisecond of load time and every missing meta tag is traffic we're leaving on the table.

- [ ] Validate XML sitemap, submit to Google Search Console
- [ ] `robots.txt` route
- [ ] Canonical URLs on every page
- [ ] Breadcrumb navigation with BreadcrumbList JSON-LD
- [ ] JSON-LD: Article schema on articles, Person schema on bios, Event schema on competitions
- [ ] "Related Articles" section on each article (algorithmic, based on shared tags/links)
- [ ] Auto-detect internal link opportunities (scan article body for mentions of other article titles)
- [ ] RSS/Atom feed for recent changes
- [ ] Critical CSS inlining (extract above-the-fold styles, inline in `<head>`)
- [ ] CSS/JS minification pipeline
- [ ] Lazy-load all images, serve WebP with `<picture>` fallback
- [ ] Cache headers: static assets get far-future expires, HTML gets short TTL
- [ ] Lighthouse CI integration (fail build if Performance < 85)
- [ ] Social sharing meta (Twitter Card, Open Graph) with auto-generated preview images
- [ ] Privacy-friendly analytics (Plausible or Umami, not Google Analytics)

**Files:** `app/utils/seo.py`, `app/routes/main.py`, `app/templates/base.html`, `app/templates/wiki/view.html`

---

### Stream F — Content Pipeline, Unified Theory & SEO Keyword Strategy
**Status:** 📋 Planning → Active seeding | **PRIMARY FOCUS — Phase 1 priority**
**Owner:** Unassigned

Content is the product. The framework is just the delivery mechanism. The Unified Theory of Grappling (`UNIFIED_THEORY.md`) is the intellectual backbone — every article must be written with awareness of where its subject sits within the gameplay loop.

**Phase 1 Goal:** An article for every known jiu-jitsu technique and position, organized through the Unified Theory framework so the wiki functions as a system of understanding, not just a dictionary.

#### F.0 — Unified Theory Integration (DO THIS FIRST)
- [ ] Review and internalize `UNIFIED_THEORY.md` — the conceptual framework for all content
- [ ] Create the "Gameplay Loop" overview article: the master article that explains the full causal chain (neutral → grip fight → disruption → takedown → positional advancement → isolation → submission) with links to every phase
- [ ] Create the "Grips vs. Frames" concept article — the space management dichotomy (grips remove space / offensive; frames create space / defensive; every positional battle is a grip vs. frame exchange)
- [ ] Create the "Grip Fighting" concept article — the unifying micro-game thread
- [ ] Create the "Distance Spectrum" concept article — how ground positions map from far (standing/ground) to close (chest-to-chest)
- [ ] Create the "Orientation Axis" concept article — face-to-face vs. face-to-back and why back exposure is the worst-case scenario
- [ ] Create the "Tempo and Option Space" concept article — how attacks compress options, the rhythm of attack/defense, and how momentum flips
- [ ] Create the "Physics of Top Position" concept article — potential energy, force vectors, the balancing game of efficient control
- [ ] Create the "Isolation and Submission Mechanics" concept article — how limbs are separated from body cohesion and the four force vectors (extension, compression, torsion, arterial compression)

#### F.1 — Keyword-Prioritized Content Plan
- [ ] Research: compile top 200 grappling search terms by monthly volume (Ahrefs, SEMrush, or free alternatives)
- [ ] Create prioritized article pipeline: highest volume + lowest competition = write first
- [ ] Map each target keyword to an article title, category, target word count, and Unified Theory placement (which phase of the gameplay loop, which axes)
- [ ] Track keyword rankings over time as articles publish

#### F.2 — Technique & Position Seed (Phase 1: Complete Coverage)
- [ ] Finalize YAML schema for glossary entries (see Content Taxonomy and updated schema below)
- [ ] Build full technique/position corpus: Positions (~30), Submissions (~40), Sweeps & Passes (~25), Takedowns (~20), Concepts (~20+)
- [ ] Write import script (`scripts/import_glossary.py`) to convert YAML → Article records
- [ ] Create article templates per category type that include Unified Theory fields (gameplay loop phase, distance spectrum position, orientation, grip state, options compressed, tempo implications)
- [ ] Seed People (~25), Competitions (~15), Styles (~10) as secondary priority after all techniques/positions are covered

#### F.3 — Content Quality & Article Standards
- [ ] Write style guide: tone, structure, heading hierarchy, citation format, internal linking rules
- [ ] Every technique/position article must answer the 7 Unified Theory questions (see `UNIFIED_THEORY.md` → "How This Framework Applies to Articles")
- [ ] Every article must have: hand-written meta description, at least 3 internal links, proper heading hierarchy, category/tags assigned
- [ ] Every position article must specify: distance spectrum placement, orientation, key grips contested, options available to attacker and defender
- [ ] Every submission article must specify: force vector type (extension, compression, torsion, arterial), isolation mechanism, positions it's available from, common entries
- [ ] Article review checklist for editors (incorporating Unified Theory completeness check)

#### F.4 — Phase 2+ Expansion (500+ articles)
- [ ] Competition histories, biographical deep-dives, stylistic analysis articles
- [ ] Identify authoritative sources per subject area
- [ ] Build contributor onboarding flow for content writers (not just coders)
- [ ] Advanced Unified Theory articles: chain wrestling, guard retention systems, leg lock flow charts, passing taxonomies mapped to distance spectrum

**Files:** `UNIFIED_THEORY.md`, `content/glossary/*.yml`, `content/templates/`, `docs/style-guide.md`, `scripts/import_glossary.py`

---

### Stream G — Community, Moderation & Growth
**Status:** 📋 Planning — activates after content base is established
**Owner:** Unassigned

The wiki is only as good as the community that maintains it.

- [ ] User reputation / contribution scoring system
- [ ] Article quality ratings or review workflow
- [ ] @mentions in discussions
- [ ] Admin dashboard (stats, flags, user management)
- [ ] Content flagging / reporting system
- [ ] Email notification system (watchlist changes, discussion replies)
- [ ] Community guidelines / code of conduct
- [ ] Anti-vandalism: auto-revert, IP blocking, edit throttling
- [ ] Gamification: badges for edit milestones, quality contributions
- [ ] Outreach plan: r/bjj, BJJ forums, social media, grappling podcast outreach
- [ ] User campaign launch (only after content base is strong and SEO is ranking)

**Files:** `app/models/user.py`, `app/routes/admin.py` (new), `app/templates/admin/`, `docs/community-guidelines.md`

---

## Content Taxonomy

| Category | Description | Examples |
|---|---|---|
| **Technique** | Submissions, sweeps, passes, escapes, takedowns | Armbar, Triangle, Berimbolo, Double Leg |
| **Position** | Guards, pins, dominant positions, scramble states | Mount, Closed Guard, Side Control, Turtle |
| **Concept** | Principles, strategies, theories, Unified Theory pillars | Frames, Pressure, Grip Fighting, Tempo, Distance Spectrum |
| **Person** | Practitioners, instructors, competitors, pioneers | Helio Gracie, Marcelo Garcia, Gordon Ryan |
| **Competition** | Tournaments, rulesets, organizations | ADCC, IBJJF Worlds, EBI |
| **Glossary** | Terminology, Japanese/Portuguese terms, slang | Oss, Shrimping, Pulling Guard |
| **Style** | Martial arts disciplines | BJJ, Judo, Wrestling, Sambo, Catch Wrestling |

Technique subcategories: Submissions (chokes, joint locks, leg locks, compression), Sweeps, Guard Passes, Takedowns, Escapes, Transitions.

### Unified Theory Overlay

Every technique and position article maps onto the Unified Theory framework (see `UNIFIED_THEORY.md`):

| Unified Theory Axis | What It Captures | Values |
|---|---|---|
| **Gameplay Loop Phase** | Where this sits in the causal chain | Neutral, Grip Fight, Disruption, Takedown, Ground Position, Isolation, Submission |
| **Distance Spectrum** | Chest-to-chest distance (ground only) | Far (standing/seated), Mid (knee-based, open guards), Close (chest-to-chest pins) |
| **Orientation** | Facing relationship | Face-to-face, Face-to-back, Side-on |
| **Grip State** | Dominant grips contested in this position | Position-specific (e.g., underhook vs. whizzer, collar vs. sleeve) |
| **Options Compressed** | What the opponent can no longer do | Position-specific (e.g., "cannot hip escape toward underhook side") |
| **Tempo Direction** | Who has initiative | Attacker advantage, Neutral, Scramble |
| **Force Vector** | Submission finish mechanic (submissions only) | Extension, Compression/Wedge, Torsion, Arterial Compression |

## Glossary Entry Schema (YAML)

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
target_keyword: "armbar"
monthly_search_volume: 22000

# --- Unified Theory Fields ---
gameplay_loop_phase: submission
distance_spectrum: close       # attacker's hips tight to opponent's shoulder
orientation: face-to-face      # or face-to-back for belly-down armbar
force_vector: extension        # hyperextension of the elbow joint
isolation_mechanism: "Hips pinch the shoulder while legs control the torso, isolating the arm from the body's kinetic chain."
options_compressed: "Opponent cannot use the trapped arm for frames or grips. Torso rotation is restricted by leg pressure."
tempo_implications: "Terminal — if grip is secured with proper hip position, defender's options approach zero. Failed attempt returns to positional exchange."
grip_battle: "Attacker fights to control the wrist and break the defender's grip (clasped hands, pants grip). Defender fights to connect hands and create a unified structure to resist extension."
```

### Initial Seed Categories

- **Positions (~30):** Mount, Side Control, Back Mount, Closed Guard, Open Guard, Half Guard, Butterfly Guard, De La Riva, Spider Guard, Lasso Guard, X-Guard, Single Leg X, Rubber Guard, Worm Guard, Z-Guard, Knee Shield, Turtle, North-South, Knee on Belly, Headquarters, 50/50, Saddle/Inside Sankaku, Ashi Garami, Outside Ashi, Cross Ashi, Truck, Lockdown, Deep Half, Reverse De La Riva, Octopus Guard
- **Submissions (~40):** Armbar, Triangle Choke, RNC, Guillotine, Kimura, Americana, Omoplata, D'Arce, Anaconda, Ezekiel, Baseball Bat Choke, Bow and Arrow, Cross Collar Choke, Loop Choke, North-South Choke, Von Flue, Heel Hook, Toe Hold, Kneebar, Calf Slicer, Bicep Slicer, Wrist Lock, Gogoplata, Twister, Electric Chair, Banana Split, Buggy Choke, Straight Ankle Lock, Estima Lock, Mounted Triangle, Inverted Triangle, Peruvian Necktie, Japanese Necktie, Arm Triangle, Pace Choke, Suloev Stretch, Tarikoplata, Baratoplata, Monoplata
- **Sweeps & Passes (~25):** Scissor Sweep, Hip Bump, Flower Sweep, Pendulum, Tripod, Sickle, Balloon, Berimbolo, Kiss of the Dragon, Toreando, Knee Slice, Leg Drag, Over-Under, Stack Pass, Smash Pass, Long Step, Cartwheel Pass, X-Pass, Bull Fighter, Body Lock Pass, Headquarters Pass, Leg Weave, Folding Pass, Double Under
- **Takedowns (~20):** Double Leg, Single Leg, High Crotch, Fireman's Carry, Ankle Pick, Snap Down, Arm Drag, Duck Under, Osoto Gari, Ouchi Gari, Kouchi Gari, Seoi Nage, Harai Goshi, Uchi Mata, Tomoe Nage, Sumi Gaeshi, Guard Pull, Imanari Roll, Flying Armbar, Flying Triangle
- **Concepts (~20):** Frames, Underhooks, Overhooks, Pummeling, Shrimping, Bridging, Base, Posture, Pressure, Weight Distribution, Grip Fighting, Guard Retention, Leg Pummeling, Inside Position, Kuzushi, Connection, Wedges, Levers, Timing, Chain Wrestling
- **People (~25):** Helio Gracie, Carlos Gracie, Rolls Gracie, Rickson Gracie, Royce Gracie, Roger Gracie, Marcelo Garcia, Andre Galvao, Gordon Ryan, John Danaher, Craig Jones, Lachlan Giles, Mikey Musumeci, Keenan Cornelius, Leandro Lo, Buchecha, Bernardo Faria, Demian Maia, BJ Penn, Eddie Bravo, Dean Lister, Garry Tonon, Nicky Ryan, Meregali, Ffion Davies
- **Competitions (~15):** ADCC, IBJJF Worlds, Pan Ams, Europeans, ADCC Trials, EBI, Quintet, Polaris, WNO, Fight to Win, Copa Podio, Abu Dhabi Grand Slam, NAGA, Grappling Industries, SUG
- **Styles (~10):** BJJ, Judo, Freestyle Wrestling, Greco-Roman, Sambo, Combat Sambo, Catch Wrestling, Luta Livre, Shoot Wrestling, No-Gi Grappling

---

## Git Workflow

See `CONTRIBUTING.md` for the full guide.

- `main` is protected — no direct pushes
- Feature branches: `stream-x/description` (e.g., `stream-d/animation-system`)
- PRs require 1 review before merge
- Commits reference their stream: `[Stream D] Add scroll-triggered module reveals`
- Conventional commit style preferred
- **Every PR that completes a task must check the box in CLAUDE.md** — this updates the live kanban
- **Frontend PRs must pass the Manifesto check:** does it match the design system? Is it fast? Is it fluid?
- Before starting work, check `/roadmap` on the live site to see current project state

## Getting Started

```bash
git clone https://github.com/keenancornelius/grappling-wiki.git
cd grappling-wiki
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit with your settings
python run.py          # http://localhost:5000
```

## Conventions

- **Python:** PEP 8, enforced by flake8 + black
- **Templates:** Jinja2, CSRF on all POST forms, proper escaping
- **CSS:** Follow the Design Manifesto section above. No rogue colors or radii.
- **JS:** Vanilla only. No jQuery. No React. No frameworks. If you need a library, justify the bytes.
- **Commits:** `[Stream X] Short description`
- **Branches:** `stream-x/feature-name`
- **Content:** Markdown with standard heading hierarchy
- **Tests:** pytest, target >80% coverage on routes and models
- **Performance:** every PR checked against the Performance Standards table above
