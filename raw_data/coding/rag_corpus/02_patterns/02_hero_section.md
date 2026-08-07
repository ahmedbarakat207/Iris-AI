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
