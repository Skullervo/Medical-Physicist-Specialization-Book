# Sairaalafyysikko Platform — Design System & Redesign Specification

> **Purpose**: This document is a complete visual design specification for Claude Code to implement across the entire Django site. Drop this file into the project root and reference it when making CSS/template changes.

---

## 1. Design Philosophy

**Aesthetic direction**: "Nordic Observatory" — clean, dark, scientific precision meets Scandinavian restraint. Think: a high-end research instrument's control interface crossed with a well-designed dark-mode study app. Not flashy, not generic. Every element earns its pixel.

**Key principles**:
- **Depth through subtlety**: Use layered backgrounds with very slight transparency differences rather than heavy borders
- **Information density done right**: Medical physics is complex — design for scanability without sacrificing elegance
- **Purposeful color**: Each specialty has a signature color that appears consistently in accents, not backgrounds
- **Typography carries the hierarchy**: Size, weight, and spacing do most of the work — decoration is minimal
- **Motion with restraint**: Subtle transitions on interaction, no gratuitous animation

---

## 2. Color System

### 2.1 Background Layers (dark → light)

Replace the current palette entirely. The new backgrounds have a subtle cool blue undertone instead of pure grey:

```css
:root {
  /* Background hierarchy — 4 layers of depth */
  --bg-base:        #0f1219;    /* Page background, deepest */
  --bg-surface:     #161b26;    /* Cards, sidebar, main panels */
  --bg-raised:      #1c2333;    /* Elevated elements: dropdowns, modals, hover cards */
  --bg-overlay:     #232b3e;    /* Tooltips, floating menus, active states */

  /* Surface variants for interactive states */
  --bg-hover:       #1e2636;    /* Hover on surface elements */
  --bg-active:      #243044;    /* Active/pressed state */
  --bg-selected:    #1a2740;    /* Selected item background */
}
```

### 2.2 Border & Divider System

Move away from visible borders toward subtle dividers. Most containers should NOT have visible borders:

```css
:root {
  --border-subtle:    rgba(255, 255, 255, 0.06);   /* Default dividers */
  --border-default:   rgba(255, 255, 255, 0.10);   /* Visible when needed */
  --border-strong:    rgba(255, 255, 255, 0.15);   /* Input fields, focused */
  --border-accent:    rgba(99, 179, 237, 0.40);    /* Focus rings, active borders */
}
```

**Key change**: Replace `border: 1px solid #34495e` everywhere with either no border (use shadow + bg difference for depth) or `border: 1px solid var(--border-subtle)`.

### 2.3 Text Colors

```css
:root {
  --text-primary:    #e8edf5;    /* Headings, primary content */
  --text-secondary:  #94a3b8;    /* Body text, descriptions */
  --text-tertiary:   #64748b;    /* Labels, captions, metadata */
  --text-disabled:   #475569;    /* Disabled states */
  --text-inverse:    #0f1219;    /* Text on bright backgrounds */
}
```

### 2.4 Accent Colors — Specialty Palette

Each specialty gets ONE signature color used for icons, left-border accents, and interactive highlights:

```css
:root {
  /* Specialty signatures */
  --color-radiologia:    #60a5fa;   /* Cool blue — imaging */
  --color-sadehoito:     #34d399;   /* Emerald — radiation therapy */
  --color-isotooppi:     #a78bfa;   /* Violet — nuclear medicine */
  --color-knf:           #fb923c;   /* Amber — neurophysiology */
  --color-fysiologia:    #f87171;   /* Rose — clinical physiology */
  --color-anatomia:      #2dd4bf;   /* Teal — anatomy */

  /* Functional colors */
  --color-success:       #34d399;
  --color-warning:       #fbbf24;
  --color-error:         #f87171;
  --color-info:          #60a5fa;

  /* Primary action color */
  --color-primary:       #60a5fa;
  --color-primary-hover: #3b82f6;
  --color-primary-muted: rgba(96, 165, 250, 0.15);
}
```

### 2.5 Generating Muted Backgrounds from Accent Colors

For badges, tags, and specialty-tinted cards, use the accent color at very low opacity:

```css
/* Usage pattern: */
.badge-radiologia {
  background: rgba(96, 165, 250, 0.12);
  color: var(--color-radiologia);
}
```

