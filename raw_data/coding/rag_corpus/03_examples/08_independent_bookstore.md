# Example — Independent Bookstore (Vanilla CSS Architecture)

Tags: example, full-site, bookstore, books, independent-retail, vanilla-css, dark-theme, maroon, cream, serif, editorial, staff-picks

Niche: independent neighborhood bookstore.
Architecture: vanilla CSS, custom properties.
Palette: deep maroon canvas (#2B1018), warm cream text (#F2E8D8), brass accent (#C9A35C).
Signature element: a staff-picks "shelf" — a horizontally scrolling row of book
spines with staff name and one-line pitch on hover/tap.
Sections: header, hero, staff-picks shelf, event calendar strip, sections-by-genre
grid, newsletter, footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Marlowe &amp; Sons Booksellers | Independent Bookstore</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Karla:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --maroon:#2B1018; --maroon-light:#3A1721; --maroon-lighter:#4A1F2D; --line:#5C2A39;
  --cream:#F2E8D8; --cream-dim:#C9AFA0; --brass:#C9A35C; --brass-hover:#DBB873;
  --radius:8px; --radius-lg:14px;
  --transition: all 0.35s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow-lg: 0 20px 50px rgba(0,0,0,0.45);
  --serif:'Libre Caslon Text', serif; --sans:'Karla', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--maroon);color:var(--cream);line-height:1.7;overflow-x:hidden;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;} button{cursor:pointer;font-family:inherit;}
.container{max-width:1180px;margin:0 auto;padding:0 2rem;}
.section{padding:6rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.76rem;color:var(--brass);margin-bottom:1rem;font-weight:600;}
.section-title{font-family:var(--serif);font-size:2.5rem;font-weight:700;margin-bottom:1rem;}
.section-subtitle{color:var(--cream-dim);font-size:1.02rem;max-width:560px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.85rem 2rem;border:none;border-radius:var(--radius);font-size:0.88rem;font-weight:700;transition:var(--transition);}
.btn-primary{background:var(--brass);color:var(--maroon);}
.btn-primary:hover{background:var(--brass-hover);transform:translateY(-2px);}
.btn-outline{background:transparent;color:var(--cream);border:1.5px solid var(--line);}
.btn-outline:hover{border-color:var(--brass);color:var(--brass);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.4rem 0;transition:var(--transition);}
.header.scrolled{background:rgba(43,16,24,0.94);backdrop-filter:blur(14px);padding:1rem 0;box-shadow:0 2px 24px rgba(0,0,0,0.3);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--serif);font-size:1.4rem;font-weight:700;font-style:italic;}
.logo span{color:var(--brass);font-style:normal;}
.nav-list{display:flex;list-style:none;gap:2.2rem;align-items:center;}
.nav-list a{font-size:0.84rem;font-weight:600;letter-spacing:0.5px;position:relative;padding:0.2rem 0;}
.nav-list a::after{content:"";position:absolute;bottom:-2px;left:0;width:0;height:2px;background:var(--brass);transition:var(--transition);}
.nav-list a:hover::after,.nav-list a.active::after{width:100%;}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:22px;height:2px;background:var(--cream);transition:var(--transition);}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:86vh;display:flex;align-items:center;padding-top:6rem;background:linear-gradient(160deg,var(--maroon) 0%,var(--maroon-light) 60%,var(--maroon) 100%);}
.hero-grid{display:grid;grid-template-columns:1.1fr 0.9fr;gap:3.5rem;align-items:center;}
.hero-label{display:inline-block;padding:0.4rem 1rem;border:1px solid rgba(201,163,92,0.4);border-radius:30px;font-size:0.76rem;letter-spacing:2px;text-transform:uppercase;color:var(--brass);margin-bottom:1.8rem;}
.hero-title{font-family:var(--serif);font-size:3.4rem;font-weight:700;line-height:1.15;margin-bottom:1.3rem;}
.hero-title em{font-style:italic;color:var(--brass);}
.hero-desc{font-size:1.05rem;color:var(--cream-dim);max-width:440px;margin-bottom:2rem;}
.hero-visual{aspect-ratio:3/4;border-radius:var(--radius-lg);background:linear-gradient(150deg,var(--maroon-lighter),var(--maroon-light));border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:5rem;}

