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
├── UNIFIED_THEORY.md       # Internal reference: how grappling works (positional hierarchy, distance, force vectors). Informs graph layout, not article requirements.
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

**Knowledge Graph: The Inverse Tree (Option Compression Model)**

The 3D knowledge graph is the visual crown jewel of GrapplingWiki. It is NOT a random cluster map — it is a **top-down inverse tree** that mirrors the Unified Theory's causal chain.

**Three Semantic Axes:**

| Axis | What it encodes | Negative | Zero | Positive |
|---|---|---|---|---|
| **X** | Guard leg reconnection spectrum | Most closed (legs locked around opponent) | Leg entanglements | Most open (feet on opponent, grips only) → Standing |
| **Y** | Optionality (the causal chain) | Top of tree = max options (standing) | — | Bottom of tree = end states (submissions/tap) |
| **Z** | Offense / defense spectrum | Defensive perspective (frames, retention, escapes) | Neutral | Offensive perspective (attacks, passes, submissions) |

**X-Axis Spectrum (left → right):**
Closed Guard → Half Guard → Deep Half → Knee Shield/Quarter Guard → Single Leg X / Ashi Garami (leg locks) → Lasso → De La Riva → Spider → Sit-up Guard → Wrestle-ups → Standing

This spectrum encodes how the guard player's legs connect: fully locked around the opponent (closed guard, leftmost) through progressively more open configurations to standing (rightmost). The spectrum wraps — far open guards can wrestle up back to standing.

The tree structure is canonical and must be maintained by every contributor.

**The Tree Structure:**

```
Standing Neutral (TOP — max optionality, both players on feet, Z=0)
├── Upper Body Takedowns (throws, clinch takedowns, Z+)
└── Lower Body Takedowns (single/double leg, ankle picks, Z+)
    │
    ├── GUARDS (sorted by leg reconnection on X — closed leftmost, open rightmost, Z-)
    │   ├── Close Distance Guards (Closed Guard, Rubber Guard) ← X far left
    │   ├── Mid Distance Guards (Butterfly, Half Guard, Z-Guard)
    │   ├── Leg Entanglements (Ashi Garami, Saddle, 50/50, Outside Ashi, Cross Ashi, Z≈0)
    │   └── Far Distance Guards (DLR, Spider, X-Guard, Lasso) → X right
    │
    ├── FRONT HEADLOCK (face-to-back, Z+, X far right — OPPOSITE of close guards)
    │   └── Guillotine, Darce, Anaconda, Peruvian Necktie, Japanese Necktie
    │
    └── PASSED / DOMINANT POSITIONS (BELOW guards on Y — passing is a step down the chain, Z+)
        ├── Side Control
        ├── Knee on Belly
        ├── Mount
        └── Back Control
            │
            └── SUBMISSIONS (BOTTOM — end states, color = force vector type)
                ├── Arterial (crimson): chokes — RNC, guillotine, darce, triangle
                ├── Extension (coral): hyperextension — armbar, kneebar
                ├── Torsion (amber): joint rotation — kimura, heel hook, toe hold
                └── Compression (teal): slicers — calf slicer, bicep slicer
```

**Structural Rules:**
1. Standing Neutral is ALWAYS the top node (highest Y value) — both players standing = highest average head height, maximum option space. Z=0 (neutral).
2. The tree branches downward through takedowns into either guards, front headlock, or passed positions. Takedowns are Z+ (offensive actions).
3. Guards are sorted horizontally on X by leg reconnection: closed (leftmost) → open (rightmost). Guards are Z- (defensive positions — the bottom player is maintaining/creating space).
4. **Leg entanglements are a guard subsystem** — they are guard positions where control is through leg-on-leg entanglement. They are the gateway to leg lock submissions. Z≈0 because entanglements are symmetrical (both players can attack, especially in 50/50).
5. **Front headlock is the offensive mirror of close guard** — same Y tier, opposite X (far right), Z+ (offensive). Face-to-back control from sprawls and snap downs. Gateway to guillotines, darces, anacondas, neckties.
6. Dominant positions (side control, mount, KOB, back control) sit BELOW guards on the Y axis — passing guard is a step further down the causal chain. Z+ (offensive — top player controls).
7. Submissions are colored by force vector type (NOT generic technique green). They connect ONLY to the Combat Zones they're available from. They are terminal endpoints — lightning strikes them as the final destination. Add new submissions to both `SUBMISSION_SLUGS` and `FORCE_VECTORS` in `graph-engine.js`.
8. Sweeps are NOT nodes — they are polarity flips (edges) that connect a guard to the dominant position achieved.
9. Passes are NOT nodes — they are distance compressions (edges) that connect a far guard to a closer position.
10. Person, Competition, and Style articles are EXCLUDED from the graph entirely — they are not part of the physical system.

