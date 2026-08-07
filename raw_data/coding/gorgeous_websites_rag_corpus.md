# Gorgeous Single-File Websites — RAG Training Corpus

Combined corpus for retrieval-augmented generation. Each section below is delimited
by a '---' separator and a '## SOURCE: path' marker so a chunker can split on those
boundaries to recover the original document set if desired.

---
## SOURCE: 00_principles/00_INDEX.md

# RAG Corpus Index — Gorgeous Single-File Websites

This corpus trains a small coding model to generate beautiful, complete, single-file
HTML websites (HTML + CSS + vanilla JS, no build step, no frameworks required).

## Folder map

- `00_principles/` — design philosophy and decision rules. Retrieve these when the
  model needs to decide *what* to build (palette, type, spacing, motion, copy) before
  writing code.
- `01_architectures/` — the two reference CSS/JS architectures the model should choose
  between. Retrieve when starting a new file, to pick boilerplate and conventions.
- `02_patterns/` — small, self-contained, copy-adaptable code patterns (nav, hero, cards,
  modal, cart, filters, forms, carousel, footer, reveal-on-scroll, toasts). Retrieve when
  the model needs one specific component.
- `03_examples/` — 17 full, complete, single-file gorgeous website examples spanning many
  industries and both architectures. Retrieve as whole-example grounding when the model
  needs to see an entire page hang together, or when a niche close to the request exists.

## How to use this corpus at generation time

1. Identify the site's subject, audience, and single primary job (see
   `01_design_philosophy.md`).
2. Pick an architecture from `01_architectures/` — utility-class (Tailwind CDN) for
   fast iteration and animation-heavy interactivity, or vanilla CSS variables for
   maximum control over a very specific, restrained aesthetic.
3. Pull 2-4 patterns from `02_patterns/` that match the requested sections.
4. Adapt one close-niche example from `03_examples/` as a structural reference, but
   never copy its palette, copy, or signature element verbatim — every brief gets its
   own choices.
5. Build one complete, self-contained `.html` file. No external dependencies except
   Google Fonts and the Tailwind CDN script (when using the utility architecture).

## Non-negotiables learned from the reference examples

- Always a single `.html` file: inline `<style>`, inline `<script>`, no build tooling.
- Dark, premium palettes are common but not mandatory — match the palette to the brief.
- Every interactive site has: a sticky/fixed header that changes on scroll, scroll-reveal
  animations via `IntersectionObserver`, smooth-scroll anchor navigation, a mobile menu
  toggle, and real (not fake) interactivity for anything stateful (cart, filters, forms).
- Buttons, links, and inputs all get visible hover and focus states.
- Empty states (empty cart, no filter results) are designed, not left blank.
- Accessibility basics: `aria-label`s on icon-only buttons, `alt` text, keyboard-safe
  `:focus-visible` outlines, `prefers-reduced-motion` consideration on heavy animation.

---
## SOURCE: 00_principles/01_design_philosophy.md

# Design Philosophy — Making a Site "Gorgeous" Instead of "Generic"

Tags: philosophy, design-process, anti-template, planning

## The single most important rule

A gorgeous site is never a neutral container for content. Every choice — palette,
typeface pairing, spacing rhythm, the one animated moment — is made *for this specific
subject* and would look wrong on a different brief. If a choice would survive being
pasted into an unrelated site unchanged, it's a default, not a decision. Replace it.

Before writing a line of HTML, decide explicitly:

1. **Subject** — what is this, concretely? Not "an online store" but "a Japanese
   knife shop selling hand-forged carbon-steel blades to home cooks who've outgrown
   starter sets."
2. **Audience** — who is reading this, and what do they already believe or want?
3. **Single job** — what is the one thing this page must accomplish? A storefront's
   job is "make me want to own this object." A SaaS landing page's job is "make me
   believe this saves me time today."
4. **Signature element** — the one thing a visitor will remember and describe to a
   friend. Spend your boldness here. Keep everything else disciplined and quiet around it.

## Avoid the three AI-default looks

Generated sites cluster around three palettes regardless of subject. Notice if you're
defaulting into one and deliberately choose something else unless the brief specifically
calls for it:

1. Warm cream background (`#F4F1EA`-ish) + high-contrast serif display + terracotta accent.
2. Near-black background + a single bright acid-green or violet accent (this corpus's
   own Aethon example uses a version of this — vary the accent hue and warmth when
   generating new sites so the model doesn't memorize violet-on-black as "the" answer).
3. Broadsheet layout: hairline rules, zero border-radius, dense newspaper columns.

All three are legitimate *when the brief calls for them*. The failure mode is reaching
for one out of habit. A bakery, a children's coding camp, and a private equity fund
should never default to the same near-black-plus-violet template.

## Color systems that read as intentional

Define a palette as 4-6 named values, not "pick a background and a blue":

- A **canvas** color (the dominant background) — often a near-black, near-white, or a
  desaturated brand hue, with 2-3 tonal steps (`canvas`, `canvas-light`, `canvas-card`)
  so surfaces can sit on top of each other with visible depth.
- One **accent** color tied to the subject, not just "a nice color." A wine bar's
  accent might be a deep burgundy; a kids' STEM camp's might be a saturated orange;
  a private bank's might be a muted gold or forest green. Avoid violet/indigo as a
  reflexive default — it's overused in generated work.
- A **text** scale: full-opacity for headlines, 70-90% opacity (or a slightly muted
  hex) for body copy, 40-60% for captions/meta, 20-30% for fine print/disclaimers.
  Using opacity steps of a single white/black, rather than many unrelated grays, is
  what makes a dark or light UI feel cohesive rather than patchworked.
- A **state** set: success, danger/error, and sometimes warning — desaturate these
  slightly so they don't fight the brand accent for attention.

## Typography carries personality

Pick two, occasionally three, type roles and commit:

- **Display** — what headlines are set in. Allowed to have real personality: a
  condensed grotesque for something fast and technical, a humanist serif for
  something heritage or editorial, a heavy geometric sans for something bold and
  consumer-facing.
- **Body** — optimized for reading at small sizes. Often a clean grotesque/humanist
  sans even when the display face is a serif.
- **Utility/mono** (optional) — for prices, code, stats, timestamps, captions. A
  monospace or a tabular-figure sans signals "this number is precise."

Pair faces deliberately. Don't default to Inter-for-everything — that itself becomes
a tell. When Inter (or a similar grotesque) genuinely fits the brief, use it, but pick
the weight range and letter-spacing rhythm on purpose: e.g. extra-bold tight tracking
for a sneaker drop, light wide tracking for a minimalist skincare brand.

Set an explicit type scale with `clamp()` for hero headlines so they respond fluidly
between mobile and desktop, e.g.:

```css
.hero-title { font-size: clamp(2.5rem, 7vw, 6rem); line-height: 1; letter-spacing: -0.03em; }
```

## Spacing and rhythm

Use a consistent spacing scale (Tailwind's default scale or a custom 4px/8px-based
one) so paddings and gaps feel related rather than arbitrary. Sections typically get
generous vertical padding (`5-8rem` / `py-24` to `py-32` range) so the page breathes;
cramped sections are one of the fastest ways a site reads as unfinished.

Watch CSS specificity when sections and components share class names — a `.section`
rule and a more specific `.section.cta` rule can silently cancel padding/margin
declarations. Keep section spacing rules in one predictable place.

## Structure should mean something

Numbered steps (01 / 02 / 03), eyebrows ("OUR PROCESS"), and dividers are common in
generated sites — but only use a number when the content is genuinely sequential
(an actual process, a timeline, ranked results). If three feature cards have no real
order, don't fake one by numbering them; use icons or category labels instead.

## Motion is a deliberate choice, not a checklist

A gorgeous site usually has:

- A **page-load or hero moment** — a soft fade/slide-up, a subtle floating shape, a
  gradient that shifts slowly. Subtle, not bouncy.
- **Scroll-triggered reveals** via `IntersectionObserver`, applied to section content
  as it enters the viewport (fade + translateY, ~0.6-0.7s, a soft cubic-bezier).
- **Hover micro-interactions** on every clickable surface — cards lift or their image
  scales slightly, buttons get a subtle shimmer sweep or shadow glow, nav links grow
  an underline from the center outward.
- **One orchestrated signature moment** appropriate to the subject — e.g. a live
  filtering inventory grid for a dealership, a color-swatch picker for apparel, an
  animated stat counter for a fintech dashboard.

But restraint matters more than density. Scattered, competing animations are a strong
signal of "AI-generated." If every element pulses, floats, and glows, none of it reads
as intentional. Pick one or two animated ideas per page and execute them well; let
most of the page be still.

Always respect motion sensitivity where reasonably easy:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}
```

## Copy is design material

Never ship "Lorem ipsum" or generic placeholder copy ("Our Amazing Product") for a
finished deliverable — write real, specific copy as if the business exists:

- Headlines should say something only this business could say, grounded in its
  actual subject matter, not generic superlatives ("the best", "amazing", "world-class").
- Buttons name the action ("Shop the Drop", "Schedule a Test Drive", "Reserve a
  Table"), not a generic "Submit" or "Click Here".
- Empty states and errors speak in the product's voice and say what happened and
  what to do next — never just "Error" or a blank box.
- Microcopy (the line under a newsletter form, the caption under a price) is a real
  opportunity for personality, not boilerplate filler.

## Process checklist before writing code

1. Name the subject, audience, and single job in one or two sentences.
2. Sketch a palette (4-6 named hex values) and a type pairing (2-3 roles).
3. Decide the one signature element.
4. Sketch the section order as a short outline (hero → ... → footer).
5. Check the plan against the three AI-default looks — revise anything that's a
   reflex rather than a choice.
6. Only then write the HTML/CSS/JS, following the plan.

---
## SOURCE: 00_principles/02_motion_principles.md

# Motion & Interaction Principles

Tags: animation, transitions, easing, micro-interactions, scroll-reveal

## Standard easing curves seen across gorgeous sites

Reach for these instead of plain `ease` or `linear` — they read as considered:

```css
/* Snappy, slightly overshooting — good for cards, buttons, badges popping in */
cubic-bezier(0.34, 1.56, 0.64, 1)

/* Smooth deceleration — good for panel slides, drawers, reveal-on-scroll */
cubic-bezier(0.16, 1, 0.3, 1)

/* Standard material-style ease — good for general hover transitions */
cubic-bezier(0.25, 0.46, 0.45, 0.94)
```

## Timing guide

| Interaction | Duration | Notes |
|---|---|---|
| Button/link hover (color, background) | 0.2s–0.3s | fast, snappy |
| Card hover (lift, image scale) | 0.3s–0.4s | slightly slower than buttons |
| Drawer / panel slide-in | 0.3s–0.4s | use the decel curve |
| Scroll reveal (fade + translateY) | 0.6s–0.7s | slower, feels orchestrated |
| Toast in/out | 0.3s–0.4s | snappy in, slightly faster out |
| Ambient float / pulse loops | 4s–8s | slow, ambient, never distracting |
| Page transitions / hero load | 0.4s–0.8s, staggered | stagger children by ~80-150ms |

## Reveal-on-scroll pattern (vanilla JS, framework-agnostic)

CSS:

```css
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
```

JS:

```js
const revealElements = document.querySelectorAll('.reveal');
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
revealElements.forEach(el => revealObserver.observe(el));
```

For staggered grids (cards appearing one after another), add a small per-index delay
instead of (or in addition to) the observer:

```js
cards.forEach((card, i) => {
  setTimeout(() => card.classList.add('visible'), i * 80);
});
```

## Scroll-spy header and nav (sticky header that reacts to scroll position)

```js
const header = document.getElementById('site-header');
window.addEventListener('scroll', () => {
  if (window.scrollY > 80) {
    header.classList.add('scrolled'); // apply blurred glass background + shadow
  } else {
    header.classList.remove('scrolled');
  }
}, { passive: true });
```

Pair with a section-aware nav-link highlighter:

```js
const navLinks = document.querySelectorAll('.nav-link');
const sections = document.querySelectorAll('section[id]');
const navObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      navLinks.forEach(link => {
        link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
      });
    }
  });
}, { threshold: 0.3, rootMargin: '-80px 0px -50% 0px' });
sections.forEach(s => navObserver.observe(s));
```

## Hover micro-interactions worth having

- **Underline-grow nav links**: a `::after` pseudo-element, `width: 0` at rest,
  `width: 100%` on hover/active, transition with the decel curve, anchored from center
  (`left: 50%; transform: translateX(-50%)`) so it grows outward symmetrically.
- **Card lift + image zoom**: on `.card:hover`, lift the card (`translateY(-4px)` to
  `-8px`) and slightly scale an inner image (`scale(1.05)` to `1.08`) — scale the
  image, not the whole card, so the card border/shadow stays crisp.
- **Button shimmer sweep**: a `::before` pseudo-element with a diagonal translucent
  gradient that slides from `-100%` to `100%` of the button's width on hover.
- **Color swatch / chip selection**: scale up slightly and add a ring/outline offset
  from the background to indicate selection, distinct from plain hover state.
- **Icon buttons (cart, wishlist, menu)**: background fades in on hover
  (`bg-white/5` → slightly stronger), icon color shifts toward the accent.

## Stateful UI feedback patterns

- **Badge pop**: when a count increases (cart badge), retrigger a `scale(0) → scale(1)`
  pop animation by removing and re-adding the animation (`el.style.animation = 'none'; el.offsetHeight; el.style.animation = '...';`).
- **Toast notifications**: slide in from off-screen (`translateX(120%) → 0`), pause
  ~2-3 seconds, then animate out and remove from the DOM. Stack multiple toasts in a
  fixed-position container with `flex-direction: column; gap`.
- **Loading/skeleton states**: a shimmering gradient background
  (`background-size: 200% 100%`, animated `background-position`) communicates "content
  is coming" better than a blank space or spinner alone for card-shaped content.

## Restraint rule

Each additional simultaneously-animating element divides the attention given to all
others. A page with one slowly breathing gradient blob, clean scroll reveals, and crisp
hover states reads as premium. A page where the blob pulses, the heading has a shimmer,
the button glows, and three icons spin all at once reads as unfinished, however
technically each effect was implemented correctly. When in doubt, cut.

---
## SOURCE: 01_architectures/01_tailwind_utility_architecture.md

# Architecture A — Tailwind CDN + Utility Classes

Tags: architecture, tailwind, boilerplate, head-setup

Use this architecture when the site is animation-heavy, has lots of small interactive
states (badges, swatches, drawers), or benefits from rapid utility-class iteration.
This is the architecture used by the "Aethon" storefront reference example.

## Required `<head>` boilerplate

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BRAND — One-line value proposition</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            canvas: { DEFAULT: '#0B0A09', light: '#15130F', lighter: '#1E1B16', card: '#171410' },
            accent: { DEFAULT: '#C9874A', hover: '#DA9A5C', glow: 'rgba(201,135,74,0.3)' },
            surface: { DEFAULT: '#211D17', light: '#2C2620' }
          },
          fontFamily: {
            sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            display: ['Fraunces', 'serif']
          },
          animation: {
            'slide-in': 'slideIn 0.4s cubic-bezier(0.16,1,0.3,1)',
            'fade-in': 'fadeIn 0.3s ease-out',
            'float': 'float 6s ease-in-out infinite',
            'badge-pop': 'badgePop 0.3s cubic-bezier(0.34,1.56,0.64,1)'
          },
          keyframes: {
            slideIn: { '0%': { transform: 'translateX(100%)' }, '100%': { transform: 'translateX(0)' } },
            fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
            float: { '0%,100%': { transform: 'translateY(0px)' }, '50%': { transform: 'translateY(-10px)' } },
            badgePop: { '0%': { transform: 'scale(0)' }, '100%': { transform: 'scale(1)' } }
          }
        }
      }
    }
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Fraunces:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    /* hand-written CSS for anything Tailwind utilities can't express cleanly:
       gradients, pseudo-elements, custom keyframes, glass effects, fluid type */
  </style>
</head>
```

### Key conventions

- Define the brand palette **inside `tailwind.config`**, not just as raw hex in
  classes, so `bg-accent`, `text-accent`, `border-accent/30` etc. all stay consistent
  and themeable from one place.
- `canvas` / `canvas-light` / `canvas-lighter` / `canvas-card` give you a tonal ramp
  for stacking surfaces (page background → header glass → card → modal).
- Always define an `accent` with `DEFAULT`, `hover`, and `glow` (an rgba version for
  box-shadows) so CTAs have a consistent hover and glow treatment.
- Pick **two font roles** in `fontFamily`: `sans` for body/UI text, and either `sans`
  again or a contrasting `display` face for headlines (a serif/slab paired against a
  grotesque sans reads as more designed than two grotesques).
- Put true custom CSS — gradients, `::before`/`::after`, `backdrop-filter`, custom
  cubic-beziers not in Tailwind's default set, fluid `clamp()` type — in the `<style>`
  block. Don't fight Tailwind to express things it's not built for.

## Always-include utility CSS snippets

```css
* { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
body { font-family: 'Inter', system-ui, -apple-system, sans-serif; overflow-x: hidden; }
::selection { background: rgba(201,135,74,0.3); color: #fff; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #15130F; }
::-webkit-scrollbar-thumb { background: #2C2620; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #C9874A; }

.glass { background: rgba(21,19,15,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
.glass-light { background: rgba(255,255,255,0.03); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }

.gradient-text {
  background: linear-gradient(135deg, #ffffff 0%, #C9874A 50%, #ffffff 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  background-size: 200% auto; animation: gradientShift 4s ease-in-out infinite;
}
@keyframes gradientShift { 0%,100% { background-position: 0% center; } 50% { background-position: 100% center; } }

input:focus, button:focus-visible { outline: 2px solid #C9874A; outline-offset: 2px; }

.hero-title { font-size: clamp(2.5rem, 7vw, 6rem); line-height: 1; letter-spacing: -0.03em; }
.hero-sub { font-size: clamp(1rem, 2vw, 1.35rem); }

.reveal { opacity: 0; transform: translateY(30px); transition: all 0.7s cubic-bezier(0.16,1,0.3,1); }
.reveal.visible { opacity: 1; transform: translateY(0); }
```

## Body structure convention

```html
<body class="bg-canvas text-white min-h-screen">
  <div id="toast-container" class="fixed top-6 right-6 z-[100] flex flex-col gap-3"></div>

  <header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
    <!-- glass nav bar, see 02_patterns/01_navigation.md -->
  </header>

  <main>
    <!-- <section> per content block, each with consistent vertical padding (py-24 lg:py-32) -->
  </main>

  <footer class="border-t border-white/5 bg-canvas-light">
    <!-- see 02_patterns/08_footer.md -->
  </footer>

  <script>
    (function() {
      // all page state + rendering + event wiring in one IIFE, see 02_patterns for specifics
    })();
  </script>
</body>
```

## When to choose this architecture

- The brief implies a product grid, cart, wishlist, filters, or other multi-state
  interactive commerce/app-like experience.
- The brief wants heavy use of glassmorphism, gradient text, glow effects, or a dense
  animation vocabulary — Tailwind's utility classes make rapid iteration on these
  much faster than hand-rolled CSS.
- Speed of generation matters more than absolute control over every CSS rule.

---
## SOURCE: 01_architectures/02_vanilla_css_architecture.md

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

---
## SOURCE: 02_patterns/01_navigation_header.md

# Pattern — Navigation Header

Tags: pattern, header, navigation, mobile-menu, scroll-spy, sticky

A gorgeous header is fixed/sticky, starts mostly transparent or lightly glassy over the
hero, and gains a stronger glass/blur background once the user scrolls. It includes a
logo, centered or left-aligned nav links, a right-aligned action cluster (icons or
CTA button), and a mobile hamburger menu that slides/expands open.

## Utility-class version (Tailwind architecture)

```html
<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="glass border-b border-white/5">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 lg:h-20">
        <button id="mobile-menu-btn" class="lg:hidden p-2 -ml-2 text-white/70 hover:text-white transition-colors" aria-label="Open menu">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
        <a href="#" class="flex items-center gap-2 group">
          <span class="text-xl font-bold tracking-tight lg:text-2xl group-hover:text-accent transition-colors duration-300">BRAND</span>
        </a>
        <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
          <a href="#shop" class="nav-link active text-sm font-medium text-white/90 hover:text-white transition-colors tracking-wide uppercase">Shop</a>
          <a href="#about" class="nav-link text-sm font-medium text-white/50 hover:text-white transition-colors tracking-wide uppercase">About</a>
          <a href="#contact" class="nav-link text-sm font-medium text-white/50 hover:text-white transition-colors tracking-wide uppercase">Contact</a>
        </nav>
        <div class="flex items-center gap-1 sm:gap-3">
          <button class="p-2.5 rounded-full text-white/60 hover:text-white hover:bg-white/5 transition-all duration-200" aria-label="Search">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
  <div id="mobile-nav" class="hidden lg:hidden glass border-b border-white/5">
    <div class="max-w-7xl mx-auto px-4 py-6 flex flex-col gap-4">
      <a href="#shop" class="text-lg font-medium text-white/90 hover:text-accent transition-colors">Shop</a>
      <a href="#about" class="text-lg font-medium text-white/50 hover:text-accent transition-colors">About</a>
      <a href="#contact" class="text-lg font-medium text-white/50 hover:text-accent transition-colors">Contact</a>
    </div>
  </div>
</header>
```

Underline-grow nav-link CSS:

```css
.nav-link { position: relative; }
.nav-link::after {
  content: ''; position: absolute; bottom: -4px; left: 50%; width: 0; height: 1.5px;
  background: #C9874A; transition: all 0.3s cubic-bezier(0.16,1,0.3,1); transform: translateX(-50%);
}
.nav-link:hover::after, .nav-link.active::after { width: 100%; }
```

Mobile toggle JS (swaps hamburger ↔ close icon, closes on link click):

```js
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileNav = document.getElementById('mobile-nav');
mobileMenuBtn.addEventListener('click', () => {
  mobileNav.classList.toggle('hidden');
});
mobileNav.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => mobileNav.classList.add('hidden'));
});
```

Scroll-reactive header background:

```js
const header = document.getElementById('site-header');
window.addEventListener('scroll', () => {
  if (window.scrollY > 80) {
    header.style.background = 'rgba(8,8,10,0.85)';
    header.style.backdropFilter = 'blur(20px)';
    header.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
  } else {
    header.style.background = '';
    header.style.backdropFilter = '';
    header.style.borderBottom = '';
  }
}, { passive: true });
```

## Vanilla-CSS version (custom-properties architecture)

```html
<header class="header" id="header">
  <div class="container header-inner">
    <a href="#" class="logo">
      <div class="logo-icon">B</div>
      <span>Brand</span>
    </a>
    <nav class="nav" id="nav">
      <ul class="nav-list">
        <li><a href="#hero" class="active">Home</a></li>
        <li><a href="#products">Products</a></li>
        <li><a href="#about">About</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
    </nav>
    <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>
<div class="overlay" id="overlay"></div>
```

```css
.header { position: fixed; top: 0; left: 0; width: 100%; z-index: 1000; padding: 1.2rem 0; transition: var(--transition); }
.header.scrolled { background: rgba(10,10,10,0.95); backdrop-filter: blur(20px); padding: 0.8rem 0; box-shadow: 0 2px 30px rgba(0,0,0,0.5); }
.logo-icon { width: 40px; height: 40px; background: var(--accent); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; color: var(--black); }
.nav-list { display: flex; list-style: none; gap: 2.5rem; align-items: center; }
.nav-list a { font-size: 0.9rem; font-weight: 500; letter-spacing: 1px; text-transform: uppercase; position: relative; padding: 0.25rem 0; }
.nav-list a::after { content: ""; position: absolute; bottom: -2px; left: 0; width: 0; height: 2px; background: var(--accent); transition: var(--transition); }
.nav-list a:hover::after, .nav-list a.active::after { width: 100%; }
.menu-toggle { display: none; flex-direction: column; gap: 5px; background: none; border: none; padding: 4px; z-index: 1001; }
.menu-toggle span { width: 24px; height: 2px; background: var(--white); transition: var(--transition); display: block; }
@media (max-width: 900px) {
  .nav-list { display: none; } /* replaced by a slide-out panel toggled with .open */
  .menu-toggle { display: flex; }
}
```

```js
const header = document.getElementById('header');
const menuToggle = document.getElementById('menu-toggle');
const nav = document.getElementById('nav');
const overlay = document.getElementById('overlay');

function toggleMenu() {
  menuToggle.classList.toggle('active');
  nav.classList.toggle('open');
  overlay.classList.toggle('active');
  document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
}
menuToggle.addEventListener('click', toggleMenu);
overlay.addEventListener('click', toggleMenu);

window.addEventListener('scroll', () => {
  header.classList.toggle('scrolled', window.scrollY > 50);
});
```

## Rules to follow regardless of architecture

- The logo always links to `#` or the hero anchor and gets a subtle hover color shift.
- Icon-only buttons (search, cart, wishlist, menu) always get `aria-label`.
- The active nav link should be visually distinct (full opacity vs. ~50% opacity, or
  a filled underline) and should update automatically via scroll-spy, not stay static.
- Mobile nav should close automatically when a link inside it is clicked, and should
  lock body scroll (`document.body.style.overflow = 'hidden'`) while open if it's a
  full overlay/drawer rather than a simple dropdown.

---
## SOURCE: 02_patterns/02_hero_section.md

# Pattern — Hero Section

Tags: pattern, hero, headline, landing-page, above-the-fold

The hero is the page's thesis. It must communicate the subject, the value
proposition, and the primary action within the first viewport, on every screen size.

## Anatomy (works for either architecture)

1. **Eyebrow / badge** — a small pill above the headline, optional but common
   ("New Collection 2025", "Official Dealer", "Now in Beta"). Skip it if it would just
   restate the headline.
2. **Headline** — large, fluid type (`clamp()`), tight letter-spacing for bold/heavy
   weights, normal or wide tracking for light weights. Often two lines, with one
   word or phrase styled distinctly (gradient text, accent color, different weight).
3. **Subheadline** — one to two sentences of real, specific supporting copy. Muted
   text color, comfortable line-height, capped width so lines don't run too long
   (`max-width: 32-40rem`).
4. **Primary + secondary CTA** — a filled accent button for the main action, a quieter
   outlined/ghost button for a secondary path (e.g. "Shop Now" + "View Lookbook").
5. **Proof / stats row** (optional) — 2-4 short stat blocks separated by thin
   dividers, only if real, specific numbers exist for this brief.
6. **Visual** — a product shot placeholder, an icon-driven graphic panel, an ambient
   ammoniated gradient blob, or (for data products) a live mini-demo. On a single-file
   build with no real imagery, build an evocative graphic panel rather than leaving a
   blank box — see the visual-panel snippet below.
7. **Scroll cue** (optional) — a small "Scroll" label with an animated indicator,
   useful when the hero is a full `100vh` and content continues below the fold.

## Utility-class version

```html
<section class="relative min-h-[100vh] flex items-center hero-gradient overflow-hidden pt-20">
  <div class="absolute inset-0 overflow-hidden pointer-events-none">
    <div class="absolute top-1/4 -right-32 w-96 h-96 bg-accent/5 rounded-full blur-3xl animate-float"></div>
    <div class="absolute bottom-1/4 -left-32 w-80 h-80 bg-accent/3 rounded-full blur-3xl animate-float" style="animation-delay:-3s"></div>
  </div>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full relative z-10">
    <div class="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
      <div class="space-y-8">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/5">
          <span class="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
          <span class="text-xs font-medium text-accent tracking-wider uppercase">Eyebrow Label</span>
        </div>
        <h1 class="hero-title font-extrabold text-white leading-none">
          Headline Line One<br><span class="gradient-text">Accent Phrase</span>
        </h1>
        <p class="hero-sub text-white/50 max-w-lg leading-relaxed font-light">
          One to two sentences of specific, real supporting copy for this exact brief.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 pt-2">
          <a href="#primary" class="btn-primary inline-flex items-center justify-center gap-3 bg-accent hover:bg-accent-hover text-white font-semibold px-8 py-4 rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-accent/25 hover:-translate-y-0.5">
            <span>Primary Action</span>
            <svg class="animate-arrow-move" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
          </a>
          <a href="#secondary" class="inline-flex items-center justify-center gap-2 border border-white/15 hover:border-white/30 text-white/80 hover:text-white font-medium px-8 py-4 rounded-xl transition-all duration-300 hover:bg-white/5">
            <span>Secondary Action</span>
          </a>
        </div>
        <div class="flex items-center gap-8 pt-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-white">2.5K+</div>
            <div class="text-xs text-white/40 mt-1 uppercase tracking-wider">Stat Label</div>
          </div>
          <div class="w-px h-10 bg-white/10"></div>
          <div class="text-center">
            <div class="text-2xl font-bold text-white">98%</div>
            <div class="text-xs text-white/40 mt-1 uppercase tracking-wider">Stat Label</div>
          </div>
        </div>
      </div>
      <div class="relative hidden lg:flex items-center justify-center">
        <!-- visual panel: see below -->
      </div>
    </div>
  </div>
</section>
```

Background helper:

```css
.hero-gradient {
  background:
    radial-gradient(ellipse at 70% 20%, rgba(201,135,74,0.08) 0%, transparent 60%),
    radial-gradient(ellipse at 30% 80%, rgba(201,135,74,0.05) 0%, transparent 50%);
}
```

### Visual panel (no real photography available)

When there's no product photo, build an evocative graphic panel instead of leaving
empty space — a bordered card with a gradient wash, a centered icon or monogram, and
a small caption block:

```html
<div class="relative w-full max-w-md aspect-[3/4] rounded-3xl overflow-hidden border border-white/10 bg-surface">
  <div class="absolute inset-0 bg-gradient-to-br from-accent/10 via-transparent to-accent/5"></div>
  <div class="absolute inset-0 flex items-center justify-center">
    <div class="text-center space-y-6 p-8">
      <div class="w-48 h-48 mx-auto rounded-2xl bg-gradient-to-br from-accent/20 to-accent/5 flex items-center justify-center">
        <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="0.5" class="text-accent"><!-- subject-relevant icon --></svg>
      </div>
      <div class="space-y-2">
        <p class="text-sm text-white/30 uppercase tracking-[0.2em]">Featured</p>
        <p class="text-lg font-semibold text-white">Caption Line</p>
      </div>
    </div>
  </div>
</div>
```

## Vanilla-CSS version

```html
<section class="hero" id="hero">
  <div class="container">
    <div class="hero-content">
      <span class="hero-label">Eyebrow Label</span>
      <h1 class="hero-title">Plain Headline Words <em>Accent Phrase</em></h1>
      <p class="hero-desc">One to two sentences of specific, real supporting copy.</p>
      <div class="hero-actions">
        <a href="#primary" class="btn btn-primary">Primary Action</a>
        <a href="#secondary" class="btn btn-outline">Secondary Action</a>
      </div>
      <div class="hero-stats">
        <div class="hero-stat"><h4>50+</h4><p>Stat Label</p></div>
        <div class="hero-stat"><h4>25</h4><p>Stat Label</p></div>
      </div>
    </div>
  </div>
  <div class="scroll-indicator">
    <div class="scroll-mouse"></div>
    <span>Scroll</span>
  </div>
</section>
```

```css
.hero { min-height: 100vh; display: flex; align-items: center; position: relative; overflow: hidden; background: linear-gradient(135deg, var(--black) 0%, var(--dark-gray) 50%, var(--black) 100%); }
.hero::before { content: ""; position: absolute; top: -50%; right: -20%; width: 80%; height: 200%; background: radial-gradient(ellipse, rgba(201,135,74,0.06) 0%, transparent 60%); pointer-events: none; }
.hero-label { display: inline-block; padding: 0.4rem 1rem; background: rgba(201,135,74,0.15); border: 1px solid rgba(201,135,74,0.3); border-radius: 30px; font-size: 0.8rem; letter-spacing: 3px; text-transform: uppercase; color: var(--accent); margin-bottom: 2rem; font-weight: 600; }
.hero-title { font-size: 4.5rem; font-weight: 200; line-height: 1.1; margin-bottom: 1.5rem; letter-spacing: -1px; }
.hero-title em { font-style: normal; font-weight: 700; color: var(--accent); }
.hero-desc { font-size: 1.15rem; color: var(--text-muted); line-height: 1.8; margin-bottom: 2.5rem; max-width: 520px; }
.hero-actions { display: flex; gap: 1rem; flex-wrap: wrap; }
.hero-stats { display: flex; gap: 3rem; margin-top: 4rem; padding-top: 2.5rem; border-top: 1px solid var(--light-gray); flex-wrap: wrap; }
.hero-stat h4 { font-size: 2rem; font-weight: 700; color: var(--accent); line-height: 1; margin-bottom: 0.25rem; }
.hero-stat p { font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
.scroll-indicator { position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; gap: 0.5rem; color: var(--text-muted); font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; }
.scroll-mouse { width: 24px; height: 38px; border: 2px solid var(--lighter-gray); border-radius: 12px; position: relative; }
.scroll-mouse::after { content: ""; position: absolute; top: 6px; left: 50%; transform: translateX(-50%); width: 3px; height: 8px; background: var(--accent); border-radius: 3px; animation: scrollDown 1.5s infinite; }
@keyframes scrollDown { 0% { opacity: 1; top: 6px; } 100% { opacity: 0; top: 20px; } }
@media (max-width: 768px) { .hero-title { font-size: 2.5rem; } .hero-stats { gap: 1.5rem; } }
```

## Rules

- Mobile: hero text must reflow to one column, stat rows must wrap, hero min-height
  often relaxes from `100vh` to `auto`/`90vh` with extra top padding to clear a fixed
  header.
- Never use a stock "big number + small label + gradient" stat row as a reflex — only
  include the stats row if real, specific, brief-relevant numbers make sense.
- The headline's accent phrase (gradient text, colored `<em>`, or a different weight)
  should be the literal product/value, not a generic word like "Better" or "Faster".

---
## SOURCE: 02_patterns/03_card_grids.md

# Pattern — Card Grids (Products, Services, Models, Team, Pricing)

Tags: pattern, cards, grid, product-card, service-card, pricing-card, hover-effects

Card grids are the most reused structural unit across these site types: product
listings, service offerings, model lineups, team bios, pricing tiers, blog previews.

## Generic grid container

```css
.grid-product { display: grid; grid-template-columns: repeat(1, 1fr); gap: 1.5rem; }
@media (min-width: 640px) { .grid-product { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .grid-product { grid-template-columns: repeat(4, 1fr); } }
```

or, vanilla-CSS equivalent for a 3-up feature/service grid:

```css
.services-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
@media (max-width: 900px) { .services-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) { .services-grid { grid-template-columns: 1fr; } }
```

## Product card (utility-class, with hover quick-add + color swatches)

```html
<div class="product-card group" data-product-id="1">
  <div class="relative aspect-[3/4] rounded-2xl overflow-hidden bg-gradient-to-br from-amber-900/30 to-slate-900 border border-white/5 mb-4 cursor-pointer">
    <div class="absolute inset-0 flex items-center justify-center transition-transform duration-700 product-image">
      <!-- category icon or product graphic -->
    </div>
    <div class="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent product-overlay opacity-0 transition-opacity duration-300"></div>
    <span class="absolute top-3 left-3 bg-accent text-white text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-full">New</span>
    <button onclick="addToCart(1); event.stopPropagation();" class="quick-add-btn absolute bottom-4 left-4 right-4 bg-white/95 hover:bg-white text-black font-semibold text-sm py-3 rounded-xl opacity-0 transform translate-y-2 transition-all duration-300 flex items-center justify-center gap-2">
      Quick Add
    </button>
  </div>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <p class="text-xs text-white/35 uppercase tracking-wider">Category</p>
      <div class="flex items-center gap-1.5">
        <!-- color swatches, see pattern below -->
      </div>
    </div>
    <h3 class="font-semibold text-sm text-white/90 group-hover:text-white transition-colors line-clamp-1">Product Name</h3>
    <p class="text-sm font-bold text-white">$89.00</p>
  </div>
</div>
```

```css
.product-card:hover .product-image { transform: scale(1.08); }
.product-card:hover .quick-add-btn { opacity: 1; transform: translateY(0); }
.product-card:hover .product-overlay { opacity: 1; }
```

### Color swatch picker

```html
<button onclick="selectSwatch(1, '#1A1A1A')" class="color-swatch w-4 h-4 rounded-full border border-white/15 selected" style="background-color: #1A1A1A" aria-label="Color option 1"></button>
```

```css
.color-swatch { transition: all 0.2s ease; }
.color-swatch:hover { transform: scale(1.2); }
.color-swatch.selected { box-shadow: 0 0 0 2px #0B0A09, 0 0 0 3.5px #C9874A; transform: scale(1.15); }
```

## Service / feature card (vanilla-CSS, icon + title + description)

```html
<div class="service-card">
  <div class="service-icon">🔧</div>
  <h3 class="service-title">Service Title</h3>
  <p class="service-desc">One or two sentences describing the service concretely.</p>
</div>
```

```css
.service-card { background: var(--medium-gray); border-radius: var(--radius-lg); padding: 2.5rem 2rem; text-align: center; transition: var(--transition); border: 1px solid transparent; }
.service-card:hover { transform: translateY(-6px); border-color: var(--accent); box-shadow: var(--shadow-lg); }
.service-icon { font-size: 2.5rem; margin-bottom: 1.25rem; }
.service-title { font-size: 1.3rem; margin-bottom: 0.75rem; font-weight: 600; }
.service-desc { color: var(--text-muted); font-size: 0.95rem; line-height: 1.7; }
```

Note: emoji icons are an acceptable lightweight substitute for an icon library in a
dependency-free single file, but inline SVG (stroke-based, `currentColor`) reads as
more premium when the brief calls for a refined look — prefer SVG for fashion, tech,
and finance briefs; emoji can work for playful/casual briefs (food, kids, community).

## Model / item card with arrow affordance (vanilla-CSS)

```html
<div class="model-card">
  <div class="model-card-image"><span class="card-visual">🏎️</span></div>
  <div class="model-card-info">
    <p class="model-card-type">Category Label</p>
    <h3 class="model-card-name">Item Name</h3>
    <p class="model-card-price">From $XX,XXX</p>
  </div>
  <div class="model-card-arrow">→</div>
</div>
```

```css
.model-card { position: relative; background: var(--medium-gray); border-radius: var(--radius-lg); padding: 2rem; cursor: pointer; transition: var(--transition); overflow: hidden; }
.model-card:hover { background: var(--light-gray); transform: translateY(-4px); }
.model-card:hover .model-card-arrow { transform: translateX(4px); opacity: 1; }
.model-card-arrow { font-size: 1.5rem; color: var(--accent); opacity: 0.5; transition: var(--transition); position: absolute; bottom: 2rem; right: 2rem; }
```

## Pricing card (common addition for SaaS/service briefs, not in source examples but
follows the same conventions — included for coverage)

```html
<div class="pricing-card pricing-card-featured">
  <p class="pricing-tier">Pro</p>
  <p class="pricing-amount"><span class="pricing-currency">$</span>29<span class="pricing-period">/mo</span></p>
  <p class="pricing-desc">For growing teams that need more headroom.</p>
  <ul class="pricing-features">
    <li>Feature one, stated concretely</li>
    <li>Feature two, stated concretely</li>
  </ul>
  <a href="#signup" class="btn btn-primary">Start Free Trial</a>
</div>
```

```css
.pricing-card { background: var(--medium-gray); border-radius: var(--radius-lg); padding: 2.5rem; border: 1px solid var(--light-gray); transition: var(--transition); }
.pricing-card-featured { border-color: var(--accent); position: relative; transform: scale(1.03); box-shadow: var(--shadow-lg); }
.pricing-amount { font-size: 3rem; font-weight: 700; margin: 1rem 0; }
.pricing-currency { font-size: 1.5rem; vertical-align: top; }
.pricing-period { font-size: 1rem; color: var(--text-muted); font-weight: 400; }
```

## Rules

- Card hover should lift (`translateY(-4px)` to `-8px`) AND either change a border
  color or deepen a shadow — lift alone reads as incomplete.
- Stagger card entrance animation by index (`i * 80ms` delay) when a grid renders via
  JS, so cards cascade in rather than all popping simultaneously.
- Badges ("New", "Best Seller", "Limited", "Sold Out") need a small, distinct color
  per type, not one generic badge color for everything.
- Always design the empty/no-results state for a filterable grid (see
  `06_filters_and_search.md`), not just the populated state.

---
## SOURCE: 02_patterns/04_modals_and_drawers.md

# Pattern — Modals & Slide-Out Drawers

Tags: pattern, modal, drawer, cart-drawer, dialog, overlay, escape-key

Two related but distinct UI surfaces appear constantly: a **centered modal** (item
detail, confirmation) and a **slide-out drawer** (cart, filters panel, mobile nav).
Both need an overlay, an open/close mechanism, and keyboard/click-outside dismissal.

## Centered modal (vanilla-CSS — vehicle/product detail example)

```html
<div class="modal" id="detail-modal">
  <div class="modal-overlay" id="modal-overlay"></div>
  <div class="modal-content">
    <button class="modal-close" id="modal-close" aria-label="Close">&times;</button>
    <h3 id="modal-title"></h3>
    <p id="modal-price" class="modal-price"></p>
    <div class="modal-specs">
      <div><span>Year</span><strong id="modal-year"></strong></div>
      <div><span>Mileage</span><strong id="modal-mileage"></strong></div>
      <div><span>Transmission</span><strong id="modal-trans"></strong></div>
    </div>
    <p id="modal-desc" class="modal-desc"></p>
  </div>
</div>
```

```css
.modal { position: fixed; inset: 0; z-index: 2000; display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: opacity 0.3s ease; }
.modal.active { opacity: 1; pointer-events: auto; }
.modal-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.75); backdrop-filter: blur(4px); }
.modal-content { position: relative; background: var(--dark-gray); border-radius: var(--radius-lg); padding: 2.5rem; max-width: 540px; width: 90%; max-height: 85vh; overflow-y: auto; transform: translateY(20px) scale(0.98); transition: transform 0.3s cubic-bezier(0.16,1,0.3,1); box-shadow: var(--shadow-lg); }
.modal.active .modal-content { transform: translateY(0) scale(1); }
.modal-close { position: absolute; top: 1.25rem; right: 1.25rem; background: var(--medium-gray); border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 1.5rem; line-height: 1; color: var(--white); }
.modal-close:hover { background: var(--accent); color: var(--black); }
```

```js
const modal = document.getElementById('detail-modal');
const modalOverlay = document.getElementById('modal-overlay');
const modalClose = document.getElementById('modal-close');

function openModal(item) {
  document.getElementById('modal-title').textContent = item.name;
  document.getElementById('modal-price').textContent = formatPrice(item.price);
  // ...populate remaining fields...
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}
function closeModal() {
  modal.classList.remove('active');
  document.body.style.overflow = '';
}
modalClose.addEventListener('click', closeModal);
modalOverlay.addEventListener('click', closeModal);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && modal.classList.contains('active')) closeModal();
});
```

## Slide-out drawer (utility-class — cart drawer example)

```html
<aside id="cart-drawer" class="fixed top-0 right-0 h-full w-full sm:w-[420px] bg-canvas-light z-[90] translate-x-full transition-transform duration-300 flex flex-col border-l border-white/5">
  <div class="flex items-center justify-between p-6 border-b border-white/5">
    <h3 class="font-bold text-lg">Your Cart</h3>
    <button id="cart-close-btn" class="p-2 text-white/50 hover:text-white" aria-label="Close cart">&times;</button>
  </div>
  <div id="cart-items" class="flex-1 overflow-y-auto p-6 space-y-4">
    <div id="cart-empty-state" class="flex flex-col items-center justify-center h-full text-center">
      <p class="text-sm font-medium text-white/50 mb-1">Your cart is empty</p>
      <p class="text-xs text-white/25">Browse our collection and add some items</p>
    </div>
  </div>
  <div id="cart-footer" class="border-t border-white/5 p-6 space-y-4 hidden">
    <div class="flex items-center justify-between">
      <span class="font-semibold">Total</span>
      <span id="cart-total" class="text-xl font-bold text-accent">$0.00</span>
    </div>
    <button class="btn-primary w-full bg-accent hover:bg-accent-hover text-white font-semibold py-4 rounded-xl">Checkout</button>
  </div>
</aside>
<div id="cart-backdrop" class="fixed inset-0 bg-black/60 z-[85] opacity-0 pointer-events-none transition-opacity duration-300"></div>
```

```js
function openCart() {
  document.getElementById('cart-drawer').classList.remove('translate-x-full');
  const backdrop = document.getElementById('cart-backdrop');
  backdrop.classList.remove('opacity-0', 'pointer-events-none');
  document.body.style.overflow = 'hidden';
}
function closeCart() {
  document.getElementById('cart-drawer').classList.add('translate-x-full');
  const backdrop = document.getElementById('cart-backdrop');
  backdrop.classList.add('opacity-0', 'pointer-events-none');
  document.body.style.overflow = '';
}
document.getElementById('cart-backdrop').addEventListener('click', closeCart);
document.getElementById('cart-close-btn').addEventListener('click', closeCart);
```

## Rules common to both surfaces

- Always provide three ways to dismiss: an explicit close button, clicking the
  backdrop/overlay, and the Escape key.
- Lock `document.body.style.overflow = 'hidden'` while open, restore it on close, so
  the page behind doesn't scroll.
- Animate both the overlay (opacity) and the content (transform: scale or
  translate) — animating only one of the two feels unfinished.
- Drawers slide from the edge they're conceptually attached to: cart from the right
  (matches a cart icon in the top-right), mobile filters often from the left or
  bottom (bottom sheet) on small screens.
- Always design and wire up the empty state (`cart-empty-state` above) — hide it via
  a footer/state class once there's content, don't just leave the container blank.

---
## SOURCE: 02_patterns/05_cart_state_management.md

# Pattern — Cart State & Stateful JS Logic

Tags: pattern, cart, state-management, vanilla-js, localStorage-free, toast

Single-file sites have no framework and no backend, so all "app" state (cart
contents, selected filters, wishlist) lives in a plain JS object/array for the
session. Do not use `localStorage`/`sessionStorage` unless the brief explicitly asks
for persistence and explicitly accepts it not working in restricted preview contexts
— default to in-memory state so the file works everywhere it's opened.

## Core cart state shape

```js
let cart = []; // [{ id, name, price, image, qty, variant }]

function addToCart(productId, variant) {
  const product = products.find(p => p.id === productId);
  if (!product) return;
  const existing = cart.find(i => i.id === productId && i.variant === variant);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ id: product.id, name: product.name, price: product.price, variant, qty: 1 });
  }
  renderCart();
  updateCartBadge();
  showToast(`${product.name} added to cart`, 'success');
  bounceCartIcon();
}

function removeFromCart(productId, variant) {
  cart = cart.filter(i => !(i.id === productId && i.variant === variant));
  renderCart();
  updateCartBadge();
}

function updateQty(productId, variant, delta) {
  const item = cart.find(i => i.id === productId && i.variant === variant);
  if (!item) return;
  item.qty = Math.max(1, item.qty + delta);
  renderCart();
  updateCartBadge();
}

function cartTotal() {
  return cart.reduce((sum, i) => sum + i.price * i.qty, 0);
}

function cartCount() {
  return cart.reduce((sum, i) => sum + i.qty, 0);
}
```

## Rendering the cart (toggle empty vs. populated state)

```js
function renderCart() {
  const container = document.getElementById('cart-items');
  const footer = document.getElementById('cart-footer');
  const emptyState = document.getElementById('cart-empty-state');

  if (cart.length === 0) {
    emptyState.style.display = 'flex';
    footer.classList.add('hidden');
    // remove any previously rendered item rows but keep the empty-state node
    container.querySelectorAll('.cart-row').forEach(el => el.remove());
    return;
  }

  emptyState.style.display = 'none';
  footer.classList.remove('hidden');
  container.querySelectorAll('.cart-row').forEach(el => el.remove());

  cart.forEach(item => {
    const row = document.createElement('div');
    row.className = 'cart-row flex gap-4 pb-4 border-b border-white/5';
    row.innerHTML = `
      <div class="flex-1">
        <p class="font-medium text-sm">${escapeHtml(item.name)}</p>
        <p class="text-xs text-white/40">${escapeHtml(item.variant || '')}</p>
        <div class="flex items-center gap-3 mt-2">
          <button class="qty-btn" data-id="${item.id}" data-variant="${item.variant}" data-delta="-1">−</button>
          <span class="text-sm w-4 text-center">${item.qty}</span>
          <button class="qty-btn" data-id="${item.id}" data-variant="${item.variant}" data-delta="1">+</button>
        </div>
      </div>
      <p class="font-semibold text-sm">$${(item.price * item.qty).toFixed(2)}</p>
    `;
    container.appendChild(row);
  });

  document.getElementById('cart-total').textContent = `$${cartTotal().toFixed(2)}`;

  container.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', () => updateQty(btn.dataset.id, btn.dataset.variant, parseInt(btn.dataset.delta)));
  });
}

function updateCartBadge() {
  const badge = document.getElementById('cart-badge');
  const count = cartCount();
  badge.textContent = count;
  badge.classList.toggle('hidden', count === 0);
  // retrigger pop animation
  badge.style.animation = 'none';
  badge.offsetHeight; // force reflow
  badge.style.animation = 'badgePop 0.3s cubic-bezier(0.34,1.56,0.64,1)';
}
```

## Toast notifications (stackable, auto-dismiss)

```html
<div id="toast-container" class="fixed top-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none"></div>
```

```css
.toast { background: #1A1714; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 18px; display: flex; align-items: center; gap: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); transform: translateX(120%); transition: transform 0.35s cubic-bezier(0.16,1,0.3,1); pointer-events: auto; min-width: 240px; }
.toast.show { transform: translateX(0); }
.toast.success { border-left: 3px solid #4ADE80; }
.toast.error { border-left: 3px solid #F87171; }
```

```js
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 350);
  }, 2600);
}
```

## Small bounce on the cart icon when an item is added

```js
function bounceCartIcon() {
  const icon = document.getElementById('cart-icon-btn');
  icon.style.animation = 'none';
  icon.offsetHeight;
  icon.style.animation = 'cartBounce 0.4s cubic-bezier(0.34,1.56,0.64,1)';
}
```

```css
@keyframes cartBounce { 0%,100% { transform: scale(1); } 50% { transform: scale(1.2) rotate(-8deg); } }
```

## Always escape user-influenced or dynamic text before inserting via innerHTML

Even though most data in these single-file demos is hardcoded, build the habit of
escaping anything that could plausibly come from user input (search queries, form
field echoes) before interpolating into `innerHTML`:

```js
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
```

## Rules

- Every state mutation (`addToCart`, `removeFromCart`, `updateQty`) must call both the
  relevant render function AND the badge/total updater — don't let the badge drift
  out of sync with the underlying array.
- Always re-query and re-bind event listeners on dynamically rendered rows (as shown
  with `.qty-btn` above), since elements created via `innerHTML`/`createElement`
  after page load have no listeners until explicitly bound.
- Never block the UI with `alert()`/`confirm()` for cart feedback — use the toast
  pattern instead so the experience stays seamless.

---
## SOURCE: 02_patterns/06_filters_and_search.md

# Pattern — Filters, Search & Empty States

Tags: pattern, filters, search, empty-state, inventory, dynamic-rendering

Inventory-style sites (dealerships, marketplaces, catalogs) need a filter bar that
narrows a data array and re-renders a grid, plus a designed empty state for when no
items match.

## Filter bar markup (vanilla-CSS — category chips + dropdowns)

```html
<div class="filter-bar">
  <div class="filter-chips" id="category-chips">
    <button class="chip active" data-filter="all">All</button>
    <button class="chip" data-filter="sedan">Sedan</button>
    <button class="chip" data-filter="suv">SUV</button>
    <button class="chip" data-filter="coupe">Coupe</button>
  </div>
  <div class="filter-selects">
    <select id="sort-select" class="filter-select">
      <option value="default">Sort: Featured</option>
      <option value="price-asc">Price: Low to High</option>
      <option value="price-desc">Price: High to Low</option>
    </select>
    <div class="search-box">
      <input type="text" id="search-input" placeholder="Search inventory..." aria-label="Search inventory">
    </div>
  </div>
</div>
```

```css
.filter-bar { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: space-between; align-items: center; margin-bottom: 3rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--light-gray); }
.filter-chips { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.chip { padding: 0.5rem 1.2rem; border-radius: 30px; border: 1px solid var(--lighter-gray); background: transparent; color: var(--text-muted); font-size: 0.85rem; font-weight: 500; transition: var(--transition); }
.chip:hover { border-color: var(--accent); color: var(--white); }
.chip.active { background: var(--accent); border-color: var(--accent); color: var(--black); font-weight: 600; }
.filter-select { background: var(--medium-gray); border: 1px solid var(--lighter-gray); color: var(--white); padding: 0.6rem 1rem; border-radius: var(--radius); font-size: 0.85rem; }
.search-box input { background: var(--medium-gray); border: 1px solid var(--lighter-gray); color: var(--white); padding: 0.6rem 1rem; border-radius: var(--radius); font-size: 0.85rem; width: 220px; }
.search-box input:focus { outline: none; border-color: var(--accent); }
```

## Filter + search + sort logic (combine all three reactively)

```js
let activeCategory = 'all';
let activeSort = 'default';
let searchQuery = '';

function getFilteredItems() {
  let result = items.filter(item => {
    const matchesCategory = activeCategory === 'all' || item.category === activeCategory;
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  if (activeSort === 'price-asc') result = result.sort((a, b) => a.price - b.price);
  if (activeSort === 'price-desc') result = result.sort((a, b) => b.price - a.price);

  return result;
}

function renderInventory() {
  const grid = document.getElementById('inventory-grid');
  const emptyState = document.getElementById('inventory-empty');
  const filtered = getFilteredItems();

  grid.innerHTML = '';

  if (filtered.length === 0) {
    emptyState.style.display = 'flex';
    grid.style.display = 'none';
    return;
  }

  emptyState.style.display = 'none';
  grid.style.display = 'grid';

  filtered.forEach((item, i) => {
    const card = buildCard(item); // returns a DOM node, see 03_card_grids.md
    card.style.animationDelay = `${i * 60}ms`;
    card.classList.add('card-enter');
    grid.appendChild(card);
  });
}

document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    activeCategory = chip.dataset.filter;
    renderInventory();
  });
});

document.getElementById('sort-select').addEventListener('change', (e) => {
  activeSort = e.target.value;
  renderInventory();
});

let searchDebounce;
document.getElementById('search-input').addEventListener('input', (e) => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    searchQuery = e.target.value;
    renderInventory();
  }, 200);
});
```

## Designed empty state (never leave a blank grid)

```html
<div class="inventory-empty" id="inventory-empty" style="display:none;">
  <div class="empty-icon">🔍</div>
  <h3>No matches found</h3>
  <p>Try a different category or clear your search to see the full inventory.</p>
  <button class="btn btn-outline" onclick="resetFilters()">Clear Filters</button>
</div>
```

```css
.inventory-empty { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 5rem 2rem; color: var(--text-muted); }
.empty-icon { font-size: 3rem; margin-bottom: 1.5rem; opacity: 0.6; }
.inventory-empty h3 { color: var(--white); font-size: 1.3rem; margin-bottom: 0.5rem; }
.inventory-empty p { max-width: 360px; margin-bottom: 1.5rem; line-height: 1.6; }
```

```js
function resetFilters() {
  activeCategory = 'all';
  searchQuery = '';
  document.getElementById('search-input').value = '';
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  document.querySelector('.chip[data-filter="all"]').classList.add('active');
  renderInventory();
}
```

## Card stagger-in animation referenced above

```css
.card-enter { animation: cardEnter 0.5s cubic-bezier(0.16,1,0.3,1) backwards; }
@keyframes cardEnter { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
```

## Rules

- Debounce search input (150-250ms) so re-rendering doesn't thrash on every
  keystroke.
- Filtering, sorting, and search must all compose — recompute from the full source
  array every time rather than mutating it, or repeated filtering will lose items
  permanently.
- The empty state needs a way back (a "Clear Filters" action), not just an
  apology message.
- Active filter chip state must be visually unambiguous (filled background, not just
  a thin border change) since it's the only indicator of current grid contents.

---
## SOURCE: 02_patterns/07_forms_and_validation.md

# Pattern — Forms & Validation

Tags: pattern, forms, validation, contact-form, newsletter, error-states

Contact forms, newsletter signups, and booking forms appear in nearly every site type.
Validation should be real (not just `required` attributes with no feedback) and error
messaging should speak in the product's voice.

## Markup with inline error slots

```html
<form id="contact-form" novalidate>
  <div class="form-group">
    <label for="name">Full name</label>
    <input type="text" id="name" name="name" required>
    <span class="form-error" id="name-error"></span>
  </div>
  <div class="form-group">
    <label for="email">Email address</label>
    <input type="email" id="email" name="email" required>
    <span class="form-error" id="email-error"></span>
  </div>
  <div class="form-group">
    <label for="message">Message</label>
    <textarea id="message" name="message" rows="4" required></textarea>
    <span class="form-error" id="message-error"></span>
  </div>
  <button type="submit" class="btn btn-primary">Send Message</button>
  <p class="form-status" id="form-status"></p>
</form>
```

```css
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--off-white); letter-spacing: 0.3px; }
.form-group input, .form-group textarea { width: 100%; background: var(--medium-gray); border: 1px solid var(--lighter-gray); color: var(--white); padding: 0.85rem 1rem; border-radius: var(--radius); font-size: 0.95rem; font-family: inherit; transition: var(--transition); }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(74,124,89,0.15); }
.form-group input.invalid, .form-group textarea.invalid { border-color: var(--danger); }
.form-error { display: block; font-size: 0.8rem; color: var(--danger); margin-top: 0.4rem; min-height: 1.1em; }
.form-status { margin-top: 1rem; font-size: 0.9rem; }
.form-status.success { color: var(--success); }
.form-status.error { color: var(--danger); }
```

## Validation logic (real-time on blur, full check on submit)

```js
const form = document.getElementById('contact-form');

const validators = {
  name: (v) => v.trim().length >= 2 || 'Please enter your full name.',
  email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Enter a valid email address.',
  message: (v) => v.trim().length >= 10 || 'Tell us a little more — at least 10 characters.'
};

function validateField(fieldName) {
  const field = document.getElementById(fieldName);
  const errorEl = document.getElementById(`${fieldName}-error`);
  const result = validators[fieldName](field.value);
  if (result === true) {
    field.classList.remove('invalid');
    errorEl.textContent = '';
    return true;
  } else {
    field.classList.add('invalid');
    errorEl.textContent = result;
    return false;
  }
}

Object.keys(validators).forEach(fieldName => {
  const field = document.getElementById(fieldName);
  field.addEventListener('blur', () => validateField(fieldName));
  field.addEventListener('input', () => {
    if (field.classList.contains('invalid')) validateField(fieldName);
  });
});

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const allValid = Object.keys(validators).map(validateField).every(Boolean);
  const statusEl = document.getElementById('form-status');

  if (!allValid) {
    statusEl.textContent = 'Please fix the highlighted fields above.';
    statusEl.className = 'form-status error';
    return;
  }

  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Sending...';

  // Simulate submission (no backend in a single static file)
  setTimeout(() => {
    statusEl.textContent = "Thanks — we'll get back to you within one business day.";
    statusEl.className = 'form-status success';
    form.reset();
    submitBtn.disabled = false;
    submitBtn.textContent = 'Send Message';
  }, 900);
});
```

## Newsletter signup (compact inline variant)

```html
<form id="newsletter-form" class="newsletter-form">
  <input type="email" id="newsletter-email" placeholder="you@example.com" required aria-label="Email for newsletter">
  <button type="submit">Subscribe</button>
</form>
<p class="newsletter-note" id="newsletter-note">No spam. Unsubscribe anytime.</p>
```

```js
document.getElementById('newsletter-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const email = document.getElementById('newsletter-email').value;
  const note = document.getElementById('newsletter-note');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    note.textContent = 'That email doesn\'t look right — try again.';
    note.style.color = 'var(--danger)';
    return;
  }
  note.textContent = "You're on the list. Check your inbox to confirm.";
  note.style.color = 'var(--success)';
  e.target.reset();
});
```

## Rules

- Always call `e.preventDefault()` — there is no backend in a single static file, so
  a real form submission would navigate away/reload and lose the page.
- Validate on blur (so the user gets feedback as they go) and again on submit (so a
  user who never blurs a field, e.g. tabbing fast, still gets checked).
- Error copy is specific and instructive ("Enter a valid email address.") never just
  "Invalid input" or "Error".
- Disable and relabel the submit button during the simulated async action
  ("Sending...") so the click registers as having done something, then restore it.
- Success messaging confirms what happens next ("we'll get back to you within one
  business day") rather than a bare "Success!".

---
## SOURCE: 02_patterns/08_footer_and_carousel.md

# Pattern — Footer & Testimonial Carousel

Tags: pattern, footer, testimonials, carousel, social-links, sitemap

## Footer anatomy

A complete footer (not just a copyright line) usually has: a brand recap column, 2-3
link columns (sitemap-style), a newsletter or contact column, a bottom bar with
copyright + legal links + social icons.

```html
<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-brand">
      <div class="logo"><div class="logo-icon">B</div><span>Brand</span></div>
      <p class="footer-tagline">One sentence restating the brand's core promise.</p>
      <div class="social-links">
        <a href="#" aria-label="Instagram" class="social-icon"><!-- svg --></a>
        <a href="#" aria-label="Twitter" class="social-icon"><!-- svg --></a>
      </div>
    </div>
    <div class="footer-col">
      <h4>Shop</h4>
      <a href="#">New Arrivals</a>
      <a href="#">Best Sellers</a>
      <a href="#">Sale</a>
    </div>
    <div class="footer-col">
      <h4>Company</h4>
      <a href="#">About</a>
      <a href="#">Careers</a>
      <a href="#">Press</a>
    </div>
    <div class="footer-col footer-newsletter">
      <h4>Stay Updated</h4>
      <p>Get early access to drops and members-only pricing.</p>
      <form class="newsletter-form"><!-- see 07_forms_and_validation.md --></form>
    </div>
  </div>
  <div class="footer-bottom">
    <p>© 2026 Brand. All rights reserved.</p>
    <div class="footer-legal"><a href="#">Privacy</a><a href="#">Terms</a></div>
  </div>
</footer>
```

```css
.footer { background: var(--dark-gray); border-top: 1px solid var(--light-gray); padding: 5rem 0 0; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr; gap: 3rem; padding-bottom: 4rem; }
.footer-col h4 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1.25rem; color: var(--off-white); }
.footer-col a { display: block; color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.85rem; }
.footer-col a:hover { color: var(--accent); }
.social-icon { display: inline-flex; width: 38px; height: 38px; border-radius: 50%; background: var(--medium-gray); align-items: center; justify-content: center; margin-right: 0.6rem; }
.social-icon:hover { background: var(--accent); color: var(--black); }
.footer-bottom { border-top: 1px solid var(--light-gray); padding: 1.5rem 0; display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted); }
.footer-legal { display: flex; gap: 1.5rem; }
@media (max-width: 900px) { .footer-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 600px) { .footer-grid { grid-template-columns: 1fr; } .footer-bottom { flex-direction: column; gap: 1rem; text-align: center; } }
```

## Testimonial carousel (autoplay + manual dots + pause-on-hover)

```html
<div class="testimonial-carousel" id="testimonial-carousel">
  <div class="testimonial-track" id="testimonial-track">
    <div class="testimonial-slide active">
      <p class="testimonial-quote">"Specific, real-sounding quote about the actual product experience, not generic praise."</p>
      <p class="testimonial-author">Person Name <span>— Role / Context</span></p>
    </div>
    <!-- more .testimonial-slide -->
  </div>
  <div class="testimonial-dots" id="testimonial-dots"></div>
</div>
```

```css
.testimonial-carousel { position: relative; max-width: 700px; margin: 0 auto; text-align: center; }
.testimonial-slide { display: none; animation: fadeIn 0.5s ease; }
.testimonial-slide.active { display: block; }
.testimonial-quote { font-size: 1.4rem; font-weight: 300; line-height: 1.6; font-style: italic; margin-bottom: 1.5rem; color: var(--off-white); }
.testimonial-author { font-size: 0.9rem; font-weight: 600; }
.testimonial-author span { color: var(--text-muted); font-weight: 400; }
.testimonial-dots { display: flex; justify-content: center; gap: 0.5rem; margin-top: 2rem; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--lighter-gray); border: none; transition: var(--transition); }
.dot.active { background: var(--accent); width: 24px; border-radius: 4px; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
```

```js
const slides = document.querySelectorAll('.testimonial-slide');
const dotsContainer = document.getElementById('testimonial-dots');
let currentSlide = 0;
let autoplayInterval;

slides.forEach((_, i) => {
  const dot = document.createElement('button');
  dot.className = 'dot' + (i === 0 ? ' active' : '');
  dot.setAttribute('aria-label', `Go to testimonial ${i + 1}`);
  dot.addEventListener('click', () => goToSlide(i));
  dotsContainer.appendChild(dot);
});

function goToSlide(index) {
  slides[currentSlide].classList.remove('active');
  dotsContainer.children[currentSlide].classList.remove('active');
  currentSlide = index;
  slides[currentSlide].classList.add('active');
  dotsContainer.children[currentSlide].classList.add('active');
}

function nextSlide() { goToSlide((currentSlide + 1) % slides.length); }

function startAutoplay() { autoplayInterval = setInterval(nextSlide, 5000); }
function stopAutoplay() { clearInterval(autoplayInterval); }

startAutoplay();
const carousel = document.getElementById('testimonial-carousel');
carousel.addEventListener('mouseenter', stopAutoplay);
carousel.addEventListener('mouseleave', startAutoplay);
```

## Rules

- Footer link columns should reflect the actual site's sections/sitemap, not generic
  filler links — if there's no "Careers" page concept for this brief, don't include
  the link.
- Carousel autoplay must pause on hover/focus so a reader can actually finish reading
  a longer quote, and must offer manual dot navigation as an escape from the timer.
- Testimonial copy should sound like a specific person describing a specific moment,
  not a generic "Great product, highly recommend!" line.
- The footer's newsletter or CTA column should not duplicate the header's signup if
  the site already has a prominent one elsewhere — pick one primary capture point.

---
## SOURCE: 03_examples/01_coffee_roaster.md

# Example — Specialty Coffee Roaster (Tailwind Architecture)

Tags: example, full-site, coffee, roaster, food-and-beverage, ecommerce, tailwind, dark-theme, terracotta

Niche: direct-to-consumer specialty coffee roaster selling single-origin beans online.
Architecture: Tailwind CDN utility classes.
Palette: espresso brown canvas (#13100D), cream text, terracotta/clay accent (#C9874A).
Signature element: an animated "from farm to cup" process strip with connecting line
that draws in on scroll.
Sections: header, hero, process strip, product grid with cart, origin story, brew
guide cards, testimonial, newsletter, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ember & Stone Coffee Roasters | Single-Origin Coffee, Roasted Weekly</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  theme: {
    extend: {
      colors: {
        canvas: { DEFAULT: '#13100D', light: '#1C1712', card: '#211B15' },
        accent: { DEFAULT: '#C9874A', hover: '#DA9A5C', glow: 'rgba(201,135,74,0.3)' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Fraunces', 'serif']
      }
    }
  }
}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * { -webkit-font-smoothing: antialiased; }
  body { font-family:'Inter',sans-serif; overflow-x:hidden; }
  .font-display { font-family:'Fraunces',serif; }
  ::selection { background: rgba(201,135,74,0.35); }
  ::-webkit-scrollbar { width:6px; } ::-webkit-scrollbar-track{background:#1C1712;} ::-webkit-scrollbar-thumb{background:#3A2E22;border-radius:3px;}
  .hero-title{font-size:clamp(2.6rem,6vw,5.2rem);line-height:1.02;letter-spacing:-0.02em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .process-line{position:absolute;top:28px;left:0;height:2px;background:linear-gradient(90deg,#C9874A,#3A2E22);width:0;transition:width 1.4s cubic-bezier(.16,1,.3,1);}
  .process-line.visible{width:100%;}
  .grain-card:hover .grain-icon{transform:translateY(-4px) rotate(-4deg);}
  .grain-icon{transition:transform .4s cubic-bezier(.34,1.56,.64,1);}
  .product-card:hover .bag-shadow{transform:scale(1.06);}
  .bag-shadow{transition:transform .5s cubic-bezier(.16,1,.3,1);}
  input:focus,button:focus-visible{outline:2px solid #C9874A;outline-offset:2px;}
  .toast{transform:translateX(120%);transition:transform .35s cubic-bezier(.16,1,.3,1);}
  .toast.show{transform:translateX(0);}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-[#F3ECE3] min-h-screen">

<div id="toast-container" class="fixed top-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none"></div>

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <button id="mobile-menu-btn" class="lg:hidden p-2 -ml-2 text-white/70" aria-label="Open menu">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <a href="#" class="font-display text-2xl font-semibold tracking-tight">Ember &amp; Stone</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#process" class="text-sm text-white/60 hover:text-white transition-colors uppercase tracking-wide">Process</a>
        <a href="#shop" class="text-sm text-white/60 hover:text-white transition-colors uppercase tracking-wide">Shop</a>
        <a href="#brew" class="text-sm text-white/60 hover:text-white transition-colors uppercase tracking-wide">Brew Guides</a>
      </nav>
      <button id="cart-icon-btn" onclick="openCart()" class="relative p-2.5 rounded-full hover:bg-white/5 transition-colors" aria-label="Open cart">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6h15l-1.5 9h-13z"/><circle cx="9" cy="20" r="1"/><circle cx="17" cy="20" r="1"/></svg>
        <span id="cart-badge" class="hidden absolute -top-1 -right-1 bg-accent text-canvas text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center">0</span>
      </button>
    </div>
  </div>
  <div id="mobile-nav" class="hidden lg:hidden bg-canvas-light border-b border-white/5">
    <div class="px-6 py-6 flex flex-col gap-4">
      <a href="#process" class="text-white/80">Process</a><a href="#shop" class="text-white/80">Shop</a><a href="#brew" class="text-white/80">Brew Guides</a>
    </div>
  </div>
</header>

<section class="relative min-h-[92vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 75% 25%, rgba(201,135,74,0.1) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 w-full relative z-10 grid lg:grid-cols-2 gap-16 items-center">
    <div class="space-y-7">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/5">
        <span class="w-1.5 h-1.5 rounded-full bg-accent"></span>
        <span class="text-xs font-medium text-accent tracking-wider uppercase">Roasted in small batches, weekly</span>
      </div>
      <h1 class="hero-title font-display font-semibold text-white">
        Coffee that tastes<br>like <span class="text-accent">where it grew.</span>
      </h1>
      <p class="text-lg text-white/50 max-w-md leading-relaxed">
        We work directly with five family farms across Ethiopia, Colombia, and Guatemala,
        and roast every order within 48 hours of shipping.
      </p>
      <div class="flex flex-col sm:flex-row gap-4 pt-1">
        <a href="#shop" class="inline-flex items-center justify-center gap-3 bg-accent hover:bg-accent-hover text-canvas font-semibold px-8 py-4 rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-accent/25 hover:-translate-y-0.5">Shop Single-Origins</a>
        <a href="#process" class="inline-flex items-center justify-center gap-2 border border-white/15 hover:border-white/30 text-white/80 hover:text-white font-medium px-8 py-4 rounded-xl transition-all duration-300 hover:bg-white/5">How We Roast</a>
      </div>
      <div class="flex items-center gap-8 pt-3">
        <div><div class="text-2xl font-bold text-white">5</div><div class="text-xs text-white/40 uppercase tracking-wider mt-1">Partner Farms</div></div>
        <div class="w-px h-10 bg-white/10"></div>
        <div><div class="text-2xl font-bold text-white">48hr</div><div class="text-xs text-white/40 uppercase tracking-wider mt-1">Roast to Ship</div></div>
      </div>
    </div>
    <div class="relative hidden lg:flex items-center justify-center">
      <div class="relative w-full max-w-md aspect-[3/4] rounded-3xl overflow-hidden border border-white/10 bg-canvas-card">
        <div class="absolute inset-0 bg-gradient-to-br from-accent/15 via-transparent to-transparent"></div>
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="text-center space-y-6 p-8">
            <div class="w-44 h-44 mx-auto rounded-2xl bg-gradient-to-br from-accent/25 to-accent/5 flex items-center justify-center">
              <svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="text-accent"><path d="M3 9h13a3 3 0 0 1 0 6h-1"/><path d="M16 9v8a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V9z"/><line x1="6" y1="2" x2="6" y2="4"/><line x1="10" y1="2" x2="10" y2="4"/></svg>
            </div>
            <p class="text-sm text-white/30 uppercase tracking-[0.2em]">This Week's Roast</p>
            <p class="text-lg font-semibold text-white">Yirgacheffe, Ethiopia</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="process" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">From Farm to Cup</p>
      <h2 class="font-display text-4xl lg:text-5xl font-semibold">Four steps, no shortcuts</h2>
    </div>
    <div class="relative grid grid-cols-1 sm:grid-cols-4 gap-10" id="process-strip">
      <div class="process-line" id="process-line"></div>
      <div class="reveal text-center relative">
        <div class="w-14 h-14 rounded-full bg-canvas-card border border-accent/30 flex items-center justify-center mx-auto mb-4 relative z-10 text-accent font-display text-lg">1</div>
        <h3 class="font-semibold mb-2">Sourced</h3>
        <p class="text-sm text-white/45">Bought direct from five farms we've visited and paid above fair-trade price.</p>
      </div>
      <div class="reveal text-center relative" style="transition-delay:.1s">
        <div class="w-14 h-14 rounded-full bg-canvas-card border border-accent/30 flex items-center justify-center mx-auto mb-4 relative z-10 text-accent font-display text-lg">2</div>
        <h3 class="font-semibold mb-2">Cupped</h3>
        <p class="text-sm text-white/45">Every lot is tasted blind by our roastmaster before it earns a spot in the lineup.</p>
      </div>
      <div class="reveal text-center relative" style="transition-delay:.2s">
        <div class="w-14 h-14 rounded-full bg-canvas-card border border-accent/30 flex items-center justify-center mx-auto mb-4 relative z-10 text-accent font-display text-lg">3</div>
        <h3 class="font-semibold mb-2">Roasted</h3>
        <p class="text-sm text-white/45">Small 12kg batches, profiled per origin, never sitting on a shelf for weeks.</p>
      </div>
      <div class="reveal text-center relative" style="transition-delay:.3s">
        <div class="w-14 h-14 rounded-full bg-canvas-card border border-accent/30 flex items-center justify-center mx-auto mb-4 relative z-10 text-accent font-display text-lg">4</div>
        <h3 class="font-semibold mb-2">Shipped</h3>
        <p class="text-sm text-white/45">Out the door within 48 hours of roasting, one-way valve bags keep it fresh.</p>
      </div>
    </div>
  </div>
</section>

<section id="shop" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-end justify-between mb-12 reveal">
      <div>
        <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">This Week's Lineup</p>
        <h2 class="font-display text-4xl font-semibold">Single-origin bags</h2>
      </div>
    </div>
    <div id="product-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"></div>
  </div>
</section>

<section id="brew" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Brew Guides</p>
      <h2 class="font-display text-4xl font-semibold">However you make it, make it right</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="grain-card reveal bg-canvas-card border border-white/5 rounded-2xl p-8 text-center transition-transform hover:-translate-y-1">
        <div class="grain-icon text-4xl mb-4">☕</div>
        <h3 class="font-semibold mb-2">Pour Over</h3>
        <p class="text-sm text-white/45">1:16 ratio, 96°C water, 3 minute total bloom-to-drawdown.</p>
      </div>
      <div class="grain-card reveal bg-canvas-card border border-white/5 rounded-2xl p-8 text-center transition-transform hover:-translate-y-1" style="transition-delay:.1s">
        <div class="grain-icon text-4xl mb-4">🫖</div>
        <h3 class="font-semibold mb-2">French Press</h3>
        <p class="text-sm text-white/45">1:15 ratio, coarse grind, 4 minute steep before plunging.</p>
      </div>
      <div class="grain-card reveal bg-canvas-card border border-white/5 rounded-2xl p-8 text-center transition-transform hover:-translate-y-1" style="transition-delay:.2s">
        <div class="grain-icon text-4xl mb-4">⚡</div>
        <h3 class="font-semibold mb-2">Espresso</h3>
        <p class="text-sm text-white/45">1:2 ratio, fine grind, 25-30 second extraction at 9 bar.</p>
      </div>
    </div>
  </div>
</section>

<section class="py-20 border-t border-white/5">
  <div class="max-w-3xl mx-auto px-6 text-center reveal">
    <p class="text-2xl font-display font-medium text-white/85 leading-relaxed mb-6">
      "The Yirgacheffe tasted like a different drink entirely from what I'd been buying
      at the grocery store. I didn't know coffee could taste like blueberries."
    </p>
    <p class="text-sm text-white/40">Maren T. — subscriber since 2024</p>
  </div>
</section>

<section class="py-20 bg-canvas-light border-t border-white/5">
  <div class="max-w-xl mx-auto px-6 text-center reveal">
    <h3 class="font-display text-2xl font-semibold mb-3">Get next week's roast first</h3>
    <p class="text-white/45 mb-6 text-sm">One email a week. New origin notes, brew tips, and early access to limited lots.</p>
    <form id="newsletter-form" class="flex flex-col sm:flex-row gap-3">
      <input type="email" id="newsletter-email" required placeholder="you@example.com" class="flex-1 bg-canvas-card border border-white/10 rounded-xl px-4 py-3 text-sm">
      <button type="submit" class="bg-accent hover:bg-accent-hover text-canvas font-semibold px-6 py-3 rounded-xl transition-colors">Subscribe</button>
    </form>
    <p id="newsletter-note" class="text-xs text-white/30 mt-3">No spam. Unsubscribe anytime.</p>
  </div>
</section>

<footer class="border-t border-white/5 py-12">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p>© 2026 Ember &amp; Stone Coffee Roasters.</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Privacy</a><a href="#" class="hover:text-white/60">Terms</a></div>
  </div>
</footer>

<aside id="cart-drawer" class="fixed top-0 right-0 h-full w-full sm:w-[420px] bg-canvas-light z-[90] translate-x-full transition-transform duration-300 flex flex-col border-l border-white/5">
  <div class="flex items-center justify-between p-6 border-b border-white/5">
    <h3 class="font-display font-semibold text-lg">Your Bag</h3>
    <button onclick="closeCart()" class="p-2 text-white/50 hover:text-white" aria-label="Close cart">&times;</button>
  </div>
  <div id="cart-items" class="flex-1 overflow-y-auto p-6 space-y-4">
    <div id="cart-empty-state" class="flex flex-col items-center justify-center h-full text-center">
      <p class="text-sm font-medium text-white/50 mb-1">Your bag is empty</p>
      <p class="text-xs text-white/25">Add a bag of something good</p>
    </div>
  </div>
  <div id="cart-footer" class="border-t border-white/5 p-6 space-y-4 hidden">
    <div class="flex items-center justify-between"><span class="font-semibold">Total</span><span id="cart-total" class="text-xl font-bold text-accent">$0.00</span></div>
    <button class="w-full bg-accent hover:bg-accent-hover text-canvas font-semibold py-4 rounded-xl transition-colors">Checkout</button>
  </div>
</aside>
<div id="cart-backdrop" onclick="closeCart()" class="fixed inset-0 bg-black/60 z-[85] opacity-0 pointer-events-none transition-opacity duration-300"></div>

<script>
const products = [
  { id:1, name:'Yirgacheffe, Ethiopia', notes:'Blueberry · Floral · Bergamot', price:19, category:'light' },
  { id:2, name:'Huila, Colombia', notes:'Caramel · Red Apple · Brown Sugar', price:18, category:'medium' },
  { id:3, name:'Antigua, Guatemala', notes:'Chocolate · Walnut · Orange Zest', price:18, category:'medium-dark' },
  { id:4, name:'Sidamo, Ethiopia', notes:'Jasmine · Stone Fruit · Honey', price:20, category:'light' },
  { id:5, name:'Tarrazú, Costa Rica', notes:'Cherry · Almond · Brown Butter', price:19, category:'medium' },
  { id:6, name:'Decaf Blend', notes:'Cocoa · Toasted Pecan · Soft Citrus', price:17, category:'decaf' },
];

let cart = [];

function escapeHtml(str){ const d=document.createElement('div'); d.textContent=str; return d.innerHTML; }

function renderProducts(){
  const grid = document.getElementById('product-grid');
  grid.innerHTML = '';
  products.forEach((p,i) => {
    const card = document.createElement('div');
    card.className = 'product-card reveal bg-canvas-card border border-white/5 rounded-2xl p-6 transition-transform hover:-translate-y-1';
    card.style.transitionDelay = (i*60)+'ms';
    card.innerHTML = `
      <div class="bag-shadow aspect-square rounded-xl bg-gradient-to-br from-accent/20 to-transparent mb-5 flex items-center justify-center">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="text-accent"><path d="M4 8h16l-1.5 12a2 2 0 0 1-2 1.8H7.5a2 2 0 0 1-2-1.8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>
      </div>
      <p class="text-xs text-white/35 uppercase tracking-wider mb-1">${escapeHtml(p.category)} roast</p>
      <h3 class="font-display font-semibold mb-1">${escapeHtml(p.name)}</h3>
      <p class="text-xs text-white/40 mb-4">${escapeHtml(p.notes)}</p>
      <div class="flex items-center justify-between">
        <span class="font-bold">$${p.price.toFixed(2)}</span>
        <button onclick="addToCart(${p.id})" class="text-xs font-semibold bg-white/5 hover:bg-accent hover:text-canvas px-4 py-2 rounded-lg transition-colors">Add to Bag</button>
      </div>
    `;
    grid.appendChild(card);
    observeReveal(card);
  });
}

function addToCart(id){
  const product = products.find(p=>p.id===id);
  const existing = cart.find(i=>i.id===id);
  if (existing) existing.qty += 1; else cart.push({...product, qty:1});
  renderCart(); updateBadge(); showToast(`${product.name} added to bag`);
}
function removeFromCart(id){ cart = cart.filter(i=>i.id!==id); renderCart(); updateBadge(); }
function updateQty(id,delta){ const item=cart.find(i=>i.id===id); if(!item) return; item.qty=Math.max(1,item.qty+delta); renderCart(); updateBadge(); }
function cartTotal(){ return cart.reduce((s,i)=>s+i.price*i.qty,0); }
function cartCount(){ return cart.reduce((s,i)=>s+i.qty,0); }

function renderCart(){
  const container = document.getElementById('cart-items');
  const footer = document.getElementById('cart-footer');
  const emptyState = document.getElementById('cart-empty-state');
  container.querySelectorAll('.cart-row').forEach(el=>el.remove());
  if (cart.length===0){ emptyState.style.display='flex'; footer.classList.add('hidden'); return; }
  emptyState.style.display='none'; footer.classList.remove('hidden');
  cart.forEach(item=>{
    const row=document.createElement('div');
    row.className='cart-row flex gap-4 pb-4 border-b border-white/5';
    row.innerHTML=`
      <div class="flex-1">
        <p class="font-medium text-sm">${escapeHtml(item.name)}</p>
        <div class="flex items-center gap-3 mt-2">
          <button data-id="${item.id}" data-delta="-1" class="qty-btn w-6 h-6 rounded bg-white/5 hover:bg-white/10">−</button>
          <span class="text-sm w-4 text-center">${item.qty}</span>
          <button data-id="${item.id}" data-delta="1" class="qty-btn w-6 h-6 rounded bg-white/5 hover:bg-white/10">+</button>
        </div>
      </div>
      <p class="font-semibold text-sm">$${(item.price*item.qty).toFixed(2)}</p>
    `;
    container.appendChild(row);
  });
  document.getElementById('cart-total').textContent = `$${cartTotal().toFixed(2)}`;
  container.querySelectorAll('.qty-btn').forEach(btn=>{
    btn.addEventListener('click', ()=>updateQty(parseInt(btn.dataset.id), parseInt(btn.dataset.delta)));
  });
}

function updateBadge(){
  const badge = document.getElementById('cart-badge');
  const count = cartCount();
  badge.textContent = count;
  badge.classList.toggle('hidden', count===0);
  badge.style.animation='none'; badge.offsetHeight; badge.style.animation='badgePop .3s cubic-bezier(.34,1.56,.64,1)';
}

function openCart(){
  document.getElementById('cart-drawer').classList.remove('translate-x-full');
  const b=document.getElementById('cart-backdrop'); b.classList.remove('opacity-0','pointer-events-none');
  document.body.style.overflow='hidden';
}
function closeCart(){
  document.getElementById('cart-drawer').classList.add('translate-x-full');
  const b=document.getElementById('cart-backdrop'); b.classList.add('opacity-0','pointer-events-none');
  document.body.style.overflow='';
}

function showToast(message){
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast bg-canvas-card border border-white/10 rounded-xl px-5 py-3 text-sm shadow-2xl pointer-events-auto';
  toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);
  requestAnimationFrame(()=>toast.classList.add('show'));
  setTimeout(()=>{ toast.classList.remove('show'); setTimeout(()=>toast.remove(),350); }, 2400);
}

const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileNav = document.getElementById('mobile-nav');
mobileMenuBtn.addEventListener('click', ()=>mobileNav.classList.toggle('hidden'));
mobileNav.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>mobileNav.classList.add('hidden')));

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(19,16,13,0.85)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

document.getElementById('newsletter-form').addEventListener('submit', (e)=>{
  e.preventDefault();
  const note = document.getElementById('newsletter-note');
  note.textContent = "You're on the list. Welcome aboard.";
  note.style.color = '#C9874A';
  e.target.reset();
});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
function observeReveal(el){ revealObserver.observe(el); }
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

const processLine = document.getElementById('process-line');
const processObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ processLine.classList.add('visible'); processObserver.disconnect(); } });
}, {threshold:0.3});
processObserver.observe(document.getElementById('process-strip'));

renderProducts();
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/02_law_firm.md

# Example — Boutique Law Firm (Vanilla CSS Architecture)

Tags: example, full-site, law-firm, legal, professional-services, vanilla-css, light-and-dark-mix, navy, gold, serif, editorial

Niche: boutique litigation law firm.
Architecture: vanilla CSS with custom properties, no external dependencies.
Palette: deep navy canvas (#0E1525), warm ivory text, brass gold accent (#B08D4F).
Signature element: a results ticker (case outcomes) that auto-scrolls horizontally,
plus a serif-led editorial typographic system.
Sections: header, hero, results ticker, practice areas, attorney profiles,
process/timeline, testimonial, contact form, footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ashworth &amp; Cole LLP | Civil Litigation Counsel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --navy:#0E1525; --navy-light:#16203A; --navy-lighter:#1F2D4D; --line:#2B3A5E;
  --ivory:#F4F1E8; --ivory-dim:#A9B0C2; --gold:#B08D4F; --gold-hover:#C7A567;
  --radius:6px; --radius-lg:10px;
  --transition: all 0.35s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow-lg: 0 20px 50px rgba(0,0,0,0.4);
  --serif:'Playfair Display', serif; --sans:'Source Sans 3', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--navy);color:var(--ivory);line-height:1.7;overflow-x:hidden;}
a{text-decoration:none;color:inherit;}
img{max-width:100%;display:block;}
button{cursor:pointer;font-family:inherit;}
.container{max-width:1180px;margin:0 auto;padding:0 2rem;}
.section{padding:6.5rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.78rem;color:var(--gold);margin-bottom:1rem;font-weight:600;}
.section-title{font-family:var(--serif);font-size:2.6rem;font-weight:600;line-height:1.2;margin-bottom:1rem;}
.section-subtitle{color:var(--ivory-dim);font-size:1.05rem;max-width:600px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.9rem 2.1rem;border:none;border-radius:var(--radius);font-size:0.9rem;font-weight:600;letter-spacing:0.5px;transition:var(--transition);text-transform:uppercase;}
.btn-primary{background:var(--gold);color:var(--navy);}
.btn-primary:hover{background:var(--gold-hover);transform:translateY(-2px);box-shadow:0 10px 24px rgba(176,141,79,0.3);}
.btn-outline{background:transparent;color:var(--ivory);border:1px solid var(--line);}
.btn-outline:hover{border-color:var(--gold);color:var(--gold);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.4rem 0;transition:var(--transition);}
.header.scrolled{background:rgba(14,21,37,0.95);backdrop-filter:blur(16px);padding:1rem 0;box-shadow:0 2px 30px rgba(0,0,0,0.4);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--serif);font-size:1.4rem;font-weight:700;letter-spacing:0.5px;}
.logo span{color:var(--gold);}
.nav-list{display:flex;list-style:none;gap:2.3rem;align-items:center;}
.nav-list a{font-size:0.85rem;font-weight:500;letter-spacing:1px;text-transform:uppercase;position:relative;padding:0.25rem 0;}
.nav-list a::after{content:"";position:absolute;bottom:-2px;left:0;width:0;height:1.5px;background:var(--gold);transition:var(--transition);}
.nav-list a:hover::after,.nav-list a.active::after{width:100%;}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:24px;height:2px;background:var(--ivory);transition:var(--transition);}
.menu-toggle.active span:nth-child(1){transform:translateY(7px) rotate(45deg);}
.menu-toggle.active span:nth-child(2){opacity:0;}
.menu-toggle.active span:nth-child(3){transform:translateY(-7px) rotate(-45deg);}

.overlay{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:92vh;display:flex;align-items:center;position:relative;padding-top:6rem;background:linear-gradient(160deg,var(--navy) 0%, var(--navy-light) 60%, var(--navy) 100%);}
.hero::before{content:"";position:absolute;top:-30%;right:-10%;width:60%;height:160%;background:radial-gradient(ellipse, rgba(176,141,79,0.07) 0%, transparent 60%);pointer-events:none;}
.hero-grid{display:grid;grid-template-columns:1.1fr 0.9fr;gap:4rem;align-items:center;}
.hero-label{display:inline-block;padding:0.4rem 1rem;border:1px solid rgba(176,141,79,0.4);border-radius:30px;font-size:0.78rem;letter-spacing:2.5px;text-transform:uppercase;color:var(--gold);margin-bottom:2rem;}
.hero-title{font-family:var(--serif);font-size:3.6rem;font-weight:700;line-height:1.15;margin-bottom:1.5rem;letter-spacing:-0.5px;}
.hero-title em{font-style:italic;color:var(--gold);font-weight:400;}
.hero-desc{font-size:1.1rem;color:var(--ivory-dim);max-width:480px;margin-bottom:2.2rem;}
.hero-actions{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:3rem;}
.hero-stats{display:flex;gap:2.5rem;padding-top:2rem;border-top:1px solid var(--line);flex-wrap:wrap;}
.hero-stat h4{font-family:var(--serif);font-size:2rem;color:var(--gold);line-height:1;margin-bottom:0.3rem;}
.hero-stat p{font-size:0.8rem;color:var(--ivory-dim);text-transform:uppercase;letter-spacing:1px;}
.hero-visual{background:var(--navy-light);border:1px solid var(--line);border-radius:var(--radius-lg);padding:3rem 2.5rem;}
.hero-visual-quote{font-family:var(--serif);font-style:italic;font-size:1.3rem;line-height:1.5;margin-bottom:1.5rem;color:var(--ivory);}
.hero-visual-meta{font-size:0.85rem;color:var(--ivory-dim);border-top:1px solid var(--line);padding-top:1.2rem;}

.ticker-wrap{background:var(--navy-light);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:1.4rem 0;overflow:hidden;position:relative;}
.ticker-track{display:flex;gap:3.5rem;white-space:nowrap;animation:tickerScroll 28s linear infinite;width:max-content;}
.ticker-item{display:flex;align-items:center;gap:0.7rem;font-size:0.95rem;color:var(--ivory-dim);}
.ticker-item strong{color:var(--gold);font-family:var(--serif);}
@keyframes tickerScroll{from{transform:translateX(0);}to{transform:translateX(-50%);}}
.ticker-wrap:hover .ticker-track{animation-play-state:paused;}

.practice-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-top:3rem;}
.practice-card{background:var(--navy-light);border-radius:var(--radius-lg);padding:2.3rem;transition:var(--transition);border:1px solid transparent;}
.practice-card:hover{transform:translateY(-6px);border-color:var(--gold);box-shadow:var(--shadow-lg);}
.practice-num{font-family:var(--serif);font-size:0.9rem;color:var(--gold);margin-bottom:1.2rem;letter-spacing:1px;}
.practice-title{font-family:var(--serif);font-size:1.35rem;margin-bottom:0.8rem;}
.practice-desc{color:var(--ivory-dim);font-size:0.92rem;}

.attorney-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;margin-top:3rem;}
.attorney-card{text-align:center;}
.attorney-photo{width:100%;aspect-ratio:1;border-radius:50%;background:linear-gradient(135deg,var(--navy-lighter),var(--navy-light));margin-bottom:1.3rem;display:flex;align-items:center;justify-content:center;font-family:var(--serif);font-size:2.5rem;color:var(--gold);border:2px solid var(--line);}
.attorney-name{font-family:var(--serif);font-size:1.2rem;margin-bottom:0.3rem;}
.attorney-role{font-size:0.85rem;color:var(--gold);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.8rem;}
.attorney-bio{font-size:0.88rem;color:var(--ivory-dim);}

.timeline{position:relative;margin-top:3.5rem;padding-left:2.5rem;}
.timeline::before{content:"";position:absolute;left:7px;top:8px;bottom:8px;width:2px;background:var(--line);}
.timeline-item{position:relative;padding-bottom:2.8rem;}
.timeline-item:last-child{padding-bottom:0;}
.timeline-item::before{content:"";position:absolute;left:-2.5rem;top:4px;width:16px;height:16px;border-radius:50%;background:var(--navy);border:2px solid var(--gold);}
.timeline-item h4{font-family:var(--serif);font-size:1.15rem;margin-bottom:0.4rem;}
.timeline-item p{color:var(--ivory-dim);font-size:0.92rem;max-width:560px;}

.testimonial-block{max-width:680px;margin:0 auto;text-align:center;}
.testimonial-quote{font-family:var(--serif);font-size:1.5rem;font-style:italic;line-height:1.6;margin-bottom:1.5rem;}
.testimonial-author{font-size:0.9rem;color:var(--gold);font-weight:600;}

.contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:4rem;margin-top:2.5rem;align-items:start;}
.contact-info h3{font-family:var(--serif);font-size:1.5rem;margin-bottom:1rem;}
.contact-info p{color:var(--ivory-dim);margin-bottom:1.5rem;}
.contact-detail{display:flex;gap:0.8rem;align-items:flex-start;margin-bottom:1.2rem;font-size:0.92rem;}
.contact-detail strong{color:var(--gold);min-width:90px;display:inline-block;}
.form-group{margin-bottom:1.4rem;}
.form-group label{display:block;font-size:0.82rem;font-weight:600;margin-bottom:0.45rem;letter-spacing:0.3px;}
.form-group input,.form-group textarea{width:100%;background:var(--navy-light);border:1px solid var(--line);color:var(--ivory);padding:0.8rem 1rem;border-radius:var(--radius);font-size:0.92rem;font-family:inherit;transition:var(--transition);}
.form-group input:focus,.form-group textarea:focus{outline:none;border-color:var(--gold);box-shadow:0 0 0 3px rgba(176,141,79,0.15);}
.form-group input.invalid,.form-group textarea.invalid{border-color:#c0564a;}
.form-error{display:block;font-size:0.78rem;color:#c0564a;margin-top:0.35rem;min-height:1.1em;}
.form-status{margin-top:0.8rem;font-size:0.88rem;}
.form-status.success{color:#6fa888;}
.form-status.error{color:#c0564a;}

.footer{background:var(--navy-light);border-top:1px solid var(--line);padding:4rem 0 0;}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:3rem;padding-bottom:3rem;}
.footer-col h4{font-size:0.82rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:1.2rem;color:var(--ivory);}
.footer-col a,.footer-col p{display:block;color:var(--ivory-dim);font-size:0.88rem;margin-bottom:0.8rem;}
.footer-col a:hover{color:var(--gold);}
.footer-bottom{border-top:1px solid var(--line);padding:1.4rem 0;display:flex;justify-content:space-between;font-size:0.82rem;color:var(--ivory-dim);}

.reveal{opacity:0;transform:translateY(28px);transition:all 0.7s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:900px){
  .hero-grid,.contact-grid{grid-template-columns:1fr;}
  .practice-grid,.attorney-grid{grid-template-columns:1fr 1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--navy);flex-direction:column;justify-content:center;gap:2.2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.6rem;}
  .footer-grid{grid-template-columns:1fr;}
}
@media (max-width:600px){
  .practice-grid,.attorney-grid{grid-template-columns:1fr;}
  .footer-bottom{flex-direction:column;gap:0.8rem;text-align:center;}
}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Ashworth <span>&amp;</span> Cole</a>
    <nav>
      <ul class="nav-list" id="nav-list">
        <li><a href="#hero" class="active">Home</a></li>
        <li><a href="#practice">Practice Areas</a></li>
        <li><a href="#attorneys">Attorneys</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
    </nav>
    <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <span class="hero-label">Civil Litigation &amp; Commercial Disputes</span>
        <h1 class="hero-title">Counsel for the cases<br><em>that can't be lost.</em></h1>
        <p class="hero-desc">A nine-attorney firm built for complex commercial litigation — the matters too consequential for a generalist and too specific for a mega-firm.</p>
        <div class="hero-actions">
          <a href="#contact" class="btn btn-primary">Request a Consultation</a>
          <a href="#practice" class="btn btn-outline">Our Practice Areas</a>
        </div>
        <div class="hero-stats">
          <div class="hero-stat"><h4>340+</h4><p>Matters Resolved</p></div>
          <div class="hero-stat"><h4>91%</h4><p>Favorable Outcomes</p></div>
          <div class="hero-stat"><h4>22</h4><p>Years Average Tenure</p></div>
        </div>
      </div>
      <div class="hero-visual">
        <p class="hero-visual-quote">"They treated our case like it was the only one on their desk."</p>
        <div class="hero-visual-meta">General Counsel, mid-market manufacturer</div>
      </div>
    </div>
  </div>
</section>

<div class="ticker-wrap" aria-label="Recent case results">
  <div class="ticker-track" id="ticker-track">
    <div class="ticker-item"><strong>$14.2M</strong> jury verdict — breach of contract</div>
    <div class="ticker-item"><strong>Dismissed</strong> — shareholder derivative suit</div>
    <div class="ticker-item"><strong>$6.8M</strong> settlement — trade secret dispute</div>
    <div class="ticker-item"><strong>Summary Judgment</strong> — employment class action</div>
    <div class="ticker-item"><strong>$22M</strong> arbitration award — partnership dissolution</div>
  </div>
</div>

<section class="section" id="practice">
  <div class="container">
    <div class="reveal">
      <span class="section-label">What We Handle</span>
      <h2 class="section-title">Practice areas</h2>
      <p class="section-subtitle">We take a small number of matters at a time, by design, across three core areas.</p>
    </div>
    <div class="practice-grid">
      <div class="practice-card reveal">
        <div class="practice-num">01</div>
        <h3 class="practice-title">Commercial Litigation</h3>
        <p class="practice-desc">Contract disputes, partnership dissolutions, and business torts for companies with too much at stake to settle cheap.</p>
      </div>
      <div class="practice-card reveal">
        <div class="practice-num">02</div>
        <h3 class="practice-title">Employment Defense</h3>
        <p class="practice-desc">Defending employers against class actions, wrongful termination claims, and regulatory investigations.</p>
      </div>
      <div class="practice-card reveal">
        <div class="practice-num">03</div>
        <h3 class="practice-title">Intellectual Property</h3>
        <p class="practice-desc">Trade secret misappropriation, licensing disputes, and IP-driven competitive litigation.</p>
      </div>
    </div>
  </div>
</section>

<section class="section" id="attorneys" style="background:var(--navy-light);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Who You'll Work With</span>
      <h2 class="section-title">Lead counsel</h2>
    </div>
    <div class="attorney-grid">
      <div class="attorney-card reveal">
        <div class="attorney-photo">EA</div>
        <h4 class="attorney-name">Eleanor Ashworth</h4>
        <p class="attorney-role">Founding Partner</p>
        <p class="attorney-bio">25 years trying commercial disputes to verdict. Former federal clerk.</p>
      </div>
      <div class="attorney-card reveal">
        <div class="attorney-photo">DC</div>
        <h4 class="attorney-name">David Cole</h4>
        <p class="attorney-role">Founding Partner</p>
        <p class="attorney-bio">Focuses on IP and trade secret litigation for manufacturing clients.</p>
      </div>
      <div class="attorney-card reveal">
        <div class="attorney-photo">RM</div>
        <h4 class="attorney-name">Rosa Mendez</h4>
        <p class="attorney-role">Senior Counsel</p>
        <p class="attorney-bio">Leads the employment defense practice; former EEOC trial attorney.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="reveal">
      <span class="section-label">How We Work</span>
      <h2 class="section-title">From first call to resolution</h2>
    </div>
    <div class="timeline">
      <div class="timeline-item reveal"><h4>Initial Consultation</h4><p>A senior partner — not an associate — assesses your matter within 48 hours of first contact.</p></div>
      <div class="timeline-item reveal"><h4>Case Strategy</h4><p>We map the strongest path to resolution, including realistic settlement value, before you're billed for a single filing.</p></div>
      <div class="timeline-item reveal"><h4>Active Litigation</h4><p>The partner who pitched you stays lead counsel through trial — no quiet handoffs to junior staff.</p></div>
      <div class="timeline-item reveal"><h4>Resolution</h4><p>Settlement, verdict, or dismissal — we close the loop with a plain-English summary of what it means for your business.</p></div>
    </div>
  </div>
</section>

<section class="section" style="background:var(--navy-light);">
  <div class="container">
    <div class="testimonial-block reveal">
      <p class="testimonial-quote">"We had three other firms tell us to settle. Ashworth & Cole told us why we shouldn't — and proved it at trial."</p>
      <p class="testimonial-author">CFO, regional logistics company</p>
    </div>
  </div>
</section>

<section class="section" id="contact">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Get In Touch</span>
      <h2 class="section-title">Request a consultation</h2>
    </div>
    <div class="contact-grid">
      <div class="contact-info reveal">
        <h3>Speak with a partner directly</h3>
        <p>Every inquiry is reviewed personally by a founding partner within one business day — not routed through intake staff.</p>
        <div class="contact-detail"><strong>Office</strong> 412 Exchange Place, Suite 1900</div>
        <div class="contact-detail"><strong>Phone</strong> (212) 555-0148</div>
        <div class="contact-detail"><strong>Hours</strong> Mon–Fri, 8:30am–6pm ET</div>
      </div>
      <form id="contact-form" class="reveal" novalidate>
        <div class="form-group">
          <label for="name">Full name</label>
          <input type="text" id="name" name="name" required>
          <span class="form-error" id="name-error"></span>
        </div>
        <div class="form-group">
          <label for="email">Email address</label>
          <input type="email" id="email" name="email" required>
          <span class="form-error" id="email-error"></span>
        </div>
        <div class="form-group">
          <label for="message">Briefly describe your matter</label>
          <textarea id="message" name="message" rows="4" required></textarea>
          <span class="form-error" id="message-error"></span>
        </div>
        <button type="submit" class="btn btn-primary">Send Inquiry</button>
        <p class="form-status" id="form-status"></p>
      </form>
    </div>
  </div>
</section>

<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-col">
      <h4>Ashworth &amp; Cole LLP</h4>
      <p>Civil litigation counsel for companies who can't afford to lose the matter that matters most.</p>
    </div>
    <div class="footer-col">
      <h4>Firm</h4>
      <a href="#practice">Practice Areas</a>
      <a href="#attorneys">Attorneys</a>
      <a href="#contact">Contact</a>
    </div>
    <div class="footer-col">
      <h4>Legal</h4>
      <a href="#">Privacy Policy</a>
      <a href="#">Terms of Use</a>
      <a href="#">Disclaimer</a>
    </div>
  </div>
  <div class="container footer-bottom">
    <p>© 2026 Ashworth &amp; Cole LLP. Attorney advertising.</p>
    <p>This is not legal advice. Past results do not guarantee future outcomes.</p>
  </div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function () {
  const header = document.getElementById('header');
  const menuToggle = document.getElementById('menu-toggle');
  const navList = document.getElementById('nav-list');
  const overlay = document.getElementById('overlay');

  function toggleMenu(){
    menuToggle.classList.toggle('active');
    navList.classList.toggle('open');
    overlay.classList.toggle('active');
    document.body.style.overflow = navList.classList.contains('open') ? 'hidden' : '';
  }
  menuToggle.addEventListener('click', toggleMenu);
  overlay.addEventListener('click', toggleMenu);
  navList.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    if (navList.classList.contains('open')) toggleMenu();
  }));

  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });

  const navLinks = document.querySelectorAll('.nav-list a');
  const sections = document.querySelectorAll('section[id]');
  const navObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        navLinks.forEach(link => link.classList.toggle('active', link.getAttribute('href') === `#${id}`));
      }
    });
  }, { threshold: 0.3, rootMargin: '-80px 0px -50% 0px' });
  sections.forEach(s => navObserver.observe(s));

  const revealEls = document.querySelectorAll('.reveal');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
  revealEls.forEach(el => revealObserver.observe(el));

  const form = document.getElementById('contact-form');
  const validators = {
    name: (v) => v.trim().length >= 2 || 'Please enter your full name.',
    email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Enter a valid email address.',
    message: (v) => v.trim().length >= 10 || 'Tell us a bit more about your matter.'
  };
  function validateField(fieldName){
    const field = document.getElementById(fieldName);
    const errorEl = document.getElementById(`${fieldName}-error`);
    const result = validators[fieldName](field.value);
    if (result === true) { field.classList.remove('invalid'); errorEl.textContent=''; return true; }
    field.classList.add('invalid'); errorEl.textContent = result; return false;
  }
  Object.keys(validators).forEach(fieldName => {
    const field = document.getElementById(fieldName);
    field.addEventListener('blur', () => validateField(fieldName));
    field.addEventListener('input', () => { if (field.classList.contains('invalid')) validateField(fieldName); });
  });
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const allValid = Object.keys(validators).map(validateField).every(Boolean);
    const statusEl = document.getElementById('form-status');
    if (!allValid) { statusEl.textContent = 'Please fix the highlighted fields above.'; statusEl.className = 'form-status error'; return; }
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true; submitBtn.textContent = 'Sending...';
    setTimeout(() => {
      statusEl.textContent = "Thank you — a partner will respond within one business day.";
      statusEl.className = 'form-status success';
      form.reset();
      submitBtn.disabled = false; submitBtn.textContent = 'Send Inquiry';
    }, 900);
  });
});
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/03_bouldering_gym.md

# Example — Indoor Bouldering Gym (Tailwind Architecture)

Tags: example, full-site, climbing, bouldering, gym, fitness, tailwind, dark-theme, lime, charcoal, route-grades

Niche: indoor bouldering gym with graded routes and day passes/memberships.
Architecture: Tailwind CDN utility classes.
Palette: charcoal canvas (#16181A), chalky off-white text, electric lime accent (#C8FF4D).
Signature element: an interactive route-grade legend with a live "today's resets" grid
that color-codes difficulty.
Sections: header, hero, grade legend / today's resets grid, membership tiers,
class schedule, community/testimonial, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Crux Bouldering Co. | Climb. Reset. Repeat.</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  theme: { extend: {
    colors: { canvas:{DEFAULT:'#16181A',light:'#1F2123',card:'#26282A'}, accent:{DEFAULT:'#C8FF4D',hover:'#D7FF77',glow:'rgba(200,255,77,0.25)'} },
    fontFamily: { sans:['Inter','system-ui','sans-serif'], display:['Archivo Black','sans-serif'] }
  }}
}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Archivo+Black&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
  .font-display{font-family:'Archivo Black',sans-serif;}
  ::selection{background:rgba(200,255,77,0.3);}
  .hero-title{font-size:clamp(2.8rem,7vw,6.2rem);line-height:0.95;letter-spacing:-0.02em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .grade-cell{transition:all .25s cubic-bezier(.34,1.56,.64,1);}
  .grade-cell:hover{transform:scale(1.08);}
  .tier-card{transition:all .3s cubic-bezier(.25,.46,.45,.94);}
  .tier-card.featured{transform:scale(1.04);}
  input:focus,button:focus-visible{outline:2px solid #C8FF4D;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <button id="mobile-menu-btn" class="lg:hidden p-2 -ml-2" aria-label="Open menu">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <a href="#" class="font-display text-xl tracking-tight">CRUX</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#grades" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">Today's Resets</a>
        <a href="#membership" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">Membership</a>
        <a href="#schedule" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">Schedule</a>
      </nav>
      <a href="#membership" class="bg-accent text-canvas font-bold text-sm px-5 py-2.5 rounded-full hover:bg-accent-hover transition-colors">Day Pass</a>
    </div>
  </div>
  <div id="mobile-nav" class="hidden lg:hidden bg-canvas-light border-b border-white/5">
    <div class="px-6 py-6 flex flex-col gap-4">
      <a href="#grades">Today's Resets</a><a href="#membership">Membership</a><a href="#schedule">Schedule</a>
    </div>
  </div>
</header>

<section class="relative min-h-[92vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 80% 30%, rgba(200,255,77,0.06) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
    <p class="text-accent text-sm font-bold uppercase tracking-widest mb-6">42 New Routes This Week</p>
    <h1 class="hero-title font-display text-white mb-8">
      SEND<br><span class="text-accent">HARDER.</span>
    </h1>
    <p class="text-lg text-white/50 max-w-md mb-10 leading-relaxed">
      18,000 sq ft of bouldering, 9 wall angles, and a reset crew that never lets the
      board go stale.
    </p>
    <div class="flex flex-col sm:flex-row gap-4">
      <a href="#membership" class="bg-accent hover:bg-accent-hover text-canvas font-bold px-8 py-4 rounded-xl transition-all hover:-translate-y-0.5">Get a Day Pass — $22</a>
      <a href="#grades" class="border border-white/15 hover:border-white/30 font-semibold px-8 py-4 rounded-xl transition-all hover:bg-white/5">See Today's Sets</a>
    </div>
  </div>
</section>

<section id="grades" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="reveal mb-12">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Live Board</p>
      <h2 class="font-display text-3xl lg:text-4xl">Today's Resets by Grade</h2>
      <p class="text-white/45 mt-2 max-w-lg">Tap a grade to see how many problems are live on the floor right now.</p>
    </div>
    <div id="grade-legend" class="grid grid-cols-3 sm:grid-cols-6 gap-3 mb-10"></div>
    <div class="bg-canvas-card border border-white/5 rounded-2xl p-6 flex items-center justify-between reveal">
      <div>
        <p class="text-sm text-white/40">Selected grade</p>
        <p id="selected-grade-label" class="font-display text-2xl text-accent">V0–V2</p>
      </div>
      <div class="text-right">
        <p id="selected-grade-count" class="font-display text-3xl">14</p>
        <p class="text-sm text-white/40">live problems</p>
      </div>
    </div>
  </div>
</section>

<section id="membership" class="py-24 lg:py-32">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Membership</p>
      <h2 class="font-display text-3xl lg:text-4xl">Pick your commitment</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="tier-card reveal bg-canvas-card border border-white/5 rounded-2xl p-8">
        <p class="text-sm text-white/40 uppercase tracking-wide mb-2">Drop In</p>
        <p class="font-display text-4xl mb-4">$22</p>
        <ul class="space-y-2 text-sm text-white/55 mb-6">
          <li>Single day access</li>
          <li>Shoe rental included</li>
          <li>No commitment</li>
        </ul>
        <button class="w-full border border-white/15 hover:border-accent hover:text-accent font-semibold py-3 rounded-xl transition-all">Buy Pass</button>
      </div>
      <div class="tier-card featured reveal bg-canvas-card border border-accent rounded-2xl p-8 relative">
        <span class="absolute -top-3 left-8 bg-accent text-canvas text-xs font-bold px-3 py-1 rounded-full">Most Popular</span>
        <p class="text-sm text-white/40 uppercase tracking-wide mb-2">Monthly</p>
        <p class="font-display text-4xl mb-4">$89<span class="text-base text-white/40">/mo</span></p>
        <ul class="space-y-2 text-sm text-white/55 mb-6">
          <li>Unlimited climbing</li>
          <li>2 free guest passes/mo</li>
          <li>10% off gear &amp; rentals</li>
        </ul>
        <button class="w-full bg-accent hover:bg-accent-hover text-canvas font-bold py-3 rounded-xl transition-all">Join Now</button>
      </div>
      <div class="tier-card reveal bg-canvas-card border border-white/5 rounded-2xl p-8">
        <p class="text-sm text-white/40 uppercase tracking-wide mb-2">Annual</p>
        <p class="font-display text-4xl mb-4">$799<span class="text-base text-white/40">/yr</span></p>
        <ul class="space-y-2 text-sm text-white/55 mb-6">
          <li>Everything in Monthly</li>
          <li>2 months free vs. monthly</li>
          <li>Locked-in rate</li>
        </ul>
        <button class="w-full border border-white/15 hover:border-accent hover:text-accent font-semibold py-3 rounded-xl transition-all">Join Now</button>
      </div>
    </div>
  </div>
</section>

<section id="schedule" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-14 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">This Week</p>
      <h2 class="font-display text-3xl lg:text-4xl">Class schedule</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="reveal bg-canvas-card border border-white/5 rounded-xl p-5"><p class="text-xs text-accent uppercase tracking-wide mb-2">Mon, 6:30pm</p><p class="font-semibold">Movement Fundamentals</p></div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-xl p-5"><p class="text-xs text-accent uppercase tracking-wide mb-2">Wed, 7:00pm</p><p class="font-semibold">Comp Training Squad</p></div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-xl p-5"><p class="text-xs text-accent uppercase tracking-wide mb-2">Fri, 6:00pm</p><p class="font-semibold">Women's Climb Night</p></div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-xl p-5"><p class="text-xs text-accent uppercase tracking-wide mb-2">Sat, 10:00am</p><p class="font-semibold">Youth Climb Club</p></div>
    </div>
  </div>
</section>

<section class="py-20 border-t border-white/5">
  <div class="max-w-3xl mx-auto px-6 text-center reveal">
    <p class="text-2xl font-medium text-white/85 leading-relaxed mb-6">"I came for one drop-in and never left. The reset crew here keeps the board honest — nothing feels stale after week one."</p>
    <p class="text-sm text-white/40">Jordan P. — member since 2023</p>
  </div>
</section>

<footer class="border-t border-white/5 py-12 bg-canvas-light">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p>© 2026 Crux Bouldering Co.</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Waiver</a><a href="#" class="hover:text-white/60">Contact</a></div>
  </div>
</footer>

<script>
const grades = [
  { label:'V0–V2', count:14, color:'#C8FF4D' },
  { label:'V3–V4', count:22, color:'#9FE85C' },
  { label:'V5–V6', count:17, color:'#F5D547' },
  { label:'V7–V8', count:9, color:'#F2994A' },
  { label:'V9–V10', count:5, color:'#EB5757' },
  { label:'V11+', count:2, color:'#9B51E0' },
];

function renderGrades(){
  const wrap = document.getElementById('grade-legend');
  wrap.innerHTML = '';
  grades.forEach((g,i) => {
    const cell = document.createElement('button');
    cell.className = 'grade-cell reveal bg-canvas-card border border-white/5 rounded-xl p-4 text-left hover:border-white/20';
    cell.style.transitionDelay = (i*50)+'ms';
    cell.innerHTML = `
      <div class="w-3 h-3 rounded-full mb-3" style="background:${g.color}"></div>
      <p class="font-display text-sm mb-1">${g.label}</p>
      <p class="text-xs text-white/40">${g.count} live</p>
    `;
    cell.addEventListener('click', () => selectGrade(g));
    wrap.appendChild(cell);
    revealObserver.observe(cell);
  });
}
function selectGrade(g){
  document.getElementById('selected-grade-label').textContent = g.label;
  document.getElementById('selected-grade-label').style.color = g.color;
  const countEl = document.getElementById('selected-grade-count');
  countEl.textContent = g.count;
  countEl.style.animation = 'none'; countEl.offsetHeight; countEl.style.animation = 'pop .3s cubic-bezier(.34,1.56,.64,1)';
}

const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileNav = document.getElementById('mobile-nav');
mobileMenuBtn.addEventListener('click', () => mobileNav.classList.toggle('hidden'));
mobileNav.querySelectorAll('a').forEach(l => l.addEventListener('click', () => mobileNav.classList.add('hidden')));

const header = document.getElementById('site-header');
window.addEventListener('scroll', () => {
  if (window.scrollY>80){ header.style.background='rgba(22,24,26,0.85)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

renderGrades();
</script>

<style>
@keyframes pop { 0%{transform:scale(0.7);opacity:0.5;} 100%{transform:scale(1);opacity:1;} }
</style>
</body>
</html>
```

---
## SOURCE: 03_examples/04_ceramics_studio.md

# Example — Artisan Ceramics Studio (Vanilla CSS Architecture, Light Mode)

Tags: example, full-site, ceramics, pottery, artisan, craft, vanilla-css, light-theme, clay, sand, ecommerce

Niche: small-batch ceramics studio selling handmade tableware.
Architecture: vanilla CSS with custom properties, no external dependencies.
Palette: warm sand/cream canvas (#F4EEE4), espresso text, terracotta clay accent (#B5602E).
Signature element: a horizontal kiln-firing process strip showing the four stages a
piece passes through, with a subtle progress fill on scroll.
Sections: header, hero, process strip, shop grid with cart, studio story, care guide,
newsletter, footer.

This is a LIGHT-MODE example — note the inverted contrast relationships versus the
dark-theme examples elsewhere in this corpus: canvas is light, text is dark, cards
are a slightly lighter/warmer tone than canvas rather than darker.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hearth &amp; Hand Ceramics | Handmade Stoneware Tableware</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Karla:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --sand:#F4EEE4; --sand-card:#FBF8F2; --cream-line:#E3D9C7;
  --espresso:#3A2E22; --espresso-dim:#6B5D4D; --clay:#B5602E; --clay-hover:#C97540; --clay-dark:#964F25;
  --radius:10px; --radius-lg:18px;
  --transition: all 0.35s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow: 0 10px 30px rgba(58,46,34,0.08);
  --shadow-lg: 0 20px 50px rgba(58,46,34,0.14);
  --serif:'Cormorant Garamond', serif; --sans:'Karla', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--sand);color:var(--espresso);line-height:1.65;overflow-x:hidden;}
a{text-decoration:none;color:inherit;}
img{max-width:100%;display:block;}
button{cursor:pointer;font-family:inherit;}
.container{max-width:1180px;margin:0 auto;padding:0 2rem;}
.section{padding:6rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.78rem;color:var(--clay);margin-bottom:1rem;font-weight:700;}
.section-title{font-family:var(--serif);font-size:2.7rem;font-weight:600;line-height:1.15;margin-bottom:1rem;}
.section-subtitle{color:var(--espresso-dim);font-size:1.05rem;max-width:560px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.9rem 2.1rem;border:none;border-radius:var(--radius);font-size:0.88rem;font-weight:700;letter-spacing:0.4px;transition:var(--transition);}
.btn-primary{background:var(--clay);color:#fff;}
.btn-primary:hover{background:var(--clay-hover);transform:translateY(-2px);box-shadow:0 12px 26px rgba(181,96,46,0.28);}
.btn-outline{background:transparent;color:var(--espresso);border:1.5px solid var(--cream-line);}
.btn-outline:hover{border-color:var(--clay);color:var(--clay);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.4rem 0;transition:var(--transition);}
.header.scrolled{background:rgba(244,238,228,0.92);backdrop-filter:blur(14px);padding:1rem 0;box-shadow:0 2px 24px rgba(58,46,34,0.08);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--serif);font-size:1.5rem;font-weight:700;}
.logo span{color:var(--clay);}
.nav-list{display:flex;list-style:none;gap:2.3rem;align-items:center;}
.nav-list a{font-size:0.85rem;font-weight:600;letter-spacing:0.6px;position:relative;padding:0.25rem 0;}
.nav-list a::after{content:"";position:absolute;bottom:-2px;left:0;width:0;height:2px;background:var(--clay);transition:var(--transition);}
.nav-list a:hover::after,.nav-list a.active::after{width:100%;}
.cart-btn{position:relative;background:none;border:none;padding:0.4rem;}
.cart-badge{position:absolute;top:-4px;right:-6px;background:var(--clay);color:#fff;font-size:0.65rem;font-weight:700;width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;}
.cart-badge.hidden{display:none;}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:24px;height:2px;background:var(--espresso);transition:var(--transition);}
.menu-toggle.active span:nth-child(1){transform:translateY(7px) rotate(45deg);}
.menu-toggle.active span:nth-child(2){opacity:0;}
.menu-toggle.active span:nth-child(3){transform:translateY(-7px) rotate(-45deg);}
.overlay{position:fixed;inset:0;background:rgba(58,46,34,0.5);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:88vh;display:flex;align-items:center;position:relative;padding-top:6rem;}
.hero-grid{display:grid;grid-template-columns:1.05fr 0.95fr;gap:4rem;align-items:center;}
.hero-label{display:inline-block;padding:0.4rem 1rem;background:rgba(181,96,46,0.1);border:1px solid rgba(181,96,46,0.25);border-radius:30px;font-size:0.78rem;letter-spacing:2px;text-transform:uppercase;color:var(--clay-dark);margin-bottom:2rem;font-weight:700;}
.hero-title{font-family:var(--serif);font-size:3.7rem;font-weight:600;line-height:1.1;margin-bottom:1.4rem;letter-spacing:-0.5px;}
.hero-title em{font-style:italic;color:var(--clay);font-weight:700;}
.hero-desc{font-size:1.1rem;color:var(--espresso-dim);max-width:460px;margin-bottom:2.2rem;}
.hero-actions{display:flex;gap:1rem;flex-wrap:wrap;}
.hero-visual{position:relative;aspect-ratio:1;border-radius:var(--radius-lg);background:linear-gradient(150deg,#E8DCC8,#D9C8AC);display:flex;align-items:center;justify-content:center;box-shadow:var(--shadow-lg);}
.hero-visual-icon{font-size:5rem;}

.process-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:2rem;margin-top:3.5rem;position:relative;}
.process-bar{position:absolute;top:27px;left:0;height:2px;background:var(--cream-line);width:100%;}
.process-bar-fill{position:absolute;top:27px;left:0;height:2px;background:var(--clay);width:0;transition:width 1.3s cubic-bezier(0.16,1,0.3,1);}
.process-step{text-align:center;position:relative;}
.process-icon{width:56px;height:56px;border-radius:50%;background:var(--sand-card);border:2px solid var(--cream-line);display:flex;align-items:center;justify-content:center;margin:0 auto 1.2rem;font-size:1.5rem;position:relative;z-index:2;transition:var(--transition);}
.process-step.active .process-icon{border-color:var(--clay);background:var(--clay);color:#fff;}
.process-step h4{font-family:var(--serif);font-size:1.15rem;margin-bottom:0.4rem;}
.process-step p{font-size:0.85rem;color:var(--espresso-dim);}

.shop-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1.5rem;margin-top:3rem;}
.product-card{background:var(--sand-card);border-radius:var(--radius-lg);overflow:hidden;transition:var(--transition);border:1px solid var(--cream-line);}
.product-card:hover{transform:translateY(-6px);box-shadow:var(--shadow-lg);}
.product-image{aspect-ratio:1;background:linear-gradient(150deg,#E8DCC8,#D9C8AC);display:flex;align-items:center;justify-content:center;font-size:3rem;position:relative;}
.product-info{padding:1.4rem;}
.product-cat{font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:var(--clay);margin-bottom:0.4rem;font-weight:700;}
.product-name{font-family:var(--serif);font-size:1.15rem;margin-bottom:0.5rem;}
.product-footer{display:flex;align-items:center;justify-content:space-between;}
.product-price{font-weight:700;font-size:1.05rem;}
.add-btn{background:var(--sand);border:1px solid var(--cream-line);color:var(--espresso);font-size:0.78rem;font-weight:700;padding:0.5rem 0.9rem;border-radius:8px;transition:var(--transition);}
.add-btn:hover{background:var(--clay);color:#fff;border-color:var(--clay);}

.story-grid{display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center;margin-top:2rem;}
.story-visual{aspect-ratio:4/3;border-radius:var(--radius-lg);background:linear-gradient(150deg,#E8DCC8,#D9C8AC);display:flex;align-items:center;justify-content:center;font-size:4rem;}
.story-text p{color:var(--espresso-dim);margin-bottom:1.2rem;font-size:1.02rem;}

.care-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-top:3rem;}
.care-card{background:var(--sand-card);border-radius:var(--radius-lg);padding:2rem;border:1px solid var(--cream-line);}
.care-card h4{font-family:var(--serif);font-size:1.2rem;margin-bottom:0.6rem;}
.care-card p{color:var(--espresso-dim);font-size:0.92rem;}

.newsletter-section{background:var(--clay);color:#fff;text-align:center;}
.newsletter-section h3{font-family:var(--serif);font-size:2rem;margin-bottom:0.8rem;}
.newsletter-section p{opacity:0.9;margin-bottom:2rem;}
.newsletter-form{display:flex;gap:0.8rem;max-width:420px;margin:0 auto;flex-wrap:wrap;justify-content:center;}
.newsletter-form input{flex:1;min-width:200px;padding:0.85rem 1.1rem;border-radius:var(--radius);border:none;font-family:inherit;font-size:0.92rem;}
.newsletter-form button{background:var(--espresso);color:#fff;border:none;padding:0.85rem 1.6rem;border-radius:var(--radius);font-weight:700;font-size:0.9rem;}
.newsletter-note{margin-top:1rem;font-size:0.82rem;opacity:0.85;}

.footer{background:var(--espresso);color:var(--sand);padding:3.5rem 0 0;}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:3rem;padding-bottom:2.5rem;}
.footer-col h4{font-size:0.8rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:1.1rem;opacity:0.6;}
.footer-col a,.footer-col p{display:block;color:var(--sand);opacity:0.75;font-size:0.88rem;margin-bottom:0.75rem;}
.footer-col a:hover{opacity:1;color:var(--clay-hover);}
.footer-bottom{border-top:1px solid rgba(244,238,228,0.12);padding:1.3rem 0;display:flex;justify-content:space-between;font-size:0.8rem;opacity:0.6;}

.cart-drawer{position:fixed;top:0;right:0;height:100%;width:400px;background:var(--sand-card);z-index:1100;transform:translateX(100%);transition:transform 0.35s cubic-bezier(0.16,1,0.3,1);display:flex;flex-direction:column;box-shadow:-10px 0 40px rgba(0,0,0,0.15);}
.cart-drawer.open{transform:translateX(0);}
.cart-header{display:flex;justify-content:space-between;align-items:center;padding:1.6rem;border-bottom:1px solid var(--cream-line);}
.cart-header h3{font-family:var(--serif);font-size:1.3rem;}
.cart-close{background:var(--sand);border:none;width:32px;height:32px;border-radius:50%;font-size:1.2rem;}
.cart-items{flex:1;overflow-y:auto;padding:1.6rem;}
.cart-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;color:var(--espresso-dim);}
.cart-row{display:flex;gap:1rem;padding-bottom:1.2rem;margin-bottom:1.2rem;border-bottom:1px solid var(--cream-line);}
.qty-btn{width:24px;height:24px;border-radius:6px;border:1px solid var(--cream-line);background:var(--sand);}
.cart-footer{padding:1.6rem;border-top:1px solid var(--cream-line);}
.cart-total-row{display:flex;justify-content:space-between;margin-bottom:1rem;font-weight:700;}
.cart-backdrop{position:fixed;inset:0;background:rgba(58,46,34,0.5);z-index:1050;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.cart-backdrop.active{opacity:1;pointer-events:auto;}

.reveal{opacity:0;transform:translateY(28px);transition:all 0.7s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .hero-grid,.story-grid{grid-template-columns:1fr;}
  .shop-grid{grid-template-columns:repeat(2,1fr);}
  .process-strip{grid-template-columns:repeat(2,1fr);row-gap:2.5rem;}
  .process-bar,.process-bar-fill{display:none;}
  .care-grid{grid-template-columns:1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--sand);flex-direction:column;justify-content:center;gap:2.2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.6rem;}
  .footer-grid{grid-template-columns:1fr;}
  .cart-drawer{width:100%;}
}
@media (max-width:600px){
  .shop-grid{grid-template-columns:1fr;}
  .footer-bottom{flex-direction:column;gap:0.7rem;text-align:center;}
}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Hearth <span>&amp;</span> Hand</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero" class="active">Home</a></li>
      <li><a href="#shop">Shop</a></li>
      <li><a href="#story">Our Story</a></li>
      <li><a href="#care">Care Guide</a></li>
    </ul></nav>
    <div style="display:flex;align-items:center;gap:0.5rem;">
      <button class="cart-btn" id="cart-btn" aria-label="Open cart">
        🧺<span class="cart-badge hidden" id="cart-badge">0</span>
      </button>
      <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <span class="hero-label">Small-Batch, Wood-Fired Stoneware</span>
        <h1 class="hero-title">Tableware shaped<br>by <em>one pair of hands.</em></h1>
        <p class="hero-desc">Every piece is thrown, glazed, and fired in our backyard studio — no molds, no two pieces quite the same.</p>
        <div class="hero-actions">
          <a href="#shop" class="btn btn-primary">Shop the Collection</a>
          <a href="#story" class="btn btn-outline">Meet the Studio</a>
        </div>
      </div>
      <div class="hero-visual"><span class="hero-visual-icon">🏺</span></div>
    </div>
  </div>
</section>

<section class="section" id="process" style="background:var(--sand-card);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">How Each Piece Is Made</span>
      <h2 class="section-title">From clay to your table</h2>
    </div>
    <div class="process-strip" id="process-strip">
      <div class="process-bar"></div>
      <div class="process-bar-fill" id="process-fill"></div>
      <div class="process-step reveal"><div class="process-icon">🧱</div><h4>Throw</h4><p>Hand-thrown on the wheel from local stoneware clay.</p></div>
      <div class="process-step reveal"><div class="process-icon">☀️</div><h4>Dry</h4><p>Air-dried slowly over 5-7 days to prevent cracking.</p></div>
      <div class="process-step reveal"><div class="process-icon">🎨</div><h4>Glaze</h4><p>Hand-dipped in small-batch glazes mixed in-house.</p></div>
      <div class="process-step reveal"><div class="process-icon">🔥</div><h4>Fire</h4><p>Wood-fired at 2,300°F for a one-of-a-kind finish.</p></div>
    </div>
  </div>
</section>

<section class="section" id="shop">
  <div class="container">
    <div class="reveal">
      <span class="section-label">The Collection</span>
      <h2 class="section-title">Shop tableware</h2>
    </div>
    <div class="shop-grid" id="shop-grid"></div>
  </div>
</section>

<section class="section" id="story" style="background:var(--sand-card);">
  <div class="container">
    <div class="story-grid">
      <div class="story-visual reveal">🧑‍🎨</div>
      <div class="story-text reveal">
        <span class="section-label">Our Story</span>
        <h2 class="section-title">Started in a garage, still in one</h2>
        <p>Hearth &amp; Hand began in 2019 when Mara started throwing bowls for friends on a wheel
        wedged between the lawnmower and the recycling bins. Six years later, the garage is bigger
        but the process hasn't changed — every piece still passes through her hands alone.</p>
        <p>We fire in small kiln loads of 30-40 pieces, which means waitlists during the holidays
        and the occasional sold-out glaze. We think that's a fair trade for never compromising
        on how a piece is made.</p>
      </div>
    </div>
  </div>
</section>

<section class="section" id="care">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Living With Stoneware</span>
      <h2 class="section-title">Care guide</h2>
    </div>
    <div class="care-grid">
      <div class="care-card reveal"><h4>Dishwasher Safe</h4><p>All glazed pieces are dishwasher and microwave safe. Hand-wash unglazed bases.</p></div>
      <div class="care-card reveal"><h4>Expect Variation</h4><p>Glaze pooling and slight color shifts are part of the wood-firing process, not a flaw.</p></div>
      <div class="care-card reveal"><h4>Avoid Thermal Shock</h4><p>Let pieces come to room temperature before moving from fridge to oven.</p></div>
    </div>
  </div>
</section>

<section class="section newsletter-section">
  <div class="container">
    <h3>Get first access to new glaze drops</h3>
    <p>We restock in small batches — subscribers hear first.</p>
    <form class="newsletter-form" id="newsletter-form">
      <input type="email" id="newsletter-email" placeholder="you@example.com" required>
      <button type="submit">Subscribe</button>
    </form>
    <p class="newsletter-note" id="newsletter-note">No spam, just clay dust and good news.</p>
  </div>
</section>

<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-col">
      <h4>Hearth &amp; Hand Ceramics</h4>
      <p>Hand-thrown stoneware tableware, fired in small batches in our backyard studio.</p>
    </div>
    <div class="footer-col"><h4>Shop</h4><a href="#shop">All Tableware</a><a href="#">Gift Cards</a><a href="#">Seconds Sale</a></div>
    <div class="footer-col"><h4>Studio</h4><a href="#story">Our Story</a><a href="#care">Care Guide</a><a href="#">Wholesale Inquiries</a></div>
  </div>
  <div class="container footer-bottom"><p>© 2026 Hearth &amp; Hand Ceramics.</p><p>Made in small batches, always.</p></div>
</footer>

<div class="cart-drawer" id="cart-drawer">
  <div class="cart-header"><h3>Your Basket</h3><button class="cart-close" id="cart-close" aria-label="Close cart">&times;</button></div>
  <div class="cart-items" id="cart-items">
    <div class="cart-empty" id="cart-empty"><p>Your basket is empty.</p></div>
  </div>
  <div class="cart-footer" id="cart-footer" style="display:none;">
    <div class="cart-total-row"><span>Total</span><span id="cart-total">$0.00</span></div>
    <button class="btn btn-primary" style="width:100%;justify-content:center;">Checkout</button>
  </div>
</div>
<div class="cart-backdrop" id="cart-backdrop"></div>

<script>
document.addEventListener('DOMContentLoaded', function () {
  const products = [
    { id:1, name:'Speckled Dinner Plate', cat:'Dinnerware', price:42, icon:'🍽️' },
    { id:2, name:'Wood-Ash Cereal Bowl', cat:'Dinnerware', price:34, icon:'🥣' },
    { id:3, name:'Carved Mug, Sand Glaze', cat:'Drinkware', price:28, icon:'☕' },
    { id:4, name:'Serving Platter', cat:'Serveware', price:68, icon:'🍲' },
    { id:5, name:'Pinch Bowl Set of 3', cat:'Serveware', price:36, icon:'🫕' },
    { id:6, name:'Carved Vase, Tall', cat:'Home', price:58, icon:'🏺' },
    { id:7, name:'Soup Mug', cat:'Drinkware', price:30, icon:'🍵' },
    { id:8, name:'Butter Dish', cat:'Dinnerware', price:38, icon:'🧈' },
  ];
  let cart = [];

  function escapeHtml(str){ const d=document.createElement('div'); d.textContent=str; return d.innerHTML; }

  function renderProducts(){
    const grid = document.getElementById('shop-grid');
    grid.innerHTML = '';
    products.forEach((p,i)=>{
      const card = document.createElement('div');
      card.className = 'product-card reveal';
      card.style.transitionDelay = (i*60)+'ms';
      card.innerHTML = `
        <div class="product-image">${p.icon}</div>
        <div class="product-info">
          <p class="product-cat">${escapeHtml(p.cat)}</p>
          <h3 class="product-name">${escapeHtml(p.name)}</h3>
          <div class="product-footer">
            <span class="product-price">$${p.price.toFixed(2)}</span>
            <button class="add-btn" data-id="${p.id}">Add</button>
          </div>
        </div>
      `;
      grid.appendChild(card);
      revealObserver.observe(card);
    });
    grid.querySelectorAll('.add-btn').forEach(btn=>{
      btn.addEventListener('click', ()=>addToCart(parseInt(btn.dataset.id)));
    });
  }

  function addToCart(id){
    const product = products.find(p=>p.id===id);
    const existing = cart.find(i=>i.id===id);
    if (existing) existing.qty+=1; else cart.push({...product, qty:1});
    renderCart(); updateBadge();
  }
  function updateQty(id,delta){
    const item = cart.find(i=>i.id===id);
    if(!item) return;
    item.qty = Math.max(1, item.qty+delta);
    renderCart(); updateBadge();
  }
  function cartTotal(){ return cart.reduce((s,i)=>s+i.price*i.qty,0); }
  function cartCount(){ return cart.reduce((s,i)=>s+i.qty,0); }

  function renderCart(){
    const container = document.getElementById('cart-items');
    const footer = document.getElementById('cart-footer');
    const empty = document.getElementById('cart-empty');
    container.querySelectorAll('.cart-row').forEach(el=>el.remove());
    if (cart.length===0){ empty.style.display='flex'; footer.style.display='none'; return; }
    empty.style.display='none'; footer.style.display='block';
    cart.forEach(item=>{
      const row = document.createElement('div');
      row.className = 'cart-row';
      row.innerHTML = `
        <div style="flex:1;">
          <p style="font-weight:600;font-size:0.92rem;">${escapeHtml(item.name)}</p>
          <div style="display:flex;align-items:center;gap:0.6rem;margin-top:0.5rem;">
            <button class="qty-btn" data-id="${item.id}" data-delta="-1">−</button>
            <span style="font-size:0.9rem;width:1rem;text-align:center;">${item.qty}</span>
            <button class="qty-btn" data-id="${item.id}" data-delta="1">+</button>
          </div>
        </div>
        <p style="font-weight:700;font-size:0.92rem;">$${(item.price*item.qty).toFixed(2)}</p>
      `;
      container.appendChild(row);
    });
    document.getElementById('cart-total').textContent = `$${cartTotal().toFixed(2)}`;
    container.querySelectorAll('.qty-btn').forEach(btn=>{
      btn.addEventListener('click', ()=>updateQty(parseInt(btn.dataset.id), parseInt(btn.dataset.delta)));
    });
  }
  function updateBadge(){
    const badge = document.getElementById('cart-badge');
    const count = cartCount();
    badge.textContent = count;
    badge.classList.toggle('hidden', count===0);
  }

  const cartDrawer = document.getElementById('cart-drawer');
  const cartBackdrop = document.getElementById('cart-backdrop');
  document.getElementById('cart-btn').addEventListener('click', ()=>{
    cartDrawer.classList.add('open'); cartBackdrop.classList.add('active'); document.body.style.overflow='hidden';
  });
  function closeCart(){ cartDrawer.classList.remove('open'); cartBackdrop.classList.remove('active'); document.body.style.overflow=''; }
  document.getElementById('cart-close').addEventListener('click', closeCart);
  cartBackdrop.addEventListener('click', closeCart);
  document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeCart(); });

  const header = document.getElementById('header');
  const menuToggle = document.getElementById('menu-toggle');
  const navList = document.getElementById('nav-list');
  const overlay = document.getElementById('overlay');
  function toggleMenu(){
    menuToggle.classList.toggle('active'); navList.classList.toggle('open'); overlay.classList.toggle('active');
    document.body.style.overflow = navList.classList.contains('open') ? 'hidden' : '';
  }
  menuToggle.addEventListener('click', toggleMenu);
  overlay.addEventListener('click', toggleMenu);
  navList.querySelectorAll('a').forEach(link=>link.addEventListener('click', ()=>{ if(navList.classList.contains('open')) toggleMenu(); }));
  window.addEventListener('scroll', ()=>{ header.classList.toggle('scrolled', window.scrollY>40); }, {passive:true});

  const revealObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
  }, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

  const processFill = document.getElementById('process-fill');
  const processObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ processFill.style.width='100%'; processObserver.disconnect(); } });
  }, {threshold:0.3});
  processObserver.observe(document.getElementById('process-strip'));

  document.getElementById('newsletter-form').addEventListener('submit', (e)=>{
    e.preventDefault();
    document.getElementById('newsletter-note').textContent = "You're in! Watch your inbox for the next firing.";
    e.target.reset();
  });

  renderProducts();
});
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/05_fintech_budgeting_app.md

# Example — Fintech Budgeting App Landing Page (Tailwind Architecture)

Tags: example, full-site, fintech, saas, budgeting-app, tailwind, dark-theme, emerald, mono, animated-counters, dashboard-mockup

Niche: consumer budgeting/personal-finance SaaS app landing page (not e-commerce —
no cart; conversion goal is sign-up).
Architecture: Tailwind CDN utility classes.
Palette: near-black canvas (#0A0E0C), emerald accent (#34D399), monospace for all
dollar figures/stats to signal precision.
Signature element: an animated dashboard mockup panel with counting-up stat numbers
that animate when scrolled into view, using requestAnimationFrame easing rather than
a plugin.
Sections: header, hero with dashboard mockup, animated stats strip, feature grid,
how-it-works steps, pricing, FAQ accordion, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ledgerly | Budgeting That Actually Sticks</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  theme:{extend:{
    colors:{ canvas:{DEFAULT:'#0A0E0C',light:'#10150F',card:'#161C16'}, accent:{DEFAULT:'#34D399',hover:'#4FE3AC',glow:'rgba(52,211,153,0.25)'} },
    fontFamily:{ sans:['Inter','system-ui','sans-serif'], mono:['JetBrains Mono','monospace'] }
  }}
}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
  .font-mono{font-family:'JetBrains Mono',monospace;}
  ::selection{background:rgba(52,211,153,0.3);}
  .hero-title{font-size:clamp(2.6rem,6vw,5rem);line-height:1.03;letter-spacing:-0.025em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .mockup-bar{transition:width 1.2s cubic-bezier(.16,1,.3,1);}
  .accordion-content{max-height:0;overflow:hidden;transition:max-height .35s cubic-bezier(.16,1,.3,1);}
  .accordion-item.open .accordion-content{max-height:200px;}
  .accordion-item.open .accordion-chevron{transform:rotate(180deg);}
  .accordion-chevron{transition:transform .3s ease;}
  input:focus,button:focus-visible{outline:2px solid #34D399;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <a href="#" class="font-bold text-xl tracking-tight">Ledgerly</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#features" class="text-sm text-white/60 hover:text-white">Features</a>
        <a href="#how" class="text-sm text-white/60 hover:text-white">How It Works</a>
        <a href="#pricing" class="text-sm text-white/60 hover:text-white">Pricing</a>
      </nav>
      <a href="#pricing" class="bg-accent hover:bg-accent-hover text-canvas font-semibold text-sm px-5 py-2.5 rounded-lg transition-colors">Get Started Free</a>
    </div>
  </div>
</header>

<section class="relative min-h-[94vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 25% 25%, rgba(52,211,153,0.07) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10 grid lg:grid-cols-2 gap-16 items-center">
    <div class="space-y-7">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/5">
        <span class="w-1.5 h-1.5 rounded-full bg-accent"></span>
        <span class="text-xs font-medium text-accent tracking-wider uppercase">Now with automatic bill detection</span>
      </div>
      <h1 class="hero-title font-extrabold text-white">
        See where your<br>money <span class="text-accent">actually</span> goes.
      </h1>
      <p class="text-lg text-white/50 max-w-md leading-relaxed">
        Ledgerly connects to your accounts and sorts every transaction automatically —
        no spreadsheets, no manual categorizing, no guilt-tripping.
      </p>
      <div class="flex flex-col sm:flex-row gap-4">
        <a href="#pricing" class="bg-accent hover:bg-accent-hover text-canvas font-semibold px-8 py-4 rounded-xl transition-all hover:-translate-y-0.5">Start Free — No Card Required</a>
        <a href="#how" class="border border-white/15 hover:border-white/30 font-medium px-8 py-4 rounded-xl transition-all hover:bg-white/5">See How It Works</a>
      </div>
    </div>
    <div class="relative">
      <div class="bg-canvas-card border border-white/10 rounded-2xl p-6 shadow-2xl">
        <div class="flex items-center justify-between mb-6">
          <p class="text-sm text-white/40">This Month</p>
          <p class="text-xs text-accent font-mono">+ on track</p>
        </div>
        <p class="font-mono text-3xl font-bold mb-1" id="stat-spent">$0</p>
        <p class="text-xs text-white/40 mb-6">spent of $3,200 budget</p>
        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-xs mb-1.5"><span class="text-white/60">Groceries</span><span class="font-mono text-white/40">$412 / $500</span></div>
            <div class="h-2 bg-white/5 rounded-full overflow-hidden"><div class="mockup-bar h-full bg-accent rounded-full" style="width:0%" data-target="82"></div></div>
          </div>
          <div>
            <div class="flex justify-between text-xs mb-1.5"><span class="text-white/60">Dining Out</span><span class="font-mono text-white/40">$268 / $300</span></div>
            <div class="h-2 bg-white/5 rounded-full overflow-hidden"><div class="mockup-bar h-full bg-yellow-400 rounded-full" style="width:0%" data-target="89"></div></div>
          </div>
          <div>
            <div class="flex justify-between text-xs mb-1.5"><span class="text-white/60">Subscriptions</span><span class="font-mono text-white/40">$84 / $120</span></div>
            <div class="h-2 bg-white/5 rounded-full overflow-hidden"><div class="mockup-bar h-full bg-accent rounded-full" style="width:0%" data-target="70"></div></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="py-16 border-t border-white/5 bg-canvas-light">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 grid grid-cols-2 sm:grid-cols-4 gap-8 text-center" id="stats-strip">
    <div class="reveal"><p class="font-mono text-3xl font-bold text-accent" data-counter="148000" id="counter-1">0</p><p class="text-xs text-white/40 uppercase tracking-wider mt-2">Accounts Connected</p></div>
    <div class="reveal"><p class="font-mono text-3xl font-bold text-accent" data-counter="2400000" id="counter-2">0</p><p class="text-xs text-white/40 uppercase tracking-wider mt-2">Tracked Monthly ($)</p></div>
    <div class="reveal"><p class="font-mono text-3xl font-bold text-accent" data-counter="94" id="counter-3">0</p><p class="text-xs text-white/40 uppercase tracking-wider mt-2">% Stay On Budget</p></div>
    <div class="reveal"><p class="font-mono text-3xl font-bold text-accent" data-counter="4" id="counter-4">0</p><p class="text-xs text-white/40 uppercase tracking-wider mt-2">Minute Setup</p></div>
  </div>
</section>

<section id="features" class="py-24 lg:py-32">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Why Ledgerly</p>
      <h2 class="text-3xl lg:text-4xl font-bold">Built for people who hate budgeting apps</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8">
        <div class="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-5"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="1.5"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-7"/></svg></div>
        <h3 class="font-semibold mb-2">Auto-categorized</h3>
        <p class="text-sm text-white/45">Every transaction is sorted the moment it posts — no manual tagging, ever.</p>
      </div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8" style="transition-delay:.1s">
        <div class="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-5"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg></div>
        <h3 class="font-semibold mb-2">Real-time alerts</h3>
        <p class="text-sm text-white/45">A nudge the moment you're close to a budget line, not a surprise at month-end.</p>
      </div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8" style="transition-delay:.2s">
        <div class="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-5"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="1.5"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>
        <h3 class="font-semibold mb-2">Bank-level security</h3>
        <p class="text-sm text-white/45">256-bit encryption and read-only account access — we can't move your money.</p>
      </div>
    </div>
  </div>
</section>

<section id="how" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Getting Started</p>
      <h2 class="text-3xl lg:text-4xl font-bold">Three steps, four minutes</h2>
    </div>
    <div class="space-y-6">
      <div class="reveal flex gap-6 items-start bg-canvas-card border border-white/5 rounded-2xl p-6">
        <span class="font-mono text-accent text-xl font-bold">01</span>
        <div><h3 class="font-semibold mb-1">Connect your accounts</h3><p class="text-sm text-white/45">Securely link checking, savings, and credit cards via your bank's login.</p></div>
      </div>
      <div class="reveal flex gap-6 items-start bg-canvas-card border border-white/5 rounded-2xl p-6">
        <span class="font-mono text-accent text-xl font-bold">02</span>
        <div><h3 class="font-semibold mb-1">Set your budget lines</h3><p class="text-sm text-white/45">We suggest starting amounts based on your last 90 days of spending.</p></div>
      </div>
      <div class="reveal flex gap-6 items-start bg-canvas-card border border-white/5 rounded-2xl p-6">
        <span class="font-mono text-accent text-xl font-bold">03</span>
        <div><h3 class="font-semibold mb-1">Get out of the way</h3><p class="text-sm text-white/45">Ledgerly tracks everything automatically — check in weekly, not daily.</p></div>
      </div>
    </div>
  </div>
</section>

<section id="pricing" class="py-24 lg:py-32">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Pricing</p>
      <h2 class="text-3xl lg:text-4xl font-bold">Simple, honest pricing</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-2xl mx-auto">
      <div class="reveal bg-canvas-card border border-white/10 rounded-2xl p-8">
        <p class="text-sm text-white/40 uppercase tracking-wide mb-2">Free</p>
        <p class="font-mono text-4xl font-bold mb-4">$0</p>
        <ul class="space-y-2 text-sm text-white/55 mb-6">
          <li>1 connected account</li>
          <li>Auto-categorization</li>
          <li>Weekly email summary</li>
        </ul>
        <a href="#" class="block text-center border border-white/15 hover:border-accent hover:text-accent font-semibold py-3 rounded-xl transition-all">Start Free</a>
      </div>
      <div class="reveal bg-canvas-card border border-accent rounded-2xl p-8 relative">
        <span class="absolute -top-3 left-8 bg-accent text-canvas text-xs font-bold px-3 py-1 rounded-full">Most Popular</span>
        <p class="text-sm text-white/40 uppercase tracking-wide mb-2">Plus</p>
        <p class="font-mono text-4xl font-bold mb-4">$8<span class="text-base text-white/40">/mo</span></p>
        <ul class="space-y-2 text-sm text-white/55 mb-6">
          <li>Unlimited accounts</li>
          <li>Real-time alerts</li>
          <li>Custom budget categories</li>
        </ul>
        <a href="#" class="block text-center bg-accent hover:bg-accent-hover text-canvas font-bold py-3 rounded-xl transition-all">Start 14-Day Trial</a>
      </div>
    </div>
  </div>
</section>

<section class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-3xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-12 reveal"><h2 class="text-3xl font-bold">Common questions</h2></div>
    <div class="space-y-3" id="faq-list">
      <div class="accordion-item reveal bg-canvas-card border border-white/5 rounded-xl">
        <button class="accordion-trigger w-full flex items-center justify-between p-5 text-left font-medium">
          <span>Is my bank data safe?</span>
          <svg class="accordion-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="accordion-content px-5"><p class="text-sm text-white/50 pb-5">Yes — we use read-only, 256-bit encrypted connections through a regulated banking partner. Ledgerly never has the ability to move money.</p></div>
      </div>
      <div class="accordion-item reveal bg-canvas-card border border-white/5 rounded-xl">
        <button class="accordion-trigger w-full flex items-center justify-between p-5 text-left font-medium">
          <span>Can I cancel anytime?</span>
          <svg class="accordion-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="accordion-content px-5"><p class="text-sm text-white/50 pb-5">Yes, with one click from your account settings — no calls, no retention flow.</p></div>
      </div>
      <div class="accordion-item reveal bg-canvas-card border border-white/5 rounded-xl">
        <button class="accordion-trigger w-full flex items-center justify-between p-5 text-left font-medium">
          <span>Which banks are supported?</span>
          <svg class="accordion-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="accordion-content px-5"><p class="text-sm text-white/50 pb-5">Over 11,000 banks and credit unions in the US and Canada, including every major institution.</p></div>
      </div>
    </div>
  </div>
</section>

<footer class="border-t border-white/5 py-12">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p>© 2026 Ledgerly, Inc.</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Privacy</a><a href="#" class="hover:text-white/60">Security</a></div>
  </div>
</footer>

<script>
const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

function animateBars(){
  document.querySelectorAll('.mockup-bar').forEach(bar=>{
    bar.style.width = bar.dataset.target + '%';
  });
  let spent = 0;
  const target = 764;
  const spentEl = document.getElementById('stat-spent');
  const tick = () => {
    spent = Math.min(target, spent + Math.ceil(target/40));
    spentEl.textContent = '$' + spent.toLocaleString();
    if (spent < target) requestAnimationFrame(tick);
  };
  tick();
}
const mockupObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ animateBars(); mockupObserver.disconnect(); } });
}, {threshold:0.4});
mockupObserver.observe(document.getElementById('stat-spent'));

function animateCounter(el, target){
  let current = 0;
  const duration = 1400;
  const start = performance.now();
  function format(n){
    if (n >= 1000000) return '$' + (n/1000000).toFixed(1) + 'M';
    if (n >= 1000 && target >= 1000) return n.toLocaleString();
    return n.toString();
  }
  function step(now){
    const progress = Math.min(1, (now-start)/duration);
    const eased = 1 - Math.pow(1-progress, 3);
    current = Math.floor(eased * target);
    el.textContent = el.id === 'counter-3' ? current + '%' : (el.id==='counter-4' ? current : format(current));
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}
const statsObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      document.querySelectorAll('[data-counter]').forEach(el=>animateCounter(el, parseInt(el.dataset.counter)));
      statsObserver.disconnect();
    }
  });
}, {threshold:0.3});
statsObserver.observe(document.getElementById('stats-strip'));

document.querySelectorAll('.accordion-trigger').forEach(trigger=>{
  trigger.addEventListener('click', ()=>{
    const item = trigger.closest('.accordion-item');
    const wasOpen = item.classList.contains('open');
    document.querySelectorAll('.accordion-item').forEach(i=>i.classList.remove('open'));
    if (!wasOpen) item.classList.add('open');
  });
});

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(10,14,12,0.85)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/06_plant_shop.md

# Example — Botanical Plant Shop (Vanilla CSS Architecture, Light Mode)

Tags: example, full-site, plants, botanical, garden-shop, vanilla-css, light-theme, sage-green, cream, care-icons, ecommerce

Niche: houseplant shop selling plants online with care-difficulty ratings.
Architecture: vanilla CSS, custom properties, light mode.
Palette: cream canvas (#FAF7F0), deep sage accent (#5B7B5C), terracotta secondary (#C97B4A).
Signature element: a care-level icon system (light/water/difficulty) shown as three
small glyph+label rows on every product card, plus a "find your plant" quiz-style
filter by light condition.
Sections: header, hero, light-condition filter quiz, plant grid with cart, care
philosophy, FAQ, footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fern &amp; Folia | Houseplants for Every Light</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500;600;700&family=Nunito+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --cream:#FAF7F0; --cream-card:#FFFFFF; --line:#E5DFD0;
  --ink:#2E3328; --ink-dim:#6B7263; --sage:#5B7B5C; --sage-hover:#6E916F; --terracotta:#C97B4A;
  --radius:14px; --radius-lg:22px;
  --transition: all 0.3s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow: 0 10px 26px rgba(46,51,40,0.08); --shadow-lg: 0 20px 46px rgba(46,51,40,0.13);
  --serif:'Fraunces', serif; --sans:'Nunito Sans', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--cream);color:var(--ink);line-height:1.65;overflow-x:hidden;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;} button{cursor:pointer;font-family:inherit;}
.container{max-width:1160px;margin:0 auto;padding:0 2rem;}
.section{padding:5.5rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:2.5px;font-size:0.76rem;color:var(--sage);margin-bottom:0.9rem;font-weight:700;}
.section-title{font-family:var(--serif);font-size:2.5rem;font-weight:600;margin-bottom:1rem;}
.section-subtitle{color:var(--ink-dim);font-size:1rem;max-width:540px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.85rem 2rem;border:none;border-radius:var(--radius);font-size:0.88rem;font-weight:700;transition:var(--transition);}
.btn-primary{background:var(--sage);color:#fff;}
.btn-primary:hover{background:var(--sage-hover);transform:translateY(-2px);box-shadow:0 12px 24px rgba(91,123,92,0.28);}
.btn-outline{background:transparent;color:var(--ink);border:1.5px solid var(--line);}
.btn-outline:hover{border-color:var(--sage);color:var(--sage);}
.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.3rem 0;transition:var(--transition);}
.header.scrolled{background:rgba(250,247,240,0.92);backdrop-filter:blur(14px);padding:0.95rem 0;box-shadow:0 2px 20px rgba(46,51,40,0.06);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--serif);font-size:1.4rem;font-weight:700;}
.logo span{color:var(--sage);}
.nav-list{display:flex;list-style:none;gap:2.2rem;align-items:center;}
.nav-list a{font-size:0.84rem;font-weight:600;position:relative;padding:0.2rem 0;}
.nav-list a::after{content:"";position:absolute;bottom:-2px;left:0;width:0;height:2px;background:var(--sage);transition:var(--transition);}
.nav-list a:hover::after,.nav-list a.active::after{width:100%;}
.header-actions{display:flex;align-items:center;gap:0.5rem;}
.cart-btn{position:relative;background:none;border:none;font-size:1.2rem;padding:0.4rem;}
.cart-badge{position:absolute;top:-2px;right:-4px;background:var(--terracotta);color:#fff;font-size:0.62rem;font-weight:700;width:17px;height:17px;border-radius:50%;display:flex;align-items:center;justify-content:center;}
.cart-badge.hidden{display:none;}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:22px;height:2px;background:var(--ink);transition:var(--transition);}
.overlay{position:fixed;inset:0;background:rgba(46,51,40,0.45);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:86vh;display:flex;align-items:center;padding-top:6rem;}
.hero-grid{display:grid;grid-template-columns:1.05fr 0.95fr;gap:3.5rem;align-items:center;}
.hero-label{display:inline-block;padding:0.4rem 1rem;background:rgba(91,123,92,0.1);border-radius:30px;font-size:0.76rem;letter-spacing:1.5px;text-transform:uppercase;color:var(--sage);margin-bottom:1.8rem;font-weight:700;}
.hero-title{font-family:var(--serif);font-size:3.4rem;font-weight:600;line-height:1.12;margin-bottom:1.3rem;}
.hero-title em{font-style:italic;color:var(--sage);}
.hero-desc{font-size:1.05rem;color:var(--ink-dim);max-width:440px;margin-bottom:2rem;}
.hero-visual{aspect-ratio:1;border-radius:var(--radius-lg);background:linear-gradient(150deg,#E8EFE3,#D3E0CC);display:flex;align-items:center;justify-content:center;font-size:5rem;box-shadow:var(--shadow-lg);}

.quiz-box{background:var(--cream-card);border-radius:var(--radius-lg);padding:2.5rem;box-shadow:var(--shadow);margin-top:3rem;text-align:center;}
.quiz-box h3{font-family:var(--serif);font-size:1.5rem;margin-bottom:0.5rem;}
.quiz-box p{color:var(--ink-dim);margin-bottom:1.8rem;}
.light-options{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;}
.light-chip{background:var(--cream);border:1.5px solid var(--line);border-radius:var(--radius);padding:1.1rem 1.6rem;font-weight:700;font-size:0.9rem;transition:var(--transition);display:flex;flex-direction:column;align-items:center;gap:0.5rem;min-width:120px;}
.light-chip span.icon{font-size:1.6rem;}
.light-chip:hover{border-color:var(--sage);}
.light-chip.active{background:var(--sage);border-color:var(--sage);color:#fff;}

.plant-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1.4rem;margin-top:2.5rem;}
.plant-card{background:var(--cream-card);border-radius:var(--radius-lg);overflow:hidden;border:1px solid var(--line);transition:var(--transition);}
.plant-card:hover{transform:translateY(-5px);box-shadow:var(--shadow-lg);}
.plant-card.hidden-by-filter{display:none;}
.plant-image{aspect-ratio:1;background:linear-gradient(150deg,#E8EFE3,#D3E0CC);display:flex;align-items:center;justify-content:center;font-size:3rem;}
.plant-info{padding:1.3rem;}
.plant-name{font-family:var(--serif);font-size:1.1rem;margin-bottom:0.6rem;}
.care-icons{display:flex;gap:0.8rem;margin-bottom:0.9rem;}
.care-icon{display:flex;align-items:center;gap:0.3rem;font-size:0.72rem;color:var(--ink-dim);}
.plant-footer{display:flex;align-items:center;justify-content:space-between;}
.plant-price{font-weight:700;}
.add-btn{background:var(--cream);border:1px solid var(--line);color:var(--ink);font-size:0.76rem;font-weight:700;padding:0.45rem 0.85rem;border-radius:8px;transition:var(--transition);}
.add-btn:hover{background:var(--sage);color:#fff;border-color:var(--sage);}

.philosophy-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-top:2.5rem;}
.philosophy-card{text-align:center;padding:1.5rem;}
.philosophy-icon{font-size:2.2rem;margin-bottom:1rem;}
.philosophy-card h4{font-family:var(--serif);font-size:1.15rem;margin-bottom:0.5rem;}
.philosophy-card p{color:var(--ink-dim);font-size:0.9rem;}

.faq-item{border-bottom:1px solid var(--line);padding:1.3rem 0;}
.faq-question{display:flex;justify-content:space-between;align-items:center;cursor:pointer;font-weight:700;}
.faq-chevron{transition:transform 0.3s ease;}
.faq-item.open .faq-chevron{transform:rotate(180deg);}
.faq-answer{max-height:0;overflow:hidden;transition:max-height 0.3s cubic-bezier(0.16,1,0.3,1);}
.faq-item.open .faq-answer{max-height:160px;}
.faq-answer p{padding-top:0.8rem;color:var(--ink-dim);font-size:0.92rem;}

.footer{background:var(--ink);color:var(--cream);padding:3.2rem 0 0;}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:3rem;padding-bottom:2.2rem;}
.footer-col h4{font-size:0.78rem;text-transform:uppercase;letter-spacing:1.3px;margin-bottom:1rem;opacity:0.6;}
.footer-col a,.footer-col p{display:block;color:var(--cream);opacity:0.78;font-size:0.86rem;margin-bottom:0.7rem;}
.footer-col a:hover{opacity:1;color:#A8C2A0;}
.footer-bottom{border-top:1px solid rgba(250,247,240,0.12);padding:1.2rem 0;display:flex;justify-content:space-between;font-size:0.78rem;opacity:0.6;}

.cart-drawer{position:fixed;top:0;right:0;height:100%;width:400px;background:var(--cream-card);z-index:1100;transform:translateX(100%);transition:transform 0.35s cubic-bezier(0.16,1,0.3,1);display:flex;flex-direction:column;box-shadow:-10px 0 40px rgba(0,0,0,0.12);}
.cart-drawer.open{transform:translateX(0);}
.cart-header{display:flex;justify-content:space-between;align-items:center;padding:1.5rem;border-bottom:1px solid var(--line);}
.cart-close{background:var(--cream);border:none;width:30px;height:30px;border-radius:50%;font-size:1.1rem;}
.cart-items{flex:1;overflow-y:auto;padding:1.5rem;}
.cart-empty{display:flex;align-items:center;justify-content:center;height:100%;color:var(--ink-dim);text-align:center;}
.cart-row{display:flex;gap:1rem;padding-bottom:1.1rem;margin-bottom:1.1rem;border-bottom:1px solid var(--line);}
.qty-btn{width:22px;height:22px;border-radius:6px;border:1px solid var(--line);background:var(--cream);}
.cart-footer{padding:1.5rem;border-top:1px solid var(--line);}
.cart-total-row{display:flex;justify-content:space-between;margin-bottom:0.9rem;font-weight:700;}
.cart-backdrop{position:fixed;inset:0;background:rgba(46,51,40,0.45);z-index:1050;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.cart-backdrop.active{opacity:1;pointer-events:auto;}

.reveal{opacity:0;transform:translateY(26px);transition:all 0.65s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .hero-grid{grid-template-columns:1fr;}
  .plant-grid{grid-template-columns:repeat(2,1fr);}
  .philosophy-grid{grid-template-columns:1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--cream);flex-direction:column;justify-content:center;gap:2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.4rem;}
  .footer-grid{grid-template-columns:1fr;}
  .cart-drawer{width:100%;}
}
@media (max-width:600px){ .plant-grid{grid-template-columns:1fr;} .footer-bottom{flex-direction:column;gap:0.6rem;text-align:center;} }
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Fern <span>&amp;</span> Folia</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero" class="active">Home</a></li>
      <li><a href="#shop">Shop</a></li>
      <li><a href="#care">Our Philosophy</a></li>
      <li><a href="#faq">FAQ</a></li>
    </ul></nav>
    <div class="header-actions">
      <button class="cart-btn" id="cart-btn" aria-label="Open cart">🪴<span class="cart-badge hidden" id="cart-badge">0</span></button>
      <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <span class="hero-label">Plants That Match Your Light</span>
        <h1 class="hero-title">Stop killing<br><em>the same plant twice.</em></h1>
        <p class="hero-desc">Every plant we sell is tagged by real light and water needs — find one that matches your space, not just your aesthetic.</p>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;">
          <a href="#shop" class="btn btn-primary">Shop Plants</a>
          <a href="#quiz" class="btn btn-outline">Find My Match</a>
        </div>
      </div>
      <div class="hero-visual">🌿</div>
    </div>
  </div>
</section>

<section class="section" id="quiz" style="background:var(--cream-card);">
  <div class="container">
    <div class="quiz-box reveal">
      <h3>What kind of light does your space get?</h3>
      <p>Tap one and we'll filter the shop below.</p>
      <div class="light-options" id="light-options">
        <button class="light-chip active" data-light="all"><span class="icon">🏠</span>All Plants</button>
        <button class="light-chip" data-light="bright"><span class="icon">☀️</span>Bright Light</button>
        <button class="light-chip" data-light="medium"><span class="icon">⛅</span>Medium Light</button>
        <button class="light-chip" data-light="low"><span class="icon">🌥️</span>Low Light</button>
      </div>
    </div>
  </div>
</section>

<section class="section" id="shop">
  <div class="container">
    <div class="reveal">
      <span class="section-label">The Shop</span>
      <h2 class="section-title">Find your plant</h2>
    </div>
    <div class="plant-grid" id="plant-grid"></div>
  </div>
</section>

<section class="section" id="care" style="background:var(--cream-card);">
  <div class="container">
    <div class="reveal" style="text-align:center;">
      <span class="section-label">Our Philosophy</span>
      <h2 class="section-title">We'd rather sell you fewer plants</h2>
      <p class="section-subtitle" style="margin:0 auto;">than watch you replace the same one three times.</p>
    </div>
    <div class="philosophy-grid">
      <div class="philosophy-card reveal"><div class="philosophy-icon">🔍</div><h4>Honest Difficulty Ratings</h4><p>We rate every plant on a simple scale — no marketing spin on "easy care."</p></div>
      <div class="philosophy-card reveal"><div class="philosophy-icon">💬</div><h4>Real Care Support</h4><p>Email a photo of a struggling plant and a real grower will write back within a day.</p></div>
      <div class="philosophy-card reveal"><div class="philosophy-icon">🌱</div><h4>30-Day Guarantee</h4><p>If a plant doesn't make it in its first month, we'll replace it once, free.</p></div>
    </div>
  </div>
</section>

<section class="section" id="faq">
  <div class="container" style="max-width:760px;">
    <div class="reveal" style="text-align:center;margin-bottom:2rem;">
      <h2 class="section-title">Questions, answered</h2>
    </div>
    <div class="faq-item reveal">
      <div class="faq-question">How are plants shipped?<span class="faq-chevron">▾</span></div>
      <div class="faq-answer"><p>Plants ship in breathable, padded boxes within 1-2 business days, with extra insulation in winter.</p></div>
    </div>
    <div class="faq-item reveal">
      <div class="faq-question">What if my plant arrives damaged?<span class="faq-chevron">▾</span></div>
      <div class="faq-answer"><p>Send a photo within 48 hours and we'll send a free replacement — no questions asked.</p></div>
    </div>
    <div class="faq-item reveal">
      <div class="faq-question">Do you ship pots and soil too?<span class="faq-chevron">▾</span></div>
      <div class="faq-answer"><p>Every plant ships in a nursery pot; decorative pots and potting mix are sold separately.</p></div>
    </div>
  </div>
</section>

<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-col"><h4>Fern &amp; Folia</h4><p>Houseplants matched honestly to the light you actually have.</p></div>
    <div class="footer-col"><h4>Shop</h4><a href="#shop">All Plants</a><a href="#">Plant Care Kits</a><a href="#">Gift Cards</a></div>
    <div class="footer-col"><h4>Help</h4><a href="#faq">FAQ</a><a href="#">Shipping</a><a href="#">Contact</a></div>
  </div>
  <div class="container footer-bottom"><p>© 2026 Fern &amp; Folia.</p><p>Grown with care, shipped with more.</p></div>
</footer>

<div class="cart-drawer" id="cart-drawer">
  <div class="cart-header"><h3 style="font-family:var(--serif);font-size:1.25rem;">Your Cart</h3><button class="cart-close" id="cart-close" aria-label="Close cart">&times;</button></div>
  <div class="cart-items" id="cart-items"><div class="cart-empty" id="cart-empty"><p>Your cart is empty.</p></div></div>
  <div class="cart-footer" id="cart-footer" style="display:none;">
    <div class="cart-total-row"><span>Total</span><span id="cart-total">$0.00</span></div>
    <button class="btn btn-primary" style="width:100%;justify-content:center;">Checkout</button>
  </div>
</div>
<div class="cart-backdrop" id="cart-backdrop"></div>

<script>
document.addEventListener('DOMContentLoaded', function(){
  const plants = [
    { id:1, name:'Snake Plant', light:'low', water:'Low', difficulty:'Easy', price:32, icon:'🪴' },
    { id:2, name:'Fiddle Leaf Fig', light:'bright', water:'Medium', difficulty:'Hard', price:58, icon:'🌳' },
    { id:3, name:'Pothos Marble Queen', light:'medium', water:'Low', difficulty:'Easy', price:24, icon:'🍃' },
    { id:4, name:'Monstera Deliciosa', light:'bright', water:'Medium', difficulty:'Medium', price:46, icon:'🌿' },
    { id:5, name:'ZZ Plant', light:'low', water:'Low', difficulty:'Easy', price:28, icon:'🌱' },
    { id:6, name:'Calathea Orbifolia', light:'medium', water:'High', difficulty:'Hard', price:34, icon:'🍀' },
    { id:7, name:'String of Pearls', light:'bright', water:'Low', difficulty:'Medium', price:22, icon:'🌵' },
    { id:8, name:'Peace Lily', light:'medium', water:'Medium', difficulty:'Easy', price:26, icon:'🌼' },
  ];
  let cart = [];
  let activeLight = 'all';

  function escapeHtml(str){ const d=document.createElement('div'); d.textContent=str; return d.innerHTML; }

  function renderPlants(){
    const grid = document.getElementById('plant-grid');
    grid.innerHTML = '';
    plants.forEach((p,i)=>{
      const card = document.createElement('div');
      card.className = 'plant-card reveal';
      card.dataset.light = p.light;
      card.style.transitionDelay = (i*50)+'ms';
      card.innerHTML = `
        <div class="plant-image">${p.icon}</div>
        <div class="plant-info">
          <h3 class="plant-name">${escapeHtml(p.name)}</h3>
          <div class="care-icons">
            <span class="care-icon">💧 ${p.water}</span>
            <span class="care-icon">📈 ${p.difficulty}</span>
          </div>
          <div class="plant-footer">
            <span class="plant-price">$${p.price.toFixed(2)}</span>
            <button class="add-btn" data-id="${p.id}">Add</button>
          </div>
        </div>
      `;
      grid.appendChild(card);
      revealObserver.observe(card);
    });
    grid.querySelectorAll('.add-btn').forEach(btn=>btn.addEventListener('click', ()=>addToCart(parseInt(btn.dataset.id))));
    applyFilter();
  }

  function applyFilter(){
    document.querySelectorAll('.plant-card').forEach(card=>{
      const matches = activeLight === 'all' || card.dataset.light === activeLight;
      card.classList.toggle('hidden-by-filter', !matches);
    });
  }
  document.querySelectorAll('.light-chip').forEach(chip=>{
    chip.addEventListener('click', ()=>{
      document.querySelectorAll('.light-chip').forEach(c=>c.classList.remove('active'));
      chip.classList.add('active');
      activeLight = chip.dataset.light;
      applyFilter();
      document.getElementById('shop').scrollIntoView({behavior:'smooth', block:'start'});
    });
  });

  function addToCart(id){
    const plant = plants.find(p=>p.id===id);
    const existing = cart.find(i=>i.id===id);
    if (existing) existing.qty+=1; else cart.push({...plant, qty:1});
    renderCart(); updateBadge();
  }
  function updateQty(id,delta){ const item=cart.find(i=>i.id===id); if(!item) return; item.qty=Math.max(1,item.qty+delta); renderCart(); updateBadge(); }
  function cartTotal(){ return cart.reduce((s,i)=>s+i.price*i.qty,0); }
  function cartCount(){ return cart.reduce((s,i)=>s+i.qty,0); }

  function renderCart(){
    const container = document.getElementById('cart-items');
    const footer = document.getElementById('cart-footer');
    const empty = document.getElementById('cart-empty');
    container.querySelectorAll('.cart-row').forEach(el=>el.remove());
    if (cart.length===0){ empty.style.display='flex'; footer.style.display='none'; return; }
    empty.style.display='none'; footer.style.display='block';
    cart.forEach(item=>{
      const row = document.createElement('div');
      row.className='cart-row';
      row.innerHTML = `
        <div style="flex:1;"><p style="font-weight:700;font-size:0.9rem;">${escapeHtml(item.name)}</p>
        <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.45rem;">
          <button class="qty-btn" data-id="${item.id}" data-delta="-1">−</button>
          <span style="font-size:0.88rem;width:1rem;text-align:center;">${item.qty}</span>
          <button class="qty-btn" data-id="${item.id}" data-delta="1">+</button>
        </div></div>
        <p style="font-weight:700;font-size:0.9rem;">$${(item.price*item.qty).toFixed(2)}</p>
      `;
      container.appendChild(row);
    });
    document.getElementById('cart-total').textContent = `$${cartTotal().toFixed(2)}`;
    container.querySelectorAll('.qty-btn').forEach(btn=>btn.addEventListener('click', ()=>updateQty(parseInt(btn.dataset.id), parseInt(btn.dataset.delta))));
  }
  function updateBadge(){ const badge=document.getElementById('cart-badge'); const count=cartCount(); badge.textContent=count; badge.classList.toggle('hidden', count===0); }

  const cartDrawer = document.getElementById('cart-drawer');
  const cartBackdrop = document.getElementById('cart-backdrop');
  document.getElementById('cart-btn').addEventListener('click', ()=>{ cartDrawer.classList.add('open'); cartBackdrop.classList.add('active'); document.body.style.overflow='hidden'; });
  function closeCart(){ cartDrawer.classList.remove('open'); cartBackdrop.classList.remove('active'); document.body.style.overflow=''; }
  document.getElementById('cart-close').addEventListener('click', closeCart);
  cartBackdrop.addEventListener('click', closeCart);
  document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeCart(); });

  const header = document.getElementById('header');
  const menuToggle = document.getElementById('menu-toggle');
  const navList = document.getElementById('nav-list');
  const overlay = document.getElementById('overlay');
  function toggleMenu(){ menuToggle.classList.toggle('active'); navList.classList.toggle('open'); overlay.classList.toggle('active'); document.body.style.overflow = navList.classList.contains('open')?'hidden':''; }
  menuToggle.addEventListener('click', toggleMenu);
  overlay.addEventListener('click', toggleMenu);
  navList.querySelectorAll('a').forEach(link=>link.addEventListener('click', ()=>{ if(navList.classList.contains('open')) toggleMenu(); }));
  window.addEventListener('scroll', ()=>{ header.classList.toggle('scrolled', window.scrollY>40); }, {passive:true});

  document.querySelectorAll('.faq-question').forEach(q=>{
    q.addEventListener('click', ()=>q.closest('.faq-item').classList.toggle('open'));
  });

  const revealObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
  }, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

  renderPlants();
});
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/07_boxing_mma_gym.md

# Example — Boxing & MMA Gym (Tailwind Architecture)

Tags: example, full-site, boxing, mma, gym, fitness, combat-sports, tailwind, dark-theme, blood-orange, fighter-roster, aggressive

Niche: boxing and MMA training gym with a competitive fight team.
Architecture: Tailwind CDN utility classes.
Palette: matte black canvas (#0C0C0C), blood orange accent (#FF4422), heavy condensed
display type for aggression.
Signature element: a fighter roster grid showing each athlete's record (W-L-D) as a
bold stat block, with a hover state revealing their next fight date.
Sections: header, hero, class types, fighter roster, membership tiers, schedule,
testimonial, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ironclad Combat Club | Boxing &amp; MMA Training</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#0C0C0C',light:'#161616',card:'#1C1C1C'}, accent:{DEFAULT:'#FF4422',hover:'#FF6644',glow:'rgba(255,68,34,0.3)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], display:['Oswald','sans-serif'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Oswald:wght@500;600;700;800&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
  .font-display{font-family:'Oswald',sans-serif;text-transform:uppercase;}
  ::selection{background:rgba(255,68,34,0.35);}
  .hero-title{font-size:clamp(3rem,8vw,7rem);line-height:0.92;letter-spacing:-0.01em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .fighter-card{transition:transform .35s cubic-bezier(.25,.46,.45,.94);}
  .fighter-card:hover{transform:translateY(-6px);}
  .fighter-overlay{opacity:0;transition:opacity .3s ease;}
  .fighter-card:hover .fighter-overlay{opacity:1;}
  input:focus,button:focus-visible{outline:2px solid #FF4422;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <button id="mobile-menu-btn" class="lg:hidden p-2 -ml-2" aria-label="Open menu">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <a href="#" class="font-display text-xl font-bold tracking-wide">IRONCLAD</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#classes" class="font-display text-sm text-white/60 hover:text-white tracking-wide">Classes</a>
        <a href="#fighters" class="font-display text-sm text-white/60 hover:text-white tracking-wide">Fight Team</a>
        <a href="#membership" class="font-display text-sm text-white/60 hover:text-white tracking-wide">Membership</a>
      </nav>
      <a href="#membership" class="bg-accent hover:bg-accent-hover font-display font-bold text-sm px-5 py-2.5 transition-colors">Free Trial Class</a>
    </div>
  </div>
  <div id="mobile-nav" class="hidden lg:hidden bg-canvas-light border-b border-white/5">
    <div class="px-6 py-6 flex flex-col gap-4 font-display">
      <a href="#classes">Classes</a><a href="#fighters">Fight Team</a><a href="#membership">Membership</a>
    </div>
  </div>
</header>

<section class="relative min-h-[94vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 75% 30%, rgba(255,68,34,0.1) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
    <p class="text-accent font-display font-bold tracking-widest mb-6">EST. 2014 · BOXING · MUAY THAI · MMA</p>
    <h1 class="hero-title font-display font-bold text-white mb-8">
      TRAIN LIKE<br>YOU FIGHT.
    </h1>
    <p class="text-lg text-white/50 max-w-md mb-10 leading-relaxed">
      No mirrors, no fluff — just coaches who've competed, a fight team that trains
      next to you, and a heavy bag room that never closes early.
    </p>
    <div class="flex flex-col sm:flex-row gap-4">
      <a href="#membership" class="bg-accent hover:bg-accent-hover font-display font-bold px-8 py-4 transition-all hover:-translate-y-0.5">Claim Free Trial Class</a>
      <a href="#classes" class="border border-white/15 hover:border-white/30 font-display font-semibold px-8 py-4 transition-all hover:bg-white/5">View Class Schedule</a>
    </div>
  </div>
</section>

<section id="classes" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent font-display font-bold tracking-widest mb-3">DISCIPLINES</p>
      <h2 class="font-display text-3xl lg:text-5xl font-bold">Three ways to get hit</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="reveal bg-canvas-card border border-white/5 p-8"><div class="text-4xl mb-4">🥊</div><h3 class="font-display text-xl font-bold mb-2">Boxing</h3><p class="text-sm text-white/45">Footwork, combinations, and pad work — fundamentals first, sparring earned.</p></div>
      <div class="reveal bg-canvas-card border border-white/5 p-8" style="transition-delay:.1s"><div class="text-4xl mb-4">🦵</div><h3 class="font-display text-xl font-bold mb-2">Muay Thai</h3><p class="text-sm text-white/45">Clinch work, elbows, and the eight-limb game from coaches trained in Thailand.</p></div>
      <div class="reveal bg-canvas-card border border-white/5 p-8" style="transition-delay:.2s"><div class="text-4xl mb-4">🤼</div><h3 class="font-display text-xl font-bold mb-2">MMA</h3><p class="text-sm text-white/45">Striking-to-grappling transitions for those building toward amateur competition.</p></div>
    </div>
  </div>
</section>

<section id="fighters" class="py-24 lg:py-32">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent font-display font-bold tracking-widest mb-3">OUR FIGHT TEAM</p>
      <h2 class="font-display text-3xl lg:text-5xl font-bold">The ones who compete</h2>
    </div>
    <div id="fighter-grid" class="grid grid-cols-2 sm:grid-cols-4 gap-5"></div>
  </div>
</section>

<section id="membership" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent font-display font-bold tracking-widest mb-3">MEMBERSHIP</p>
      <h2 class="font-display text-3xl lg:text-5xl font-bold">No contracts, no excuses</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="reveal bg-canvas-card border border-white/5 p-8">
        <p class="font-display text-sm text-white/40 tracking-widest mb-2">DROP-IN</p>
        <p class="font-display text-4xl font-bold mb-4">$25</p>
        <ul class="space-y-2 text-sm text-white/55 mb-6"><li>Single class</li><li>Glove rental included</li></ul>
        <button class="w-full border border-white/15 hover:border-accent hover:text-accent font-display font-bold py-3 transition-all">Book a Class</button>
      </div>
      <div class="reveal bg-canvas-card border border-accent p-8 relative">
        <span class="absolute -top-3 left-8 bg-accent font-display text-xs font-bold px-3 py-1">MOST JOIN THIS</span>
        <p class="font-display text-sm text-white/40 tracking-widest mb-2">UNLIMITED</p>
        <p class="font-display text-4xl font-bold mb-4">$159<span class="text-base text-white/40">/mo</span></p>
        <ul class="space-y-2 text-sm text-white/55 mb-6"><li>All classes, all disciplines</li><li>Open mat access</li><li>No contract</li></ul>
        <button class="w-full bg-accent hover:bg-accent-hover font-display font-bold py-3 transition-all">Start Membership</button>
      </div>
      <div class="reveal bg-canvas-card border border-white/5 p-8">
        <p class="font-display text-sm text-white/40 tracking-widest mb-2">FIGHT TEAM</p>
        <p class="font-display text-4xl font-bold mb-4">By Invite</p>
        <ul class="space-y-2 text-sm text-white/55 mb-6"><li>Competition-track training</li><li>Corner support at events</li></ul>
        <button class="w-full border border-white/15 hover:border-accent hover:text-accent font-display font-bold py-3 transition-all">Inquire</button>
      </div>
    </div>
  </div>
</section>

<section class="py-20 border-t border-white/5">
  <div class="max-w-3xl mx-auto px-6 text-center reveal">
    <p class="text-2xl font-medium text-white/85 leading-relaxed mb-6">"I walked in soft and scared of the bag. A year later I had my first amateur fight. This place doesn't coddle you, and that's exactly why it works."</p>
    <p class="text-sm text-white/40 font-display">— DEVON R., MEMBER SINCE 2023</p>
  </div>
</section>

<footer class="border-t border-white/5 py-12 bg-canvas-light">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p class="font-display">© 2026 IRONCLAD COMBAT CLUB</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Waiver</a><a href="#" class="hover:text-white/60">Contact</a></div>
  </div>
</footer>

<script>
const fighters = [
  { name:'Marcus Reyes', weight:'Welterweight', record:'8-1-0', next:'Sept 14' },
  { name:'Tia Nakamura', weight:'Bantamweight', record:'6-0-1', next:'Oct 3' },
  { name:'Diego Ferreira', weight:'Lightweight', record:'11-2-0', next:'Aug 29' },
  { name:'Sam Okafor', weight:'Middleweight', record:'4-1-0', next:'Sept 21' },
];
function renderFighters(){
  const grid = document.getElementById('fighter-grid');
  grid.innerHTML = '';
  fighters.forEach((f,i)=>{
    const card = document.createElement('div');
    card.className = 'fighter-card reveal relative bg-canvas-card border border-white/5 aspect-[3/4] overflow-hidden cursor-pointer';
    card.style.transitionDelay = (i*60)+'ms';
    card.innerHTML = `
      <div class="absolute inset-0 bg-gradient-to-br from-accent/10 to-transparent flex items-center justify-center">
        <span class="font-display text-5xl font-bold text-white/10">${f.name.split(' ').map(n=>n[0]).join('')}</span>
      </div>
      <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
        <p class="font-display font-bold text-sm">${f.name}</p>
        <p class="text-xs text-white/50">${f.weight}</p>
        <p class="font-display text-accent font-bold text-sm mt-1">${f.record}</p>
      </div>
      <div class="fighter-overlay absolute inset-0 bg-black/85 flex flex-col items-center justify-center text-center p-4">
        <p class="text-xs text-white/40 uppercase tracking-wide mb-2">Next Fight</p>
        <p class="font-display text-xl font-bold text-accent">${f.next}</p>
      </div>
    `;
    grid.appendChild(card);
    revealObserver.observe(card);
  });
}

const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileNav = document.getElementById('mobile-nav');
mobileMenuBtn.addEventListener('click', ()=>mobileNav.classList.toggle('hidden'));
mobileNav.querySelectorAll('a').forEach(l=>l.addEventListener('click', ()=>mobileNav.classList.add('hidden')));

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(12,12,12,0.9)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

renderFighters();
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/08_independent_bookstore.md

# Example — Independent Bookstore (Vanilla CSS Architecture)

Tags: example, full-site, bookstore, books, independent-retail, vanilla-css, dark-theme, maroon, cream, serif, editorial, staff-picks

Niche: independent neighborhood bookstore.
Architecture: vanilla CSS, custom properties.
Palette: deep maroon canvas (#2B1018), warm cream text (#F2E8D8), brass accent (#C9A35C).
Signature element: a staff-picks "shelf" — a horizontally scrolling row of book
spines with staff name and one-line pitch on hover/tap.
Sections: header, hero, staff-picks shelf, event calendar strip, sections-by-genre
grid, newsletter, footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Marlowe &amp; Sons Booksellers | Independent Bookstore</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Karla:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --maroon:#2B1018; --maroon-light:#3A1721; --maroon-lighter:#4A1F2D; --line:#5C2A39;
  --cream:#F2E8D8; --cream-dim:#C9AFA0; --brass:#C9A35C; --brass-hover:#DBB873;
  --radius:8px; --radius-lg:14px;
  --transition: all 0.35s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow-lg: 0 20px 50px rgba(0,0,0,0.45);
  --serif:'Libre Caslon Text', serif; --sans:'Karla', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--maroon);color:var(--cream);line-height:1.7;overflow-x:hidden;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;} button{cursor:pointer;font-family:inherit;}
.container{max-width:1180px;margin:0 auto;padding:0 2rem;}
.section{padding:6rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.76rem;color:var(--brass);margin-bottom:1rem;font-weight:600;}
.section-title{font-family:var(--serif);font-size:2.5rem;font-weight:700;margin-bottom:1rem;}
.section-subtitle{color:var(--cream-dim);font-size:1.02rem;max-width:560px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.85rem 2rem;border:none;border-radius:var(--radius);font-size:0.88rem;font-weight:700;transition:var(--transition);}
.btn-primary{background:var(--brass);color:var(--maroon);}
.btn-primary:hover{background:var(--brass-hover);transform:translateY(-2px);}
.btn-outline{background:transparent;color:var(--cream);border:1.5px solid var(--line);}
.btn-outline:hover{border-color:var(--brass);color:var(--brass);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.4rem 0;transition:var(--transition);}
.header.scrolled{background:rgba(43,16,24,0.94);backdrop-filter:blur(14px);padding:1rem 0;box-shadow:0 2px 24px rgba(0,0,0,0.3);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--serif);font-size:1.4rem;font-weight:700;font-style:italic;}
.logo span{color:var(--brass);font-style:normal;}
.nav-list{display:flex;list-style:none;gap:2.2rem;align-items:center;}
.nav-list a{font-size:0.84rem;font-weight:600;letter-spacing:0.5px;position:relative;padding:0.2rem 0;}
.nav-list a::after{content:"";position:absolute;bottom:-2px;left:0;width:0;height:2px;background:var(--brass);transition:var(--transition);}
.nav-list a:hover::after,.nav-list a.active::after{width:100%;}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:22px;height:2px;background:var(--cream);transition:var(--transition);}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:86vh;display:flex;align-items:center;padding-top:6rem;background:linear-gradient(160deg,var(--maroon) 0%,var(--maroon-light) 60%,var(--maroon) 100%);}
.hero-grid{display:grid;grid-template-columns:1.1fr 0.9fr;gap:3.5rem;align-items:center;}
.hero-label{display:inline-block;padding:0.4rem 1rem;border:1px solid rgba(201,163,92,0.4);border-radius:30px;font-size:0.76rem;letter-spacing:2px;text-transform:uppercase;color:var(--brass);margin-bottom:1.8rem;}
.hero-title{font-family:var(--serif);font-size:3.4rem;font-weight:700;line-height:1.15;margin-bottom:1.3rem;}
.hero-title em{font-style:italic;color:var(--brass);}
.hero-desc{font-size:1.05rem;color:var(--cream-dim);max-width:440px;margin-bottom:2rem;}
.hero-visual{aspect-ratio:3/4;border-radius:var(--radius-lg);background:linear-gradient(150deg,var(--maroon-lighter),var(--maroon-light));border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:5rem;}

.shelf-wrap{margin-top:3rem;overflow-x:auto;padding-bottom:1rem;}
.shelf{display:flex;gap:1.2rem;width:max-content;}
.book-card{width:180px;flex-shrink:0;cursor:pointer;}
.book-spine{aspect-ratio:2/3;border-radius:6px;background:linear-gradient(160deg,var(--maroon-lighter),var(--maroon-light));border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:2.5rem;margin-bottom:0.9rem;position:relative;overflow:hidden;transition:var(--transition);}
.book-card:hover .book-spine{transform:translateY(-6px);border-color:var(--brass);}
.book-pick-overlay{position:absolute;inset:0;background:rgba(43,16,24,0.95);display:flex;align-items:center;justify-content:center;padding:1rem;text-align:center;opacity:0;transition:opacity 0.3s ease;}
.book-card:hover .book-pick-overlay{opacity:1;}
.book-pick-overlay p{font-size:0.78rem;font-style:italic;font-family:var(--serif);}
.book-title{font-family:var(--serif);font-size:0.95rem;font-weight:700;margin-bottom:0.2rem;}
.book-staff{font-size:0.76rem;color:var(--brass);}

.events-strip{display:flex;gap:1.2rem;overflow-x:auto;margin-top:2.5rem;padding-bottom:0.5rem;}
.event-card{background:var(--maroon-light);border:1px solid var(--line);border-radius:var(--radius);padding:1.4rem;min-width:240px;flex-shrink:0;}
.event-date{font-family:var(--serif);color:var(--brass);font-size:0.85rem;margin-bottom:0.5rem;}
.event-title{font-weight:700;margin-bottom:0.3rem;}
.event-desc{font-size:0.85rem;color:var(--cream-dim);}

.genre-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1.3rem;margin-top:2.5rem;}
.genre-card{background:var(--maroon-light);border:1px solid var(--line);border-radius:var(--radius-lg);padding:2rem 1.5rem;text-align:center;transition:var(--transition);}
.genre-card:hover{transform:translateY(-5px);border-color:var(--brass);}
.genre-icon{font-size:2rem;margin-bottom:0.8rem;}
.genre-card h4{font-family:var(--serif);font-size:1.05rem;}

.newsletter-section{background:var(--maroon-light);text-align:center;border-top:1px solid var(--line);border-bottom:1px solid var(--line);}
.newsletter-section h3{font-family:var(--serif);font-size:1.9rem;margin-bottom:0.7rem;}
.newsletter-section p{color:var(--cream-dim);margin-bottom:1.8rem;}
.newsletter-form{display:flex;gap:0.7rem;max-width:400px;margin:0 auto;flex-wrap:wrap;justify-content:center;}
.newsletter-form input{flex:1;min-width:200px;padding:0.8rem 1rem;border-radius:var(--radius);border:1px solid var(--line);background:var(--maroon);color:var(--cream);font-family:inherit;}
.newsletter-form button{background:var(--brass);color:var(--maroon);border:none;padding:0.8rem 1.5rem;border-radius:var(--radius);font-weight:700;}
.newsletter-note{margin-top:0.9rem;font-size:0.8rem;color:var(--cream-dim);}

.footer{padding:3.2rem 0 0;}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:3rem;padding-bottom:2.2rem;}
.footer-col h4{font-size:0.78rem;text-transform:uppercase;letter-spacing:1.3px;margin-bottom:1rem;color:var(--brass);}
.footer-col a,.footer-col p{display:block;color:var(--cream-dim);font-size:0.86rem;margin-bottom:0.7rem;}
.footer-col a:hover{color:var(--brass);}
.footer-bottom{border-top:1px solid var(--line);padding:1.2rem 0;display:flex;justify-content:space-between;font-size:0.8rem;color:var(--cream-dim);}

.reveal{opacity:0;transform:translateY(26px);transition:all 0.65s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .hero-grid{grid-template-columns:1fr;}
  .genre-grid{grid-template-columns:repeat(2,1fr);}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--maroon);flex-direction:column;justify-content:center;gap:2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.4rem;}
  .footer-grid{grid-template-columns:1fr;}
}
@media (max-width:600px){ .footer-bottom{flex-direction:column;gap:0.6rem;text-align:center;} }
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Marlowe <span>&amp;</span> Sons</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero" class="active">Home</a></li>
      <li><a href="#picks">Staff Picks</a></li>
      <li><a href="#events">Events</a></li>
      <li><a href="#sections">Browse</a></li>
    </ul></nav>
    <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <span class="hero-label">Independent Since 1987</span>
        <h1 class="hero-title">Browse slower.<br><em>Read better.</em></h1>
        <p class="hero-desc">Three rooms, twelve thousand titles, and a staff that will absolutely talk you out of buying the wrong book.</p>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;">
          <a href="#picks" class="btn btn-primary">See Staff Picks</a>
          <a href="#events" class="btn btn-outline">Upcoming Events</a>
        </div>
      </div>
      <div class="hero-visual">📚</div>
    </div>
  </div>
</section>

<section class="section" id="picks">
  <div class="container">
    <div class="reveal">
      <span class="section-label">This Month's Shelf</span>
      <h2 class="section-title">Staff picks</h2>
      <p class="section-subtitle">Hover (or tap) a spine to see why we picked it.</p>
    </div>
    <div class="shelf-wrap">
      <div class="shelf" id="shelf"></div>
    </div>
  </div>
</section>

<section class="section" id="events" style="background:var(--maroon-light);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">What's On</span>
      <h2 class="section-title">Upcoming events</h2>
    </div>
    <div class="events-strip">
      <div class="event-card"><p class="event-date">JUL 8, 7PM</p><p class="event-title">Author Talk: Reyna Ortiz</p><p class="event-desc">Debut novelist discusses her new collection of linked stories.</p></div>
      <div class="event-card"><p class="event-date">JUL 15, 6PM</p><p class="event-title">Poetry Open Mic</p><p class="event-desc">Sign up at the counter — five minutes, any style.</p></div>
      <div class="event-card"><p class="event-date">JUL 22, 11AM</p><p class="event-title">Storytime &amp; Craft</p><p class="event-desc">For ages 4-7, with a take-home craft each week.</p></div>
      <div class="event-card"><p class="event-date">AUG 2, 7PM</p><p class="event-title">Book Club: July Pick</p><p class="event-desc">This month's selection is on the staff picks table.</p></div>
    </div>
  </div>
</section>

<section class="section" id="sections">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Browse</span>
      <h2 class="section-title">Wander a section</h2>
    </div>
    <div class="genre-grid">
      <div class="genre-card reveal"><div class="genre-icon">🔍</div><h4>Mystery</h4></div>
      <div class="genre-card reveal"><div class="genre-icon">🚀</div><h4>Sci-Fi</h4></div>
      <div class="genre-card reveal"><div class="genre-icon">📜</div><h4>History</h4></div>
      <div class="genre-card reveal"><div class="genre-icon">🌙</div><h4>Poetry</h4></div>
    </div>
  </div>
</section>

<section class="section newsletter-section">
  <div class="container">
    <h3>Get the staff picks letter</h3>
    <p>One email a month, written by the staff, never by marketing.</p>
    <form class="newsletter-form" id="newsletter-form">
      <input type="email" id="newsletter-email" placeholder="you@example.com" required>
      <button type="submit">Subscribe</button>
    </form>
    <p class="newsletter-note" id="newsletter-note">Unsubscribe anytime, we won't take it personally.</p>
  </div>
</section>

<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-col"><h4>Marlowe &amp; Sons</h4><p>An independent bookstore in three rooms, open since 1987.</p></div>
    <div class="footer-col"><h4>Visit</h4><a href="#">Hours &amp; Directions</a><a href="#events">Events Calendar</a><a href="#">Gift Cards</a></div>
    <div class="footer-col"><h4>Shop</h4><a href="#picks">Staff Picks</a><a href="#sections">Browse Sections</a><a href="#">Special Orders</a></div>
  </div>
  <div class="container footer-bottom"><p>© 2026 Marlowe &amp; Sons Booksellers.</p><p>Shop indie, read deep.</p></div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function(){
  const books = [
    { title:'The Quiet Atlas', staff:'Pick by Jo', icon:'📘', pitch:'"A debut that made me cancel plans to finish it in one sitting."' },
    { title:'Salt &amp; Static', staff:'Pick by Mara', icon:'📗', pitch:'"Sharp, funny, and devastating in the last twenty pages."' },
    { title:'The Long Ferry', staff:'Pick by Theo', icon:'📙', pitch:'"Slow-burn literary fiction for readers who liked Sally Rooney."' },
    { title:'Field Notes on Leaving', staff:'Pick by Jo', icon:'📕', pitch:'"Essays that read like letters from a friend who left town."' },
    { title:'The Cartographer\\'s Wife', staff:'Pick by Mara', icon:'📔', pitch:'"Historical fiction with an ending I still think about."' },
    { title:'Static Bloom', staff:'Pick by Theo', icon:'📒', pitch:'"Poetry collection that reads fast but lingers for weeks."' },
  ];
  function escapeHtml(str){ const d=document.createElement('div'); d.textContent=str; return d.innerHTML; }
  function renderShelf(){
    const shelf = document.getElementById('shelf');
    shelf.innerHTML = '';
    books.forEach(b=>{
      const card = document.createElement('div');
      card.className = 'book-card';
      card.innerHTML = `
        <div class="book-spine">
          ${b.icon}
          <div class="book-pick-overlay"><p>${escapeHtml(b.pitch)}</p></div>
        </div>
        <p class="book-title">${escapeHtml(b.title)}</p>
        <p class="book-staff">${escapeHtml(b.staff)}</p>
      `;
      shelf.appendChild(card);
    });
  }
  renderShelf();

  const header = document.getElementById('header');
  const menuToggle = document.getElementById('menu-toggle');
  const navList = document.getElementById('nav-list');
  const overlay = document.getElementById('overlay');
  function toggleMenu(){ menuToggle.classList.toggle('active'); navList.classList.toggle('open'); overlay.classList.toggle('active'); document.body.style.overflow = navList.classList.contains('open')?'hidden':''; }
  menuToggle.addEventListener('click', toggleMenu);
  overlay.addEventListener('click', toggleMenu);
  navList.querySelectorAll('a').forEach(link=>link.addEventListener('click', ()=>{ if(navList.classList.contains('open')) toggleMenu(); }));
  window.addEventListener('scroll', ()=>{ header.classList.toggle('scrolled', window.scrollY>40); }, {passive:true});

  const revealObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
  }, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

  document.getElementById('newsletter-form').addEventListener('submit', (e)=>{
    e.preventDefault();
    document.getElementById('newsletter-note').textContent = "You're on the list — first letter goes out next month.";
    e.target.reset();
  });
});
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/09_private_aviation_charter.md

# Example — Private Aviation Charter (Tailwind Architecture)

Tags: example, full-site, private-jet, aviation, luxury, charter, tailwind, dark-theme, obsidian, champagne-gold, route-selector, luxury-minimal

Niche: private jet charter booking service.
Architecture: Tailwind CDN utility classes.
Palette: obsidian canvas (#0B0B0D), champagne gold accent (#D4AF7A), generous
whitespace, restrained motion (luxury = quiet, not flashy).
Signature element: a city-pair route selector — two dropdowns (from/to) that update
an estimated flight time and price range live, no page reload.
Sections: header, hero, route selector, fleet cards, how-charter-works steps,
testimonial, contact/inquiry form, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aerion Charter | Private Jet Charter, On Your Schedule</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#0B0B0D',light:'#131315',card:'#191919'}, accent:{DEFAULT:'#D4AF7A',hover:'#E2C394',glow:'rgba(212,175,122,0.25)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], display:['Cormorant Garamond','serif'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Cormorant+Garamond:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;font-weight:300;}
  .font-display{font-family:'Cormorant Garamond',serif;}
  ::selection{background:rgba(212,175,122,0.25);}
  .hero-title{font-size:clamp(2.6rem,6vw,5.4rem);line-height:1.05;letter-spacing:-0.01em;}
  .reveal{opacity:0;transform:translateY(24px);transition:all .8s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  select:focus,input:focus,button:focus-visible{outline:1px solid #D4AF7A;outline-offset:2px;}
  .route-line{stroke-dasharray:4 4;animation:dash 30s linear infinite;}
  @keyframes dash{to{stroke-dashoffset:-1000;}}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-24">
      <a href="#" class="font-display text-2xl tracking-wide">AERION</a>
      <nav class="hidden lg:flex items-center gap-12 absolute left-1/2 -translate-x-1/2">
        <a href="#route" class="text-xs text-white/60 hover:text-white uppercase tracking-[0.15em]">Plan a Flight</a>
        <a href="#fleet" class="text-xs text-white/60 hover:text-white uppercase tracking-[0.15em]">Fleet</a>
        <a href="#contact" class="text-xs text-white/60 hover:text-white uppercase tracking-[0.15em]">Inquire</a>
      </nav>
      <a href="#contact" class="border border-accent/50 text-accent hover:bg-accent hover:text-canvas text-xs uppercase tracking-[0.1em] px-6 py-3 transition-all">Request Quote</a>
    </div>
  </div>
</header>

<section class="relative min-h-[94vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 70% 20%, rgba(212,175,122,0.06) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
    <p class="text-accent text-xs uppercase tracking-[0.2em] mb-8">On-Demand Private Aviation</p>
    <h1 class="hero-title font-display text-white mb-8 max-w-3xl">
      Your schedule.<br>Never the airline's.
    </h1>
    <p class="text-lg text-white/45 max-w-md mb-10 leading-relaxed font-light">
      Access over 4,000 light and midsize jets across North America, bookable in
      as little as four hours' notice.
    </p>
    <a href="#route" class="inline-flex items-center gap-3 border border-accent/50 text-accent hover:bg-accent hover:text-canvas text-xs uppercase tracking-[0.1em] px-8 py-4 transition-all">Plan Your Route</a>
  </div>
</section>

<section id="route" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-14 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Plan a Flight</p>
      <h2 class="font-display text-3xl lg:text-4xl">Where are you headed?</h2>
    </div>
    <div class="bg-canvas-card border border-white/10 p-8 lg:p-10 reveal">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
        <div>
          <label class="block text-xs text-white/40 uppercase tracking-wide mb-2">Departing From</label>
          <select id="from-select" class="w-full bg-canvas border border-white/10 px-4 py-3 text-sm">
            <option value="nyc">New York (TEB)</option>
            <option value="la">Los Angeles (VNY)</option>
            <option value="miami">Miami (OPF)</option>
            <option value="chicago">Chicago (MDW)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-white/40 uppercase tracking-wide mb-2">Flying To</label>
          <select id="to-select" class="w-full bg-canvas border border-white/10 px-4 py-3 text-sm">
            <option value="la">Los Angeles (VNY)</option>
            <option value="nyc">New York (TEB)</option>
            <option value="miami">Miami (OPF)</option>
            <option value="chicago">Chicago (MDW)</option>
            <option value="aspen">Aspen (ASE)</option>
          </select>
        </div>
      </div>
      <div class="grid grid-cols-2 gap-6 pt-6 border-t border-white/10">
        <div>
          <p class="text-xs text-white/40 uppercase tracking-wide mb-2">Estimated Flight Time</p>
          <p id="flight-time" class="font-display text-3xl text-accent">5h 10m</p>
        </div>
        <div>
          <p class="text-xs text-white/40 uppercase tracking-wide mb-2">Estimated Price Range</p>
          <p id="flight-price" class="font-display text-3xl text-accent">$24,000 – $38,000</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="fleet" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">The Fleet</p>
      <h2 class="font-display text-3xl lg:text-4xl">Three categories, one standard</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-8">
      <div class="reveal text-center">
        <div class="aspect-[4/3] bg-canvas-card border border-white/5 mb-5 flex items-center justify-center text-5xl">🛩️</div>
        <h3 class="font-display text-xl mb-2">Light Jet</h3>
        <p class="text-sm text-white/45 mb-3">Up to 6 passengers · 1,500nm range</p>
        <p class="text-accent text-sm">From $4,800/hr</p>
      </div>
      <div class="reveal text-center" style="transition-delay:.1s">
        <div class="aspect-[4/3] bg-canvas-card border border-white/5 mb-5 flex items-center justify-center text-5xl">✈️</div>
        <h3 class="font-display text-xl mb-2">Midsize Jet</h3>
        <p class="text-sm text-white/45 mb-3">Up to 9 passengers · 2,800nm range</p>
        <p class="text-accent text-sm">From $6,900/hr</p>
      </div>
      <div class="reveal text-center" style="transition-delay:.2s">
        <div class="aspect-[4/3] bg-canvas-card border border-white/5 mb-5 flex items-center justify-center text-5xl">🛫</div>
        <h3 class="font-display text-xl mb-2">Heavy Jet</h3>
        <p class="text-sm text-white/45 mb-3">Up to 14 passengers · 4,500nm range</p>
        <p class="text-accent text-sm">From $11,200/hr</p>
      </div>
    </div>
  </div>
</section>

<section class="py-24 lg:py-32">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal"><h2 class="font-display text-3xl lg:text-4xl">How charter works</h2></div>
    <div class="grid grid-cols-1 sm:grid-cols-4 gap-8 text-center">
      <div class="reveal"><p class="font-display text-3xl text-accent mb-3">01</p><p class="text-sm text-white/55">Tell us your route and travel dates</p></div>
      <div class="reveal" style="transition-delay:.1s"><p class="font-display text-3xl text-accent mb-3">02</p><p class="text-sm text-white/55">We source quotes from vetted operators</p></div>
      <div class="reveal" style="transition-delay:.2s"><p class="font-display text-3xl text-accent mb-3">03</p><p class="text-sm text-white/55">You choose the aircraft and confirm</p></div>
      <div class="reveal" style="transition-delay:.3s"><p class="font-display text-3xl text-accent mb-3">04</p><p class="text-sm text-white/55">Arrive 10 minutes before departure</p></div>
    </div>
  </div>
</section>

<section class="py-20 bg-canvas-light border-t border-white/5">
  <div class="max-w-2xl mx-auto px-6 text-center reveal">
    <p class="font-display text-2xl text-white/85 leading-relaxed mb-6">"We booked four hours before wheels-up for a family emergency. Aerion had us in the air in under three."</p>
    <p class="text-sm text-white/40 uppercase tracking-wide">Client since 2022</p>
  </div>
</section>

<section id="contact" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-2xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-12 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Get a Quote</p>
      <h2 class="font-display text-3xl">Request charter availability</h2>
    </div>
    <form id="contact-form" class="reveal space-y-5" novalidate>
      <div>
        <input type="text" id="name" placeholder="Full name" required class="w-full bg-canvas-card border border-white/10 px-4 py-3 text-sm">
        <span class="text-xs text-red-400 block mt-1" id="name-error"></span>
      </div>
      <div>
        <input type="email" id="email" placeholder="Email address" required class="w-full bg-canvas-card border border-white/10 px-4 py-3 text-sm">
        <span class="text-xs text-red-400 block mt-1" id="email-error"></span>
      </div>
      <div>
        <textarea id="message" placeholder="Route, dates, and passenger count" rows="3" required class="w-full bg-canvas-card border border-white/10 px-4 py-3 text-sm"></textarea>
        <span class="text-xs text-red-400 block mt-1" id="message-error"></span>
      </div>
      <button type="submit" class="w-full border border-accent/50 text-accent hover:bg-accent hover:text-canvas text-xs uppercase tracking-[0.1em] py-4 transition-all">Request Quote</button>
      <p class="text-sm text-center" id="form-status"></p>
    </form>
  </div>
</section>

<footer class="border-t border-white/5 py-12">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-white/30 uppercase tracking-wide">
    <p>© 2026 Aerion Charter</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Privacy</a><a href="#" class="hover:text-white/60">Safety</a></div>
  </div>
</footer>

<script>
const routes = {
  'nyc-la':{time:'5h 25m', price:'$26,000 – $41,000'}, 'la-nyc':{time:'5h 10m', price:'$26,000 – $41,000'},
  'nyc-miami':{time:'2h 45m', price:'$12,000 – $19,000'}, 'miami-nyc':{time:'2h 50m', price:'$12,000 – $19,000'},
  'nyc-chicago':{time:'2h 10m', price:'$9,500 – $15,000'}, 'chicago-nyc':{time:'2h 15m', price:'$9,500 – $15,000'},
  'la-miami':{time:'4h 50m', price:'$24,000 – $38,000'}, 'miami-la':{time:'4h 55m', price:'$24,000 – $38,000'},
  'la-chicago':{time:'4h 05m', price:'$18,000 – $28,000'}, 'chicago-la':{time:'4h 10m', price:'$18,000 – $28,000'},
  'nyc-aspen':{time:'4h 15m', price:'$19,000 – $29,000'}, 'la-aspen':{time:'2h 05m', price:'$10,000 – $16,000'},
  'miami-aspen':{time:'4h 30m', price:'$20,000 – $31,000'}, 'chicago-aspen':{time:'2h 35m', price:'$11,500 – $18,000'},
  'miami-chicago':{time:'3h 05m', price:'$13,500 – $21,000'}, 'chicago-miami':{time:'3h 10m', price:'$13,500 – $21,000'},
};
function updateRoute(){
  const from = document.getElementById('from-select').value;
  const to = document.getElementById('to-select').value;
  if (from === to) {
    document.getElementById('flight-time').textContent = '—';
    document.getElementById('flight-price').textContent = 'Select two different cities';
    return;
  }
  const key = `${from}-${to}`;
  const reverseKey = `${to}-${from}`;
  const route = routes[key] || routes[reverseKey] || { time:'3h 30m', price:'$15,000 – $24,000' };
  document.getElementById('flight-time').textContent = route.time;
  document.getElementById('flight-price').textContent = route.price;
}
document.getElementById('from-select').addEventListener('change', updateRoute);
document.getElementById('to-select').addEventListener('change', updateRoute);
updateRoute();

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(11,11,13,0.9)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

const form = document.getElementById('contact-form');
const validators = {
  name: v => v.trim().length >= 2 || 'Please enter your full name.',
  email: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Enter a valid email address.',
  message: v => v.trim().length >= 10 || 'Tell us a bit more about your trip.'
};
function validateField(id){
  const field = document.getElementById(id);
  const errorEl = document.getElementById(`${id}-error`);
  const result = validators[id](field.value);
  if (result === true) { errorEl.textContent=''; return true; }
  errorEl.textContent = result; return false;
}
Object.keys(validators).forEach(id=>{
  document.getElementById(id).addEventListener('blur', ()=>validateField(id));
});
form.addEventListener('submit', (e)=>{
  e.preventDefault();
  const allValid = Object.keys(validators).map(validateField).every(Boolean);
  const status = document.getElementById('form-status');
  if (!allValid) { status.textContent = 'Please fix the highlighted fields.'; status.className='text-sm text-center text-red-400'; return; }
  const btn = form.querySelector('button[type=submit]');
  btn.disabled = true; btn.textContent = 'Sending...';
  setTimeout(()=>{
    status.textContent = "Thank you — a charter specialist will respond within the hour.";
    status.className = 'text-sm text-center text-accent';
    form.reset(); btn.disabled=false; btn.textContent='Request Quote';
  }, 900);
});
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/10_kids_stem_camp.md

# Example — Children's STEM Summer Camp (Vanilla CSS Architecture, Light Mode)

Tags: example, full-site, kids, stem, summer-camp, education, vanilla-css, light-theme, playful, bright-colors, multicolor, age-track-selector

Niche: summer STEM day camp for kids ages 6-14.
Architecture: vanilla CSS, custom properties, light mode.
Palette: bright white canvas (#FFFFFF), saturated multicolor accents (coral #FF6B5B,
sky blue #3EC1D3, sunny yellow #FFC93C, grass green #4CAF6D) — distinct per age track,
rounded playful sans display type.
Signature element: an age-track selector (Explorers 6-8 / Builders 9-11 / Inventors
12-14) that swaps the visible curriculum card set and the accent color used on buttons.
Sections: header, hero, age-track selector + curriculum cards, weekly themes strip,
safety/staff-ratio reassurance section, registration CTA, footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spark Lab Camps | STEM Summer Camp for Kids 6-14</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --white:#FFFFFF; --offwhite:#F7F9FC; --line:#E7ECF2;
  --ink:#26324A; --ink-dim:#6B7794;
  --coral:#FF6B5B; --sky:#3EC1D3; --yellow:#FFC93C; --green:#4CAF6D;
  --active:#FF6B5B; --active-dim:rgba(255,107,91,0.12);
  --radius:18px; --radius-lg:26px;
  --transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  --shadow: 0 10px 28px rgba(38,50,74,0.08); --shadow-lg: 0 20px 48px rgba(38,50,74,0.12);
  --display:'Baloo 2', sans-serif; --sans:'Nunito', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--white);color:var(--ink);line-height:1.65;overflow-x:hidden;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;} button{cursor:pointer;font-family:inherit;}
.container{max-width:1160px;margin:0 auto;padding:0 2rem;}
.section{padding:5.5rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:2px;font-size:0.78rem;color:var(--active);margin-bottom:0.8rem;font-weight:800;transition:color 0.3s ease;}
.section-title{font-family:var(--display);font-size:2.5rem;font-weight:700;margin-bottom:1rem;}
.section-subtitle{color:var(--ink-dim);font-size:1.02rem;max-width:540px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.9rem 2.1rem;border:none;border-radius:50px;font-size:0.92rem;font-weight:800;transition:var(--transition);}
.btn-primary{background:var(--active);color:#fff;}
.btn-primary:hover{transform:translateY(-3px) scale(1.02);box-shadow:var(--shadow-lg);}
.btn-outline{background:var(--white);color:var(--ink);border:2px solid var(--line);}
.btn-outline:hover{border-color:var(--active);color:var(--active);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.2rem 0;background:rgba(255,255,255,0.9);backdrop-filter:blur(10px);transition:var(--transition);border-bottom:1px solid transparent;}
.header.scrolled{box-shadow:0 2px 20px rgba(38,50,74,0.06);border-bottom-color:var(--line);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--display);font-size:1.5rem;font-weight:800;display:flex;align-items:center;gap:0.5rem;}
.nav-list{display:flex;list-style:none;gap:2rem;align-items:center;}
.nav-list a{font-size:0.88rem;font-weight:700;}
.nav-list a:hover{color:var(--active);}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:24px;height:3px;border-radius:2px;background:var(--ink);transition:var(--transition);}
.overlay{position:fixed;inset:0;background:rgba(38,50,74,0.4);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:88vh;display:flex;align-items:center;padding-top:6rem;background:radial-gradient(circle at 85% 15%, rgba(62,193,211,0.08), transparent 50%), radial-gradient(circle at 10% 85%, rgba(255,201,60,0.1), transparent 50%);}
.hero-grid{display:grid;grid-template-columns:1.05fr 0.95fr;gap:3.5rem;align-items:center;}
.hero-label{display:inline-flex;align-items:center;gap:0.5rem;padding:0.5rem 1.1rem;background:var(--active-dim);border-radius:50px;font-size:0.8rem;font-weight:800;color:var(--active);margin-bottom:1.6rem;transition:var(--transition);}
.hero-title{font-family:var(--display);font-size:3.3rem;font-weight:700;line-height:1.1;margin-bottom:1.3rem;}
.hero-title span{color:var(--active);transition:color 0.3s ease;}
.hero-desc{font-size:1.05rem;color:var(--ink-dim);max-width:460px;margin-bottom:2rem;}
.hero-visual{aspect-ratio:1;border-radius:var(--radius-lg);background:linear-gradient(150deg,#FFF3D6,#FFE0D6);display:flex;align-items:center;justify-content:center;font-size:5.5rem;box-shadow:var(--shadow-lg);}

.track-tabs{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin:2.5rem 0;}
.track-tab{background:var(--offwhite);border:2px solid var(--line);border-radius:50px;padding:0.9rem 1.8rem;font-weight:800;font-size:0.92rem;transition:var(--transition);display:flex;align-items:center;gap:0.6rem;}
.track-tab .age-pill{font-size:0.74rem;background:var(--line);padding:0.2rem 0.6rem;border-radius:20px;font-weight:700;}
.track-tab.active{color:#fff;border-color:transparent;}
.track-tab.active .age-pill{background:rgba(255,255,255,0.25);}

.curriculum-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;}
.curriculum-card{background:var(--offwhite);border-radius:var(--radius-lg);padding:2rem;border:1px solid var(--line);transition:var(--transition);}
.curriculum-card:hover{transform:translateY(-5px);box-shadow:var(--shadow-lg);}
.curriculum-icon{font-size:2.3rem;margin-bottom:1rem;}
.curriculum-card h4{font-family:var(--display);font-size:1.2rem;margin-bottom:0.5rem;}
.curriculum-card p{color:var(--ink-dim);font-size:0.92rem;}

.weeks-strip{display:flex;gap:1.2rem;overflow-x:auto;margin-top:2.5rem;padding-bottom:0.5rem;}
.week-card{background:var(--white);border:2px solid var(--line);border-radius:var(--radius);padding:1.4rem;min-width:200px;flex-shrink:0;text-align:center;}
.week-num{font-family:var(--display);font-size:0.8rem;color:var(--active);font-weight:800;margin-bottom:0.5rem;}
.week-theme{font-weight:800;font-size:0.95rem;}

.safety-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-top:2.5rem;text-align:center;}
.safety-stat{font-family:var(--display);font-size:2.4rem;color:var(--active);margin-bottom:0.4rem;}
.safety-label{font-size:0.88rem;color:var(--ink-dim);font-weight:700;}

.cta-section{background:linear-gradient(120deg,var(--coral),var(--yellow));text-align:center;border-radius:var(--radius-lg);padding:3.5rem 2rem;margin:0 2rem;}
.cta-section h3{font-family:var(--display);font-size:2.1rem;color:#fff;margin-bottom:0.8rem;}
.cta-section p{color:rgba(255,255,255,0.9);margin-bottom:1.8rem;}
.cta-section .btn{background:#fff;color:var(--coral);}

.footer{padding:3.5rem 0 0;border-top:1px solid var(--line);margin-top:4rem;}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:3rem;padding-bottom:2.2rem;}
.footer-col h4{font-size:0.8rem;text-transform:uppercase;letter-spacing:1.3px;margin-bottom:1rem;color:var(--ink-dim);}
.footer-col a,.footer-col p{display:block;color:var(--ink-dim);font-size:0.88rem;margin-bottom:0.7rem;}
.footer-col a:hover{color:var(--active);}
.footer-bottom{border-top:1px solid var(--line);padding:1.2rem 2rem;display:flex;justify-content:space-between;font-size:0.82rem;color:var(--ink-dim);}

.reveal{opacity:0;transform:translateY(24px);transition:all 0.6s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .hero-grid{grid-template-columns:1fr;}
  .curriculum-grid,.safety-grid{grid-template-columns:1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--white);flex-direction:column;justify-content:center;gap:2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.3rem;}
  .footer-grid{grid-template-columns:1fr;}
}
@media (max-width:600px){ .footer-bottom{flex-direction:column;gap:0.6rem;text-align:center;} .cta-section{margin:0 1rem;} }
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">⚡ Spark Lab</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero">Home</a></li>
      <li><a href="#tracks">Camp Tracks</a></li>
      <li><a href="#weeks">Weekly Themes</a></li>
      <li><a href="#safety">Safety</a></li>
    </ul></nav>
    <div style="display:flex;align-items:center;gap:1rem;">
      <a href="#cta" class="btn btn-primary" style="padding:0.7rem 1.5rem;font-size:0.85rem;">Register</a>
      <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <span class="hero-label" id="hero-badge">🚀 Now Enrolling for Summer</span>
        <h1 class="hero-title">Camp where kids<br>build <span id="hero-accent-word">robots</span>, not boredom.</h1>
        <p class="hero-desc">Hands-on STEM camp for ages 6-14 — coding, robotics, and engineering, taught by real engineers who actually like kids.</p>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;">
          <a href="#cta" class="btn btn-primary">Reserve a Spot</a>
          <a href="#tracks" class="btn btn-outline">See Camp Tracks</a>
        </div>
      </div>
      <div class="hero-visual">🤖</div>
    </div>
  </div>
</section>

<section class="section" id="tracks">
  <div class="container">
    <div class="reveal" style="text-align:center;">
      <span class="section-label">Pick a Track</span>
      <h2 class="section-title">Three camps, three age groups</h2>
      <p class="section-subtitle" style="margin:0 auto;">Tap an age group to see that week's curriculum.</p>
    </div>
    <div class="track-tabs" id="track-tabs">
      <button class="track-tab active" data-track="explorers" style="background:var(--coral);color:#fff;border-color:transparent;">🔍 Explorers <span class="age-pill">6-8</span></button>
      <button class="track-tab" data-track="builders">🔧 Builders <span class="age-pill">9-11</span></button>
      <button class="track-tab" data-track="inventors">💡 Inventors <span class="age-pill">12-14</span></button>
    </div>
    <div class="curriculum-grid" id="curriculum-grid"></div>
  </div>
</section>

<section class="section" id="weeks" style="background:var(--offwhite);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">This Summer</span>
      <h2 class="section-title">Weekly themes</h2>
    </div>
    <div class="weeks-strip">
      <div class="week-card"><p class="week-num">WEEK 1</p><p class="week-theme">🚀 Space &amp; Rockets</p></div>
      <div class="week-card"><p class="week-num">WEEK 2</p><p class="week-theme">🤖 Robotics</p></div>
      <div class="week-card"><p class="week-num">WEEK 3</p><p class="week-theme">🎮 Game Design</p></div>
      <div class="week-card"><p class="week-num">WEEK 4</p><p class="week-theme">🌱 Eco Engineering</p></div>
      <div class="week-card"><p class="week-num">WEEK 5</p><p class="week-theme">⚡ Circuits &amp; Power</p></div>
    </div>
  </div>
</section>

<section class="section" id="safety">
  <div class="container">
    <div class="reveal" style="text-align:center;">
      <span class="section-label">Parents, Read This</span>
      <h2 class="section-title">Safety is non-negotiable</h2>
    </div>
    <div class="safety-grid">
      <div class="reveal"><p class="safety-stat">1:8</p><p class="safety-label">Staff-to-camper ratio</p></div>
      <div class="reveal"><p class="safety-stat">100%</p><p class="safety-label">Background-checked staff</p></div>
      <div class="reveal"><p class="safety-stat">12yrs</p><p class="safety-label">Running summer camps</p></div>
    </div>
  </div>
</section>

<section class="section" id="cta">
  <div class="container">
    <div class="cta-section reveal">
      <h3>Spots fill by early May</h3>
      <p>Register now to lock in your child's preferred week and track.</p>
      <a href="#" class="btn">Start Registration</a>
    </div>
  </div>
</section>

<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-col"><h4>Spark Lab Camps</h4><p>Hands-on STEM summer camp for kids 6-14, run by real engineers.</p></div>
    <div class="footer-col"><h4>Camp</h4><a href="#tracks">Camp Tracks</a><a href="#weeks">Weekly Themes</a><a href="#safety">Safety Info</a></div>
    <div class="footer-col"><h4>Families</h4><a href="#">FAQ</a><a href="#">Financial Aid</a><a href="#">Contact Us</a></div>
  </div>
  <div class="container footer-bottom"><p>© 2026 Spark Lab Camps.</p><p>Building curious minds since 2014.</p></div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function(){
  const tracks = {
    explorers: { color:'#FF6B5B', word:'robots', curriculum:[
      { icon:'🧱', title:'LEGO Robotics', desc:'Build and program simple robots using block-based coding.' },
      { icon:'🔬', title:'Mini Science Lab', desc:'Hands-on experiments with everyday kitchen-cabinet materials.' },
      { icon:'🎨', title:'Design Thinking', desc:'Invent solutions to silly problems using the engineering process.' },
    ]},
    builders: { color:'#3EC1D3', word:'apps', curriculum:[
      { icon:'💻', title:'Intro to Scratch Coding', desc:'Build playable games and animations with visual block coding.' },
      { icon:'⚙️', title:'Circuit Building', desc:'Wire real circuits and learn how electricity actually moves.' },
      { icon:'🏗️', title:'Bridge Engineering', desc:'Design, build, and stress-test bridges out of recycled materials.' },
    ]},
    inventors: { color:'#4CAF6D', word:'inventions', curriculum:[
      { icon:'🐍', title:'Python Fundamentals', desc:'Write real, text-based code to build small games and tools.' },
      { icon:'🦾', title:'Advanced Robotics', desc:'Program sensor-driven robots to navigate mazes autonomously.' },
      { icon:'🚀', title:'Capstone Invention', desc:'Design an original invention and pitch it on Demo Day.' },
    ]}
  };

  function renderCurriculum(trackKey){
    const t = tracks[trackKey];
    const grid = document.getElementById('curriculum-grid');
    grid.innerHTML = '';
    t.curriculum.forEach((c,i)=>{
      const card = document.createElement('div');
      card.className = 'curriculum-card reveal';
      card.style.transitionDelay = (i*70)+'ms';
      card.innerHTML = `<div class="curriculum-icon">${c.icon}</div><h4>${c.title}</h4><p>${c.desc}</p>`;
      grid.appendChild(card);
      revealObserver.observe(card);
    });
    document.getElementById('hero-accent-word').textContent = t.word;
    document.documentElement.style.setProperty('--active', t.color);
    document.documentElement.style.setProperty('--active-dim', t.color + '1F');
  }

  document.querySelectorAll('.track-tab').forEach(tab=>{
    tab.addEventListener('click', ()=>{
      document.querySelectorAll('.track-tab').forEach(tb=>{ tb.classList.remove('active'); tb.style.background=''; tb.style.color=''; tb.style.borderColor=''; });
      tab.classList.add('active');
      const color = tracks[tab.dataset.track].color;
      tab.style.background = color; tab.style.color = '#fff'; tab.style.borderColor = 'transparent';
      renderCurriculum(tab.dataset.track);
    });
  });

  const header = document.getElementById('header');
  const menuToggle = document.getElementById('menu-toggle');
  const navList = document.getElementById('nav-list');
  const overlay = document.getElementById('overlay');
  function toggleMenu(){ menuToggle.classList.toggle('active'); navList.classList.toggle('open'); overlay.classList.toggle('active'); document.body.style.overflow = navList.classList.contains('open')?'hidden':''; }
  menuToggle.addEventListener('click', toggleMenu);
  overlay.addEventListener('click', toggleMenu);
  navList.querySelectorAll('a').forEach(link=>link.addEventListener('click', ()=>{ if(navList.classList.contains('open')) toggleMenu(); }));
  window.addEventListener('scroll', ()=>{ header.classList.toggle('scrolled', window.scrollY>40); }, {passive:true});

  const revealObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
  }, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

  renderCurriculum('explorers');
});
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/11_craft_cocktail_bar.md

# Example — Craft Cocktail Bar (Tailwind Architecture)

Tags: example, full-site, cocktail-bar, nightlife, bar, hospitality, tailwind, dark-theme, plum, neon-pink, flip-cards, menu

Niche: craft cocktail bar with a rotating seasonal menu.
Architecture: Tailwind CDN utility classes.
Palette: deep plum canvas (#1A0E1A), neon pink accent (#FF3D9A), moody and saturated.
Signature element: cocktail menu flip cards — each card flips on click/hover to
reveal the ingredient list and glassware on the back face, using a 3D CSS transform.
Sections: header, hero, menu flip-card grid, atmosphere/about, reservations CTA,
hours/location, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Velvet Hour | Craft Cocktail Bar</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#1A0E1A',light:'#241327',card:'#2C1730'}, accent:{DEFAULT:'#FF3D9A',hover:'#FF66AE',glow:'rgba(255,61,154,0.3)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], display:['Cormorant Garamond','serif'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Cormorant+Garamond:wght@500;600;700&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
  .font-display{font-family:'Cormorant Garamond',serif;}
  ::selection{background:rgba(255,61,154,0.3);}
  .hero-title{font-size:clamp(2.8rem,6.5vw,5.6rem);line-height:1.0;letter-spacing:-0.01em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .flip-card{perspective:1200px;height:340px;cursor:pointer;}
  .flip-inner{position:relative;width:100%;height:100%;transition:transform .6s cubic-bezier(.25,.8,.25,1);transform-style:preserve-3d;}
  .flip-card.flipped .flip-inner{transform:rotateY(180deg);}
  .flip-face{position:absolute;inset:0;backface-visibility:hidden;border-radius:1rem;}
  .flip-back{transform:rotateY(180deg);}
  input:focus,button:focus-visible{outline:2px solid #FF3D9A;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <a href="#" class="font-display text-2xl">Velvet Hour</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#menu" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">Menu</a>
        <a href="#about" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">About</a>
        <a href="#visit" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">Visit</a>
      </nav>
      <a href="#visit" class="bg-accent hover:bg-accent-hover text-white font-semibold text-sm px-5 py-2.5 rounded-full transition-colors">Reserve a Table</a>
    </div>
  </div>
</header>

<section class="relative min-h-[92vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 75% 25%, rgba(255,61,154,0.1) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10 text-center">
    <p class="text-accent text-sm uppercase tracking-[0.2em] mb-6">A Speakeasy on Elm Street</p>
    <h1 class="hero-title font-display text-white mb-8">
      Drinks built for<br><span class="text-accent">slow nights.</span>
    </h1>
    <p class="text-lg text-white/50 max-w-md mx-auto mb-10 leading-relaxed">
      A seasonal cocktail menu, low light, and a bar team that asks what you actually
      like before they pour anything.
    </p>
    <a href="#menu" class="inline-flex items-center gap-2 bg-accent hover:bg-accent-hover text-white font-semibold px-8 py-4 rounded-full transition-all hover:-translate-y-0.5">View the Menu</a>
  </div>
</section>

<section id="menu" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">This Season</p>
      <h2 class="font-display text-4xl">Tap a card to flip it</h2>
    </div>
    <div id="menu-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"></div>
  </div>
</section>

<section id="about" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-4xl mx-auto px-6 lg:px-8 text-center reveal">
    <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">About Us</p>
    <h2 class="font-display text-3xl lg:text-4xl mb-6">No TVs. No top-40. No rush.</h2>
    <p class="text-white/50 leading-relaxed">
      Velvet Hour opened in 2019 behind an unmarked door, on the idea that a bar could
      be a place you actually talk to people. The menu changes with the seasons, the
      lighting stays low, and the only soundtrack is a vinyl record someone on staff
      picked that night.
    </p>
  </div>
</section>

<section id="visit" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-5xl mx-auto px-6 lg:px-8 grid sm:grid-cols-2 gap-12">
    <div class="reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Hours</p>
      <h2 class="font-display text-3xl mb-6">When we're open</h2>
      <div class="space-y-2 text-white/60 text-sm">
        <div class="flex justify-between border-b border-white/5 py-2"><span>Tue – Thu</span><span>6pm – 1am</span></div>
        <div class="flex justify-between border-b border-white/5 py-2"><span>Fri – Sat</span><span>6pm – 2am</span></div>
        <div class="flex justify-between border-b border-white/5 py-2"><span>Sun – Mon</span><span>Closed</span></div>
      </div>
    </div>
    <div class="reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Reservations</p>
      <h2 class="font-display text-3xl mb-6">Book a table</h2>
      <p class="text-white/50 mb-6 text-sm">Walk-ins welcome at the bar; tables of 4+ recommended to reserve ahead.</p>
      <a href="#" class="inline-flex items-center gap-2 bg-accent hover:bg-accent-hover text-white font-semibold px-7 py-3.5 rounded-full transition-all">Reserve Now</a>
    </div>
  </div>
</section>

<footer class="border-t border-white/5 py-12 bg-canvas-light">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p>© 2026 Velvet Hour</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Private Events</a><a href="#" class="hover:text-white/60">Contact</a></div>
  </div>
</footer>

<script>
const cocktails = [
  { name:'Smoke & Mirrors', front:'🥃', notes:'Mezcal · Smoked Cherry · Lime', ingredients:'2oz mezcal, 0.75oz smoked cherry syrup, 0.75oz lime, dash mole bitters', glass:'Rocks glass, smoked' },
  { name:'Midnight Fig', front:'🍸', notes:'Gin · Fig · Black Pepper', ingredients:'2oz gin, 0.5oz fig liqueur, 0.5oz lemon, black pepper tincture', glass:'Coupe' },
  { name:'Velvet Old Fashioned', front:'🥃', notes:'Bourbon · Demerara · Orange', ingredients:'2oz bourbon, 0.25oz demerara syrup, orange bitters, orange peel', glass:'Rocks glass' },
  { name:'Paper Crane', front:'🍹', notes:'Vodka · Yuzu · Elderflower', ingredients:'1.5oz vodka, 0.5oz yuzu, 0.5oz elderflower, soda top', glass:'Highball' },
  { name:'Last Light', front:'🍷', notes:'Rye · Aperitivo · Grapefruit', ingredients:'1.5oz rye, 1oz bitter aperitivo, 0.5oz grapefruit, soda', glass:'Wine glass' },
  { name:'Honey & Ash', front:'🥃', notes:'Scotch · Honey · Lapsang', ingredients:'2oz scotch, 0.5oz honey syrup, lapsang tea reduction', glass:'Rocks glass, smoked' },
];

function renderMenu(){
  const grid = document.getElementById('menu-grid');
  grid.innerHTML = '';
  cocktails.forEach((c,i)=>{
    const card = document.createElement('div');
    card.className = 'flip-card reveal';
    card.style.transitionDelay = (i*60)+'ms';
    card.innerHTML = `
      <div class="flip-inner">
        <div class="flip-face flip-front bg-canvas-card border border-white/10 flex flex-col items-center justify-center text-center p-6">
          <div class="text-5xl mb-4">${c.front}</div>
          <h3 class="font-display text-2xl mb-2">${c.name}</h3>
          <p class="text-sm text-white/40">${c.notes}</p>
          <p class="text-xs text-white/25 mt-6">Tap to see recipe</p>
        </div>
        <div class="flip-face flip-back bg-accent flex flex-col items-center justify-center text-center p-6 text-white">
          <p class="text-xs uppercase tracking-wide opacity-75 mb-3">Recipe</p>
          <p class="text-sm leading-relaxed mb-4">${c.ingredients}</p>
          <p class="text-xs uppercase tracking-wide opacity-75">Served In</p>
          <p class="font-display text-lg">${c.glass}</p>
        </div>
      </div>
    `;
    card.addEventListener('click', ()=>card.classList.toggle('flipped'));
    grid.appendChild(card);
    revealObserver.observe(card);
  });
}

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(26,14,26,0.85)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

renderMenu();
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/12_architecture_studio.md

# Example — Architecture & Interior Design Studio (Vanilla CSS Architecture)

Tags: example, full-site, architecture, interior-design, studio, portfolio, vanilla-css, light-theme, concrete-gray, minimal, before-after-slider

Niche: architecture and interior design studio portfolio.
Architecture: vanilla CSS, custom properties, light/minimal mode.
Palette: warm white canvas (#FAFAF8), concrete gray accent (#7A7670), near-black text.
Signature element: a draggable before/after renovation slider (mouse + touch) using a
clip-path reveal, no library.
Sections: header, hero, before/after slider, project grid, philosophy statement,
services list, contact, footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Halden Studio | Architecture &amp; Interior Design</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Neue+Montreal:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --white:#FAFAF8; --white-card:#FFFFFF; --line:#E2E0D9;
  --ink:#191815; --ink-dim:#6E6A62; --concrete:#7A7670; --concrete-dark:#5C594F;
  --radius:2px; --radius-lg:4px;
  --transition: all 0.4s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow-lg: 0 24px 60px rgba(25,24,21,0.1);
  --sans:'Inter', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--white);color:var(--ink);line-height:1.7;overflow-x:hidden;font-weight:300;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;} button{cursor:pointer;font-family:inherit;}
.container{max-width:1240px;margin:0 auto;padding:0 2.5rem;}
.section{padding:7rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.72rem;color:var(--concrete-dark);margin-bottom:1.2rem;font-weight:600;}
.section-title{font-size:2.4rem;font-weight:300;line-height:1.2;margin-bottom:1rem;letter-spacing:-0.5px;}
.section-title strong{font-weight:600;}
.section-subtitle{color:var(--ink-dim);font-size:1rem;max-width:520px;}
.btn{display:inline-flex;align-items:center;gap:0.6rem;padding:0.95rem 2rem;border:1px solid var(--ink);font-size:0.82rem;font-weight:500;letter-spacing:0.8px;text-transform:uppercase;transition:var(--transition);}
.btn-primary{background:var(--ink);color:var(--white);}
.btn-primary:hover{background:var(--concrete-dark);border-color:var(--concrete-dark);}
.btn-outline{background:transparent;color:var(--ink);}
.btn-outline:hover{background:var(--ink);color:var(--white);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.6rem 0;transition:var(--transition);mix-blend-mode:normal;}
.header.scrolled{background:rgba(250,250,248,0.95);backdrop-filter:blur(10px);padding:1.2rem 0;box-shadow:0 1px 0 var(--line);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-size:1.15rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;}
.nav-list{display:flex;list-style:none;gap:2.5rem;align-items:center;}
.nav-list a{font-size:0.78rem;letter-spacing:1px;text-transform:uppercase;font-weight:500;}
.nav-list a:hover{color:var(--concrete-dark);}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:22px;height:1.5px;background:var(--ink);transition:var(--transition);}
.overlay{position:fixed;inset:0;background:rgba(25,24,21,0.4);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:88vh;display:flex;align-items:center;padding-top:6rem;}
.hero-title{font-size:3.6rem;font-weight:300;line-height:1.1;letter-spacing:-1px;margin-bottom:1.6rem;max-width:780px;}
.hero-title strong{font-weight:600;}
.hero-desc{font-size:1.05rem;color:var(--ink-dim);max-width:480px;margin-bottom:2.2rem;}

.slider-wrap{position:relative;aspect-ratio:16/9;border-radius:var(--radius-lg);overflow:hidden;margin-top:3rem;cursor:ew-resize;user-select:none;box-shadow:var(--shadow-lg);}
.slider-before,.slider-after{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:1rem;font-weight:500;letter-spacing:1px;text-transform:uppercase;color:#fff;}
.slider-before{background:linear-gradient(135deg,#4A4843,#2C2A26);}
.slider-after{background:linear-gradient(135deg,#D9D4C5,#B8B19E);color:var(--ink);clip-path:inset(0 50% 0 0);}
.slider-handle{position:absolute;top:0;bottom:0;left:50%;width:3px;background:#fff;transform:translateX(-50%);box-shadow:0 0 0 1px rgba(0,0,0,0.1);}
.slider-handle::after{content:"⇔";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:46px;height:46px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem;box-shadow:var(--shadow-lg);}
.slider-label{position:absolute;top:1.2rem;font-size:0.72rem;letter-spacing:1.5px;text-transform:uppercase;background:rgba(0,0,0,0.4);padding:0.4rem 0.9rem;border-radius:30px;}
.slider-label.before-label{left:1.2rem;}
.slider-label.after-label{right:1.2rem;background:rgba(255,255,255,0.6);color:var(--ink);}

.project-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;margin-top:3rem;}
.project-card{aspect-ratio:4/3;position:relative;overflow:hidden;background:linear-gradient(150deg,#E8E5DB,#D4D0C2);cursor:pointer;}
.project-overlay{position:absolute;inset:0;background:rgba(25,24,21,0);display:flex;flex-direction:column;justify-content:flex-end;padding:1.4rem;transition:var(--transition);}
.project-card:hover .project-overlay{background:rgba(25,24,21,0.55);}
.project-name{color:#fff;font-size:1rem;font-weight:500;opacity:0;transform:translateY(10px);transition:var(--transition);}
.project-cat{color:rgba(255,255,255,0.7);font-size:0.78rem;opacity:0;transform:translateY(10px);transition:var(--transition);transition-delay:0.05s;}
.project-card:hover .project-name,.project-card:hover .project-cat{opacity:1;transform:translateY(0);}

.philosophy-block{max-width:780px;}
.philosophy-block p{font-size:1.6rem;font-weight:300;line-height:1.5;letter-spacing:-0.3px;}
.philosophy-block strong{font-weight:600;}

.services-list{margin-top:2.5rem;}
.service-row{display:flex;justify-content:space-between;align-items:center;padding:1.8rem 0;border-bottom:1px solid var(--line);transition:var(--transition);}
.service-row:hover{padding-left:1rem;border-color:var(--ink);}
.service-row h4{font-size:1.3rem;font-weight:400;}
.service-row span{color:var(--ink-dim);font-size:0.85rem;}

.contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:4rem;margin-top:2.5rem;}
.contact-detail{margin-bottom:1.6rem;}
.contact-detail span{display:block;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;color:var(--ink-dim);margin-bottom:0.3rem;}
.contact-detail strong{font-size:1.1rem;font-weight:500;}
.form-group{margin-bottom:1.4rem;}
.form-group label{display:block;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;color:var(--ink-dim);}
.form-group input,.form-group textarea{width:100%;background:transparent;border:none;border-bottom:1px solid var(--line);padding:0.6rem 0;font-size:0.95rem;font-family:inherit;transition:var(--transition);}
.form-group input:focus,.form-group textarea:focus{outline:none;border-color:var(--ink);}
.form-error{display:block;font-size:0.76rem;color:#A85A4A;margin-top:0.4rem;min-height:1.1em;}
.form-status{margin-top:1rem;font-size:0.85rem;}

.footer{border-top:1px solid var(--line);padding:3rem 0;display:flex;justify-content:space-between;align-items:center;font-size:0.8rem;color:var(--ink-dim);}

.reveal{opacity:0;transform:translateY(24px);transition:all 0.7s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .project-grid{grid-template-columns:repeat(2,1fr);}
  .contact-grid{grid-template-columns:1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--white);flex-direction:column;justify-content:center;gap:2.2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.4rem;}
}
@media (max-width:600px){
  .project-grid{grid-template-columns:1fr;}
  .philosophy-block p{font-size:1.25rem;}
  .footer{flex-direction:column;gap:1rem;text-align:center;}
}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Halden Studio</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero">Studio</a></li>
      <li><a href="#projects">Projects</a></li>
      <li><a href="#services">Services</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul></nav>
    <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <span class="section-label">Architecture &amp; Interior Design</span>
    <h1 class="hero-title">We design spaces that get <strong>quieter</strong> the longer you live in them.</h1>
    <p class="hero-desc">A 12-person studio working on residential renovation and ground-up builds across the Pacific Northwest.</p>
    <a href="#contact" class="btn btn-primary">Start a Project</a>

    <div class="slider-wrap" id="slider-wrap">
      <div class="slider-before"><span>BEFORE</span></div>
      <div class="slider-after" id="slider-after"><span>AFTER</span></div>
      <div class="slider-label before-label">Before</div>
      <div class="slider-label after-label">After</div>
      <div class="slider-handle" id="slider-handle"></div>
    </div>
  </div>
</section>

<section class="section" id="projects">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Selected Work</span>
      <h2 class="section-title">Recent <strong>projects</strong></h2>
    </div>
    <div class="project-grid">
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Residential</span><span class="project-name">Birch Hollow Residence</span></div></div>
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Renovation</span><span class="project-name">Cascade Loft</span></div></div>
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Commercial</span><span class="project-name">Foundry Coffee HQ</span></div></div>
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Residential</span><span class="project-name">Quarry House</span></div></div>
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Interior</span><span class="project-name">Linden Apartment</span></div></div>
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Ground-Up</span><span class="project-name">Cedar Ridge Cabin</span></div></div>
    </div>
  </div>
</section>

<section class="section" style="background:var(--white-card);border-top:1px solid var(--line);border-bottom:1px solid var(--line);">
  <div class="container">
    <div class="philosophy-block reveal">
      <span class="section-label">Our Approach</span>
      <p>We believe good design is mostly <strong>restraint</strong> — knowing which walls to remove, which materials to leave honest, and which decisions to leave for the people who'll actually live there.</p>
    </div>
  </div>
</section>

<section class="section" id="services">
  <div class="container">
    <div class="reveal">
      <span class="section-label">What We Do</span>
      <h2 class="section-title">Our <strong>services</strong></h2>
    </div>
    <div class="services-list">
      <div class="service-row reveal"><h4>Architectural Design</h4><span>Ground-up &amp; renovation</span></div>
      <div class="service-row reveal"><h4>Interior Design</h4><span>Spatial planning &amp; FF&amp;E</span></div>
      <div class="service-row reveal"><h4>Construction Administration</h4><span>On-site oversight</span></div>
      <div class="service-row reveal"><h4>Feasibility &amp; Planning</h4><span>Permitting &amp; zoning</span></div>
    </div>
  </div>
</section>

<section class="section" id="contact" style="background:var(--white-card);border-top:1px solid var(--line);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Get In Touch</span>
      <h2 class="section-title">Start a <strong>conversation</strong></h2>
    </div>
    <div class="contact-grid">
      <div class="reveal">
        <div class="contact-detail"><span>Studio</span><strong>1140 Foundry Row, Seattle, WA</strong></div>
        <div class="contact-detail"><span>Email</span><strong>studio@haldendesign.com</strong></div>
        <div class="contact-detail"><span>Phone</span><strong>(206) 555-0172</strong></div>
      </div>
      <form id="contact-form" class="reveal" novalidate>
        <div class="form-group"><label for="name">Name</label><input type="text" id="name" required><span class="form-error" id="name-error"></span></div>
        <div class="form-group"><label for="email">Email</label><input type="email" id="email" required><span class="form-error" id="email-error"></span></div>
        <div class="form-group"><label for="message">Tell us about your project</label><textarea id="message" rows="3" required></textarea><span class="form-error" id="message-error"></span></div>
        <button type="submit" class="btn btn-primary">Send Inquiry</button>
        <p class="form-status" id="form-status"></p>
      </form>
    </div>
  </div>
</section>

<footer class="container footer">
  <p>© 2026 Halden Studio</p>
  <p>Seattle, WA</p>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function(){
  const sliderWrap = document.getElementById('slider-wrap');
  const sliderAfter = document.getElementById('slider-after');
  const sliderHandle = document.getElementById('slider-handle');
  let dragging = false;

  function setSlider(percent){
    percent = Math.max(0, Math.min(100, percent));
    sliderAfter.style.clipPath = `inset(0 ${100-percent}% 0 0)`;
    sliderHandle.style.left = percent + '%';
  }
  function getPercent(clientX){
    const rect = sliderWrap.getBoundingClientRect();
    return ((clientX - rect.left) / rect.width) * 100;
  }
  sliderWrap.addEventListener('mousedown', (e)=>{ dragging = true; setSlider(getPercent(e.clientX)); });
  window.addEventListener('mousemove', (e)=>{ if(dragging) setSlider(getPercent(e.clientX)); });
  window.addEventListener('mouseup', ()=>{ dragging = false; });
  sliderWrap.addEventListener('touchstart', (e)=>{ dragging = true; setSlider(getPercent(e.touches[0].clientX)); });
  sliderWrap.addEventListener('touchmove', (e)=>{ if(dragging) setSlider(getPercent(e.touches[0].clientX)); });
  sliderWrap.addEventListener('touchend', ()=>{ dragging = false; });

  const header = document.getElementById('header');
  const menuToggle = document.getElementById('menu-toggle');
  const navList = document.getElementById('nav-list');
  const overlay = document.getElementById('overlay');
  function toggleMenu(){ menuToggle.classList.toggle('active'); navList.classList.toggle('open'); overlay.classList.toggle('active'); document.body.style.overflow = navList.classList.contains('open')?'hidden':''; }
  menuToggle.addEventListener('click', toggleMenu);
  overlay.addEventListener('click', toggleMenu);
  navList.querySelectorAll('a').forEach(link=>link.addEventListener('click', ()=>{ if(navList.classList.contains('open')) toggleMenu(); }));
  window.addEventListener('scroll', ()=>{ header.classList.toggle('scrolled', window.scrollY>40); }, {passive:true});

  const revealObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
  }, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

  const form = document.getElementById('contact-form');
  const validators = {
    name: v => v.trim().length >= 2 || 'Please enter your name.',
    email: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Enter a valid email address.',
    message: v => v.trim().length >= 10 || 'Tell us a bit more about the project.'
  };
  function validateField(id){
    const field = document.getElementById(id);
    const errorEl = document.getElementById(`${id}-error`);
    const result = validators[id](field.value);
    if (result === true) { errorEl.textContent=''; return true; }
    errorEl.textContent = result; return false;
  }
  Object.keys(validators).forEach(id=>document.getElementById(id).addEventListener('blur', ()=>validateField(id)));
  form.addEventListener('submit', (e)=>{
    e.preventDefault();
    const allValid = Object.keys(validators).map(validateField).every(Boolean);
    const status = document.getElementById('form-status');
    if (!allValid) { status.textContent = 'Please fix the highlighted fields above.'; return; }
    const btn = form.querySelector('button[type=submit]');
    btn.disabled = true; btn.textContent = 'Sending...';
    setTimeout(()=>{ status.textContent = "Thank you — we'll follow up within two business days."; form.reset(); btn.disabled=false; btn.textContent='Send Inquiry'; }, 900);
  });
});
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/13_pet_grooming_boarding.md

# Example — Pet Grooming & Boarding (Tailwind Architecture)

Tags: example, full-site, pet-grooming, pet-boarding, pets, local-service, tailwind, light-theme, coral, cream, service-tiers, booking-widget

Niche: neighborhood pet grooming and boarding service.
Architecture: Tailwind CDN utility classes, light mode (an exception to the
dark-theme-heavy default in this corpus — proves Tailwind works fine for light too).
Palette: cream canvas (#FFF8F2), warm coral accent (#FF7E5F), soft and friendly.
Signature element: a service-tier comparison table plus a lightweight booking-request
widget (date + service-type selector) that produces a confirmation summary without a
real backend.
Sections: header, hero, service tiers, booking widget, gallery/testimonials, FAQ,
footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Waggle &amp; Co. | Pet Grooming &amp; Boarding</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#FFF8F2',light:'#FFFFFF',card:'#FFFFFF'}, ink:{DEFAULT:'#2E2A26',dim:'#7A7269'}, accent:{DEFAULT:'#FF7E5F',hover:'#FF9579',glow:'rgba(255,126,95,0.25)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], display:['Quicksand','sans-serif'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Quicksand:wght@500;600;700&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;background:#FFF8F2;color:#2E2A26;}
  .font-display{font-family:'Quicksand',sans-serif;}
  ::selection{background:rgba(255,126,95,0.25);}
  .hero-title{font-size:clamp(2.4rem,5.5vw,4.6rem);line-height:1.05;}
  .reveal{opacity:0;transform:translateY(26px);transition:all .65s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .tier-card.featured{box-shadow:0 20px 45px rgba(255,126,95,0.18);}
  .faq-content{max-height:0;overflow:hidden;transition:max-height .3s cubic-bezier(.16,1,.3,1);}
  .faq-item.open .faq-content{max-height:160px;}
  .faq-item.open .faq-chevron{transform:rotate(180deg);}
  .faq-chevron{transition:transform .3s ease;}
  input:focus,select:focus,button:focus-visible{outline:2px solid #FF7E5F;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500 bg-canvas/80 backdrop-blur-sm">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <a href="#" class="font-display text-xl font-bold flex items-center gap-2">🐾 Waggle &amp; Co.</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#services" class="text-sm text-ink-dim hover:text-ink font-medium">Services</a>
        <a href="#booking" class="text-sm text-ink-dim hover:text-ink font-medium">Book Now</a>
        <a href="#faq" class="text-sm text-ink-dim hover:text-ink font-medium">FAQ</a>
      </nav>
      <a href="#booking" class="bg-accent hover:bg-accent-hover text-white font-bold text-sm px-5 py-2.5 rounded-full transition-colors">Book a Visit</a>
    </div>
  </div>
</header>

<section class="relative min-h-[88vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 80% 20%, rgba(255,126,95,0.1) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10 grid lg:grid-cols-2 gap-16 items-center">
    <div class="space-y-7">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-accent/10">
        <span class="text-xs font-bold text-accent uppercase tracking-wide">🐶 5-Star Rated on Google</span>
      </div>
      <h1 class="hero-title font-display font-bold">
        Your dog's <span class="text-accent">second</span> favorite place.
      </h1>
      <p class="text-lg text-ink-dim max-w-md leading-relaxed">
        Grooming, daycare, and overnight boarding from a team that actually remembers
        your pet's name — and their favorite treat.
      </p>
      <div class="flex flex-col sm:flex-row gap-4">
        <a href="#booking" class="bg-accent hover:bg-accent-hover text-white font-bold px-8 py-4 rounded-xl transition-all hover:-translate-y-0.5">Book a Visit</a>
        <a href="#services" class="border border-ink/15 hover:border-ink/30 font-semibold px-8 py-4 rounded-xl transition-all hover:bg-white">See Services</a>
      </div>
    </div>
    <div class="relative hidden lg:flex items-center justify-center">
      <div class="w-full max-w-md aspect-square rounded-3xl bg-white border border-ink/5 shadow-xl flex items-center justify-center text-8xl">🐕</div>
    </div>
  </div>
</section>

<section id="services" class="py-24 lg:py-32 bg-white border-t border-ink/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs font-bold uppercase tracking-[0.2em] mb-3">Our Services</p>
      <h2 class="font-display text-3xl lg:text-4xl font-bold">Pick what your pet needs</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="tier-card reveal bg-canvas rounded-2xl p-8 border border-ink/5">
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2 font-semibold">Grooming</p>
        <p class="font-display text-4xl font-bold mb-4">$45+</p>
        <ul class="space-y-2 text-sm text-ink-dim mb-6"><li>Bath &amp; brush-out</li><li>Nail trim &amp; ear cleaning</li><li>Breed-specific cut</li></ul>
        <a href="#booking" class="block text-center border border-ink/15 hover:border-accent hover:text-accent font-bold py-3 rounded-xl transition-all">Book Grooming</a>
      </div>
      <div class="tier-card featured reveal bg-canvas rounded-2xl p-8 border-2 border-accent relative">
        <span class="absolute -top-3 left-8 bg-accent text-white text-xs font-bold px-3 py-1 rounded-full">Most Booked</span>
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2 font-semibold">Daycare</p>
        <p class="font-display text-4xl font-bold mb-4">$38<span class="text-base text-ink-dim">/day</span></p>
        <ul class="space-y-2 text-sm text-ink-dim mb-6"><li>Supervised play groups</li><li>Indoor &amp; outdoor space</li><li>Webcam access</li></ul>
        <a href="#booking" class="block text-center bg-accent hover:bg-accent-hover text-white font-bold py-3 rounded-xl transition-all">Book Daycare</a>
      </div>
      <div class="tier-card reveal bg-canvas rounded-2xl p-8 border border-ink/5">
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2 font-semibold">Boarding</p>
        <p class="font-display text-4xl font-bold mb-4">$65<span class="text-base text-ink-dim">/night</span></p>
        <ul class="space-y-2 text-sm text-ink-dim mb-6"><li>Private suite</li><li>Daily walks &amp; playtime</li><li>Nightly photo update</li></ul>
        <a href="#booking" class="block text-center border border-ink/15 hover:border-accent hover:text-accent font-bold py-3 rounded-xl transition-all">Book Boarding</a>
      </div>
    </div>
  </div>
</section>

<section id="booking" class="py-24 lg:py-32">
  <div class="max-w-2xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-12 reveal">
      <p class="text-accent text-xs font-bold uppercase tracking-[0.2em] mb-3">Request a Booking</p>
      <h2 class="font-display text-3xl lg:text-4xl font-bold">Let's get something on the calendar</h2>
    </div>
    <div class="reveal bg-white rounded-2xl p-8 border border-ink/5 shadow-lg">
      <div class="space-y-5 mb-6">
        <div>
          <label class="block text-sm font-semibold mb-2">Service</label>
          <select id="service-select" class="w-full border border-ink/15 rounded-xl px-4 py-3 text-sm">
            <option value="Grooming">Grooming — from $45</option>
            <option value="Daycare">Daycare — $38/day</option>
            <option value="Boarding">Boarding — $65/night</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-semibold mb-2">Preferred Date</label>
          <input type="date" id="date-input" class="w-full border border-ink/15 rounded-xl px-4 py-3 text-sm">
        </div>
        <div>
          <label class="block text-sm font-semibold mb-2">Pet's Name</label>
          <input type="text" id="pet-name" placeholder="e.g. Biscuit" class="w-full border border-ink/15 rounded-xl px-4 py-3 text-sm">
        </div>
      </div>
      <button id="booking-submit" class="w-full bg-accent hover:bg-accent-hover text-white font-bold py-4 rounded-xl transition-all">Request Booking</button>
      <div id="booking-confirmation" class="hidden mt-5 bg-accent/10 border border-accent/30 rounded-xl p-4 text-sm">
        <p class="font-semibold mb-1">Request received! 🎉</p>
        <p class="text-ink-dim" id="confirmation-text"></p>
      </div>
    </div>
  </div>
</section>

<section class="py-20 bg-white border-t border-ink/5">
  <div class="max-w-3xl mx-auto px-6 text-center reveal">
    <p class="text-2xl font-medium text-ink/85 leading-relaxed mb-6">"They send a photo update every single night my dog boards. It's the little things — I never worry when she's there."</p>
    <p class="text-sm text-ink-dim">Priya M. &amp; Biscuit (Golden Retriever)</p>
  </div>
</section>

<section id="faq" class="py-24 lg:py-32">
  <div class="max-w-2xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-12 reveal"><h2 class="font-display text-3xl font-bold">Common questions</h2></div>
    <div class="space-y-3">
      <div class="faq-item reveal bg-white border border-ink/5 rounded-xl">
        <button class="faq-trigger w-full flex items-center justify-between p-5 text-left font-semibold"><span>Do you require vaccination records?</span><span class="faq-chevron">▾</span></button>
        <div class="faq-content px-5"><p class="text-sm text-ink-dim pb-5">Yes — current rabies, DHPP, and bordetella records are required before any stay.</p></div>
      </div>
      <div class="faq-item reveal bg-white border border-ink/5 rounded-xl">
        <button class="faq-trigger w-full flex items-center justify-between p-5 text-left font-semibold"><span>Can I tour the facility first?</span><span class="faq-chevron">▾</span></button>
        <div class="faq-content px-5"><p class="text-sm text-ink-dim pb-5">Absolutely — drop by anytime during business hours, no appointment needed.</p></div>
      </div>
      <div class="faq-item reveal bg-white border border-ink/5 rounded-xl">
        <button class="faq-trigger w-full flex items-center justify-between p-5 text-left font-semibold"><span>What breeds do you groom?</span><span class="faq-chevron">▾</span></button>
        <div class="faq-content px-5"><p class="text-sm text-ink-dim pb-5">All breeds and sizes, including breed-specific cuts for show standards.</p></div>
      </div>
    </div>
  </div>
</section>

<footer class="border-t border-ink/5 py-12 bg-white">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-ink-dim">
    <p>© 2026 Waggle &amp; Co.</p>
    <div class="flex gap-6"><a href="#" class="hover:text-ink">Vaccination Policy</a><a href="#" class="hover:text-ink">Contact</a></div>
  </div>
</footer>

<script>
document.getElementById('booking-submit').addEventListener('click', ()=>{
  const service = document.getElementById('service-select').value;
  const date = document.getElementById('date-input').value;
  const pet = document.getElementById('pet-name').value || 'your pet';
  const confirmation = document.getElementById('booking-confirmation');
  const text = document.getElementById('confirmation-text');
  if (!date) {
    text.textContent = 'Please select a preferred date before submitting.';
    confirmation.classList.remove('hidden');
    confirmation.classList.replace('bg-accent/10','bg-red-50');
    return;
  }
  confirmation.classList.replace('bg-red-50','bg-accent/10');
  const formattedDate = new Date(date + 'T00:00:00').toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric' });
  text.textContent = `We'll text you to confirm ${service} for ${pet} on ${formattedDate}.`;
  confirmation.classList.remove('hidden');
});

document.querySelectorAll('.faq-trigger').forEach(trigger=>{
  trigger.addEventListener('click', ()=>trigger.closest('.faq-item').classList.toggle('open'));
});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/14_vinyl_record_shop.md

# Example — Vinyl Record Shop (Vanilla CSS Architecture)

Tags: example, full-site, vinyl, records, music, retro, vanilla-css, dark-theme, mustard-yellow, black, retro-typography, genre-wheel, ecommerce

Niche: independent vinyl record shop, new and used.
Architecture: vanilla CSS, custom properties.
Palette: matte black canvas (#121212), mustard yellow accent (#E8B339), warm orange
secondary (#D9622B) — retro 70s print aesthetic, bold condensed display type.
Signature element: a spinning genre wheel — a circular nav where each genre sits on a
rotating dial; clicking a segment spins the wheel to center it and filters the crate
below.
Sections: header, hero, genre wheel + crate grid with cart, new arrivals strip, about,
footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Static &amp; Soul Records | New &amp; Used Vinyl</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Karla:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --black:#121212; --black-light:#1B1B1B; --black-card:#222222; --line:#333333;
  --cream:#F2EADF; --cream-dim:#A8A096; --mustard:#E8B339; --mustard-hover:#F0C457; --orange:#D9622B;
  --radius:6px; --radius-lg:12px;
  --transition: all 0.3s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow-lg: 0 20px 50px rgba(0,0,0,0.5);
  --display:'Anton', sans-serif; --sans:'Karla', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--black);color:var(--cream);line-height:1.65;overflow-x:hidden;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;} button{cursor:pointer;font-family:inherit;}
.container{max-width:1180px;margin:0 auto;padding:0 2rem;}
.section{padding:6rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.78rem;color:var(--mustard);margin-bottom:1rem;font-weight:700;}
.section-title{font-family:var(--display);font-size:2.6rem;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:1rem;}
.section-subtitle{color:var(--cream-dim);font-size:1rem;max-width:540px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.9rem 2rem;border:none;border-radius:var(--radius);font-size:0.85rem;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;transition:var(--transition);}
.btn-primary{background:var(--mustard);color:var(--black);}
.btn-primary:hover{background:var(--mustard-hover);transform:translateY(-2px);box-shadow:0 10px 22px rgba(232,179,57,0.25);}
.btn-outline{background:transparent;color:var(--cream);border:1.5px solid var(--line);}
.btn-outline:hover{border-color:var(--mustard);color:var(--mustard);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.3rem 0;transition:var(--transition);}
.header.scrolled{background:rgba(18,18,18,0.95);backdrop-filter:blur(14px);padding:0.9rem 0;box-shadow:0 2px 24px rgba(0,0,0,0.4);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--display);font-size:1.3rem;text-transform:uppercase;letter-spacing:0.5px;}
.logo span{color:var(--mustard);}
.nav-list{display:flex;list-style:none;gap:2.2rem;align-items:center;}
.nav-list a{font-size:0.84rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;}
.nav-list a:hover{color:var(--mustard);}
.cart-btn{position:relative;background:none;border:none;font-size:1.2rem;}
.cart-badge{position:absolute;top:-4px;right:-6px;background:var(--orange);color:#fff;font-size:0.62rem;font-weight:700;width:17px;height:17px;border-radius:50%;display:flex;align-items:center;justify-content:center;}
.cart-badge.hidden{display:none;}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:22px;height:2px;background:var(--cream);transition:var(--transition);}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:84vh;display:flex;align-items:center;padding-top:6rem;background:radial-gradient(ellipse at 75% 30%, rgba(232,179,57,0.08), transparent 55%);}
.hero-title{font-family:var(--display);font-size:4.2rem;text-transform:uppercase;line-height:1.05;letter-spacing:0.5px;margin-bottom:1.4rem;max-width:760px;}
.hero-title span{color:var(--mustard);}
.hero-desc{font-size:1.05rem;color:var(--cream-dim);max-width:460px;margin-bottom:2rem;}

.wheel-section{display:flex;justify-content:center;margin:3rem 0;}
.genre-wheel{position:relative;width:280px;height:280px;border-radius:50%;background:var(--black-card);border:3px solid var(--line);transition:transform 0.8s cubic-bezier(0.16,1,0.3,1);}
.wheel-segment{position:absolute;width:50%;height:50%;display:flex;align-items:flex-start;justify-content:center;padding-top:1.2rem;cursor:pointer;font-family:var(--display);font-size:0.85rem;text-transform:uppercase;color:var(--cream-dim);transition:color 0.3s ease;}
.wheel-segment:hover,.wheel-segment.active{color:var(--mustard);}
.wheel-center{position:absolute;top:50%;left:50%;width:70px;height:70px;background:var(--mustard);border-radius:50%;transform:translate(-50%,-50%);display:flex;align-items:center;justify-content:center;font-size:1.8rem;box-shadow:0 0 0 6px var(--black),0 0 0 9px var(--line);}

.crate-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1.4rem;margin-top:1rem;}
.record-card{background:var(--black-card);border-radius:var(--radius-lg);overflow:hidden;border:1px solid var(--line);transition:var(--transition);}
.record-card:hover{transform:translateY(-5px);box-shadow:var(--shadow-lg);}
.record-cover{aspect-ratio:1;background:linear-gradient(150deg,var(--orange),#8C3D1A);display:flex;align-items:center;justify-content:center;font-size:2.5rem;position:relative;}
.record-info{padding:1.2rem;}
.record-artist{font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:var(--mustard);margin-bottom:0.3rem;font-weight:700;}
.record-title{font-family:var(--display);font-size:1.05rem;margin-bottom:0.6rem;text-transform:uppercase;}
.record-footer{display:flex;align-items:center;justify-content:space-between;}
.record-price{font-weight:700;}
.add-btn{background:var(--black);border:1px solid var(--line);color:var(--cream);font-size:0.74rem;font-weight:700;padding:0.45rem 0.8rem;border-radius:6px;transition:var(--transition);text-transform:uppercase;}
.add-btn:hover{background:var(--mustard);color:var(--black);border-color:var(--mustard);}

.arrivals-strip{display:flex;gap:1.2rem;overflow-x:auto;margin-top:2.5rem;padding-bottom:0.5rem;}
.arrival-card{min-width:160px;flex-shrink:0;}
.arrival-cover{aspect-ratio:1;border-radius:var(--radius);background:linear-gradient(150deg,var(--mustard),#A87B1F);display:flex;align-items:center;justify-content:center;font-size:2rem;margin-bottom:0.7rem;}
.arrival-name{font-size:0.85rem;font-weight:700;}

.about-grid{display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center;}
.about-visual{aspect-ratio:4/3;border-radius:var(--radius-lg);background:linear-gradient(150deg,var(--black-card),var(--black-light));border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:4rem;}
.about-text p{color:var(--cream-dim);margin-bottom:1.1rem;}

.footer{border-top:1px solid var(--line);padding:3rem 0;display:flex;justify-content:space-between;align-items:center;font-size:0.82rem;color:var(--cream-dim);}

.cart-drawer{position:fixed;top:0;right:0;height:100%;width:400px;background:var(--black-light);z-index:1100;transform:translateX(100%);transition:transform 0.35s cubic-bezier(0.16,1,0.3,1);display:flex;flex-direction:column;border-left:1px solid var(--line);}
.cart-drawer.open{transform:translateX(0);}
.cart-header{display:flex;justify-content:space-between;align-items:center;padding:1.5rem;border-bottom:1px solid var(--line);}
.cart-close{background:var(--black-card);border:none;width:30px;height:30px;border-radius:50%;color:var(--cream);font-size:1.1rem;}
.cart-items{flex:1;overflow-y:auto;padding:1.5rem;}
.cart-empty{display:flex;align-items:center;justify-content:center;height:100%;color:var(--cream-dim);text-align:center;}
.cart-row{display:flex;gap:1rem;padding-bottom:1.1rem;margin-bottom:1.1rem;border-bottom:1px solid var(--line);}
.qty-btn{width:22px;height:22px;border-radius:6px;border:1px solid var(--line);background:var(--black-card);color:var(--cream);}
.cart-footer{padding:1.5rem;border-top:1px solid var(--line);}
.cart-total-row{display:flex;justify-content:space-between;margin-bottom:0.9rem;font-weight:700;}
.cart-backdrop{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:1050;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.cart-backdrop.active{opacity:1;pointer-events:auto;}

.reveal{opacity:0;transform:translateY(26px);transition:all 0.65s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .crate-grid{grid-template-columns:repeat(2,1fr);}
  .about-grid{grid-template-columns:1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--black);flex-direction:column;justify-content:center;gap:2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.8rem;}
  .cart-drawer{width:100%;}
}
@media (max-width:600px){ .crate-grid{grid-template-columns:1fr;} .footer{flex-direction:column;gap:0.8rem;text-align:center;} .genre-wheel{width:220px;height:220px;} }
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Static <span>&amp;</span> Soul</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero">Home</a></li>
      <li><a href="#crate">The Crate</a></li>
      <li><a href="#about">About</a></li>
    </ul></nav>
    <div style="display:flex;align-items:center;gap:0.6rem;">
      <button class="cart-btn" id="cart-btn" aria-label="Open cart">🎧<span class="cart-badge hidden" id="cart-badge">0</span></button>
      <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <span class="section-label">New &amp; Used, Curated by Ear</span>
    <h1 class="hero-title">Dig the crate.<br>Find the <span>one.</span></h1>
    <p class="hero-desc">Three thousand records, hand-graded, and a turntable up front so you never buy a record sight-unheard.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;">
      <a href="#crate" class="btn btn-primary">Browse the Crate</a>
      <a href="#about" class="btn btn-outline">Our Story</a>
    </div>
  </div>
</section>

<section class="section" id="crate">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Spin the Wheel</span>
      <h2 class="section-title">Pick a genre</h2>
      <p class="section-subtitle">Click a slice to filter the crate below.</p>
    </div>
    <div class="wheel-section">
      <div class="genre-wheel" id="genre-wheel">
        <div class="wheel-segment active" data-genre="all" style="top:0;left:0;text-align:center;">ALL</div>
        <div class="wheel-segment" data-genre="soul" style="top:0;left:50%;text-align:center;">SOUL</div>
        <div class="wheel-segment" data-genre="jazz" style="top:50%;left:0;text-align:center;align-items:flex-end;padding-top:0;padding-bottom:1.2rem;">JAZZ</div>
        <div class="wheel-segment" data-genre="rock" style="top:50%;left:50%;text-align:center;align-items:flex-end;padding-top:0;padding-bottom:1.2rem;">ROCK</div>
        <div class="wheel-center">🎵</div>
      </div>
    </div>
    <div class="crate-grid" id="crate-grid"></div>
  </div>
</section>

<section class="section" style="background:var(--black-light);">
  <div class="container">
    <div class="reveal"><span class="section-label">Just In</span><h2 class="section-title">New arrivals</h2></div>
    <div class="arrivals-strip">
      <div class="arrival-card"><div class="arrival-cover">💿</div><p class="arrival-name">Midnight Sessions</p></div>
      <div class="arrival-card"><div class="arrival-cover">💿</div><p class="arrival-name">Coastline (Reissue)</p></div>
      <div class="arrival-card"><div class="arrival-cover">💿</div><p class="arrival-name">Brass &amp; Bone</p></div>
      <div class="arrival-card"><div class="arrival-cover">💿</div><p class="arrival-name">Static Bloom</p></div>
    </div>
  </div>
</section>

<section class="section" id="about">
  <div class="container">
    <div class="about-grid">
      <div class="about-visual reveal">📻</div>
      <div class="about-text reveal">
        <span class="section-label">Our Story</span>
        <h2 class="section-title">Twelve years, one block</h2>
        <p>Static &amp; Soul opened in 2014 in the same 800 square feet we're still in today. We grade every used record by ear before it hits the floor, and the listening station up front isn't a gimmick — we want you to hear it before you buy it.</p>
      </div>
    </div>
  </div>
</section>

<footer class="container footer">
  <p>© 2026 Static &amp; Soul Records</p>
  <p>Open Tue–Sun, Noon–8PM</p>
</footer>

<div class="cart-drawer" id="cart-drawer">
  <div class="cart-header"><h3 style="font-family:var(--display);text-transform:uppercase;">Crate</h3><button class="cart-close" id="cart-close" aria-label="Close cart">&times;</button></div>
  <div class="cart-items" id="cart-items"><div class="cart-empty" id="cart-empty"><p>Your crate is empty.</p></div></div>
  <div class="cart-footer" id="cart-footer" style="display:none;">
    <div class="cart-total-row"><span>Total</span><span id="cart-total">$0.00</span></div>
    <button class="btn btn-primary" style="width:100%;justify-content:center;">Checkout</button>
  </div>
</div>
<div class="cart-backdrop" id="cart-backdrop"></div>

<script>
document.addEventListener('DOMContentLoaded', function(){
  const records = [
    { id:1, artist:'Etta Jameson', title:'Velvet Hours', genre:'soul', price:28, icon:'💿' },
    { id:2, artist:'The Hollow Keys', title:'Brass & Bone', genre:'jazz', price:32, icon:'💿' },
    { id:3, artist:'Crater', title:'Static Bloom', genre:'rock', price:24, icon:'💿' },
    { id:4, artist:'Marvin Onyx', title:'Coastline', genre:'soul', price:30, icon:'💿' },
    { id:5, artist:'Lola Vance Trio', title:'Midnight Sessions', genre:'jazz', price:26, icon:'💿' },
    { id:6, artist:'Granite Choir', title:'Open Road', genre:'rock', price:22, icon:'💿' },
    { id:7, artist:'Dune Static', title:'Lo-Fi Pressings Vol. 2', genre:'jazz', price:29, icon:'💿' },
    { id:8, artist:'Reverie', title:'Gold Light', genre:'soul', price:27, icon:'💿' },
  ];
  let cart = [];
  let activeGenre = 'all';
  function escapeHtml(str){ const d=document.createElement('div'); d.textContent=str; return d.innerHTML; }

  function renderCrate(){
    const grid = document.getElementById('crate-grid');
    grid.innerHTML = '';
    const filtered = activeGenre === 'all' ? records : records.filter(r=>r.genre===activeGenre);
    filtered.forEach((r,i)=>{
      const card = document.createElement('div');
      card.className = 'record-card reveal';
      card.style.transitionDelay = (i*50)+'ms';
      card.innerHTML = `
        <div class="record-cover">${r.icon}</div>
        <div class="record-info">
          <p class="record-artist">${escapeHtml(r.artist)}</p>
          <h3 class="record-title">${escapeHtml(r.title)}</h3>
          <div class="record-footer">
            <span class="record-price">$${r.price.toFixed(2)}</span>
            <button class="add-btn" data-id="${r.id}">Add</button>
          </div>
        </div>
      `;
      grid.appendChild(card);
      revealObserver.observe(card);
    });
    grid.querySelectorAll('.add-btn').forEach(btn=>btn.addEventListener('click', ()=>addToCart(parseInt(btn.dataset.id))));
  }

  document.querySelectorAll('.wheel-segment').forEach(seg=>{
    seg.addEventListener('click', ()=>{
      document.querySelectorAll('.wheel-segment').forEach(s=>s.classList.remove('active'));
      seg.classList.add('active');
      activeGenre = seg.dataset.genre;
      const rotations = { all:0, soul:-90, jazz:180, rock:90 };
      document.getElementById('genre-wheel').style.transform = `rotate(${rotations[activeGenre]}deg)`;
      document.querySelectorAll('.wheel-segment').forEach(s=>{ s.style.transform = `rotate(${-rotations[activeGenre]}deg)`; });
      renderCrate();
    });
  });

  function addToCart(id){
    const record = records.find(r=>r.id===id);
    const existing = cart.find(i=>i.id===id);
    if (existing) existing.qty+=1; else cart.push({...record, qty:1});
    renderCart(); updateBadge();
  }
  function updateQty(id,delta){ const item=cart.find(i=>i.id===id); if(!item) return; item.qty=Math.max(1,item.qty+delta); renderCart(); updateBadge(); }
  function cartTotal(){ return cart.reduce((s,i)=>s+i.price*i.qty,0); }
  function cartCount(){ return cart.reduce((s,i)=>s+i.qty,0); }

  function renderCart(){
    const container = document.getElementById('cart-items');
    const footer = document.getElementById('cart-footer');
    const empty = document.getElementById('cart-empty');
    container.querySelectorAll('.cart-row').forEach(el=>el.remove());
    if (cart.length===0){ empty.style.display='flex'; footer.style.display='none'; return; }
    empty.style.display='none'; footer.style.display='block';
    cart.forEach(item=>{
      const row = document.createElement('div');
      row.className='cart-row';
      row.innerHTML = `
        <div style="flex:1;"><p style="font-weight:700;font-size:0.9rem;">${escapeHtml(item.title)}</p>
        <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.45rem;">
          <button class="qty-btn" data-id="${item.id}" data-delta="-1">−</button>
          <span style="font-size:0.88rem;width:1rem;text-align:center;">${item.qty}</span>
          <button class="qty-btn" data-id="${item.id}" data-delta="1">+</button>
        </div></div>
        <p style="font-weight:700;font-size:0.9rem;">$${(item.price*item.qty).toFixed(2)}</p>
      `;
      container.appendChild(row);
    });
    document.getElementById('cart-total').textContent = `$${cartTotal().toFixed(2)}`;
    container.querySelectorAll('.qty-btn').forEach(btn=>btn.addEventListener('click', ()=>updateQty(parseInt(btn.dataset.id), parseInt(btn.dataset.delta))));
  }
  function updateBadge(){ const badge=document.getElementById('cart-badge'); const count=cartCount(); badge.textContent=count; badge.classList.toggle('hidden', count===0); }

  const cartDrawer = document.getElementById('cart-drawer');
  const cartBackdrop = document.getElementById('cart-backdrop');
  document.getElementById('cart-btn').addEventListener('click', ()=>{ cartDrawer.classList.add('open'); cartBackdrop.classList.add('active'); document.body.style.overflow='hidden'; });
  function closeCart(){ cartDrawer.classList.remove('open'); cartBackdrop.classList.remove('active'); document.body.style.overflow=''; }
  document.getElementById('cart-close').addEventListener('click', closeCart);
  cartBackdrop.addEventListener('click', closeCart);
  document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeCart(); });

  const header = document.getElementById('header');
  const menuToggle = document.getElementById('menu-toggle');
  const navList = document.getElementById('nav-list');
  const overlay = document.getElementById('overlay');
  function toggleMenu(){ menuToggle.classList.toggle('active'); navList.classList.toggle('open'); overlay.classList.toggle('active'); document.body.style.overflow = navList.classList.contains('open')?'hidden':''; }
  menuToggle.addEventListener('click', toggleMenu);
  overlay.addEventListener('click', toggleMenu);
  navList.querySelectorAll('a').forEach(link=>link.addEventListener('click', ()=>{ if(navList.classList.contains('open')) toggleMenu(); }));
  window.addEventListener('scroll', ()=>{ header.classList.toggle('scrolled', window.scrollY>40); }, {passive:true});

  const revealObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
  }, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

  renderCrate();
});
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/15_yoga_wellness_studio.md

# Example — Yoga & Wellness Studio (Tailwind Architecture, Light/Airy)

Tags: example, full-site, yoga, wellness, studio, fitness, tailwind, light-theme, sand, dusty-rose, airy, class-schedule, calm

Niche: boutique yoga and wellness studio.
Architecture: Tailwind CDN utility classes, light/airy mode — demonstrates that
Tailwind isn't only for dark, dense, glassy designs; restraint and whitespace work
just as well as a utility-class strategy.
Palette: warm sand canvas (#FAF6F1), dusty rose accent (#C98B82), generous whitespace,
thin weights, slow gentle motion only.
Signature element: a weekly class-schedule grid (days × time slots) that highlights
the current day and lets you filter by class type.
Sections: header, hero, class-type filter + weekly schedule grid, instructor intro,
membership, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Still Water Yoga | Studio &amp; Wellness Classes</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#FAF6F1',light:'#FFFFFF',card:'#FFFFFF'}, ink:{DEFAULT:'#332B28',dim:'#8C7F77'}, accent:{DEFAULT:'#C98B82',hover:'#D6A097',glow:'rgba(201,139,130,0.2)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], display:['Cormorant Garamond','serif'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Cormorant+Garamond:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;background:#FAF6F1;color:#332B28;font-weight:300;}
  .font-display{font-family:'Cormorant Garamond',serif;}
  ::selection{background:rgba(201,139,130,0.2);}
  .hero-title{font-size:clamp(2.4rem,5.5vw,4.4rem);line-height:1.1;letter-spacing:-0.01em;}
  .reveal{opacity:0;transform:translateY(20px);transition:all .8s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .schedule-cell.hidden-by-filter{opacity:0.15;}
  input:focus,select:focus,button:focus-visible{outline:2px solid #C98B82;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500 bg-canvas/85 backdrop-blur-sm">
  <div class="max-w-6xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <a href="#" class="font-display text-2xl">Still Water</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#schedule" class="text-sm text-ink-dim hover:text-ink">Schedule</a>
        <a href="#instructors" class="text-sm text-ink-dim hover:text-ink">Instructors</a>
        <a href="#membership" class="text-sm text-ink-dim hover:text-ink">Membership</a>
      </nav>
      <a href="#membership" class="border border-accent text-accent hover:bg-accent hover:text-white text-sm px-5 py-2.5 rounded-full transition-colors">Try a Free Class</a>
    </div>
  </div>
</header>

<section class="relative min-h-[86vh] flex items-center pt-24">
  <div class="max-w-6xl mx-auto px-6 lg:px-8 grid lg:grid-cols-2 gap-16 items-center">
    <div class="space-y-7">
      <p class="text-accent text-xs uppercase tracking-[0.2em]">A Quiet Studio in the City</p>
      <h1 class="hero-title font-display">
        Slow down.<br>Breathe deeper.
      </h1>
      <p class="text-lg text-ink-dim max-w-md leading-relaxed">
        Twelve weekly classes across vinyasa, restorative, and sound bath — taught
        by instructors who studied for years before they ever taught a single class.
      </p>
      <div class="flex flex-col sm:flex-row gap-4">
        <a href="#schedule" class="bg-accent hover:bg-accent-hover text-white font-medium px-8 py-4 rounded-full transition-all">View Class Schedule</a>
        <a href="#membership" class="border border-ink/15 hover:border-ink/30 font-medium px-8 py-4 rounded-full transition-all">See Membership</a>
      </div>
    </div>
    <div class="relative hidden lg:flex items-center justify-center">
      <div class="w-full max-w-sm aspect-[3/4] rounded-3xl bg-gradient-to-br from-accent/10 to-canvas-light border border-ink/5 flex items-center justify-center text-7xl">🧘</div>
    </div>
  </div>
</section>

<section id="schedule" class="py-24 lg:py-32 bg-white border-t border-ink/5">
  <div class="max-w-6xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-12 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">This Week</p>
      <h2 class="font-display text-3xl lg:text-4xl">Class schedule</h2>
    </div>
    <div class="flex justify-center gap-3 mb-10 flex-wrap" id="class-filters">
      <button class="filter-chip active px-5 py-2 rounded-full border border-accent bg-accent text-white text-sm font-medium" data-type="all">All Classes</button>
      <button class="filter-chip px-5 py-2 rounded-full border border-ink/15 text-sm font-medium" data-type="Vinyasa">Vinyasa</button>
      <button class="filter-chip px-5 py-2 rounded-full border border-ink/15 text-sm font-medium" data-type="Restorative">Restorative</button>
      <button class="filter-chip px-5 py-2 rounded-full border border-ink/15 text-sm font-medium" data-type="Sound Bath">Sound Bath</button>
    </div>
    <div class="overflow-x-auto">
      <div id="schedule-grid" class="grid gap-2" style="grid-template-columns: 100px repeat(7, minmax(110px,1fr)); min-width:880px;"></div>
    </div>
  </div>
</section>

<section id="instructors" class="py-24 lg:py-32">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Meet the Team</p>
      <h2 class="font-display text-3xl lg:text-4xl">Our instructors</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-10 text-center">
      <div class="reveal"><div class="w-28 h-28 mx-auto rounded-full bg-accent/10 flex items-center justify-center text-3xl mb-4">🌿</div><h3 class="font-display text-xl mb-1">Anaya Patel</h3><p class="text-sm text-ink-dim">Vinyasa &amp; Restorative, 11 years teaching</p></div>
      <div class="reveal" style="transition-delay:.1s"><div class="w-28 h-28 mx-auto rounded-full bg-accent/10 flex items-center justify-center text-3xl mb-4">🌙</div><h3 class="font-display text-xl mb-1">Noah Bergström</h3><p class="text-sm text-ink-dim">Sound Bath &amp; Meditation, trained in Bali</p></div>
      <div class="reveal" style="transition-delay:.2s"><div class="w-28 h-28 mx-auto rounded-full bg-accent/10 flex items-center justify-center text-3xl mb-4">🌸</div><h3 class="font-display text-xl mb-1">Wren Okafor</h3><p class="text-sm text-ink-dim">Restorative &amp; Prenatal Yoga</p></div>
    </div>
  </div>
</section>

<section id="membership" class="py-24 lg:py-32 bg-white border-t border-ink/5">
  <div class="max-w-4xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Membership</p>
      <h2 class="font-display text-3xl lg:text-4xl">Find your rhythm</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="reveal text-center border border-ink/10 rounded-2xl p-8">
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2">Drop-In</p>
        <p class="font-display text-3xl mb-4">$28</p>
        <p class="text-sm text-ink-dim">Single class, any style</p>
      </div>
      <div class="reveal text-center border-2 border-accent rounded-2xl p-8 relative">
        <span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-accent text-white text-xs px-3 py-1 rounded-full">Most Popular</span>
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2">Unlimited</p>
        <p class="font-display text-3xl mb-4">$149<span class="text-base text-ink-dim">/mo</span></p>
        <p class="text-sm text-ink-dim">Every class, every week</p>
      </div>
      <div class="reveal text-center border border-ink/10 rounded-2xl p-8">
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2">10-Class Pack</p>
        <p class="font-display text-3xl mb-4">$220</p>
        <p class="text-sm text-ink-dim">Never expires</p>
      </div>
    </div>
  </div>
</section>

<footer class="py-12 border-t border-ink/5">
  <div class="max-w-6xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-ink-dim">
    <p>© 2026 Still Water Yoga</p>
    <div class="flex gap-6"><a href="#" class="hover:text-ink">Studio Etiquette</a><a href="#" class="hover:text-ink">Contact</a></div>
  </div>
</footer>

<script>
const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
const todayIndex = (new Date().getDay() + 6) % 7; // Mon=0
const schedule = {
  '7:00 AM':  ['Vinyasa','','Restorative','','Vinyasa','',''],
  '9:00 AM':  ['','Sound Bath','','Sound Bath','','Vinyasa',''],
  '12:00 PM': ['Restorative','Vinyasa','','Vinyasa','Restorative','',''],
  '5:30 PM':  ['Vinyasa','','Vinyasa','','','','Restorative'],
  '7:00 PM':  ['','Restorative','Sound Bath','','Vinyasa','',''],
};
let activeType = 'all';

function renderSchedule(){
  const grid = document.getElementById('schedule-grid');
  grid.innerHTML = '';
  grid.innerHTML += `<div></div>`;
  days.forEach((d,i)=>{
    grid.innerHTML += `<div class="text-center text-xs font-semibold uppercase tracking-wide py-2 ${i===todayIndex ? 'text-accent' : 'text-ink-dim'}">${d}</div>`;
  });
  Object.entries(schedule).forEach(([time, classes])=>{
    grid.innerHTML += `<div class="text-xs text-ink-dim flex items-center pr-2">${time}</div>`;
    classes.forEach((cls,i)=>{
      const isToday = i===todayIndex;
      const cell = document.createElement('div');
      cell.className = `schedule-cell rounded-lg p-2 text-center text-xs min-h-[44px] flex items-center justify-center ${cls ? 'bg-accent/10 text-accent font-medium' : 'bg-ink/[0.02] text-ink-dim/30'} ${isToday ? 'ring-1 ring-accent/40' : ''}`;
      cell.textContent = cls || '—';
      if (cls) cell.dataset.type = cls;
      grid.appendChild(cell);
    });
  });
  applyFilter();
}
function applyFilter(){
  document.querySelectorAll('.schedule-cell').forEach(cell=>{
    if (!cell.dataset.type) return;
    cell.classList.toggle('hidden-by-filter', activeType !== 'all' && cell.dataset.type !== activeType);
  });
}
document.querySelectorAll('.filter-chip').forEach(chip=>{
  chip.addEventListener('click', ()=>{
    document.querySelectorAll('.filter-chip').forEach(c=>{ c.classList.remove('active','bg-accent','text-white','border-accent'); c.classList.add('border-ink/15'); });
    chip.classList.add('active','bg-accent','text-white','border-accent');
    chip.classList.remove('border-ink/15');
    activeType = chip.dataset.type;
    applyFilter();
  });
});

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  header.style.boxShadow = window.scrollY > 40 ? '0 2px 20px rgba(51,43,40,0.06)' : 'none';
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

renderSchedule();
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/16_artisan_knife_maker.md

# Example — Artisan Knife & Cutlery Maker (Vanilla CSS Architecture)

Tags: example, full-site, knives, cutlery, blacksmith, artisan, vanilla-css, dark-theme, steel-gray, deep-red, forging-process, ecommerce, craftsmanship

Niche: hand-forged kitchen and outdoor knife maker.
Architecture: vanilla CSS, custom properties.
Palette: steel gray canvas (#1C1C1E), deep red/ember accent (#B83A2E), industrial and
serious.
Signature element: a vertical forging-process timeline with a glowing "ember" dot
that travels down the line as the user scrolls, using scroll-position-based fill.
Sections: header, hero, forging timeline, knife collection grid with cart, materials
philosophy, care guide, footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ashforge Cutlery | Hand-Forged Kitchen Knives</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Karla:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --steel:#1C1C1E; --steel-light:#262628; --steel-card:#2E2E30; --line:#3D3D40;
  --silver:#E8E6E1; --silver-dim:#9C9A96; --ember:#B83A2E; --ember-hover:#CC4836; --ember-glow:rgba(184,58,46,0.4);
  --radius:6px; --radius-lg:12px;
  --transition: all 0.3s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow-lg: 0 20px 50px rgba(0,0,0,0.5);
  --display:'Oswald', sans-serif; --sans:'Karla', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--steel);color:var(--silver);line-height:1.65;overflow-x:hidden;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;} button{cursor:pointer;font-family:inherit;}
.container{max-width:1180px;margin:0 auto;padding:0 2rem;}
.section{padding:6rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.76rem;color:var(--ember);margin-bottom:1rem;font-weight:600;}
.section-title{font-family:var(--display);font-size:2.5rem;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:1rem;font-weight:600;}
.section-subtitle{color:var(--silver-dim);font-size:1rem;max-width:540px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.9rem 2.1rem;border:none;border-radius:var(--radius);font-size:0.85rem;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;transition:var(--transition);}
.btn-primary{background:var(--ember);color:#fff;}
.btn-primary:hover{background:var(--ember-hover);transform:translateY(-2px);box-shadow:0 10px 24px var(--ember-glow);}
.btn-outline{background:transparent;color:var(--silver);border:1.5px solid var(--line);}
.btn-outline:hover{border-color:var(--ember);color:var(--ember);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.3rem 0;transition:var(--transition);}
.header.scrolled{background:rgba(28,28,30,0.95);backdrop-filter:blur(14px);padding:0.9rem 0;box-shadow:0 2px 24px rgba(0,0,0,0.4);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--display);font-size:1.3rem;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;}
.logo span{color:var(--ember);}
.nav-list{display:flex;list-style:none;gap:2.2rem;align-items:center;}
.nav-list a{font-size:0.84rem;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;}
.nav-list a:hover{color:var(--ember);}
.cart-btn{position:relative;background:none;border:none;font-size:1.2rem;}
.cart-badge{position:absolute;top:-4px;right:-6px;background:var(--ember);color:#fff;font-size:0.62rem;font-weight:700;width:17px;height:17px;border-radius:50%;display:flex;align-items:center;justify-content:center;}
.cart-badge.hidden{display:none;}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:22px;height:2px;background:var(--silver);transition:var(--transition);}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:84vh;display:flex;align-items:center;padding-top:6rem;background:radial-gradient(ellipse at 75% 25%, rgba(184,58,46,0.08), transparent 55%);}
.hero-title{font-family:var(--display);font-size:3.8rem;text-transform:uppercase;line-height:1.08;letter-spacing:0.5px;margin-bottom:1.4rem;max-width:760px;font-weight:600;}
.hero-title span{color:var(--ember);}
.hero-desc{font-size:1.05rem;color:var(--silver-dim);max-width:460px;margin-bottom:2rem;}

.forge-timeline{position:relative;margin-top:3.5rem;padding-left:3rem;max-width:680px;}
.forge-line{position:absolute;left:11px;top:8px;bottom:8px;width:2px;background:var(--line);}
.forge-line-fill{position:absolute;left:11px;top:8px;width:2px;background:var(--ember);height:0%;transition:height 0.1s linear;box-shadow:0 0 8px var(--ember-glow);}
.forge-step{position:relative;padding-bottom:3rem;}
.forge-step:last-child{padding-bottom:0;}
.forge-step::before{content:"";position:absolute;left:-3rem;top:2px;width:24px;height:24px;border-radius:50%;background:var(--steel-card);border:2px solid var(--line);transition:var(--transition);}
.forge-step.active::before{border-color:var(--ember);box-shadow:0 0 0 4px var(--ember-glow);}
.forge-step h4{font-family:var(--display);font-size:1.2rem;text-transform:uppercase;margin-bottom:0.4rem;}
.forge-step p{color:var(--silver-dim);font-size:0.92rem;max-width:520px;}

.knife-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-top:3rem;}
.knife-card{background:var(--steel-card);border-radius:var(--radius-lg);overflow:hidden;border:1px solid var(--line);transition:var(--transition);}
.knife-card:hover{transform:translateY(-5px);box-shadow:var(--shadow-lg);}
.knife-image{aspect-ratio:4/3;background:linear-gradient(150deg,#3D3D40,#262628);display:flex;align-items:center;justify-content:center;font-size:2.8rem;}
.knife-info{padding:1.4rem;}
.knife-cat{font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:var(--ember);margin-bottom:0.4rem;font-weight:700;}
.knife-name{font-family:var(--display);font-size:1.1rem;margin-bottom:0.6rem;text-transform:uppercase;}
.knife-footer{display:flex;align-items:center;justify-content:space-between;}
.knife-price{font-weight:700;}
.add-btn{background:var(--steel);border:1px solid var(--line);color:var(--silver);font-size:0.76rem;font-weight:700;padding:0.45rem 0.85rem;border-radius:6px;transition:var(--transition);text-transform:uppercase;}
.add-btn:hover{background:var(--ember);color:#fff;border-color:var(--ember);}

.materials-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-top:2.5rem;}
.material-card{text-align:center;padding:1.8rem;background:var(--steel-card);border-radius:var(--radius-lg);border:1px solid var(--line);}
.material-icon{font-size:2rem;margin-bottom:1rem;}
.material-card h4{font-family:var(--display);font-size:1.05rem;margin-bottom:0.5rem;text-transform:uppercase;}
.material-card p{color:var(--silver-dim);font-size:0.88rem;}

.care-list{margin-top:2.5rem;}
.care-row{display:flex;gap:1.2rem;padding:1.4rem 0;border-bottom:1px solid var(--line);}
.care-row-num{font-family:var(--display);color:var(--ember);font-size:1.3rem;min-width:40px;}
.care-row h4{font-size:1rem;margin-bottom:0.3rem;}
.care-row p{color:var(--silver-dim);font-size:0.9rem;}

.footer{border-top:1px solid var(--line);padding:3rem 0;display:flex;justify-content:space-between;align-items:center;font-size:0.82rem;color:var(--silver-dim);}

.cart-drawer{position:fixed;top:0;right:0;height:100%;width:400px;background:var(--steel-light);z-index:1100;transform:translateX(100%);transition:transform 0.35s cubic-bezier(0.16,1,0.3,1);display:flex;flex-direction:column;border-left:1px solid var(--line);}
.cart-drawer.open{transform:translateX(0);}
.cart-header{display:flex;justify-content:space-between;align-items:center;padding:1.5rem;border-bottom:1px solid var(--line);}
.cart-close{background:var(--steel-card);border:none;width:30px;height:30px;border-radius:50%;color:var(--silver);font-size:1.1rem;}
.cart-items{flex:1;overflow-y:auto;padding:1.5rem;}
.cart-empty{display:flex;align-items:center;justify-content:center;height:100%;color:var(--silver-dim);text-align:center;}
.cart-row{display:flex;gap:1rem;padding-bottom:1.1rem;margin-bottom:1.1rem;border-bottom:1px solid var(--line);}
.qty-btn{width:22px;height:22px;border-radius:6px;border:1px solid var(--line);background:var(--steel-card);color:var(--silver);}
.cart-footer{padding:1.5rem;border-top:1px solid var(--line);}
.cart-total-row{display:flex;justify-content:space-between;margin-bottom:0.9rem;font-weight:700;}
.cart-backdrop{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:1050;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.cart-backdrop.active{opacity:1;pointer-events:auto;}

.reveal{opacity:0;transform:translateY(26px);transition:all 0.65s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .knife-grid,.materials-grid{grid-template-columns:repeat(2,1fr);}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--steel);flex-direction:column;justify-content:center;gap:2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.6rem;}
  .cart-drawer{width:100%;}
}
@media (max-width:600px){ .knife-grid,.materials-grid{grid-template-columns:1fr;} .footer{flex-direction:column;gap:0.8rem;text-align:center;} }
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Ashforge <span>Cutlery</span></a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero">Home</a></li>
      <li><a href="#process">Our Process</a></li>
      <li><a href="#shop">Shop</a></li>
      <li><a href="#care">Care Guide</a></li>
    </ul></nav>
    <div style="display:flex;align-items:center;gap:0.6rem;">
      <button class="cart-btn" id="cart-btn" aria-label="Open cart">🔪<span class="cart-badge hidden" id="cart-badge">0</span></button>
      <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <span class="section-label">Hand-Forged, One at a Time</span>
    <h1 class="hero-title">A blade forged<br>by <span>fire and hand.</span></h1>
    <p class="hero-desc">Every Ashforge knife starts as raw carbon steel and ends as a tool you'll hand down — no factory stamping, no shortcuts.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;">
      <a href="#shop" class="btn btn-primary">Shop Knives</a>
      <a href="#process" class="btn btn-outline">See the Process</a>
    </div>
  </div>
</section>

<section class="section" id="process" style="background:var(--steel-light);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">From Bar Stock to Blade</span>
      <h2 class="section-title">The forging process</h2>
    </div>
    <div class="forge-timeline" id="forge-timeline">
      <div class="forge-line"></div>
      <div class="forge-line-fill" id="forge-fill"></div>
      <div class="forge-step" data-step="0"><h4>Forge</h4><p>Carbon steel is heated to 2,000°F and hand-hammered into a rough blade shape.</p></div>
      <div class="forge-step" data-step="1"><h4>Grind</h4><p>The bevel is shaped on a slack belt grinder, checked by hand at every pass.</p></div>
      <div class="forge-step" data-step="2"><h4>Heat Treat</h4><p>Quenched and tempered to lock in hardness without making the steel brittle.</p></div>
      <div class="forge-step" data-step="3"><h4>Handle &amp; Finish</h4><p>Fitted with a stabilized wood handle, hand-sanded to a satin finish.</p></div>
      <div class="forge-step" data-step="4"><h4>Edge &amp; Inspect</h4><p>Final hand-sharpened edge, tested for sharpness before it ships.</p></div>
    </div>
  </div>
</section>

<section class="section" id="shop">
  <div class="container">
    <div class="reveal">
      <span class="section-label">The Collection</span>
      <h2 class="section-title">Shop knives</h2>
    </div>
    <div class="knife-grid" id="knife-grid"></div>
  </div>
</section>

<section class="section" style="background:var(--steel-light);">
  <div class="container">
    <div class="reveal"><span class="section-label">What We Use</span><h2 class="section-title">Materials</h2></div>
    <div class="materials-grid">
      <div class="material-card reveal"><div class="material-icon">⚒️</div><h4>1095 Carbon Steel</h4><p>High-carbon steel that takes an exceptionally sharp, easy-to-maintain edge.</p></div>
      <div class="material-card reveal"><div class="material-icon">🪵</div><h4>Stabilized Walnut</h4><p>Resin-stabilized hardwood handles, resistant to moisture and warping.</p></div>
      <div class="material-card reveal"><div class="material-icon">🛡️</div><h4>Mosaic Pins</h4><p>Hand-set decorative pins, no two knives quite identical.</p></div>
    </div>
  </div>
</section>

<section class="section" id="care">
  <div class="container">
    <div class="reveal"><span class="section-label">Keeping It Sharp</span><h2 class="section-title">Care guide</h2></div>
    <div class="care-list">
      <div class="care-row reveal"><span class="care-row-num">01</span><div><h4>Hand wash only</h4><p>Never put a carbon steel blade in the dishwasher — hand wash and dry immediately.</p></div></div>
      <div class="care-row reveal"><span class="care-row-num">02</span><div><h4>Oil after use</h4><p>A light coat of mineral oil prevents the carbon steel from developing rust.</p></div></div>
      <div class="care-row reveal"><span class="care-row-num">03</span><div><h4>Strop weekly</h4><p>A leather strop between full sharpenings keeps the edge keen for months.</p></div></div>
    </div>
  </div>
</section>

<footer class="container footer">
  <p>© 2026 Ashforge Cutlery</p>
  <p>Forged in small batches, by hand.</p>
</footer>

<div class="cart-drawer" id="cart-drawer">
  <div class="cart-header"><h3 style="font-family:var(--display);text-transform:uppercase;">Your Order</h3><button class="cart-close" id="cart-close" aria-label="Close cart">&times;</button></div>
  <div class="cart-items" id="cart-items"><div class="cart-empty" id="cart-empty"><p>Your cart is empty.</p></div></div>
  <div class="cart-footer" id="cart-footer" style="display:none;">
    <div class="cart-total-row"><span>Total</span><span id="cart-total">$0.00</span></div>
    <button class="btn btn-primary" style="width:100%;justify-content:center;">Checkout</button>
  </div>
</div>
<div class="cart-backdrop" id="cart-backdrop"></div>

<script>
document.addEventListener('DOMContentLoaded', function(){
  const knives = [
    { id:1, name:'8" Chef Knife', cat:'Kitchen', price:240, icon:'🔪' },
    { id:2, name:'4" Paring Knife', cat:'Kitchen', price:120, icon:'🔪' },
    { id:3, name:'6" Boning Knife', cat:'Kitchen', price:180, icon:'🔪' },
    { id:4, name:'Bushcraft Fixed Blade', cat:'Outdoor', price:210, icon:'🗡️' },
    { id:5, name:'Folding EDC Knife', cat:'Outdoor', price:165, icon:'🗡️' },
    { id:6, name:'Santoku Knife', cat:'Kitchen', price:255, icon:'🔪' },
  ];
  let cart = [];
  function escapeHtml(str){ const d=document.createElement('div'); d.textContent=str; return d.innerHTML; }

  function renderKnives(){
    const grid = document.getElementById('knife-grid');
    grid.innerHTML = '';
    knives.forEach((k,i)=>{
      const card = document.createElement('div');
      card.className = 'knife-card reveal';
      card.style.transitionDelay = (i*60)+'ms';
      card.innerHTML = `
        <div class="knife-image">${k.icon}</div>
        <div class="knife-info">
          <p class="knife-cat">${escapeHtml(k.cat)}</p>
          <h3 class="knife-name">${escapeHtml(k.name)}</h3>
          <div class="knife-footer"><span class="knife-price">$${k.price.toFixed(2)}</span><button class="add-btn" data-id="${k.id}">Add</button></div>
        </div>
      `;
      grid.appendChild(card);
      revealObserver.observe(card);
    });
    grid.querySelectorAll('.add-btn').forEach(btn=>btn.addEventListener('click', ()=>addToCart(parseInt(btn.dataset.id))));
  }

  function addToCart(id){
    const knife = knives.find(k=>k.id===id);
    const existing = cart.find(i=>i.id===id);
    if (existing) existing.qty+=1; else cart.push({...knife, qty:1});
    renderCart(); updateBadge();
  }
  function updateQty(id,delta){ const item=cart.find(i=>i.id===id); if(!item) return; item.qty=Math.max(1,item.qty+delta); renderCart(); updateBadge(); }
  function cartTotal(){ return cart.reduce((s,i)=>s+i.price*i.qty,0); }
  function cartCount(){ return cart.reduce((s,i)=>s+i.qty,0); }

  function renderCart(){
    const container = document.getElementById('cart-items');
    const footer = document.getElementById('cart-footer');
    const empty = document.getElementById('cart-empty');
    container.querySelectorAll('.cart-row').forEach(el=>el.remove());
    if (cart.length===0){ empty.style.display='flex'; footer.style.display='none'; return; }
    empty.style.display='none'; footer.style.display='block';
    cart.forEach(item=>{
      const row = document.createElement('div');
      row.className='cart-row';
      row.innerHTML = `
        <div style="flex:1;"><p style="font-weight:700;font-size:0.9rem;">${escapeHtml(item.name)}</p>
        <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.45rem;">
          <button class="qty-btn" data-id="${item.id}" data-delta="-1">−</button>
          <span style="font-size:0.88rem;width:1rem;text-align:center;">${item.qty}</span>
          <button class="qty-btn" data-id="${item.id}" data-delta="1">+</button>
        </div></div>
        <p style="font-weight:700;font-size:0.9rem;">$${(item.price*item.qty).toFixed(2)}</p>
      `;
      container.appendChild(row);
    });
    document.getElementById('cart-total').textContent = `$${cartTotal().toFixed(2)}`;
    container.querySelectorAll('.qty-btn').forEach(btn=>btn.addEventListener('click', ()=>updateQty(parseInt(btn.dataset.id), parseInt(btn.dataset.delta))));
  }
  function updateBadge(){ const badge=document.getElementById('cart-badge'); const count=cartCount(); badge.textContent=count; badge.classList.toggle('hidden', count===0); }

  const cartDrawer = document.getElementById('cart-drawer');
  const cartBackdrop = document.getElementById('cart-backdrop');
  document.getElementById('cart-btn').addEventListener('click', ()=>{ cartDrawer.classList.add('open'); cartBackdrop.classList.add('active'); document.body.style.overflow='hidden'; });
  function closeCart(){ cartDrawer.classList.remove('open'); cartBackdrop.classList.remove('active'); document.body.style.overflow=''; }
  document.getElementById('cart-close').addEventListener('click', closeCart);
  cartBackdrop.addEventListener('click', closeCart);
  document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeCart(); });

  const header = document.getElementById('header');
  const menuToggle = document.getElementById('menu-toggle');
  const navList = document.getElementById('nav-list');
  const overlay = document.getElementById('overlay');
  function toggleMenu(){ menuToggle.classList.toggle('active'); navList.classList.toggle('open'); overlay.classList.toggle('active'); document.body.style.overflow = navList.classList.contains('open')?'hidden':''; }
  menuToggle.addEventListener('click', toggleMenu);
  overlay.addEventListener('click', toggleMenu);
  navList.querySelectorAll('a').forEach(link=>link.addEventListener('click', ()=>{ if(navList.classList.contains('open')) toggleMenu(); }));
  window.addEventListener('scroll', ()=>{ header.classList.toggle('scrolled', window.scrollY>40); }, {passive:true});

  const revealObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
  }, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

  const forgeSteps = document.querySelectorAll('.forge-step');
  const forgeFill = document.getElementById('forge-fill');
  const forgeTimeline = document.getElementById('forge-timeline');
  function updateForge(){
    const rect = forgeTimeline.getBoundingClientRect();
    const viewportMid = window.innerHeight * 0.6;
    const totalHeight = rect.height;
    const scrolled = Math.max(0, Math.min(totalHeight, viewportMid - rect.top));
    const percent = (scrolled / totalHeight) * 100;
    forgeFill.style.height = percent + '%';
    forgeSteps.forEach(step=>{
      const stepRect = step.getBoundingClientRect();
      step.classList.toggle('active', stepRect.top < viewportMid);
    });
  }
  window.addEventListener('scroll', updateForge, {passive:true});
  updateForge();

  renderKnives();
});
</script>
</body>
</html>
```

---
## SOURCE: 03_examples/17_electric_bike_startup.md

# Example — Electric Bike Startup (Tailwind Architecture)

Tags: example, full-site, ebike, electric-bike, startup, product-launch, tailwind, dark-theme, electric-blue, spec-comparison, range-slider, tech

Niche: direct-to-consumer electric bike company launching a new model.
Architecture: Tailwind CDN utility classes.
Palette: near-black canvas (#0A0B0D), electric blue accent (#3D8BFF), crisp technical
feel with mono accents for spec numbers.
Signature element: an interactive range/spec comparison — a slider that adjusts
"rider weight" and live-updates an estimated range number, plus a model comparison
table (this model vs. previous generation).
Sections: header, hero, live range calculator, spec comparison table, gallery (icon
grid standing in for photos), reserve/preorder CTA, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Volt Cycles | The All-New Volt One E-Bike</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#0A0B0D',light:'#121317',card:'#181A1F'}, accent:{DEFAULT:'#3D8BFF',hover:'#5C9DFF',glow:'rgba(61,139,255,0.3)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], mono:['JetBrains Mono','monospace'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
  .font-mono{font-family:'JetBrains Mono',monospace;}
  ::selection{background:rgba(61,139,255,0.3);}
  .hero-title{font-size:clamp(2.6rem,6.5vw,5.6rem);line-height:0.98;letter-spacing:-0.02em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  input[type=range]{-webkit-appearance:none;height:6px;background:#23252B;border-radius:3px;}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:22px;height:22px;border-radius:50%;background:#3D8BFF;cursor:pointer;box-shadow:0 0 0 6px rgba(61,139,255,0.15);}
  input:focus,button:focus-visible{outline:2px solid #3D8BFF;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <a href="#" class="font-bold text-xl tracking-tight">VOLT</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#range" class="text-sm text-white/60 hover:text-white">Range Calculator</a>
        <a href="#specs" class="text-sm text-white/60 hover:text-white">Specs</a>
        <a href="#preorder" class="text-sm text-white/60 hover:text-white">Preorder</a>
      </nav>
      <a href="#preorder" class="bg-accent hover:bg-accent-hover text-white font-semibold text-sm px-5 py-2.5 rounded-lg transition-colors">Reserve — $99</a>
    </div>
  </div>
</header>

<section class="relative min-h-[94vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 25% 25%, rgba(61,139,255,0.08) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
    <p class="text-accent text-sm font-mono uppercase tracking-widest mb-6">INTRODUCING VOLT ONE</p>
    <h1 class="hero-title font-extrabold text-white mb-8 max-w-4xl">
      75 miles per charge.<br><span class="text-accent">Zero compromises.</span>
    </h1>
    <p class="text-lg text-white/50 max-w-md mb-10 leading-relaxed">
      A torque sensor that actually feels human, a battery that lasts a week of
      commutes, and a frame that doesn't look like a science project.
    </p>
    <div class="flex flex-col sm:flex-row gap-4">
      <a href="#preorder" class="bg-accent hover:bg-accent-hover text-white font-semibold px-8 py-4 rounded-xl transition-all hover:-translate-y-0.5">Reserve Yours — $99</a>
      <a href="#range" class="border border-white/15 hover:border-white/30 font-medium px-8 py-4 rounded-xl transition-all hover:bg-white/5">Calculate Your Range</a>
    </div>
  </div>
</section>

<section id="range" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-3xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-14 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Range Calculator</p>
      <h2 class="text-3xl lg:text-4xl font-bold">How far will you go?</h2>
    </div>
    <div class="reveal bg-canvas-card border border-white/10 rounded-2xl p-8 lg:p-10">
      <div class="mb-8">
        <div class="flex justify-between mb-3">
          <label class="text-sm text-white/60">Rider Weight</label>
          <span class="font-mono text-accent font-bold" id="weight-display">165 lbs</span>
        </div>
        <input type="range" id="weight-slider" min="100" max="280" value="165" class="w-full">
      </div>
      <div class="mb-8">
        <div class="flex justify-between mb-3">
          <label class="text-sm text-white/60">Assist Mode</label>
          <span class="font-mono text-accent font-bold" id="mode-display">Eco</span>
        </div>
        <input type="range" id="mode-slider" min="0" max="2" value="0" step="1" class="w-full">
      </div>
      <div class="pt-6 border-t border-white/10 text-center">
        <p class="text-xs text-white/40 uppercase tracking-wide mb-2">Estimated Range</p>
        <p class="font-mono text-5xl font-bold text-accent" id="range-result">75 mi</p>
      </div>
    </div>
  </div>
</section>

<section id="specs" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-14 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Spec Comparison</p>
      <h2 class="text-3xl lg:text-4xl font-bold">Volt One vs. Gen 1</h2>
    </div>
    <div class="reveal overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-white/10">
            <th class="text-left py-4 text-white/40 font-medium">Spec</th>
            <th class="text-left py-4 text-white/60 font-medium">Gen 1</th>
            <th class="text-left py-4 text-accent font-bold">Volt One</th>
          </tr>
        </thead>
        <tbody class="font-mono">
          <tr class="border-b border-white/5"><td class="py-4 text-white/50">Range</td><td class="py-4">42 mi</td><td class="py-4 text-accent font-bold">75 mi</td></tr>
          <tr class="border-b border-white/5"><td class="py-4 text-white/50">Top Speed</td><td class="py-4">20 mph</td><td class="py-4 text-accent font-bold">28 mph</td></tr>
          <tr class="border-b border-white/5"><td class="py-4 text-white/50">Charge Time</td><td class="py-4">5.5 hrs</td><td class="py-4 text-accent font-bold">3.2 hrs</td></tr>
          <tr class="border-b border-white/5"><td class="py-4 text-white/50">Weight</td><td class="py-4">52 lbs</td><td class="py-4 text-accent font-bold">44 lbs</td></tr>
          <tr><td class="py-4 text-white/50">Motor Torque</td><td class="py-4">65 Nm</td><td class="py-4 text-accent font-bold">85 Nm</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="py-24 lg:py-32">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Engineering</p>
      <h2 class="text-3xl lg:text-4xl font-bold">Built different, on purpose</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8 text-center"><div class="text-4xl mb-4">🔋</div><h3 class="font-semibold mb-2">Removable Battery</h3><p class="text-sm text-white/45">Pull it out and charge inside — no more dragging an extension cord to the garage.</p></div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8 text-center" style="transition-delay:.1s"><div class="text-4xl mb-4">⚙️</div><h3 class="font-semibold mb-2">Torque Sensor Pedal Assist</h3><p class="text-sm text-white/45">Responds to how hard you're pedaling, not just whether you are — it feels like a bike, not a scooter.</p></div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8 text-center" style="transition-delay:.2s"><div class="text-4xl mb-4">🔒</div><h3 class="font-semibold mb-2">Integrated GPS Lock</h3><p class="text-sm text-white/45">Built-in tracking and remote motor lock if it's ever moved without your phone nearby.</p></div>
    </div>
  </div>
</section>

<section id="preorder" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-2xl mx-auto px-6 lg:px-8 text-center">
    <div class="reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Limited First Run</p>
      <h2 class="text-3xl lg:text-4xl font-bold mb-4">Reserve your Volt One</h2>
      <p class="text-white/50 mb-8">$99 fully refundable deposit. First deliveries ship in October.</p>
      <a href="#" class="inline-flex items-center gap-2 bg-accent hover:bg-accent-hover text-white font-semibold px-10 py-4 rounded-xl transition-all hover:-translate-y-0.5">Reserve Now — $99</a>
      <p class="text-xs text-white/30 mt-4">No payment until your build slot is confirmed.</p>
    </div>
  </div>
</section>

<footer class="border-t border-white/5 py-12">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p>© 2026 Volt Cycles, Inc.</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Warranty</a><a href="#" class="hover:text-white/60">Support</a></div>
  </div>
</footer>

<script>
const weightSlider = document.getElementById('weight-slider');
const modeSlider = document.getElementById('mode-slider');
const modes = ['Eco', 'Trail', 'Boost'];
const baseRangeByMode = [75, 58, 42];

function updateRange(){
  const weight = parseInt(weightSlider.value);
  const modeIndex = parseInt(modeSlider.value);
  document.getElementById('weight-display').textContent = weight + ' lbs';
  document.getElementById('mode-display').textContent = modes[modeIndex];
  const weightPenalty = Math.max(0, (weight - 165) * 0.12);
  const range = Math.max(18, Math.round(baseRangeByMode[modeIndex] - weightPenalty));
  document.getElementById('range-result').textContent = range + ' mi';
}
weightSlider.addEventListener('input', updateRange);
modeSlider.addEventListener('input', updateRange);
updateRange();

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(10,11,13,0.85)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));
</script>
</body>
</html>
```

