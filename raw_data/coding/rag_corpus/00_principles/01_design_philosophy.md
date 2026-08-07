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
