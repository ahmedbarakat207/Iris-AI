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
