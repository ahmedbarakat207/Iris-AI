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
