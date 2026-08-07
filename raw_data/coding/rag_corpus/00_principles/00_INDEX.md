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
