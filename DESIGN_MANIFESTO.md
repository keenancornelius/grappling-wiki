# GrapplingWiki — Design Manifesto

> We weren't supposed to build this. No one asked for the world's most
> beautifully engineered grappling encyclopedia. We did it anyway.

---

## The Spirit

GrapplingWiki is not a database with a theme on top. It is a living, breathing
piece of software that should make people stop scrolling. Every pixel, every
transition, every micro-interaction exists to communicate one thing: **someone
who actually cares built this.**

We are freedom fighters with text editors. We are designers who roll. We are
engineers who understand that the armbar article should feel as precise as the
technique itself. If your commit doesn't move the needle toward something that
makes a visitor say *"wait, this is a wiki?"* — reconsider the commit.

---

## Design Principles

### 1. Speed Is a Feature

Nothing else matters if the page takes two seconds to load. We treat
performance as a design constraint, not an optimization pass.

- Target: sub-200ms server response, sub-1s full paint on 3G
- Zero render-blocking resources. Inline critical CSS. Async everything else.
- No heavy frameworks. Vanilla JS. Small, surgical libraries only when they
  earn their bytes (e.g., a 4KB animation library, not a 90KB one).
- Images are lazy-loaded, WebP, and sized to their container. No art
  department bloat.
- Every template gets a performance budget. If a page exceeds 100KB total
  transfer, it gets flagged in code review.

### 2. Fluid, Not Flashy

Animations exist to communicate state changes and guide attention — not to
show off. But within that constraint, they should be *gorgeous.*

- Page transitions: crossfade content regions, not full-page reloads where
  avoidable (use fetch + DOM swap for internal navigation).
- Click feedback: subtle scale + opacity pulse on interactive elements.
  Instant. Never more than 150ms.
- Scroll-triggered reveals: content modules fade/slide into place as they
  enter the viewport. Staggered timing. Eased curves. No bounce.
- Hover states: every clickable element responds. Underlines slide in. Cards
  lift with a hair of shadow. Buttons shift tone.
- Loading states: skeleton screens, not spinners. The layout is always
  present; only the data arrives.
- Diff views, history timelines, and search results should animate in as
  data streams — never pop.

### 3. Modular Information Architecture

Every page is composed of discrete, self-contained **modules** — cards,
panels, sections — that a user can scan, reorder mentally, and interact with
independently.

- Article pages: hero header module, table of contents module, content body,
  related techniques sidebar, revision metadata footer, discussion preview.
- Homepage: featured article spotlight, trending edits ticker, category
  grid, contribution call-to-action, live stats dashboard.
- Category pages: filterable grid of article cards with thumbnail, title,
  one-line summary, and tag chips.
- Each module has clear visual boundaries (spacing, not heavy borders),
  consistent internal padding, and a predictable interaction model.
- Modules should be draggable/collapsible where it makes sense (user
  preferences, admin dashboards). Progressive enhancement — works without JS,
  delights with it.

### 4. The Aesthetic: Underground Precision

The look is **black, white, and silver**. No pastels. No rounded-corner
friendliness. This is a tool built by people who understand leverage.

