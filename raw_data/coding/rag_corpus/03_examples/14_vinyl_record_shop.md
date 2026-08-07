# Example — Vinyl Record Shop (Vanilla CSS Architecture)

Tags: example, full-site, vinyl, records, music, retro, vanilla-css, dark-theme, mustard-yellow, black, retro-typography, genre-wheel, ecommerce

Niche: independent vinyl record shop, new and used.
Architecture: vanilla CSS, custom properties.
Palette: matte black canvas (#121212), mustard yellow accent (#E8B339), warm orange
secondary (#D9622B) — retro 70s print aesthetic, bold condensed display type.
Signature element: a spinning genre wheel — a circular nav where each genre sits on a
rotating dial; clicking a segment spins the wheel to center it and filters the crate
below.
Sections: header, hero, genre wheel + crate grid with cart, new arrivals strip, about,
footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Static &amp; Soul Records | New &amp; Used Vinyl</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Anton&amp;family=Karla:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --black:#121212; --black-light:#1B1B1B; --black-card:#222222; --line:#333333;
  --cream:#F2EADF; --cream-dim:#A8A096; --mustard:#E8B339; --mustard-hover:#F0C457; --orange:#D9622B;
  --radius:6px; --radius-lg:12px;
  --transition: all 0.3s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow-lg: 0 20px 50px rgba(0,0,0,0.5);
  --display:'Anton', sans-serif; --sans:'Karla', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--black);color:var(--cream);line-height:1.65;overflow-x:hidden;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;} button{cursor:pointer;font-family:inherit;}
.container{max-width:1180px;margin:0 auto;padding:0 2rem;}
.section{padding:6rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.78rem;color:var(--mustard);margin-bottom:1rem;font-weight:700;}
.section-title{font-family:var(--display);font-size:2.6rem;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:1rem;}
.section-subtitle{color:var(--cream-dim);font-size:1rem;max-width:540px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.9rem 2rem;border:none;border-radius:var(--radius);font-size:0.85rem;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;transition:var(--transition);}
.btn-primary{background:var(--mustard);color:var(--black);}
.btn-primary:hover{background:var(--mustard-hover);transform:translateY(-2px);box-shadow:0 10px 22px rgba(232,179,57,0.25);}
.btn-outline{background:transparent;color:var(--cream);border:1.5px solid var(--line);}
.btn-outline:hover{border-color:var(--mustard);color:var(--mustard);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.3rem 0;transition:var(--transition);}
.header.scrolled{background:rgba(18,18,18,0.95);backdrop-filter:blur(14px);padding:0.9rem 0;box-shadow:0 2px 24px rgba(0,0,0,0.4);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--display);font-size:1.3rem;text-transform:uppercase;letter-spacing:0.5px;}
.logo span{color:var(--mustard);}
.nav-list{display:flex;list-style:none;gap:2.2rem;align-items:center;}
.nav-list a{font-size:0.84rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;}
.nav-list a:hover{color:var(--mustard);}
.cart-btn{position:relative;background:none;border:none;font-size:1.2rem;}
.cart-badge{position:absolute;top:-4px;right:-6px;background:var(--orange);color:#fff;font-size:0.62rem;font-weight:700;width:17px;height:17px;border-radius:50%;display:flex;align-items:center;justify-content:center;}
.cart-badge.hidden{display:none;}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:22px;height:2px;background:var(--cream);transition:var(--transition);}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:84vh;display:flex;align-items:center;padding-top:6rem;background:radial-gradient(ellipse at 75% 30%, rgba(232,179,57,0.08), transparent 55%);}
.hero-title{font-family:var(--display);font-size:4.2rem;text-transform:uppercase;line-height:1.05;letter-spacing:0.5px;margin-bottom:1.4rem;max-width:760px;}
.hero-title span{color:var(--mustard);}
.hero-desc{font-size:1.05rem;color:var(--cream-dim);max-width:460px;margin-bottom:2rem;}