---

## 3. Typography

### 3.1 Font Stack

Replace Inter with **Outfit** (display/headings) + **Source Sans 3** (body). These are distinctive but highly readable:

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --font-display:   'Outfit', sans-serif;
  --font-body:      'Source Sans 3', sans-serif;
  --font-mono:      'JetBrains Mono', monospace;
}
```

### 3.2 Type Scale

```css
:root {
  --text-xs:    0.75rem;     /* 12px — captions, timestamps */
  --text-sm:    0.8125rem;   /* 13px — metadata, small labels */
  --text-base:  0.9375rem;   /* 15px — body text (slightly larger than 14) */
  --text-md:    1.0625rem;   /* 17px — emphasized body */
  --text-lg:    1.25rem;     /* 20px — section titles */
  --text-xl:    1.5rem;      /* 24px — page headings */
  --text-2xl:   1.875rem;    /* 30px — hero headings */
  --text-3xl:   2.25rem;     /* 36px — landing page hero */
}
```

### 3.3 Application Rules

| Context | Font | Weight | Size | Color |
|---------|------|--------|------|-------|
| Page title (h1) | --font-display | 700 | --text-2xl | --text-primary |
| Section heading (h2) | --font-display | 600 | --text-xl | --text-primary |
| Card title (h3) | --font-display | 600 | --text-lg | --text-primary |
| Body text | --font-body | 400 | --text-base | --text-secondary |
| Labels / metadata | --font-body | 500 | --text-sm | --text-tertiary |
| Code / formulas | --font-mono | 400 | --text-sm | --color-primary |
| Navigation links | --font-body | 500 | --text-sm | --text-secondary |
| Button text | --font-display | 600 | --text-sm | (depends on variant) |

---

## 4. Spacing & Layout

### 4.1 Spacing Scale

```css
:root {
  --space-1:   4px;
  --space-2:   8px;
  --space-3:   12px;
  --space-4:   16px;
  --space-5:   20px;
  --space-6:   24px;
  --space-8:   32px;
  --space-10:  40px;
  --space-12:  48px;
  --space-16:  64px;
}
```

### 4.2 Border Radius

```css
:root {
  --radius-sm:   6px;
  --radius-md:   10px;
  --radius-lg:   14px;
  --radius-xl:   20px;
  --radius-full: 9999px;
}
```

**Change from current**: Slightly larger radii for a softer, more modern look. Cards use `--radius-lg`, buttons use `--radius-md`, badges use `--radius-full`.

### 4.3 Shadows

```css
:root {
  --shadow-sm:  0 1px 2px rgba(0, 0, 0, 0.2);
  --shadow-md:  0 2px 8px rgba(0, 0, 0, 0.25), 0 1px 2px rgba(0, 0, 0, 0.15);
  --shadow-lg:  0 8px 24px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2);
  --shadow-xl:  0 20px 48px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 20px rgba(96, 165, 250, 0.15);  /* For focused/highlighted elements */
}
```

### 4.4 Page Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│  HEADER (64px, sticky)                                   │
├────────┬───────────────────────────────────┬─────────────┤
│SIDEBAR │          MAIN CONTENT             │   TOC       │
│ 260px  │     max-width: 900px              │  220px      │
│        │     padding: 32px 40px            │  (optional) │
│        │                                   │             │
└────────┴───────────────────────────────────┴─────────────┘
```

- **Sidebar**: `width: 260px`, `bg: var(--bg-surface)`, no right border (use subtle shadow instead)
- **Main content**: centered within remaining space, `max-width: 900px` for reading views, `1200px` for dashboard/grid views
- **TOC**: `width: 220px`, only on EPA content pages

---

## 5. Component Specifications

### 5.1 Header

```
┌──────────────────────────────────────────────────────────┐
│ ⚛ Sairaalafyysikko          [Sisältö] [Tentit] [Quiz] [📊] │
└──────────────────────────────────────────────────────────┘
```

