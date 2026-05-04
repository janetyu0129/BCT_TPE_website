# NexaOS Design System Rules

## Project Overview

Single-file vanilla HTML/CSS/JS dashboard (`index.html`). No build system, no framework, no external dependencies. All styles are inline within the `<style>` block; all logic is inline within the `<script>` block.

---

## Figma MCP Integration

### Required Flow (do not skip steps)

1. Run `get_design_context` for the target node to get structured layout, color, and typography data
2. If the response is truncated, run `get_metadata` to map the node tree, then re-fetch specific child nodes individually
3. Run `get_screenshot` for a visual reference — use it as the source of truth throughout implementation
4. Download any assets returned (images, SVGs) — use `localhost` sources directly without modification
5. Translate the Figma output (React + Tailwind) into vanilla HTML + CSS custom properties matching this project's conventions
6. Validate the final result against the screenshot before marking complete

### Asset Rules

- IMPORTANT: If the Figma MCP server returns a `localhost` source for an image or SVG, use it directly
- IMPORTANT: Do NOT install or import any icon libraries — use Unicode/HTML entities as the project already does (e.g. `&#9638;`, `&#128200;`)
- IMPORTANT: Do NOT use placeholder images — if a real asset source is provided, use it

---

## Design Tokens

All tokens are CSS custom properties defined in `:root` inside the `<style>` block in `index.html`.

### IMPORTANT: Never hardcode raw hex values — always reference a CSS variable.

```css
:root {
  /* Backgrounds */
  --bg-base:     #080810;   /* page background */
  --bg-surface:  #0f0f1a;   /* sidebar, header */
  --bg-card:     #13131f;   /* card backgrounds */
  --bg-hover:    #1a1a2e;   /* hover states */

  /* Borders */
  --border:      #1e1e35;
  --border-light:#2a2a45;

  /* Purple scale */
  --purple-900:  #1a0a2e;
  --purple-800:  #2d1060;
  --purple-700:  #4a1fa8;
  --purple-600:  #6d28d9;
  --purple-500:  #8b5cf6;
  --purple-400:  #a78bfa;
  --purple-300:  #c4b5fd;
  --purple-200:  #ddd6fe;

  /* Accent helpers */
  --accent:      #8b5cf6;
  --accent-glow: rgba(139,92,246,.35);
  --accent-dim:  rgba(139,92,246,.12);

  /* Text */
  --text-primary:   #f1f0ff;
  --text-secondary: #9999bb;
  --text-muted:     #55557a;

  /* Status colors */
  --green:   #10b981;
  --red:     #f43f5e;
  --orange:  #f59e0b;
  --cyan:    #06b6d4;

  /* Layout */
  --sidebar-w: 240px;
  --header-h:  64px;
  --radius:    12px;
  --radius-sm: 8px;
}
```

If Figma introduces a new color not covered by existing tokens, **add it to `:root`** rather than hardcoding it inline.

---

## Component Patterns

All components are CSS classes. New components go in the `<style>` block, grouped by section with a comment header. HTML goes in `<body>`.

### Layout

| Class | Purpose |
|---|---|
| `.sidebar` | Fixed 240px left nav |
| `.main` | Right content area (`margin-left: var(--sidebar-w)`) |
| `.header` | Sticky top bar (`height: var(--header-h)`) |
| `.content` | Scrollable main content (`padding: 28px`, `gap: 20px`) |

### Cards

```html
<div class="card">
  <div class="card-header">
    <div>
      <div class="card-title">Title</div>
      <div class="card-sub">Subtitle</div>
    </div>
    <span class="card-action">Action &rarr;</span>
  </div>
  <div class="card-body">…</div>
</div>
```

### KPI Cards

```html
<div class="kpi-card">
  <div class="kpi-icon" style="background:rgba(139,92,246,.15)">&#128200;</div>
  <div class="kpi-label">Metric Name</div>
  <div class="kpi-value">$84.2K</div>
  <div class="kpi-change up">&#8593; 12.4% vs last month</div>
</div>
```