.wheel-section{display:flex;justify-content:center;margin:3rem 0;}
.genre-wheel{position:relative;width:280px;height:280px;border-radius:50%;background:var(--black-card);border:3px solid var(--line);transition:transform 0.8s cubic-bezier(0.16,1,0.3,1);}
.wheel-segment{position:absolute;width:50%;height:50%;display:flex;align-items:flex-start;justify-content:center;padding-top:1.2rem;cursor:pointer;font-family:var(--display);font-size:0.85rem;text-transform:uppercase;color:var(--cream-dim);transition:color 0.3s ease;}
.wheel-segment:hover,.wheel-segment.active{color:var(--mustard);}
.wheel-center{position:absolute;top:50%;left:50%;width:70px;height:70px;background:var(--mustard);border-radius:50%;transform:translate(-50%,-50%);display:flex;align-items:center;justify-content:center;font-size:1.8rem;box-shadow:0 0 0 6px var(--black),0 0 0 9px var(--line);}

.crate-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1.4rem;margin-top:1rem;}
.record-card{background:var(--black-card);border-radius:var(--radius-lg);overflow:hidden;border:1px solid var(--line);transition:var(--transition);}
.record-card:hover{transform:translateY(-5px);box-shadow:var(--shadow-lg);}
.record-cover{aspect-ratio:1;background:linear-gradient(150deg,var(--orange),#8C3D1A);display:flex;align-items:center;justify-content:center;font-size:2.5rem;position:relative;}
.record-info{padding:1.2rem;}
.record-artist{font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;color:var(--mustard);margin-bottom:0.3rem;font-weight:700;}
.record-title{font-family:var(--display);font-size:1.05rem;margin-bottom:0.6rem;text-transform:uppercase;}
.record-footer{display:flex;align-items:center;justify-content:space-between;}
.record-price{font-weight:700;}
.add-btn{background:var(--black);border:1px solid var(--line);color:var(--cream);font-size:0.74rem;font-weight:700;padding:0.45rem 0.8rem;border-radius:6px;transition:var(--transition);text-transform:uppercase;}
.add-btn:hover{background:var(--mustard);color:var(--black);border-color:var(--mustard);}

.arrivals-strip{display:flex;gap:1.2rem;overflow-x:auto;margin-top:2.5rem;padding-bottom:0.5rem;}
.arrival-card{min-width:160px;flex-shrink:0;}
.arrival-cover{aspect-ratio:1;border-radius:var(--radius);background:linear-gradient(150deg,var(--mustard),#A87B1F);display:flex;align-items:center;justify-content:center;font-size:2rem;margin-bottom:0.7rem;}
.arrival-name{font-size:0.85rem;font-weight:700;}

.about-grid{display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center;}
.about-visual{aspect-ratio:4/3;border-radius:var(--radius-lg);background:linear-gradient(150deg,var(--black-card),var(--black-light));border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:4rem;}
.about-text p{color:var(--cream-dim);margin-bottom:1.1rem;}

.footer{border-top:1px solid var(--line);padding:3rem 0;display:flex;justify-content:space-between;align-items:center;font-size:0.82rem;color:var(--cream-dim);}

.cart-drawer{position:fixed;top:0;right:0;height:100%;width:400px;background:var(--black-light);z-index:1100;transform:translateX(100%);transition:transform 0.35s cubic-bezier(0.16,1,0.3,1);display:flex;flex-direction:column;border-left:1px solid var(--line);}
.cart-drawer.open{transform:translateX(0);}
.cart-header{display:flex;justify-content:space-between;align-items:center;padding:1.5rem;border-bottom:1px solid var(--line);}
.cart-close{background:var(--black-card);border:none;width:30px;height:30px;border-radius:50%;color:var(--cream);font-size:1.1rem;}
.cart-items{flex:1;overflow-y:auto;padding:1.5rem;}
.cart-empty{display:flex;align-items:center;justify-content:center;height:100%;color:var(--cream-dim);text-align:center;}
.cart-row{display:flex;gap:1rem;padding-bottom:1.1rem;margin-bottom:1.1rem;border-bottom:1px solid var(--line);}
.qty-btn{width:22px;height:22px;border-radius:6px;border:1px solid var(--line);background:var(--black-card);color:var(--cream);}
.cart-footer{padding:1.5rem;border-top:1px solid var(--line);}
.cart-total-row{display:flex;justify-content:space-between;margin-bottom:0.9rem;font-weight:700;}
.cart-backdrop{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:1050;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.cart-backdrop.active{opacity:1;pointer-events:auto;}

.reveal{opacity:0;transform:translateY(26px);transition:all 0.65s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .crate-grid{grid-template-columns:repeat(2,1fr);}
  .about-grid{grid-template-columns:1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--black);flex-direction:column;justify-content:center;gap:2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.8rem;}
  .cart-drawer{width:100%;}
}
@media (max-width:600px){ .crate-grid{grid-template-columns:1fr;} .footer{flex-direction:column;gap:0.8rem;text-align:center;} .genre-wheel{width:220px;height:220px;} }
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Static <span>&amp;</span> Soul</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero">Home</a></li>
      <li><a href="#crate">The Crate</a></li>
      <li><a href="#about">About</a></li>
    </ul></nav>
    <div style="display:flex;align-items:center;gap:0.6rem;">
      <button class="cart-btn" id="cart-btn" aria-label="Open cart">🎧<span class="cart-badge hidden" id="cart-badge">0</span></button>
      <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <span class="section-label">New &amp; Used, Curated by Ear</span>
    <h1 class="hero-title">Dig the crate.<br>Find the <span>one.</span></h1>
    <p class="hero-desc">Three thousand records, hand-graded, and a turntable up front so you never buy a record sight-unheard.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;">
      <a href="#crate" class="btn btn-primary">Browse the Crate</a>
      <a href="#about" class="btn btn-outline">Our Story</a>
    </div>
  </div>
</section>

<section class="section" id="crate">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Spin the Wheel</span>
      <h2 class="section-title">Pick a genre</h2>
      <p class="section-subtitle">Click a slice to filter the crate below.</p>
    </div>
    <div class="wheel-section">
      <div class="genre-wheel" id="genre-wheel">
        <div class="wheel-segment active" data-genre="all" style="top:0;left:0;text-align:center;">ALL</div>
        <div class="wheel-segment" data-genre="soul" style="top:0;left:50%;text-align:center;">SOUL</div>
        <div class="wheel-segment" data-genre="jazz" style="top:50%;left:0;text-align:center;align-items:flex-end;padding-top:0;padding-bottom:1.2rem;">JAZZ</div>
        <div class="wheel-segment" data-genre="rock" style="top:50%;left:50%;text-align:center;align-items:flex-end;padding-top:0;padding-bottom:1.2rem;">ROCK</div>
        <div class="wheel-center">🎵</div>
      </div>
    </div>
    <div class="crate-grid" id="crate-grid"></div>
  </div>
</section>

<section class="section" style="background:var(--black-light);">
  <div class="container">
    <div class="reveal"><span class="section-label">Just In</span><h2 class="section-title">New arrivals</h2></div>
    <div class="arrivals-strip">
      <div class="arrival-card"><div class="arrival-cover">💿</div><p class="arrival-name">Midnight Sessions</p></div>
      <div class="arrival-card"><div class="arrival-cover">💿</div><p class="arrival-name">Coastline (Reissue)</p></div>
      <div class="arrival-card"><div class="arrival-cover">💿</div><p class="arrival-name">Brass &amp; Bone</p></div>
      <div class="arrival-card"><div class="arrival-cover">💿</div><p class="arrival-name">Static Bloom</p></div>
    </div>
  </div>
</section>

<section class="section" id="about">
  <div class="container">
    <div class="about-grid">
      <div class="about-visual reveal">📻</div>
      <div class="about-text reveal">
        <span class="section-label">Our Story</span>
        <h2 class="section-title">Twelve years, one block</h2>
        <p>Static &amp; Soul opened in 2014 in the same 800 square feet we're still in today. We grade every used record by ear before it hits the floor, and the listening station up front isn't a gimmick — we want you to hear it before you buy it.</p>
      </div>
    </div>
  </div>
</section>

<footer class="container footer">
  <p>© 2026 Static &amp; Soul Records</p>
  <p>Open Tue–Sun, Noon–8PM</p>
</footer>

<div class="cart-drawer" id="cart-drawer">
  <div class="cart-header"><h3 style="font-family:var(--display);text-transform:uppercase;">Crate</h3><button class="cart-close" id="cart-close" aria-label="Close cart">&times;</button></div>
  <div class="cart-items" id="cart-items"><div class="cart-empty" id="cart-empty"><p>Your crate is empty.</p></div></div>
  <div class="cart-footer" id="cart-footer" style="display:none;">
    <div class="cart-total-row"><span>Total</span><span id="cart-total">$0.00</span></div>
    <button class="btn btn-primary" style="width:100%;justify-content:center;">Checkout</button>
  </div>
</div>
<div class="cart-backdrop" id="cart-backdrop"></div>

<script>
document.addEventListener('DOMContentLoaded', function(){
  const records = [
    { id:1, artist:'Etta Jameson', title:'Velvet Hours', genre:'soul', price:28, icon:'💿' },
    { id:2, artist:'The Hollow Keys', title:'Brass & Bone', genre:'jazz', price:32, icon:'💿' },
    { id:3, artist:'Crater', title:'Static Bloom', genre:'rock', price:24, icon:'💿' },
    { id:4, artist:'Marvin Onyx', title:'Coastline', genre:'soul', price:30, icon:'💿' },
    { id:5, artist:'Lola Vance Trio', title:'Midnight Sessions', genre:'jazz', price:26, icon:'💿' },
    { id:6, artist:'Granite Choir', title:'Open Road', genre:'rock', price:22, icon:'💿' },
    { id:7, artist:'Dune Static', title:'Lo-Fi Pressings Vol. 2', genre:'jazz', price:29, icon:'💿' },
    { id:8, artist:'Reverie', title:'Gold Light', genre:'soul', price:27, icon:'💿' },
  ];
  let cart = [];
  let activeGenre = 'all';
  function escapeHtml(str){ const d=document.createElement('div'); d.textContent=str; return d.innerHTML; }

  function renderCrate(){
    const grid = document.getElementById('crate-grid');
    grid.innerHTML = '';
    const filtered = activeGenre === 'all' ? records : records.filter(r=>r.genre===activeGenre);
    filtered.forEach((r,i)=>{
      const card = document.createElement('div');
      card.className = 'record-card reveal';
      card.style.transitionDelay = (i*50)+'ms';
      card.innerHTML = `
        <div class="record-cover">${r.icon}</div>
        <div class="record-info">
          <p class="record-artist">${escapeHtml(r.artist)}</p>
          <h3 class="record-title">${escapeHtml(r.title)}</h3>
          <div class="record-footer">
            <span class="record-price">$${r.price.toFixed(2)}</span>
            <button class="add-btn" data-id="${r.id}">Add</button>
          </div>
        </div>
      `;
      grid.appendChild(card);
      revealObserver.observe(card);
    });
    grid.querySelectorAll('.add-btn').forEach(btn=>btn.addEventListener('click', ()=>addToCart(parseInt(btn.dataset.id))));
  }

  document.querySelectorAll('.wheel-segment').forEach(seg=>{
    seg.addEventListener('click', ()=>{
      document.querySelectorAll('.wheel-segment').forEach(s=>s.classList.remove('active'));
      seg.classList.add('active');
      activeGenre = seg.dataset.genre;
      const rotations = { all:0, soul:-90, jazz:180, rock:90 };
      document.getElementById('genre-wheel').style.transform = `rotate(${rotations[activeGenre]}deg)`;
      document.querySelectorAll('.wheel-segment').forEach(s=>{ s.style.transform = `rotate(${-rotations[activeGenre]}deg)`; });
      renderCrate();
    });
  });

  function addToCart(id){
    const record = records.find(r=>r.id===id);
    const existing = cart.find(i=>i.id===id);
    if (existing) existing.qty+=1; else cart.push({...record, qty:1});
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
        <div style="flex:1;"><p style="font-weight:700;font-size:0.9rem;">${escapeHtml(item.title)}</p>
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

  renderCrate();
});
</script>
</body>
</html>
```