- Height: `64px`
- Background: `var(--bg-surface)` with `backdrop-filter: blur(12px)` and slight transparency
- Bottom edge: `box-shadow: 0 1px 0 var(--border-subtle)` — no visible border line
- Logo: Use `⚛` atom symbol (Unicode U+269B) or Font Awesome `fa-atom` in `var(--color-primary)`, size 1.5rem
- Title: "Sairaalafyysikko" in `--font-display` weight 700, letter-spacing: -0.02em
- Nav items: pill-shaped hover states (`border-radius: var(--radius-full)`, `background: var(--bg-hover)`)
- Active nav item: `background: var(--color-primary-muted)`, `color: var(--color-primary)`

### 5.2 Sidebar Navigation

- Background: `var(--bg-surface)`, separated from content by `box-shadow: 1px 0 0 var(--border-subtle)`
- **Section groups** (Radiologia, Sädehoito, etc.): Collapsible with smooth rotate animation on chevron
- **Section header**: `font-size: var(--text-xs)`, `text-transform: uppercase`, `letter-spacing: 0.08em`, `color: var(--text-tertiary)`, `margin-bottom: var(--space-2)`. Add a tiny colored dot (4px circle) in the specialty color before each group name.
- **Nav links**: `padding: 8px 12px`, `border-radius: var(--radius-md)`, no icons by default (text only for cleanliness). On hover: `background: var(--bg-hover)`. Active: `background: var(--color-primary-muted)`, left border 2px accent.
- Scrollbar: thin, matching `var(--border-subtle)` thumb on transparent track

### 5.3 Cards

**Standard Card** (used for stat boxes, specialty cards, exam cards):

```css
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  border-color: var(--border-default);
  box-shadow: var(--shadow-md);
}
```

No `transform: translateY()` on hover — it feels cheap. Use border brightening + shadow deepening instead.

**Stat Card** (dashboard numbers):

```css
.stat-card {
  /* Same as card but: */
  text-align: center;
  padding: var(--space-5) var(--space-6);
}
.stat-card .stat-value {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  /* Color varies: use specialty color or functional color */
}
.stat-card .stat-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-top: var(--space-1);
}
```

**Clickable Card** (specialty areas, exam topics):

Add a left-colored stripe (3px) in the specialty color. On hover, the stripe grows slightly brighter:

```css
.card-specialty {
  border-left: 3px solid var(--specialty-color);
  padding-left: calc(var(--space-6) - 3px);
}
```

### 5.4 Buttons

**Primary Button**:
```css
.btn-primary {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-sm);
  padding: 10px 20px;
  background: var(--color-primary);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background 0.15s ease, box-shadow 0.15s ease;
}
.btn-primary:hover {
  background: var(--color-primary-hover);
  box-shadow: 0 0 16px rgba(96, 165, 250, 0.25);
}
```

**Ghost Button** (secondary actions):
```css
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 10px 20px;
}
.btn-ghost:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-strong);
}
```

**Icon Button** (edit, delete, add section):
```css
.btn-icon {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--text-tertiary);
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-icon:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.btn-icon.danger:hover {
  background: rgba(248, 113, 113, 0.12);
  color: var(--color-error);
}
```

### 5.5 Badges & Tags

```css
.badge {
  font-family: var(--font-body);
  font-weight: 600;
  font-size: var(--text-xs);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
/* Example: year badge */
.badge-neutral {
  background: var(--bg-overlay);
  color: var(--text-tertiary);
}
/* Example: model answer available */
.badge-accent {
  background: rgba(167, 139, 250, 0.12);
  color: var(--color-isotooppi);
}
```

### 5.6 Form Inputs

```css
input[type="text"],
input[type="search"],
textarea,
select {
  font-family: var(--font-body);
  font-size: var(--text-base);
  padding: 10px 14px;
  background: var(--bg-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
input:focus, textarea:focus, select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.15);
}
input::placeholder {
  color: var(--text-disabled);
}
```

### 5.7 Lists & Question Rows

For the exam question list (`examquestion_area.html`):

```css
.question-row {
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-subtle);
  transition: background 0.12s ease;
}
.question-row:last-child {
  border-bottom: none;
}
.question-row:hover {
  background: var(--bg-hover);
}
```

No `onmouseover`/`onmouseout` inline JS for hover effects — use pure CSS `:hover`.

### 5.8 Modals

