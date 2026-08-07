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
