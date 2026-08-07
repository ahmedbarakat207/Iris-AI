# Architecture B — Vanilla CSS with Custom Properties

Tags: architecture, vanilla-css, custom-properties, boilerplate, head-setup

Use this architecture when the brief wants a restrained, highly-controlled aesthetic,
when no CDN dependency is desired at all (fully offline-safe single file), or when the
design has few interactive states and benefits from precise, hand-written CSS rather
than utility classes. This is the architecture used by the Porsche dealership
reference example.

## Required `<head>` boilerplate

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Brand Name | One-line value proposition</title>
<style>
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --black: #0A0A0A;
  --dark-gray: #141414;
  --medium-gray: #1E1E1E;
  --light-gray: #2A2A2A;
  --lighter-gray: #3A3A3A;
  --white: #F5F5F5;
  --off-white: #E8E8E8;
  --text-muted: #8A8A8A;
  --accent: #4A7C59;
  --accent-hover: #5C9268;
  --accent-dark: #3A6147;
  --danger: #E74C3C;
  --success: #2ECC71;
  --radius: 8px;
  --radius-lg: 16px;
  --transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --shadow: 0 8px 32px rgba(0,0,0,0.4);
  --shadow-lg: 0 16px 48px rgba(0,0,0,0.5);
  --font-main: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
}

html { scroll-behavior: smooth; font-size: 16px; }
body { font-family: var(--font-main); background: var(--black); color: var(--white); line-height: 1.6; overflow-x: hidden; -webkit-font-smoothing: antialiased; }
a { text-decoration: none; color: inherit; transition: var(--transition); }
img { max-width: 100%; display: block; }
button { cursor: pointer; font-family: inherit; }

.container { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
.section { padding: 7rem 0; }
.section-header { text-align: center; margin-bottom: 4rem; }
.section-label { text-transform: uppercase; letter-spacing: 4px; font-size: 0.8rem; color: var(--accent); margin-bottom: 1rem; font-weight: 600; display: block; }
.section-title { font-size: 2.8rem; font-weight: 300; letter-spacing: -0.5px; line-height: 1.2; margin-bottom: 1rem; }
.section-title strong { font-weight: 700; }
.section-subtitle { color: var(--text-muted); font-size: 1.1rem; max-width: 600px; margin: 0 auto; }
</style>
</head>
```

### Key conventions

- **Every** color, radius, shadow, and transition curve is a custom property on
  `:root`. Nothing is a raw hex literal in component rules — this is what lets a
  whole site's palette be swapped by editing ~10 lines.
- `--transition` is defined once and reused everywhere (`transition: var(--transition);`)
  so easing feels consistent across every hover state in the file.
- Section rhythm is centralized: `.section { padding: 7rem 0; }` plus a consistent
  `.section-header` / `.section-label` / `.section-title` / `.section-subtitle` set
  used identically across every content section. This is what keeps a large
  hand-written page visually coherent without a utility framework.
- Prefer Google system fonts or a `<link>`-loaded Google Font; if the brief wants zero
  external requests at all, fall back to a system font stack as shown above
  (`'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif`).

## Reusable component classes worth defining up front

```css
.btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.9rem 2rem; border: none; border-radius: var(--radius); font-size: 0.95rem; font-weight: 600; letter-spacing: 0.5px; transition: var(--transition); text-transform: uppercase; }
.btn-primary { background: var(--accent); color: var(--black); }
.btn-primary:hover { background: var(--accent-hover); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(74,124,89,0.3); }
.btn-outline { background: transparent; color: var(--white); border: 2px solid var(--lighter-gray); }
.btn-outline:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-2px); }

.header { position: fixed; top: 0; left: 0; width: 100%; z-index: 1000; padding: 1.2rem 0; transition: var(--transition); }
.header.scrolled { background: rgba(10,10,10,0.95); backdrop-filter: blur(20px); padding: 0.8rem 0; box-shadow: 0 2px 30px rgba(0,0,0,0.5); }
```

Note the `--shadow` rgba should match the accent color's rgb so glows feel intentional
rather than a generic black shadow on every accent-colored element.

## Body structure convention

```html
<body>
  <header class="header" id="header">
    <div class="container header-inner"> <!-- logo, nav-list, menu-toggle --> </div>
  </header>

  <div class="overlay" id="overlay"></div> <!-- darkens page behind mobile nav/modal -->

  <section class="hero" id="hero"> ... </section>
  <section class="section" id="..."> ... </section>
  <!-- more sections, each toggled by scroll-spy nav -->

  <footer class="footer"> ... </footer>

  <div class="modal" id="vehicle-modal"> <!-- or whatever the detail modal is --> </div>

  <script>
    document.addEventListener('DOMContentLoaded', function () {
      // all wiring: header scroll class, nav active state, filters, modal, form
      // validation, carousel autoplay, reveal-on-scroll observer
    });
  </script>
</body>
```

## When to choose this architecture

- The brief wants a restrained, editorial, or luxury aesthetic where typography and
  whitespace do the work rather than dense utility-driven effects.
- No CDN dependency at all is desired (fully self-contained, works offline).
- The component count is moderate and benefits from named, reusable classes
  (`.model-card`, `.service-card`) rather than long utility-class strings repeated
  across many elements.
- Older browser support or stricter CSP environments are a concern (no third-party
  script tag required).