```css
.modal-backdrop {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
}
.modal-content {
  background: var(--bg-raised);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 640px;
  padding: var(--space-8);
}
```

---

## 6. Page-Specific Designs

### 6.1 Frontpage / Dashboard

**Layout**: Full-width content area (no sidebar on frontpage). Max-width 1100px, centered.

**Hero section** at top:
```
┌──────────────────────────────────────────────┐
│                                              │
│  Sairaalafyysikon                            │
│  Erikoistumiskirja                           │
│                                              │
│  Oppimisalusta sairaalafyysikon              │
│  erikoistumiskoulutukseen                    │
│                                              │
│  [Aloita opiskelu →]  [Tenttikysymykset]     │
│                                              │
└──────────────────────────────────────────────┘
```

- Title in `--font-display`, `--text-3xl`, weight 700
- Subtitle in `--text-md`, `--text-secondary`
- Background: subtle radial gradient from `var(--bg-raised)` center to `var(--bg-base)` edges
- Optional: very faint grid pattern overlay (opacity 0.03) for "scientific" feel

**Quick stats row** below hero:
- 4 stat cards in a row: Erikoisalat (6), EPA-kortit (34), Tenttikysymykset (487), Mallivastaukset
- Use the stat-card component

**Specialty grid** below stats:
- 6 cards in 2x3 grid (or 3x2 on wide screens)
- Each card has: colored left stripe, specialty icon, name, EPA count, progress indicator

### 6.2 EPA Content Pages (radiologia_ultraaani.html etc.)

**Layout**: Sidebar + Content + TOC (3-column)

- Sidebar shows specialty's EPA list
- Main content shows sections with edit/delete/add buttons
- TOC auto-generated from section titles
- Section headers: `--text-lg` in `--font-display`, with a small colored icon circle (32px) using the specialty color at 12% opacity with the icon inside

### 6.3 Exam Questions List (`examquestion_list.html`)

**Layout**: No sidebar, centered content max-width 1000px

- Stats bar: 4 stat cards (existing design, restyle with new tokens)
- Modality grid: cards with left-colored stripe, click to expand
- Remove all inline styles, use CSS classes

### 6.4 Exam Question Area (`examquestion_area.html`)

**Layout**: No sidebar, centered max-width 900px

- Back link at top (breadcrumb style, not just an arrow)
- Search input with focus glow effect
- Question rows in a card container, clean dividers
- Year/semester badges using the badge component
- "Harjoittele" button as ghost button variant

### 6.5 Quiz Home (`quiz_home.html`)

**Layout**: No sidebar, max-width 1100px

- Difficulty selector: radio buttons styled as toggle pills in a row
- Specialty grid: cards with EPA checkboxes
- Sticky bottom bar: more refined, with blur backdrop

### 6.6 Quiz Practice (`quiz_practice.html`)

**Layout**: Centered, max-width 700px (reading-focused)

- Score bar: compact, integrated into the top
- Question card: large, spacious padding
- Answer choices: pill-shaped, full-width, with radio/check indicators
- Correct answer: green left border glow
- Wrong answer: red left border glow
- Explanation section: muted blue left border accent

### 6.7 Progress Dashboard (`progress_home.html`)

**Layout**: No sidebar, max-width 1100px

- Stats grid at top (4 cards)
- Activity chart placeholder area
- EPA mastery grid with progress bars per specialty

### 6.8 Exam Templates (`exams_home.html`)

**Layout**: No sidebar, max-width 1100px

- Exam cards in a 2-column grid
- Each card: title, type badge, metadata row, start button
- Type badges: color-coded (official=green, practice=blue, mock=amber)

---

## 7. Transitions & Micro-interactions

Keep it minimal and fast:

```css
/* Standard transitions */
--transition-fast:  150ms ease;
--transition-base:  200ms ease;
--transition-slow:  300ms ease;
```

**Where to use transitions**:
- Card hover: border-color + box-shadow (200ms)
- Button hover: background + box-shadow (150ms)
- Nav link hover: background + color (150ms)
- Input focus: border-color + box-shadow (150ms)
- Sidebar collapse: height with ease-in-out (300ms)
- Modal open: opacity (200ms) + transform scale(0.98->1) (200ms)