- Background: pure black (#0a0a0a) or near-black
- Text: clean white (#ffffff) with silver (#c0c0c0) for secondary content
- Accents: one single accent color used sparingly — electric white or a
  cold steel blue (#4a9eff) for links and focus states only
- Typography: Inter (or equivalent geometric sans). Tight letter-spacing on
  headings. Generous line-height on body text. Type hierarchy is king — if
  you can't tell the heading level by glancing, the type scale is broken.
- Edges: sharp. Zero border-radius on containers. Hairline borders
  (1px solid rgba(255,255,255,0.08)) to separate modules.
- Shadows: almost none. When used, they are tight and directional — not
  diffuse glows.
- Imagery: monochrome or desaturated. Photography (when we add it) gets a
  subtle grain filter. Illustrations are line-art, not filled shapes.
- Icons: stroke-based, thin, consistent weight. Lucide or Phosphor icon set.
  Never emoji in the UI.

### 5. Responsive by Default, Not by Afterthought

- Mobile is not a "smaller desktop." It is its own experience: swipe-friendly
  navigation, collapsible modules, bottom-anchored actions, touch-target
  sizing (min 44px).
- Tablet gets a two-column layout where desktop gets three. Not a squeezed
  desktop.
- Breakpoints: 480 / 768 / 1024 / 1440. Test all four. Every PR.
- The wiki editor on mobile must be usable. Full stop. If it's painful on a
  phone, it ships with a "desktop recommended" warning until we fix it.

### 6. The Editor Is the Product

Most wiki editors are an afterthought — a textarea with a submit button. Ours
should feel like a focused writing tool.

- Live preview (side-by-side on desktop, tabbed on mobile)
- Toolbar: bold, italic, heading, link, image, list, code, blockquote. Icons,
  not text labels. Keyboard shortcuts for everything.
- Autosave drafts to localStorage every 30 seconds
- Markdown syntax highlighting in the textarea itself (CodeMirror or similar,
  only if it stays under the performance budget)
- Edit conflict detection: if someone else edited while you were writing, show
  a diff and let the user merge
- The editor should feel like writing in a premium notes app, not filling out
  a government form

### 7. Delight in the Details

- 404 page: a grappling-themed "you got swept" illustration
- Loading states: skeleton shimmer that follows the module layout exactly
- Empty states: never a blank page — always a call to action ("This article
  doesn't exist yet. Be the first to write it.")
- Micro-copy: every button label, tooltip, and error message is written with
  personality. "Save changes" not "Submit." "Couldn't find that" not "Error 404."
- Transitions between pages should preserve scroll context where possible
- Search should feel instant — debounced autocomplete with highlighted matches

---

## Performance Standards

Every contributor should internalize these numbers:

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

If a PR degrades any metric past the hard limit, it does not merge until
the regression is resolved.

---

## Animation Specification

For consistency, all animations follow these curves and durations:

- **Micro-interactions** (hover, focus, click feedback): `120ms ease-out`
- **Module reveals** (scroll-triggered): `400ms cubic-bezier(0.16, 1, 0.3, 1)` with 60ms stagger between siblings
- **Page transitions** (content swap): `250ms ease-in-out` crossfade
- **Modals/overlays**: `200ms ease-out` scale from 0.97 + fade
- **Drawer/sidebar**: `300ms cubic-bezier(0.32, 0.72, 0, 1)` slide
- **Skeleton shimmer**: `1.5s ease-in-out infinite` horizontal gradient sweep

Use CSS transitions/animations by default. Only reach for the Web Animations
API or requestAnimationFrame when CSS cannot express the interaction.

Respect `prefers-reduced-motion`. If the user has reduced motion enabled, all
animations collapse to instant state changes (0ms duration, no transform).

---

## SEO as a Growth Engine

GrapplingWiki's primary traffic source is organic search. Every design and
engineering decision must account for this.

- Content-first rendering: all article content is in the initial HTML response.
  No client-side rendering of primary content. Ever.
- Semantic HTML5: `<article>`, `<nav>`, `<aside>`, `<section>`, `<header>`,
  `<footer>`, `<main>`. Screen readers and crawlers should parse our pages
  effortlessly.
- Structured data: JSON-LD on every article (Article schema), every person
  (Person schema), every competition (Event schema). Breadcrumbs on every page.
- Internal linking: every article body should link to related techniques,
  positions, and concepts. The more interconnected the content graph, the
  stronger the domain authority.
- Target the highest-volume keywords in the grappling niche first. The content
  pipeline (Stream F) prioritizes articles by search volume and competition
  score. If "rear naked choke" gets 40K monthly searches and we don't have
  that article, that's a bug.
- Page titles follow the pattern: `{Term} — GrapplingWiki` (clean, keyword-first)
- Meta descriptions are hand-written for every article, never auto-generated
  truncation.
- Canonical URLs on every page. No duplicate content.
- Image alt text is descriptive and keyword-aware, never decorative-only.

---

## For Every Contributor

Before you write a line of code, ask:

1. **Is it fast?** Will this add latency, bytes, or render-blocking work?
2. **Is it fluid?** Does the state change animate meaningfully, or does it pop?
3. **Is it modular?** Can this component live anywhere, or is it welded to one page?
4. **Is it precise?** Are the spacing, type, and color consistent with the system?
5. **Is it discoverable?** Will a search engine find and understand this content?

If any answer is "no" or "I don't know," stop and fix it before committing.

---

*This document is the north star. The codebase is the territory. Make them match.*