.shelf-wrap{margin-top:3rem;overflow-x:auto;padding-bottom:1rem;}
.shelf{display:flex;gap:1.2rem;width:max-content;}
.book-card{width:180px;flex-shrink:0;cursor:pointer;}
.book-spine{aspect-ratio:2/3;border-radius:6px;background:linear-gradient(160deg,var(--maroon-lighter),var(--maroon-light));border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:2.5rem;margin-bottom:0.9rem;position:relative;overflow:hidden;transition:var(--transition);}
.book-card:hover .book-spine{transform:translateY(-6px);border-color:var(--brass);}
.book-pick-overlay{position:absolute;inset:0;background:rgba(43,16,24,0.95);display:flex;align-items:center;justify-content:center;padding:1rem;text-align:center;opacity:0;transition:opacity 0.3s ease;}
.book-card:hover .book-pick-overlay{opacity:1;}
.book-pick-overlay p{font-size:0.78rem;font-style:italic;font-family:var(--serif);}
.book-title{font-family:var(--serif);font-size:0.95rem;font-weight:700;margin-bottom:0.2rem;}
.book-staff{font-size:0.76rem;color:var(--brass);}

.events-strip{display:flex;gap:1.2rem;overflow-x:auto;margin-top:2.5rem;padding-bottom:0.5rem;}
.event-card{background:var(--maroon-light);border:1px solid var(--line);border-radius:var(--radius);padding:1.4rem;min-width:240px;flex-shrink:0;}
.event-date{font-family:var(--serif);color:var(--brass);font-size:0.85rem;margin-bottom:0.5rem;}
.event-title{font-weight:700;margin-bottom:0.3rem;}
.event-desc{font-size:0.85rem;color:var(--cream-dim);}

.genre-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1.3rem;margin-top:2.5rem;}
.genre-card{background:var(--maroon-light);border:1px solid var(--line);border-radius:var(--radius-lg);padding:2rem 1.5rem;text-align:center;transition:var(--transition);}
.genre-card:hover{transform:translateY(-5px);border-color:var(--brass);}
.genre-icon{font-size:2rem;margin-bottom:0.8rem;}
.genre-card h4{font-family:var(--serif);font-size:1.05rem;}

.newsletter-section{background:var(--maroon-light);text-align:center;border-top:1px solid var(--line);border-bottom:1px solid var(--line);}
.newsletter-section h3{font-family:var(--serif);font-size:1.9rem;margin-bottom:0.7rem;}
.newsletter-section p{color:var(--cream-dim);margin-bottom:1.8rem;}
.newsletter-form{display:flex;gap:0.7rem;max-width:400px;margin:0 auto;flex-wrap:wrap;justify-content:center;}
.newsletter-form input{flex:1;min-width:200px;padding:0.8rem 1rem;border-radius:var(--radius);border:1px solid var(--line);background:var(--maroon);color:var(--cream);font-family:inherit;}
.newsletter-form button{background:var(--brass);color:var(--maroon);border:none;padding:0.8rem 1.5rem;border-radius:var(--radius);font-weight:700;}
.newsletter-note{margin-top:0.9rem;font-size:0.8rem;color:var(--cream-dim);}

.footer{padding:3.2rem 0 0;}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:3rem;padding-bottom:2.2rem;}
.footer-col h4{font-size:0.78rem;text-transform:uppercase;letter-spacing:1.3px;margin-bottom:1rem;color:var(--brass);}
.footer-col a,.footer-col p{display:block;color:var(--cream-dim);font-size:0.86rem;margin-bottom:0.7rem;}
.footer-col a:hover{color:var(--brass);}
.footer-bottom{border-top:1px solid var(--line);padding:1.2rem 0;display:flex;justify-content:space-between;font-size:0.8rem;color:var(--cream-dim);}

.reveal{opacity:0;transform:translateY(26px);transition:all 0.65s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .hero-grid{grid-template-columns:1fr;}
  .genre-grid{grid-template-columns:repeat(2,1fr);}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--maroon);flex-direction:column;justify-content:center;gap:2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.4rem;}
  .footer-grid{grid-template-columns:1fr;}
}
@media (max-width:600px){ .footer-bottom{flex-direction:column;gap:0.6rem;text-align:center;} }
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Marlowe <span>&amp;</span> Sons</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero" class="active">Home</a></li>
      <li><a href="#picks">Staff Picks</a></li>
      <li><a href="#events">Events</a></li>
      <li><a href="#sections">Browse</a></li>
    </ul></nav>
    <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <span class="hero-label">Independent Since 1987</span>
        <h1 class="hero-title">Browse slower.<br><em>Read better.</em></h1>
        <p class="hero-desc">Three rooms, twelve thousand titles, and a staff that will absolutely talk you out of buying the wrong book.</p>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;">
          <a href="#picks" class="btn btn-primary">See Staff Picks</a>
          <a href="#events" class="btn btn-outline">Upcoming Events</a>
        </div>
      </div>
      <div class="hero-visual">📚</div>
    </div>
  </div>
</section>

<section class="section" id="picks">
  <div class="container">
    <div class="reveal">
      <span class="section-label">This Month's Shelf</span>
      <h2 class="section-title">Staff picks</h2>
      <p class="section-subtitle">Hover (or tap) a spine to see why we picked it.</p>
    </div>
    <div class="shelf-wrap">
      <div class="shelf" id="shelf"></div>
    </div>
  </div>