**Where NOT to animate**:
- No translateY on card hover
- No scale transforms except modal open
- No color transitions on text
- No loading spinners beyond the existing FA spinner

---

## 8. Implementation Strategy

### 8.1 File Changes

1. **`sisalto/static/sisalto/css/modern-theme.css`**: Complete rewrite with new variables (Section 2-4 above)
2. **`sisalto/static/sisalto/css/site.css`**: Update layout rules to use new variables
3. **`sisalto/static/sisalto/css/header.css`**: Update header to new spec
4. **`sisalto/static/sisalto/css/components.css`**: Rewrite component library with new specs
5. **New file: `sisalto/static/sisalto/css/pages.css`**: Page-specific styles (dashboard, quiz, etc.)
6. **Templates**: Remove ALL inline `style=""` attributes and replace with CSS classes. This is critical — the current templates are full of inline styles.

### 8.2 Template Cleanup Priority

Templates should be updated to use semantic CSS classes instead of inline styles. Priority order:

1. `base.html` — remove inline debug styles, clean up
2. `examquestion_list.html` — heavy inline styling, convert to classes
3. `examquestion_area.html` — same
4. `quiz/quiz_home.html` — same
5. `quiz/quiz_practice.html` — same
6. `progress/progress_home.html` — same
7. `exams/exams_home.html` — same
8. `frontpage_new.html` — moderate inline styling
9. EPA content pages — less inline styling, mostly ok

### 8.3 CSS Loading Order in base.html

```html
<link rel="stylesheet" href="{% static 'sisalto/css/modern-theme.css' %}">
<link rel="stylesheet" href="{% static 'sisalto/css/site.css' %}">
<link rel="stylesheet" href="{% static 'sisalto/css/header.css' %}">
<link rel="stylesheet" href="{% static 'sisalto/css/components.css' %}">
<link rel="stylesheet" href="{% static 'sisalto/css/pages.css' %}">
```

### 8.4 Fonts Loading

Add to `base.html` `<head>`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### 8.5 Things to Preserve

