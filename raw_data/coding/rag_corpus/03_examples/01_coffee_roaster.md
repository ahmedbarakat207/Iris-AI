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
