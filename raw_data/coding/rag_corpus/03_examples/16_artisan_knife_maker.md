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