- CKEditor integration (don't touch editor styles)
- MathJax rendering
- Font Awesome icons (keep the CDN link)
- All JavaScript functionality (section edit/delete/add, quiz logic, search)
- Django template tags and blocks structure
- CSRF token handling
- Mobile responsiveness (improve, don't break)

### 8.6 Things to Remove

- All inline `style=""` attributes in templates (move to CSS classes)
- All `onmouseover`/`onmouseout` inline event handlers (use CSS `:hover`)
- The `base_backup.html`, `base_new.html`, `base_new2.html` legacy templates
- Debug comments and unused CSS rules
- Any `!important` declarations in the main style blocks of `base.html`

---

## 9. Responsive Breakpoints

```css
/* Mobile first, then scale up */
@media (min-width: 640px)  { /* sm - tablets portrait */ }
@media (min-width: 768px)  { /* md - tablets landscape */ }
@media (min-width: 1024px) { /* lg - small laptops */ }
@media (min-width: 1280px) { /* xl - desktops, show sidebar */ }
@media (min-width: 1536px) { /* 2xl - wide screens, show TOC */ }
```

- Below 1024px: No sidebar, hamburger menu
- Below 1280px: No TOC
- Below 640px: Single column layouts, full-width cards

---

## 10. Quick Reference — CSS Class Naming

Use a simple, flat naming convention (not BEM, not utility-first):

```
.page-header          — page title area
.page-content         — main content wrapper
.stat-grid            — grid of stat cards
.stat-card            — individual stat
.stat-value           — big number
.stat-label           — small label under number
.card                 — base card
.card-specialty       — card with colored left stripe
.card-clickable       — card that's a link
.question-list        — container for question rows
.question-row         — individual question
.question-text        — question content
.question-meta        — badges/tags row under question
.badge                — base badge
.badge-year           — year badge
.badge-model-answer   — model answer badge
.btn                  — base button
.btn-primary          — primary action
.btn-ghost            — secondary action
.btn-icon             — icon-only button
.btn-danger           — destructive action
.nav-sidebar          — sidebar navigation
.nav-header           — header navigation
.nav-link             — navigation link
.nav-link.active      — active navigation link
.nav-group            — collapsible nav section
.nav-group-title      — section heading in nav
.form-input           — text input
.form-search          — search input with icon
.difficulty-pills     — difficulty selector group
.difficulty-pill      — individual difficulty option
.quiz-score-bar       — score display bar
.quiz-question        — question container
.quiz-choice          — answer choice
.quiz-result          — result feedback area
.modal                — modal container
.modal-backdrop       — modal overlay
.modal-header         — modal title area
.modal-body           — modal content
.modal-footer         — modal actions
```

---

## 11. Summary of Visual Changes

| Element | Before | After |
|---------|--------|-------|
| Background | `#1a252f` / `#2c3e50` | `#0f1219` / `#161b26` (deeper, bluer) |
| Borders | `#34495e` everywhere | Mostly invisible, shadow-based depth |
| Font | Inter only | Outfit (display) + Source Sans 3 (body) |
| Card hover | translateY(-2px) | Border brighten + shadow deepen |
| Buttons | Inline styles, inconsistent | Unified component classes |
| Color accent | `#3498db` flat blue | `#60a5fa` lighter, with glow effects |
| Inline styles | Hundreds of `style=""` | Zero — all in CSS files |
| Stat numbers | Font-weight only | Outfit display font, larger size |
| Section icons | Random emoji-style | Consistent 32px colored circle + FA icon |
| Hover effects | JS onmouseover | Pure CSS :hover |
| Border radius | 10-12px | 14px cards, 10px buttons, full pills |

---

## 12. Implementation Progress (päivitetty 2026-02-16)

> Tämä osio seuraa Nordic Observatory -design-järjestelmän toteutuksen edistymistä. Merkitse tehtävät valmiiksi sitä mukaa kun ne on tehty.

### 12.1 CSS-migraatio (Nordic Observatory)

Kaikki CSS-tiedostot päivitetty käyttämään uusia CSS-muuttujia. Vanhat muuttujanimet (`--bg-primary`, `--spacing-*`, `--accent-blue`) korvattu uusilla (`--bg-base`, `--space-*`, `--color-primary`). Transform-efektit (`translateY`, `scale`) poistettu hover-tiloista.

- [x] `modern-theme.css` — CSS-muuttujat, väripaletti, typografia (300+ riviä)
- [x] `components.css` — Komponenttikirjasto: kortit, napit, badget, lomakkeet, gridit (600+ riviä)
- [x] `site.css` — Layout, sidebar, TOC, scrollbar
- [x] `header.css` — Navigaatio, progress bar, save status, mobile menu
- [x] `chatbot.css` — AI-chatbot widget, viestikuplat, animaatiot
- [x] `modality.css` — EPA-korttien tyylit, proficiency-dropdown, section actions
- [x] `section-management.css` — Osionhallinta, modaalit, drag-and-drop
- [x] `base_editor.css` — Summernote dark theme, modaalit, taulukot, code blocks, MathJax
- [x] `base_summereditor.html` — Google Fonts (Outfit + Source Sans 3 + JetBrains Mono), CSS-latausjärjestys

### 12.2 Template-siivous (inline-tyylien poisto → CSS-luokat)

DESIGN_SPEC kohta 8.6: Poista kaikki `style=""` -attribuutit ja `onmouseover`/`onmouseout` -handlerit templateista.

- [ ] `base_summereditor.html` — Header inline-tyylit (`style="color: inherit"`, icon colors)
- [ ] `frontpage_new.html` — Dashboard-grid, stats-kortit, inline gradient-tyylit
- [ ] `examquestion_list.html` — Grid-layout, inline-tyylit → CSS-luokat
- [ ] `examquestion_area.html` — Filtterit, inline-tyylit
- [ ] `exam_practice.html` — Kysymyskortti, navigaationapit, feedback
- [ ] `epas.html` — EPA-listaus, erikoisalakorttien inline-tyylit
- [ ] `raportoi_ongelma.html` — Inline gradient-tyylit, osio-kortit
- [ ] `fysiologia_epas.html` — EPA-alasivulistan tyylit
- [ ] `radiologia_epas.html` — EPA-alasivulistan tyylit
- [ ] `sadehoito_epas.html` — EPA-alasivulistan tyylit
- [ ] `isotooppi_epas.html` — EPA-alasivulistan tyylit
- [ ] `knf_epas.html` — EPA-alasivulistan tyylit

### 12.3 Sivukohtaiset design-toteutukset (DESIGN_SPEC kohdat 6.1–6.8)

Jokainen sivu implementoidaan DESIGN_SPEC:n mukaisilla komponenteilla (`stat-grid`, `card-specialty`, `question-row`, `badge` jne.).

- [ ] **Dashboard** (`frontpage_new.html`) — stat-grid, card-specialty, welcome hero
- [ ] **EPA-sisältösivut** (33 kpl) — section-card refactor, yhtenäiset proficiency-dropdownit
- [ ] **Exam questions list** (`examquestion_list.html`) — question-row, badge system, filtterit
- [ ] **Exam question area** (`examquestion_area.html`) — kysymyskortit, vuosi/vaikeustaso-badget
- [ ] **Exam practice** (`exam_practice.html`) — vastauskortti, AI-feedback, navigaatio
- [ ] **Quiz home** (`quiz/quiz_home.html`) — kategoriakortit, tilastot
- [ ] **Quiz practice** (`quiz/quiz_practice.html`) — kysymys-UI, edistymispalkki (toiminnallinen: lopetuspainike + yhteenveto + älykäs kysymysvalinta toteutettu, inline-tyylit vielä siirrettävä CSS-luokiksi)
- [ ] **Progress dashboard** (`progress/progress_home.html`) — tilastokortit, grafiikat, spaced repetition (toiminnallinen: dashboard + viikkokaavio + EPA-edistyminen + SR-kertaus + saavutukset + heikot alueet + tenttivalmius toteutettu, inline-tyylit CSS-muuttujilla mutta vielä siirrettävä CSS-luokiksi)
- [ ] **Exams home** (`exams/exams_home.html`) — aihealuekortit, suoritusmerkinnät (toiminnallinen: simulaatio-CTA + Nordic Observatory -tyyli toteutettu)
- [ ] **Login** (`registration/login.html`) — toiminnallinen, Nordic Observatory inline-tyylit
- [ ] **Register** (`registration/register.html`) — toiminnallinen, Nordic Observatory inline-tyylit
- [ ] **Search results** (`search_results.html`) — toiminnallinen, Nordic Observatory inline-tyylit
- [ ] **Achievements** (`progress/achievements.html`) — toiminnallinen: earned/locked grid, Nordic Observatory inline-tyylit
- [ ] **Simulation setup** (`exams/simulation_setup.html`) — toiminnallinen: radio-valitsimet, Nordic Observatory inline-tyylit
- [ ] **Simulation active** (`exams/simulation_active.html`) — toiminnallinen: ajastin, kysymyskortit, AI-arvioinnin edistymispalkki
- [ ] **Simulation results** (`exams/simulation_results.html`) — toiminnallinen: pisteet, per-kysymys palaute, vahvuudet/heikkoudet

### 12.4 Uudet CSS-tiedostot

- [ ] `pages.css` — Sivukohtaiset tyylit (dashboard, quiz, exams, progress) kun templateit päivitetty

### 12.5 Yhteensopivuustestaus

Testaa jokaisen vaiheen jälkeen:

- [ ] Summernote-editori: toolbar, editointi, tallennus, kuvien lataus
- [ ] MathJax: inline-kaavat ($...$) ja display-kaavat ($$...$$) renderöityvät
- [ ] Kuvat: lataus, kuvatekstit, float left/right
- [ ] Taulukot: näkyvät oikein dark themessa
- [ ] Mobile: sidebar toggle, hamburger-menu, responsiivisuus
- [ ] Modaalit: avautuvat/sulkeutuvat, z-index oikein
- [ ] CSRF: getCookie() toimii, lomakkeiden tallennus
- [ ] Dark theme: yhtenäinen kaikilla sivuilla, ei "valkoisia välähdyksiä"
- [ ] Värikontrasti: WCAG AA (min 4.5:1 teksti, 3:1 isot elementit)
- [ ] Selaimet: Chrome/Edge, Firefox, mobile Chrome
