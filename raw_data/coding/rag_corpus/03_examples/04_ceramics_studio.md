# Example — Artisan Ceramics Studio (Vanilla CSS Architecture, Light Mode)

Tags: example, full-site, ceramics, pottery, artisan, craft, vanilla-css, light-theme, clay, sand, ecommerce

Niche: small-batch ceramics studio selling handmade tableware.
Architecture: vanilla CSS with custom properties, no external dependencies.
Palette: warm sand/cream canvas (#F4EEE4), espresso text, terracotta clay accent (#B5602E).
Signature element: a horizontal kiln-firing process strip showing the four stages a
piece passes through, with a subtle progress fill on scroll.
Sections: header, hero, process strip, shop grid with cart, studio story, care guide,
newsletter, footer.

This is a LIGHT-MODE example — note the inverted contrast relationships versus the
dark-theme examples elsewhere in this corpus: canvas is light, text is dark, cards
are a slightly lighter/warmer tone than canvas rather than darker.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hearth &amp; Hand Ceramics | Handmade Stoneware Tableware</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Karla:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --sand:#F4EEE4; --sand-card:#FBF8F2; --cream-line:#E3D9C7;
  --espresso:#3A2E22; --espresso-dim:#6B5D4D; --clay:#B5602E; --clay-hover:#C97540; --clay-dark:#964F25;
  --radius:10px; --radius-lg:18px;
  --transition: all 0.35s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow: 0 10px 30px rgba(58,46,34,0.08);
  --shadow-lg: 0 20px 50px rgba(58,46,34,0.14);
  --serif:'Cormorant Garamond', serif; --sans:'Karla', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--sand);color:var(--espresso);line-height:1.65;overflow-x:hidden;}
