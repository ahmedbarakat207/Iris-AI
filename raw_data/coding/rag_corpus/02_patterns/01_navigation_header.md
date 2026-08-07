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