**When adding a new article to the graph (`ARTICLE_CONNECTIONS` in `graph-engine.js`):**
- Determine which tree level(s) the technique belongs to
- Connect it to the appropriate Combat Zone node(s) from the table below
- **Submissions**: connect to every Combat Zone they're available from (e.g., armbar → `sys_close_guard`, `sys_mount`). Add slug to `SUBMISSION_SLUGS` AND classify in `FORCE_VECTORS` (arterial/extension/torsion/compression).
- **Front headlock submissions** (guillotine, darce, anaconda, neckties) connect to `sys_front_headlock`
- **Leg lock submissions** connect to `sys_leg_entangle`
- Sweeps connect to their guard of origin AND the dominant position they achieve
- Passes connect to their guard of origin AND the dominant position they land in

**Combat Zone IDs for article connections:**

| Node ID | Tree Level | Z Polarity | What connects here |
|---|---|---|---|
| `sys_standing` | Standing | 0 (neutral) | Standing concepts (grip fighting, stance, posture) |
| `sys_upper_td` | Takedowns | + (offense) | Judo throws, headlock takedowns, clinch-initiated takedowns |
| `sys_lower_td` | Takedowns | + (offense) | Double leg, single leg, ankle pick, low singles |
| `sys_far_guard` | Far Distance Guards | - (defense) | DLR, Spider, X-Guard, Lasso, RDLR |
| `sys_mid_guard` | Mid Distance Guards | - (defense) | Butterfly, Half Guard, Z-Guard, Knee Shield, Deep Half |
| `sys_close_guard` | Close Distance Guards | - (defense) | Closed Guard, Rubber Guard, Lockdown |
| `sys_leg_entangle` | Leg Entanglements | ≈0 (symmetrical) | Ashi Garami, Saddle/Inside Sankaku, 50/50, Outside Ashi, Cross Ashi |
| `sys_front_headlock` | Front Headlock | + (offense) | Guillotine, darce, anaconda, peruvian/japanese necktie. Face-to-back. Opposite of close guard on X axis. |
| `sys_side_control` | Dominant Positions | + (offense) | Side control, north-south, 100 kilos |
| `sys_mount` | Dominant Positions | + (offense) | Mount, S-mount, mounted crucifix |
| `sys_kob` | Dominant Positions | + (offense) | Knee on belly, knee on chest |
| `sys_back_control` | Dominant Positions | + (offense) | Back mount, rear body triangle, turtle (back exposure) |

**This model is a living framework.** As more articles are added and the system deepens, contributors should look for ways to refine the tree — splitting nodes when a category becomes too broad, adding new system nodes when a meaningful structural distinction emerges, and always asking: *does the graph accurately represent how the physical system of grappling actually works?*

**Knowledge Graph Color Philosophy:**

The graph's color system complements the core black/white/silver/steel-blue palette. Category colors are desaturated, cool-shifted accents:

| Category | Color | RGB | Rationale |
|---|---|---|---|
| Combat Zone nodes | Steel blue | `rgb(74, 158, 255)` | Primary accent, anchors the graph |
| Technique | Seafoam | `rgb(120, 210, 190)` | Cool green — active, physical |
| Position | Muted lavender | `rgb(160, 140, 220)` | Soft purple — spatial, structural |
| Concept | Warm silver | `rgb(200, 195, 150)` | Desaturated gold — intellectual |
| Glossary | Cool gray | `rgb(170, 170, 180)` | Neutral, reference-like |

**Force Vector Colors (Submissions):**

Submissions override category color with their force vector type. Each finish mechanic gets a distinct hue so you can read the damage type at a glance:

| Force Vector | Color | RGB | What it encodes |
|---|---|---|---|
| Arterial compression | Desaturated crimson | `rgb(190, 100, 100)` | Chokes — blood/air restriction (RNC, guillotine, darce, triangle) |
| Extension | Warm coral | `rgb(210, 140, 110)` | Hyperextension — armbar, kneebar, straight ankle lock |
| Torsion | Amber | `rgb(200, 175, 100)` | Joint rotation — kimura, americana, heel hook, toe hold |
| Compression/Wedge | Cool teal | `rgb(100, 180, 175)` | Crushing tissue against bone — calf slicer, bicep slicer |

**No rainbow palettes.** No full-saturation primaries. Every color must feel like it belongs on a #0a0a0a background next to steel blue.

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

### Stream H — Hosting, Integration & Persistent Infrastructure
**Status:** 🚨 BLOCKER — nothing persists until this is done
**Owner:** Unassigned
**Priority:** #1 — all other streams depend on this

GrapplingWiki is a sister brand to [Legion AJJ](https://legionajj.com) and [Legion San Diego](https://legionsandiego.com). The wiki drives organic search traffic → online instructional sales + gym membership leads. Current Render free tier uses ephemeral SQLite in `/tmp` — every deploy wipes all user-created content. This stream fixes that.

- [ ] Determine WordPress hosting type — is legionajj.com on shared hosting (Bluehost, SiteGround, etc.) or a VPS (DigitalOcean, Linode, etc.)? This determines whether Flask can run alongside WordPress or needs its own host.
- [ ] Set up persistent PostgreSQL database — provision a Postgres instance (Render managed DB, Neon, Supabase, or on the VPS). Get the `DATABASE_URL` connection string.
- [ ] Configure production to use Postgres — set `DATABASE_URL` env var on the hosting platform. The app already reads it in `config.py` — zero code changes needed, just the env var.
- [ ] Set up subdomain `wiki.legionajj.com` — add DNS CNAME/A record pointing to the wiki's host so the wiki shares Legion's domain authority for SEO.
- [ ] SSL certificate for subdomain — ensure HTTPS works on wiki.legionajj.com (Let's Encrypt or hosting provider's SSL).
- [ ] Verify persistence — create a test article, redeploy, confirm the article survives. This is the acceptance test for the entire stream.
- [ ] Cross-link Legion ↔ Wiki — add navigation links between legionajj.com and the wiki so users and search crawlers flow between them. "Powered by Legion AJJ" footer on wiki, "GrapplingWiki" link on Legion site.
- [ ] Shared branding pass — align wiki header/footer with Legion brand (logo, colors, CTAs for instructionals and gym sign-ups) so the sites feel like one ecosystem.
- [ ] Lead capture integration — add CTA modules on high-traffic wiki articles linking to Legion instructionals and gym trial sign-ups. These are the revenue conversion points.
- [ ] Analytics — set up privacy-friendly analytics (Plausible or Umami) on the wiki subdomain to track which articles drive traffic and which CTAs convert.

**Files:** `config.py`, `render.yaml`, DNS settings (external), hosting provider dashboard

---

### Stream A — Foundation & Infrastructure
**Status:** ✅ Scaffolded | 🔧 Needs hardening
**Owner:** Unassigned

The bones of the project. If this isn't solid, nothing else matters.

- [x] Choose and add open-source license — MIT license added to repo root so contributors know the terms
- [x] Write `Makefile` for common commands — `make run`, `make test`, `make lint`, `make format`, `make seed`, `make migrate` so no one has to memorize CLI incantations
- [x] Pre-commit hooks (black, isort, flake8) — auto-format and lint on every commit so code style is enforced without thinking
- [ ] Set up Flask-Migrate — enable `flask db migrate` / `flask db upgrade` so schema changes are versioned and deployable
- [ ] Create `.env.example` — document every environment variable (SECRET_KEY, DATABASE_URL, etc.) so new contributors can set up in one step
- [ ] GitHub Actions CI — run linting, tests, and performance budget checks on every PR so broken code can't reach main
- [ ] Refine Render deployment — ensure production config handles migrations on deploy, sets correct env vars, and restarts cleanly
- [ ] Structured logging — replace print statements with proper logging (request IDs, timestamps, levels) so production issues are debuggable
- [ ] Performance budget in CI — fail the build if any page exceeds 150KB total transfer, keeping the site fast as it grows

**Files:** `config.py`, `run.py`, `requirements.txt`, `Makefile`, `.github/workflows/ci.yml`, `.env.example`

---

### Stream B — Data Models & Database
**Status:** ✅ Models defined | 🔧 Needs migrations, indexes, seed data
**Owner:** Unassigned

The schema is the foundation of every query, every page load, every search result.

- [ ] Review and refine SQLAlchemy models — audit User, Article, ArticleRevision, Tag, and Discussion models for missing fields, bad relationships, or type issues before building on top of them
- [ ] Initialize Flask-Migrate and generate initial migration — so the database schema is version-controlled and deployable without manual SQL
- [ ] Add database indexes — slug lookups, full-text search columns, and created_at sorts so queries stay fast as the article count grows
- [ ] Seed script (`scripts/seed_db.py`) — create an admin user, initial category tags, and sample articles so a fresh install isn't an empty shell
- [ ] Model-level validation — enforce constraints (title length, slug format, required fields) in the models themselves, not just in forms, so the API and import scripts can't write bad data
- [ ] Watchlist model — let users subscribe to articles and get notified when edits happen, so active contributors can stay on top of pages they care about
- [ ] UserContribution summary table — pre-compute edit counts and recent activity per user so profile pages load instantly instead of running expensive queries
- [ ] Model unit tests (pytest) — verify relationships, constraints, and edge cases so model changes don't silently break things

**Files:** `app/models/*.py`, `migrations/`, `scripts/seed_db.py`, `tests/test_models.py`

---

### Stream C — Routes & Business Logic
**Status:** ✅ Scaffolded | 🔧 Needs edge cases, conflict detection, rate limiting
**Owner:** Unassigned

Every route is a user's entry point. It must be fast, correct, and graceful under weird inputs.

- [ ] End-to-end test — walk through the full article lifecycle (create → edit → view history → compare diffs → post on talk page) to catch integration bugs across routes
- [ ] Edit conflict detection — warn the user if someone else edited the article while they were writing, so edits don't silently overwrite each other
- [ ] Article watchlist notifications — let users see in-app alerts when watched articles are edited, so contributors can monitor pages without checking manually
- [ ] Article locking/protection — let admins lock critical articles (like core position pages) to editor-only editing, preventing drive-by vandalism
- [ ] Redirect system for renamed articles — when a title changes and the slug updates, auto-redirect the old URL so bookmarks and search engine links don't break
- [ ] Rate limiting (Flask-Limiter) — throttle edits and registration attempts so bots and bad actors can't spam the wiki
- [ ] Registration honeypot field — add a hidden form field that only bots fill in, blocking automated sign-ups without bothering real users with CAPTCHAs
- [ ] Search relevance scoring — improve result ranking so title matches, recent edits, and article completeness factor into search results instead of just raw text matching
- [ ] Integration tests for every route (pytest) — verify that each page returns correct status codes, renders expected content, and handles auth/permissions properly

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
- [ ] Live Markdown preview — show rendered HTML beside the textarea on desktop (tabbed on mobile) so authors see what their article looks like while writing
- [ ] Editor toolbar — icon buttons for bold, italic, heading, link, image, list, code, blockquote that insert Markdown syntax, so authors don't need to memorize formatting
- [ ] Keyboard shortcuts — Ctrl+S to save, Ctrl+B for bold, Ctrl+I for italic, etc. so power users can write without touching the mouse
- [ ] Autosave drafts to localStorage every 30s — protect against browser crashes and accidental navigation so no one loses a half-written article
- [ ] Markdown syntax highlighting in the textarea — color the raw Markdown (headings, links, bold) so the editing experience feels like a real writing tool, not a plain text box. Lightweight only (CodeMirror if < 40KB gzipped)
- [ ] Edit conflict warning UI — if someone else saved while you were editing, show a diff and let the user merge rather than silently overwriting their work

#### D.4 — Technique Graph Visualization
- [ ] Build the interactive technique graph — a 3D node graph where positions and techniques are nodes, transitions are edges, and submissions are terminal leaf nodes (no outbound edges). This is the visual centerpiece that shows how all of grappling connects.
- [ ] Color scheme for graph tiers — each level of the tree (standing, takedowns, guards, dominant positions, submissions) gets a distinct color so users can read the structure at a glance. Submissions colored by force vector type (chokes, hyperextensions, rotations, compressions).
- [ ] Sort nodes by tree position, not alphabetically — the graph should reflect how grappling actually flows (standing at top → submissions at bottom), not an arbitrary A-Z ordering
- [ ] Submission leaf node styling — submissions are endpoints (you win or reset), so they should look visually distinct from positions that have outbound transitions
- [ ] Make the graph explorable — click a node to navigate to the article; hover to see a preview card with title, category, and summary. The graph is a navigation tool, not just eye candy.
- [ ] Performance budget — graph must render within JS bundle limits (<40KB gzipped). Consider SVG or lightweight canvas. No heavy 3D libraries that blow the budget.
- [ ] `prefers-reduced-motion` — disable graph animations for users who have reduced motion enabled in their OS

#### D.6 — Categories Page Redesign

Replace the flat alphabetical category grid with a layout that mirrors how grappling actually works — the same tree structure used in the knowledge graph. Instead of 7 generic cards (Technique, Position, etc.), walk the user down the positional hierarchy: Standing → Takedowns → Guards → Dominant Positions → Submissions. A visitor who never touches the 3D graph should still absorb the structure of grappling just by scrolling this page.

**Layout (top → bottom, matching the graph's tree):**

1. **Standing Neutral** at top — links to standing concepts (grip fighting, stance, posture)
2. **Takedowns** — two columns: Upper Body (throws, clinch) | Lower Body (shots, ankle picks)
3. **Guards** — sorted left-to-right by distance: Close → Mid → Leg Entanglements → Far (matching the graph's X-axis). Sweeps and passes shown as transitions between tiers, not standalone cards.
4. **Dominant Positions** — Side Control | Knee on Belly | Mount | Back Control
5. **Submissions** — grouped by how they finish (chokes, hyperextensions, rotations, compressions) instead of alphabetically
6. **Concepts** woven into the tiers where they're relevant (Frames in the guard tier, Pressure in dominant positions, etc.)
7. **Reference Library** below the tree — compact cards for Person, Competition, Style, Glossary

- [ ] Redesign `/categories` route — query articles grouped by graph tier instead of just by tag, so the page reflects positional hierarchy
- [ ] Build tier-based `categories.html` template — vertical layout walking Standing → Takedowns → Guards → Dominant → Submissions so users see grappling's structure
- [ ] Guard distance ordering — sort guards left-to-right (close → mid → leg entangle → far) as a horizontal band matching the graph
- [ ] Submission grouping by finish type — organize submissions by how they work (chokes, hyperextensions, rotations, compressions) instead of A-Z
- [ ] Concept articles as contextual elements — place concepts within the tiers where they matter most, not in a separate generic bucket
- [ ] Reference Library section — Person, Competition, Style, Glossary as compact cards below the positional tree
- [ ] Collapsible tier modules — each tier section can expand/collapse (works without JS, enhanced with it)
- [ ] Visual flow indicators between tiers — show the directional relationship (standing flows to takedowns flows to guards, etc.)
- [ ] Article cards — title, one-line summary, category tag chip, and link. No thumbnails needed initially.
- [ ] Responsive — tiers stack vertically on mobile; guard distance band scrolls horizontally on small screens
- [ ] Performance budget — page stays under 150KB total, 40KB JS gzipped
- [ ] SEO — semantic HTML + BreadcrumbList JSON-LD
- [ ] `prefers-reduced-motion` — disable scroll reveals and flow animations

**Dependency:** Route needs a way to determine each article's tier. Can derive from category + subcategory, or mirror the `ARTICLE_CONNECTIONS` map from `graph-engine.js` server-side.

#### D.5 — Polish & Accessibility
- [ ] Logo and favicon — design a mark that works at 16px (favicon) and full size, so the site has a recognizable identity in browser tabs and bookmarks
- [ ] Responsive testing at all breakpoints (480 / 768 / 1024 / 1440) — verify every page looks right on phone, tablet, laptop, and desktop so nothing is broken for any screen size
- [ ] Mobile navigation — swipe-friendly menu, bottom-anchored actions, 44px touch targets so the site is usable one-handed on a phone
- [ ] Light mode toggle — dark is the default; add an optional light mode for users who prefer it (stretch goal)
- [ ] Print-friendly article styles — clean print stylesheet so users can print technique articles for gym use without UI chrome
- [ ] Accessibility audit — ARIA labels, focus management, keyboard navigation, screen reader testing so the wiki is usable for everyone
- [ ] Image upload for articles — let editors attach images (technique photos, diagrams) directly when editing, so articles aren't text-only
- [ ] Diff view improvements — word-level highlighting with toggle between inline and side-by-side views so editors can clearly see what changed between revisions

**Files:** `app/templates/*.html`, `app/static/css/style.css`, `app/static/js/wiki.js`, `app/static/images/`

---

### Stream E — SEO & Performance
**Status:** ✅ Basic SEO in place | 🔧 Needs structured data, performance hardening
**Owner:** Unassigned

Every millisecond of load time and every missing meta tag is traffic we're leaving on the table.

- [ ] Validate XML sitemap and submit to Google Search Console — make sure Google can discover and index every article so they show up in search results
- [ ] `robots.txt` route — tell crawlers what to index and what to skip (login pages, edit forms, etc.)
- [ ] Canonical URLs on every page — prevent duplicate content issues by telling search engines which URL is the "real" version of each page
- [ ] Breadcrumb navigation with BreadcrumbList JSON-LD — show users where they are in the site hierarchy and give Google rich breadcrumb snippets in search results
- [ ] JSON-LD structured data — Article schema on articles, Person schema on bios, Event schema on competitions so Google can display rich results (knowledge panels, event cards)
- [ ] "Related Articles" section on each article — algorithmically suggest related techniques/positions based on shared tags and links, keeping users exploring instead of bouncing
- [ ] Auto-detect internal link opportunities — scan article text for mentions of other article titles and suggest links, so the internal link graph stays dense as content grows
- [ ] RSS/Atom feed for recent changes — let users and aggregators subscribe to wiki activity without visiting the site
- [ ] Critical CSS inlining — extract above-the-fold styles and inline them in `<head>` so the page renders before the full stylesheet loads
- [ ] CSS/JS minification pipeline — strip whitespace and comments from production assets to reduce file size
- [ ] Lazy-load images with WebP + `<picture>` fallback — images only load when scrolled into view, in the smallest format the browser supports
- [ ] Cache headers — static assets get far-future expires (browser caches them), HTML gets short TTL (always fresh content)
- [ ] Lighthouse CI — fail the build if Performance score drops below 85, catching regressions before they ship
- [ ] Social sharing meta (Twitter Card, Open Graph) — when someone shares an article link, it previews with title, description, and image instead of a blank card
- [ ] Privacy-friendly analytics (Plausible or Umami) — track page views and referrers without cookies or personal data collection, so we know what content performs without invading privacy

**Files:** `app/utils/seo.py`, `app/routes/main.py`, `app/templates/base.html`, `app/templates/wiki/view.html`

---

### Stream F — Content Pipeline & SEO Strategy
**Status:** 📋 Planning → Active seeding | **PRIMARY FOCUS — Phase 1 priority**
**Owner:** Unassigned

Content is the product. The code is just the delivery mechanism. Phase 1 goal: an article for every known grappling technique and position, written well enough to rank in search and useful enough to be worth reading.

**Note on `UNIFIED_THEORY.md`:** This document is an internal reference that describes how grappling actually works — the positional hierarchy, distance spectrum, force vectors, etc. It informs how we arrange the knowledge graph and categorize articles, but it is NOT a framework we impose on users or require in article content. Think of it as our map of the territory, not a curriculum.

#### F.0 — Foundational Concept Articles
These articles explain the big-picture ideas that connect everything else on the wiki. They're valuable standalone content and high-traffic search targets.

- [ ] "How Grappling Works" overview article — the master article explaining the positional hierarchy from standing to submission, with links to every phase. This is the front door for new visitors.
- [ ] "Grips vs. Frames" concept article — explain the fundamental space management dichotomy (grips close distance, frames create it) that runs through every position
- [ ] "Grip Fighting" concept article — the micro-game that happens in every position, from standing collar ties to guard sleeve grips
- [ ] "Distance Management" concept article — how ground positions map from far (standing/open guard) to close (chest-to-chest pins) and why distance matters
- [ ] "Facing and Back Exposure" concept article — face-to-face vs. face-to-back and why giving up your back is the worst-case scenario in every ruleset
- [ ] "Tempo and Momentum" concept article — how attacks create pressure, how defense resets, and why initiative matters
- [ ] "Top Position Mechanics" concept article — weight distribution, pressure, base, and why gravity favors the top player
- [ ] "Submission Mechanics" concept article — the four ways submissions finish (chokes, hyperextensions, rotations, compressions) and the concept of isolating a limb from the body

#### F.1 — SEO Keyword Strategy
- [ ] Research top 200 grappling search terms by monthly volume — use Ahrefs, SEMrush, or free alternatives to find what people actually search for
- [ ] Create prioritized article pipeline — highest search volume + lowest competition = write first, so early articles have the best chance of ranking
- [ ] Map each keyword to an article title, category, and target word count — so content production has a clear queue instead of random selection
- [ ] Track keyword rankings over time — measure whether articles are actually ranking and adjust strategy based on results

#### F.2 — Technique & Position Seed (Phase 1: Complete Coverage)
- [ ] Finalize YAML schema for glossary/seed entries — define the fields each article type needs (see Content Taxonomy below) so bulk import is consistent
- [ ] Build the full technique/position corpus — Positions (~30), Submissions (~40), Sweeps & Passes (~25), Takedowns (~20), Concepts (~20+). This is the core content that makes the wiki worth visiting.
- [ ] Write import script (`scripts/import_glossary.py`) — convert YAML seed files into Article database records so content can be loaded in bulk
- [ ] Create article templates per category type — standardized structure for technique articles, position articles, concept articles, etc. so content has consistent quality
- [ ] Seed People (~25), Competitions (~15), Styles (~10) — secondary priority after techniques/positions are covered, but needed for a complete reference

#### F.3 — Content Quality & Article Standards
- [ ] Write style guide — document tone, structure, heading hierarchy, citation format, and internal linking rules so all articles read like they were written by the same team
- [ ] Minimum article requirements — every article needs: hand-written meta description, at least 3 internal links, proper heading hierarchy, and category/tags assigned
- [ ] Position article standard — should cover: where it sits in the positional hierarchy, key grips, what the top and bottom player are trying to do, and common transitions
- [ ] Submission article standard — should specify: how it finishes (choke, hyperextension, rotation, compression), which positions it's available from, common entries, and key defensive responses
- [ ] Article review checklist for editors — a quick checklist to verify completeness and quality before an article is considered "done"

#### F.4 — Phase 2+ Expansion (500+ articles)
- [ ] Competition histories, biographical deep-dives, and stylistic analysis articles — the reference content that makes the wiki comprehensive beyond just techniques
- [ ] Identify authoritative sources per subject area — build a source list so articles can cite credible references
- [ ] Contributor onboarding for content writers — a guide for non-coders who want to write articles, covering the editor, style guide, and review process
- [ ] Advanced system articles — chain wrestling, guard retention systems, leg lock flow charts, passing taxonomies. The deep-cut content for serious practitioners.

**Files:** `content/glossary/*.yml`, `content/templates/`, `docs/style-guide.md`, `scripts/import_glossary.py`

---

### Stream G — Community, Moderation & Growth
**Status:** 📋 Planning — activates after content base is established
**Owner:** Unassigned

The wiki is only as good as the community that maintains it.

- [ ] User reputation / contribution scoring — track edit counts and quality so active contributors are visible and recognized on their profiles
- [ ] Article quality ratings or review workflow — let editors flag articles as stub/draft/reviewed/featured so readers know what's reliable and contributors know what needs work
- [ ] @mentions in discussions — notify users when they're tagged in talk page threads so conversations don't die from missed replies
- [ ] Admin dashboard — centralized view of site stats, flagged content, and user management so admins can moderate without digging through the database
- [ ] Content flagging / reporting — let users flag vandalism, inaccuracies, or policy violations so bad edits surface quickly
- [ ] Email notifications — alert users when watched articles are edited or someone replies to their discussion thread, so engagement doesn't require daily manual checks
- [ ] Community guidelines / code of conduct — set expectations for contributor behavior so moderation has a clear reference point
- [ ] Anti-vandalism tools — auto-revert obvious vandalism, IP blocking, and edit throttling so one bad actor can't trash the wiki
- [ ] Gamification — badges for edit milestones and quality contributions so there's a visible reward for putting in the work
- [ ] Outreach plan — strategy for r/bjj, BJJ forums, social media, and grappling podcast outreach to build awareness once content is strong
- [ ] User campaign launch — only after the content base is solid and articles are ranking in search. Traffic proves the value; community sustains it.

**Files:** `app/models/user.py`, `app/routes/admin.py` (new), `app/templates/admin/`, `docs/community-guidelines.md`

---

## Content Taxonomy

| Category | Description | In Graph? | Examples |
|---|---|---|---|
| **Technique** | Submissions, sweeps, passes, escapes, takedowns | **YES** | Armbar, Triangle, Berimbolo, Double Leg |
| **Position** | Guards, pins, dominant positions, scramble states | **YES** | Mount, Closed Guard, Side Control, Turtle |
| **Concept** | Principles, strategies, theories, and mental models | **YES** | Frames, Pressure, Grip Fighting, Tempo |
| **Person** | Practitioners, instructors, competitors, pioneers | NO | Helio Gracie, Marcelo Garcia, Gordon Ryan |
| **Competition** | Tournaments, rulesets, organizations | NO | ADCC, IBJJF Worlds, EBI |
| **Glossary** | Terminology, Japanese/Portuguese terms, slang | NO | Oss, Shrimping, Pulling Guard |
| **Style** | Martial arts disciplines | NO | BJJ, Judo, Wrestling, Sambo, Catch Wrestling |

Technique subcategories: Submissions (chokes, joint locks, leg locks, compression), Sweeps, Guard Passes, Takedowns, Escapes, Transitions.

### Mandatory: Graph Placement for Every Technique, Position, and Concept Article

**Every article with category Technique, Position, or Concept MUST have an entry in `ARTICLE_CONNECTIONS` in `app/static/js/graph-engine.js`.** No exceptions. If an article exists in the database but has no graph connection, it floats in random space on the graph — that is a bug, not a feature.

When adding a new article, follow this sequence:

1. **Assign the correct category** (Technique, Position, or Concept). If it's Person, Competition, Style, or Glossary, it does not go in the graph.
2. **Determine the graph placement** by asking: where does this live in the inverse tree? Which system node(s) does it connect to?
3. **Classify the article's role in the tree:**
   - **Position articles** connect to their distance band (`sys_far_guard`, `sys_mid_guard`, `sys_close_guard`) or dominant position node (`sys_side_control`, `sys_mount`, `sys_kob`, `sys_back_control`).
   - **Submission articles** connect to their position of origin AND the relevant submission zone (`sys_guard_subs`, `sys_top_subs`, `sys_back_subs`). A submission that works from multiple positions connects to all of them.
   - **Sweep articles** connect to their guard of origin AND the dominant position achieved (the polarity flip destination).
   - **Pass articles** connect to the guard they defeat AND the position they land in (the distance compression destination).
   - **Takedown articles** connect to `sys_upper_td` or `sys_lower_td` based on whether they attack above or below the waist.
   - **Concept articles** connect to the system nodes where the concept is most actively contested.
4. **Add the connection** to `ARTICLE_CONNECTIONS` in `graph-engine.js`.
5. **Verify the graph** renders the article in the correct tree position.

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

# --- Graph Placement (required for Technique, Position, Concept) ---
# Maps to ARTICLE_CONNECTIONS in graph-engine.js.
# Determines where this article appears on the knowledge graph.
graph_nodes: ["sys_close_guard", "sys_mount"]
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