a{text-decoration:none;color:inherit;}
img{max-width:100%;display:block;}
button{cursor:pointer;font-family:inherit;}
.container{max-width:1180px;margin:0 auto;padding:0 2rem;}
.section{padding:6rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.78rem;color:var(--clay);margin-bottom:1rem;font-weight:700;}
.section-title{font-family:var(--serif);font-size:2.7rem;font-weight:600;line-height:1.15;margin-bottom:1rem;}
.section-subtitle{color:var(--espresso-dim);font-size:1.05rem;max-width:560px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.9rem 2.1rem;border:none;border-radius:var(--radius);font-size:0.88rem;font-weight:700;letter-spacing:0.4px;transition:var(--transition);}
.btn-primary{background:var(--clay);color:#fff;}
.btn-primary:hover{background:var(--clay-hover);transform:translateY(-2px);box-shadow:0 12px 26px rgba(181,96,46,0.28);}
.btn-outline{background:transparent;color:var(--espresso);border:1.5px solid var(--cream-line);}
.btn-outline:hover{border-color:var(--clay);color:var(--clay);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.4rem 0;transition:var(--transition);}
.header.scrolled{background:rgba(244,238,228,0.92);backdrop-filter:blur(14px);padding:1rem 0;box-shadow:0 2px 24px rgba(58,46,34,0.08);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--serif);font-size:1.5rem;font-weight:700;}
.logo span{color:var(--clay);}
.nav-list{display:flex;list-style:none;gap:2.3rem;align-items:center;}
.nav-list a{font-size:0.85rem;font-weight:600;letter-spacing:0.6px;position:relative;padding:0.25rem 0;}
.nav-list a::after{content:"";position:absolute;bottom:-2px;left:0;width:0;height:2px;background:var(--clay);transition:var(--transition);}
.nav-list a:hover::after,.nav-list a.active::after{width:100%;}
.cart-btn{position:relative;background:none;border:none;padding:0.4rem;}
.cart-badge{position:absolute;top:-4px;right:-6px;background:var(--clay);color:#fff;font-size:0.65rem;font-weight:700;width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;}
.cart-badge.hidden{display:none;}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:24px;height:2px;background:var(--espresso);transition:var(--transition);}
.menu-toggle.active span:nth-child(1){transform:translateY(7px) rotate(45deg);}
.menu-toggle.active span:nth-child(2){opacity:0;}
.menu-toggle.active span:nth-child(3){transform:translateY(-7px) rotate(-45deg);}
.overlay{position:fixed;inset:0;background:rgba(58,46,34,0.5);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:88vh;display:flex;align-items:center;position:relative;padding-top:6rem;}
.hero-grid{display:grid;grid-template-columns:1.05fr 0.95fr;gap:4rem;align-items:center;}
.hero-label{display:inline-block;padding:0.4rem 1rem;background:rgba(181,96,46,0.1);border:1px solid rgba(181,96,46,0.25);border-radius:30px;font-size:0.78rem;letter-spacing:2px;text-transform:uppercase;color:var(--clay-dark);margin-bottom:2rem;font-weight:700;}
.hero-title{font-family:var(--serif);font-size:3.7rem;font-weight:600;line-height:1.1;margin-bottom:1.4rem;letter-spacing:-0.5px;}
.hero-title em{font-style:italic;color:var(--clay);font-weight:700;}
.hero-desc{font-size:1.1rem;color:var(--espresso-dim);max-width:460px;margin-bottom:2.2rem;}
.hero-actions{display:flex;gap:1rem;flex-wrap:wrap;}
.hero-visual{position:relative;aspect-ratio:1;border-radius:var(--radius-lg);background:linear-gradient(150deg,#E8DCC8,#D9C8AC);display:flex;align-items:center;justify-content:center;box-shadow:var(--shadow-lg);}
.hero-visual-icon{font-size:5rem;}

.process-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:2rem;margin-top:3.5rem;position:relative;}
.process-bar{position:absolute;top:27px;left:0;height:2px;background:var(--cream-line);width:100%;}
.process-bar-fill{position:absolute;top:27px;left:0;height:2px;background:var(--clay);width:0;transition:width 1.3s cubic-bezier(0.16,1,0.3,1);}
.process-step{text-align:center;position:relative;}
.process-icon{width:56px;height:56px;border-radius:50%;background:var(--sand-card);border:2px solid var(--cream-line);display:flex;align-items:center;justify-content:center;margin:0 auto 1.2rem;font-size:1.5rem;position:relative;z-index:2;transition:var(--transition);}
.process-step.active .process-icon{border-color:var(--clay);background:var(--clay);color:#fff;}
.process-step h4{font-family:var(--serif);font-size:1.15rem;margin-bottom:0.4rem;}
.process-step p{font-size:0.85rem;color:var(--espresso-dim);}

.shop-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1.5rem;margin-top:3rem;}
.product-card{background:var(--sand-card);border-radius:var(--radius-lg);overflow:hidden;transition:var(--transition);border:1px solid var(--cream-line);}
.product-card:hover{transform:translateY(-6px);box-shadow:var(--shadow-lg);}
.product-image{aspect-ratio:1;background:linear-gradient(150deg,#E8DCC8,#D9C8AC);display:flex;align-items:center;justify-content:center;font-size:3rem;position:relative;}
.product-info{padding:1.4rem;}
.product-cat{font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:var(--clay);margin-bottom:0.4rem;font-weight:700;}
.product-name{font-family:var(--serif);font-size:1.15rem;margin-bottom:0.5rem;}
.product-footer{display:flex;align-items:center;justify-content:space-between;}
.product-price{font-weight:700;font-size:1.05rem;}
.add-btn{background:var(--sand);border:1px solid var(--cream-line);color:var(--espresso);font-size:0.78rem;font-weight:700;padding:0.5rem 0.9rem;border-radius:8px;transition:var(--transition);}
.add-btn:hover{background:var(--clay);color:#fff;border-color:var(--clay);}

.story-grid{display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center;margin-top:2rem;}
.story-visual{aspect-ratio:4/3;border-radius:var(--radius-lg);background:linear-gradient(150deg,#E8DCC8,#D9C8AC);display:flex;align-items:center;justify-content:center;font-size:4rem;}
.story-text p{color:var(--espresso-dim);margin-bottom:1.2rem;font-size:1.02rem;}

.care-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-top:3rem;}
.care-card{background:var(--sand-card);border-radius:var(--radius-lg);padding:2rem;border:1px solid var(--cream-line);}
.care-card h4{font-family:var(--serif);font-size:1.2rem;margin-bottom:0.6rem;}
.care-card p{color:var(--espresso-dim);font-size:0.92rem;}

.newsletter-section{background:var(--clay);color:#fff;text-align:center;}
.newsletter-section h3{font-family:var(--serif);font-size:2rem;margin-bottom:0.8rem;}
.newsletter-section p{opacity:0.9;margin-bottom:2rem;}
.newsletter-form{display:flex;gap:0.8rem;max-width:420px;margin:0 auto;flex-wrap:wrap;justify-content:center;}
.newsletter-form input{flex:1;min-width:200px;padding:0.85rem 1.1rem;border-radius:var(--radius);border:none;font-family:inherit;font-size:0.92rem;}
.newsletter-form button{background:var(--espresso);color:#fff;border:none;padding:0.85rem 1.6rem;border-radius:var(--radius);font-weight:700;font-size:0.9rem;}
.newsletter-note{margin-top:1rem;font-size:0.82rem;opacity:0.85;}

.footer{background:var(--espresso);color:var(--sand);padding:3.5rem 0 0;}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:3rem;padding-bottom:2.5rem;}
.footer-col h4{font-size:0.8rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:1.1rem;opacity:0.6;}
.footer-col a,.footer-col p{display:block;color:var(--sand);opacity:0.75;font-size:0.88rem;margin-bottom:0.75rem;}
.footer-col a:hover{opacity:1;color:var(--clay-hover);}
.footer-bottom{border-top:1px solid rgba(244,238,228,0.12);padding:1.3rem 0;display:flex;justify-content:space-between;font-size:0.8rem;opacity:0.6;}

.cart-drawer{position:fixed;top:0;right:0;height:100%;width:400px;background:var(--sand-card);z-index:1100;transform:translateX(100%);transition:transform 0.35s cubic-bezier(0.16,1,0.3,1);display:flex;flex-direction:column;box-shadow:-10px 0 40px rgba(0,0,0,0.15);}
.cart-drawer.open{transform:translateX(0);}
.cart-header{display:flex;justify-content:space-between;align-items:center;padding:1.6rem;border-bottom:1px solid var(--cream-line);}
.cart-header h3{font-family:var(--serif);font-size:1.3rem;}
.cart-close{background:var(--sand);border:none;width:32px;height:32px;border-radius:50%;font-size:1.2rem;}
.cart-items{flex:1;overflow-y:auto;padding:1.6rem;}
.cart-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;color:var(--espresso-dim);}
.cart-row{display:flex;gap:1rem;padding-bottom:1.2rem;margin-bottom:1.2rem;border-bottom:1px solid var(--cream-line);}
.qty-btn{width:24px;height:24px;border-radius:6px;border:1px solid var(--cream-line);background:var(--sand);}
.cart-footer{padding:1.6rem;border-top:1px solid var(--cream-line);}
.cart-total-row{display:flex;justify-content:space-between;margin-bottom:1rem;font-weight:700;}
.cart-backdrop{position:fixed;inset:0;background:rgba(58,46,34,0.5);z-index:1050;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.cart-backdrop.active{opacity:1;pointer-events:auto;}

.reveal{opacity:0;transform:translateY(28px);transition:all 0.7s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .hero-grid,.story-grid{grid-template-columns:1fr;}
  .shop-grid{grid-template-columns:repeat(2,1fr);}
  .process-strip{grid-template-columns:repeat(2,1fr);row-gap:2.5rem;}
  .process-bar,.process-bar-fill{display:none;}
  .care-grid{grid-template-columns:1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--sand);flex-direction:column;justify-content:center;gap:2.2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.6rem;}
  .footer-grid{grid-template-columns:1fr;}
  .cart-drawer{width:100%;}
}
@media (max-width:600px){
  .shop-grid{grid-template-columns:1fr;}
  .footer-bottom{flex-direction:column;gap:0.7rem;text-align:center;}
}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Hearth <span>&amp;</span> Hand</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero" class="active">Home</a></li>
      <li><a href="#shop">Shop</a></li>
      <li><a href="#story">Our Story</a></li>
      <li><a href="#care">Care Guide</a></li>
    </ul></nav>
    <div style="display:flex;align-items:center;gap:0.5rem;">
      <button class="cart-btn" id="cart-btn" aria-label="Open cart">
        🧺<span class="cart-badge hidden" id="cart-badge">0</span>
      </button>
      <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <span class="hero-label">Small-Batch, Wood-Fired Stoneware</span>
        <h1 class="hero-title">Tableware shaped<br>by <em>one pair of hands.</em></h1>
        <p class="hero-desc">Every piece is thrown, glazed, and fired in our backyard studio — no molds, no two pieces quite the same.</p>
        <div class="hero-actions">
          <a href="#shop" class="btn btn-primary">Shop the Collection</a>
          <a href="#story" class="btn btn-outline">Meet the Studio</a>
        </div>
      </div>
      <div class="hero-visual"><span class="hero-visual-icon">🏺</span></div>
    </div>
  </div>
</section>

<section class="section" id="process" style="background:var(--sand-card);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">How Each Piece Is Made</span>
      <h2 class="section-title">From clay to your table</h2>
    </div>
    <div class="process-strip" id="process-strip">
      <div class="process-bar"></div>
      <div class="process-bar-fill" id="process-fill"></div>
      <div class="process-step reveal"><div class="process-icon">🧱</div><h4>Throw</h4><p>Hand-thrown on the wheel from local stoneware clay.</p></div>
      <div class="process-step reveal"><div class="process-icon">☀️</div><h4>Dry</h4><p>Air-dried slowly over 5-7 days to prevent cracking.</p></div>
      <div class="process-step reveal"><div class="process-icon">🎨</div><h4>Glaze</h4><p>Hand-dipped in small-batch glazes mixed in-house.</p></div>
      <div class="process-step reveal"><div class="process-icon">🔥</div><h4>Fire</h4><p>Wood-fired at 2,300°F for a one-of-a-kind finish.</p></div>
    </div>
  </div>
</section>

<section class="section" id="shop">
  <div class="container">
    <div class="reveal">
      <span class="section-label">The Collection</span>
      <h2 class="section-title">Shop tableware</h2>
    </div>
    <div class="shop-grid" id="shop-grid"></div>
  </div>
</section>

<section class="section" id="story" style="background:var(--sand-card);">
  <div class="container">
    <div class="story-grid">
      <div class="story-visual reveal">🧑‍🎨</div>
      <div class="story-text reveal">
        <span class="section-label">Our Story</span>
        <h2 class="section-title">Started in a garage, still in one</h2>
        <p>Hearth &amp; Hand began in 2019 when Mara started throwing bowls for friends on a wheel
        wedged between the lawnmower and the recycling bins. Six years later, the garage is bigger
        but the process hasn't changed — every piece still passes through her hands alone.</p>
        <p>We fire in small kiln loads of 30-40 pieces, which means waitlists during the holidays
        and the occasional sold-out glaze. We think that's a fair trade for never compromising
        on how a piece is made.</p>
      </div>
    </div>
  </div>
</section>

<section class="section" id="care">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Living With Stoneware</span>
      <h2 class="section-title">Care guide</h2>
    </div>
    <div class="care-grid">
      <div class="care-card reveal"><h4>Dishwasher Safe</h4><p>All glazed pieces are dishwasher and microwave safe. Hand-wash unglazed bases.</p></div>
      <div class="care-card reveal"><h4>Expect Variation</h4><p>Glaze pooling and slight color shifts are part of the wood-firing process, not a flaw.</p></div>
      <div class="care-card reveal"><h4>Avoid Thermal Shock</h4><p>Let pieces come to room temperature before moving from fridge to oven.</p></div>
    </div>
  </div>
</section>

<section class="section newsletter-section">
  <div class="container">
    <h3>Get first access to new glaze drops</h3>
    <p>We restock in small batches — subscribers hear first.</p>
    <form class="newsletter-form" id="newsletter-form">
      <input type="email" id="newsletter-email" placeholder="you@example.com" required>
      <button type="submit">Subscribe</button>
    </form>
    <p class="newsletter-note" id="newsletter-note">No spam, just clay dust and good news.</p>
  </div>
</section>

<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-col">
      <h4>Hearth &amp; Hand Ceramics</h4>
      <p>Hand-thrown stoneware tableware, fired in small batches in our backyard studio.</p>
    </div>
    <div class="footer-col"><h4>Shop</h4><a href="#shop">All Tableware</a><a href="#">Gift Cards</a><a href="#">Seconds Sale</a></div>
    <div class="footer-col"><h4>Studio</h4><a href="#story">Our Story</a><a href="#care">Care Guide</a><a href="#">Wholesale Inquiries</a></div>
  </div>
  <div class="container footer-bottom"><p>© 2026 Hearth &amp; Hand Ceramics.</p><p>Made in small batches, always.</p></div>
</footer>

<div class="cart-drawer" id="cart-drawer">
  <div class="cart-header"><h3>Your Basket</h3><button class="cart-close" id="cart-close" aria-label="Close cart">&times;</button></div>
  <div class="cart-items" id="cart-items">
    <div class="cart-empty" id="cart-empty"><p>Your basket is empty.</p></div>
  </div>
  <div class="cart-footer" id="cart-footer" style="display:none;">
    <div class="cart-total-row"><span>Total</span><span id="cart-total">$0.00</span></div>
    <button class="btn btn-primary" style="width:100%;justify-content:center;">Checkout</button>
  </div>
</div>
<div class="cart-backdrop" id="cart-backdrop"></div>

<script>
document.addEventListener('DOMContentLoaded', function () {
  const products = [
    { id:1, name:'Speckled Dinner Plate', cat:'Dinnerware', price:42, icon:'🍽️' },
    { id:2, name:'Wood-Ash Cereal Bowl', cat:'Dinnerware', price:34, icon:'🥣' },
    { id:3, name:'Carved Mug, Sand Glaze', cat:'Drinkware', price:28, icon:'☕' },
    { id:4, name:'Serving Platter', cat:'Serveware', price:68, icon:'🍲' },
    { id:5, name:'Pinch Bowl Set of 3', cat:'Serveware', price:36, icon:'🫕' },
    { id:6, name:'Carved Vase, Tall', cat:'Home', price:58, icon:'🏺' },
    { id:7, name:'Soup Mug', cat:'Drinkware', price:30, icon:'🍵' },
    { id:8, name:'Butter Dish', cat:'Dinnerware', price:38, icon:'🧈' },
  ];
  let cart = [];

  function escapeHtml(str){ const d=document.createElement('div'); d.textContent=str; return d.innerHTML; }

  function renderProducts(){
    const grid = document.getElementById('shop-grid');
    grid.innerHTML = '';
    products.forEach((p,i)=>{
      const card = document.createElement('div');
      card.className = 'product-card reveal';
      card.style.transitionDelay = (i*60)+'ms';
      card.innerHTML = `
        <div class="product-image">${p.icon}</div>
        <div class="product-info">
          <p class="product-cat">${escapeHtml(p.cat)}</p>
          <h3 class="product-name">${escapeHtml(p.name)}</h3>
          <div class="product-footer">
            <span class="product-price">$${p.price.toFixed(2)}</span>
            <button class="add-btn" data-id="${p.id}">Add</button>
          </div>
        </div>
      `;
      grid.appendChild(card);
      revealObserver.observe(card);
    });
    grid.querySelectorAll('.add-btn').forEach(btn=>{
      btn.addEventListener('click', ()=>addToCart(parseInt(btn.dataset.id)));
    });
  }

  function addToCart(id){
    const product = products.find(p=>p.id===id);
    const existing = cart.find(i=>i.id===id);
    if (existing) existing.qty+=1; else cart.push({...product, qty:1});
    renderCart(); updateBadge();
  }
  function updateQty(id,delta){
    const item = cart.find(i=>i.id===id);
    if(!item) return;
    item.qty = Math.max(1, item.qty+delta);
    renderCart(); updateBadge();
  }
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
      row.className = 'cart-row';
      row.innerHTML = `
        <div style="flex:1;">
          <p style="font-weight:600;font-size:0.92rem;">${escapeHtml(item.name)}</p>
          <div style="display:flex;align-items:center;gap:0.6rem;margin-top:0.5rem;">
            <button class="qty-btn" data-id="${item.id}" data-delta="-1">−</button>
            <span style="font-size:0.9rem;width:1rem;text-align:center;">${item.qty}</span>
            <button class="qty-btn" data-id="${item.id}" data-delta="1">+</button>
          </div>
        </div>
        <p style="font-weight:700;font-size:0.92rem;">$${(item.price*item.qty).toFixed(2)}</p>
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
  }

  const cartDrawer = document.getElementById('cart-drawer');
  const cartBackdrop = document.getElementById('cart-backdrop');
  document.getElementById('cart-btn').addEventListener('click', ()=>{
    cartDrawer.classList.add('open'); cartBackdrop.classList.add('active'); document.body.style.overflow='hidden';
  });
  function closeCart(){ cartDrawer.classList.remove('open'); cartBackdrop.classList.remove('active'); document.body.style.overflow=''; }
  document.getElementById('cart-close').addEventListener('click', closeCart);
  cartBackdrop.addEventListener('click', closeCart);
  document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeCart(); });

  const header = document.getElementById('header');
  const menuToggle = document.getElementById('menu-toggle');
  const navList = document.getElementById('nav-list');
  const overlay = document.getElementById('overlay');
  function toggleMenu(){
    menuToggle.classList.toggle('active'); navList.classList.toggle('open'); overlay.classList.toggle('active');
    document.body.style.overflow = navList.classList.contains('open') ? 'hidden' : '';
  }
  menuToggle.addEventListener('click', toggleMenu);
  overlay.addEventListener('click', toggleMenu);
  navList.querySelectorAll('a').forEach(link=>link.addEventListener('click', ()=>{ if(navList.classList.contains('open')) toggleMenu(); }));
  window.addEventListener('scroll', ()=>{ header.classList.toggle('scrolled', window.scrollY>40); }, {passive:true});

  const revealObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
  }, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
  document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

  const processFill = document.getElementById('process-fill');
  const processObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{ if(entry.isIntersecting){ processFill.style.width='100%'; processObserver.disconnect(); } });
  }, {threshold:0.3});
  processObserver.observe(document.getElementById('process-strip'));

  document.getElementById('newsletter-form').addEventListener('submit', (e)=>{
    e.preventDefault();
    document.getElementById('newsletter-note').textContent = "You're in! Watch your inbox for the next firing.";
    e.target.reset();
  });

  renderProducts();
});
</script>
</body>
</html>
```