- Use `.up` (green) or `.down` (red) on `.kpi-change`
- Use `var(--accent-dim)` style backgrounds on `.kpi-icon`

### Navigation Items

```html
<a class="nav-item active">
  <i class="nav-icon">&#9638;</i> Label
  <span class="nav-badge">12</span>  <!-- optional -->
</a>
```

### Badges / Status

```html
<span class="badge badge-active">Active</span>
<span class="badge badge-trial">Trial</span>
<span class="badge badge-inactive">Inactive</span>
```

### Avatars

```html
<!-- Large (32px circle) -->
<div class="avatar">AL</div>

<!-- Small (28px circle, table rows) -->
<div class="av-sm" style="background:linear-gradient(135deg,#6d28d9,#a78bfa)">JK</div>
```

### Activity Feed

```html
<div class="feed">
  <div class="feed-item">
    <div class="feed-left">
      <div class="feed-dot" style="background:rgba(139,92,246,.2)">&#128640;</div>
      <div class="feed-line"></div>
    </div>
    <div class="feed-body">
      <div class="feed-text"><strong>Event</strong> description</div>
      <div class="feed-time">2 minutes ago &middot; Category</div>
    </div>
  </div>
</div>
```

### Grids

```css
.kpi-grid   { grid-template-columns: repeat(4, 1fr); }
.mid-grid   { grid-template-columns: 1fr 320px; }
.bottom-grid{ grid-template-columns: 1fr 1fr; }
```

All use `gap: 16px`.

### Charts

Charts are inline SVGs. Gradients and filters are defined in `<defs>`. Key IDs in use:

- `#barG` — vertical purple gradient for bar fills
- `#lineG` — horizontal purple-to-cyan gradient for line strokes
- `#glow` — feGaussianBlur + feMerge drop-shadow for dots/lines
- `#dg` — lighter glow used on donut segments

Do not duplicate these `id` values. If adding a second chart, use unique IDs (e.g. `#barG2`).

---

## Styling Rules

- IMPORTANT: Use CSS custom properties for all color, spacing, and radius values
- IMPORTANT: Never use inline `style` for colors — use a CSS class or `var(--token)`
- Exception: gradient backgrounds on `.av-sm` and `.kpi-icon` may use inline `style` with `var()` tokens
- Transitions: use `all .15s` for hover states, `all .2s` for card transforms
- Border radius: `var(--radius)` (12px) for cards, `var(--radius-sm)` (8px) for inputs/buttons
- Scrollbar: styled via `::-webkit-scrollbar` at the bottom of `<style>` — do not override

---

## Fonts & Typography

No external font library. System font stack:

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

| Use | Size | Weight |
|---|---|---|
| Section labels | 10px | 600, uppercase |
| Nav items | 14px | 500 |
| Card titles | 14px | 600 |
| Card subtitles | 12px | 400 |
| Table headers | 11px | 600, uppercase |
| Body / table | 13px | 400 |
| KPI values | 26px | 700, letter-spacing -1px |
| Logo | 18px | 700 |

---

## JavaScript

All JS lives in a single `<script>` block at the bottom of `<body>`. No modules, no bundler.

- Use `document.querySelectorAll` + `addEventListener` for interactions
- No external libraries (no jQuery, no Alpine, etc.)
- Keep logic minimal — visual state only (active nav item, tab switching)

---

## File Structure

```
/Users/yushiting/Claude/
  index.html   ← single source of truth: HTML + CSS + JS all inline
  CLAUDE.md    ← this file
```

New pages should be added as separate `.html` files in the same directory, importing shared tokens via a `<link rel="stylesheet">` to an extracted `tokens.css` if the project grows.

---

## Accessibility

- All interactive elements must have a visible focus state or `title` attribute
- Color contrast must meet WCAG AA (4.5:1 for text, 3:1 for UI elements)
- Use semantic HTML: `<aside>`, `<header>`, `<nav>`, `<main>`, `<table>` as already established
