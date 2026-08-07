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