</section>

<section class="section" id="events" style="background:var(--maroon-light);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">What's On</span>
      <h2 class="section-title">Upcoming events</h2>
    </div>
    <div class="events-strip">
      <div class="event-card"><p class="event-date">JUL 8, 7PM</p><p class="event-title">Author Talk: Reyna Ortiz</p><p class="event-desc">Debut novelist discusses her new collection of linked stories.</p></div>
      <div class="event-card"><p class="event-date">JUL 15, 6PM</p><p class="event-title">Poetry Open Mic</p><p class="event-desc">Sign up at the counter — five minutes, any style.</p></div>
      <div class="event-card"><p class="event-date">JUL 22, 11AM</p><p class="event-title">Storytime &amp; Craft</p><p class="event-desc">For ages 4-7, with a take-home craft each week.</p></div>
      <div class="event-card"><p class="event-date">AUG 2, 7PM</p><p class="event-title">Book Club: July Pick</p><p class="event-desc">This month's selection is on the staff picks table.</p></div>
    </div>
  </div>
</section>

<section class="section" id="sections">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Browse</span>
      <h2 class="section-title">Wander a section</h2>
    </div>
    <div class="genre-grid">
      <div class="genre-card reveal"><div class="genre-icon">🔍</div><h4>Mystery</h4></div>
      <div class="genre-card reveal"><div class="genre-icon">🚀</div><h4>Sci-Fi</h4></div>
      <div class="genre-card reveal"><div class="genre-icon">📜</div><h4>History</h4></div>
      <div class="genre-card reveal"><div class="genre-icon">🌙</div><h4>Poetry</h4></div>
    </div>
  </div>
</section>

<section class="section newsletter-section">
  <div class="container">
    <h3>Get the staff picks letter</h3>
    <p>One email a month, written by the staff, never by marketing.</p>
    <form class="newsletter-form" id="newsletter-form">
      <input type="email" id="newsletter-email" placeholder="you@example.com" required>
      <button type="submit">Subscribe</button>
    </form>
    <p class="newsletter-note" id="newsletter-note">Unsubscribe anytime, we won't take it personally.</p>
  </div>
</section>

<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-col"><h4>Marlowe &amp; Sons</h4><p>An independent bookstore in three rooms, open since 1987.</p></div>
    <div class="footer-col"><h4>Visit</h4><a href="#">Hours &amp; Directions</a><a href="#events">Events Calendar</a><a href="#">Gift Cards</a></div>
    <div class="footer-col"><h4>Shop</h4><a href="#picks">Staff Picks</a><a href="#sections">Browse Sections</a><a href="#">Special Orders</a></div>
  </div>
  <div class="container footer-bottom"><p>© 2026 Marlowe &amp; Sons Booksellers.</p><p>Shop indie, read deep.</p></div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function(){
  const books = [
    { title:'The Quiet Atlas', staff:'Pick by Jo', icon:'📘', pitch:'"A debut that made me cancel plans to finish it in one sitting."' },
    { title:'Salt &amp; Static', staff:'Pick by Mara', icon:'📗', pitch:'"Sharp, funny, and devastating in the last twenty pages."' },
    { title:'The Long Ferry', staff:'Pick by Theo', icon:'📙', pitch:'"Slow-burn literary fiction for readers who liked Sally Rooney."' },
    { title:'Field Notes on Leaving', staff:'Pick by Jo', icon:'📕', pitch:'"Essays that read like letters from a friend who left town."' },
    { title:'The Cartographer\\'s Wife', staff:'Pick by Mara', icon:'📔', pitch:'"Historical fiction with an ending I still think about."' },
    { title:'Static Bloom', staff:'Pick by Theo', icon:'📒', pitch:'"Poetry collection that reads fast but lingers for weeks."' },
  ];
  function escapeHtml(str){ const d=document.createElement('div'); d.textContent=str; return d.innerHTML; }
  function renderShelf(){
    const shelf = document.getElementById('shelf');
    shelf.innerHTML = '';
    books.forEach(b=>{
      const card = document.createElement('div');
      card.className = 'book-card';
      card.innerHTML = `
        <div class="book-spine">
          ${b.icon}
          <div class="book-pick-overlay"><p>${escapeHtml(b.pitch)}</p></div>
        </div>
        <p class="book-title">${escapeHtml(b.title)}</p>
        <p class="book-staff">${escapeHtml(b.staff)}</p>
      `;
      shelf.appendChild(card);
    });
  }
  renderShelf();

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

  document.getElementById('newsletter-form').addEventListener('submit', (e)=>{
    e.preventDefault();
    document.getElementById('newsletter-note').textContent = "You're on the list — first letter goes out next month.";
    e.target.reset();
  });
});
</script>
</body>
</html>
```
