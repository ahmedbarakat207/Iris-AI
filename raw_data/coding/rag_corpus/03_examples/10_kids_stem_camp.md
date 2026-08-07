# Example — Children's STEM Summer Camp (Vanilla CSS Architecture, Light Mode)

Tags: example, full-site, kids, stem, summer-camp, education, vanilla-css, light-theme, playful, bright-colors, multicolor, age-track-selector

Niche: summer STEM day camp for kids ages 6-14.
Architecture: vanilla CSS, custom properties, light mode.
Palette: bright white canvas (#FFFFFF), saturated multicolor accents (coral #FF6B5B,
sky blue #3EC1D3, sunny yellow #FFC93C, grass green #4CAF6D) — distinct per age track,
rounded playful sans display type.
Signature element: an age-track selector (Explorers 6-8 / Builders 9-11 / Inventors
12-14) that swaps the visible curriculum card set and the accent color used on buttons.
Sections: header, hero, age-track selector + curriculum cards, weekly themes strip,
safety/staff-ratio reassurance section, registration CTA, footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spark Lab Camps | STEM Summer Camp for Kids 6-14</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --white:#FFFFFF; --offwhite:#F7F9FC; --line:#E7ECF2;
  --ink:#26324A; --ink-dim:#6B7794;
  --coral:#FF6B5B; --sky:#3EC1D3; --yellow:#FFC93C; --green:#4CAF6D;
  --active:#FF6B5B; --active-dim:rgba(255,107,91,0.12);
  --radius:18px; --radius-lg:26px;
  --transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  --shadow: 0 10px 28px rgba(38,50,74,0.08); --shadow-lg: 0 20px 48px rgba(38,50,74,0.12);
  --display:'Baloo 2', sans-serif; --sans:'Nunito', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--white);color:var(--ink);line-height:1.65;overflow-x:hidden;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;} button{cursor:pointer;font-family:inherit;}
.container{max-width:1160px;margin:0 auto;padding:0 2rem;}
.section{padding:5.5rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:2px;font-size:0.78rem;color:var(--active);margin-bottom:0.8rem;font-weight:800;transition:color 0.3s ease;}
.section-title{font-family:var(--display);font-size:2.5rem;font-weight:700;margin-bottom:1rem;}
.section-subtitle{color:var(--ink-dim);font-size:1.02rem;max-width:540px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.9rem 2.1rem;border:none;border-radius:50px;font-size:0.92rem;font-weight:800;transition:var(--transition);}
.btn-primary{background:var(--active);color:#fff;}
.btn-primary:hover{transform:translateY(-3px) scale(1.02);box-shadow:var(--shadow-lg);}
.btn-outline{background:var(--white);color:var(--ink);border:2px solid var(--line);}
.btn-outline:hover{border-color:var(--active);color:var(--active);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.2rem 0;background:rgba(255,255,255,0.9);backdrop-filter:blur(10px);transition:var(--transition);border-bottom:1px solid transparent;}
.header.scrolled{box-shadow:0 2px 20px rgba(38,50,74,0.06);border-bottom-color:var(--line);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--display);font-size:1.5rem;font-weight:800;display:flex;align-items:center;gap:0.5rem;}
.nav-list{display:flex;list-style:none;gap:2rem;align-items:center;}
.nav-list a{font-size:0.88rem;font-weight:700;}
.nav-list a:hover{color:var(--active);}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:24px;height:3px;border-radius:2px;background:var(--ink);transition:var(--transition);}
.overlay{position:fixed;inset:0;background:rgba(38,50,74,0.4);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:88vh;display:flex;align-items:center;padding-top:6rem;background:radial-gradient(circle at 85% 15%, rgba(62,193,211,0.08), transparent 50%), radial-gradient(circle at 10% 85%, rgba(255,201,60,0.1), transparent 50%);}
.hero-grid{display:grid;grid-template-columns:1.05fr 0.95fr;gap:3.5rem;align-items:center;}
.hero-label{display:inline-flex;align-items:center;gap:0.5rem;padding:0.5rem 1.1rem;background:var(--active-dim);border-radius:50px;font-size:0.8rem;font-weight:800;color:var(--active);margin-bottom:1.6rem;transition:var(--transition);}
.hero-title{font-family:var(--display);font-size:3.3rem;font-weight:700;line-height:1.1;margin-bottom:1.3rem;}
.hero-title span{color:var(--active);transition:color 0.3s ease;}
.hero-desc{font-size:1.05rem;color:var(--ink-dim);max-width:460px;margin-bottom:2rem;}
.hero-visual{aspect-ratio:1;border-radius:var(--radius-lg);background:linear-gradient(150deg,#FFF3D6,#FFE0D6);display:flex;align-items:center;justify-content:center;font-size:5.5rem;box-shadow:var(--shadow-lg);}

.track-tabs{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin:2.5rem 0;}
.track-tab{background:var(--offwhite);border:2px solid var(--line);border-radius:50px;padding:0.9rem 1.8rem;font-weight:800;font-size:0.92rem;transition:var(--transition);display:flex;align-items:center;gap:0.6rem;}
.track-tab .age-pill{font-size:0.74rem;background:var(--line);padding:0.2rem 0.6rem;border-radius:20px;font-weight:700;}
.track-tab.active{color:#fff;border-color:transparent;}
.track-tab.active .age-pill{background:rgba(255,255,255,0.25);}

.curriculum-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;}
.curriculum-card{background:var(--offwhite);border-radius:var(--radius-lg);padding:2rem;border:1px solid var(--line);transition:var(--transition);}
.curriculum-card:hover{transform:translateY(-5px);box-shadow:var(--shadow-lg);}
.curriculum-icon{font-size:2.3rem;margin-bottom:1rem;}
.curriculum-card h4{font-family:var(--display);font-size:1.2rem;margin-bottom:0.5rem;}
.curriculum-card p{color:var(--ink-dim);font-size:0.92rem;}

.weeks-strip{display:flex;gap:1.2rem;overflow-x:auto;margin-top:2.5rem;padding-bottom:0.5rem;}
.week-card{background:var(--white);border:2px solid var(--line);border-radius:var(--radius);padding:1.4rem;min-width:200px;flex-shrink:0;text-align:center;}
.week-num{font-family:var(--display);font-size:0.8rem;color:var(--active);font-weight:800;margin-bottom:0.5rem;}
.week-theme{font-weight:800;font-size:0.95rem;}

.safety-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-top:2.5rem;text-align:center;}
.safety-stat{font-family:var(--display);font-size:2.4rem;color:var(--active);margin-bottom:0.4rem;}
.safety-label{font-size:0.88rem;color:var(--ink-dim);font-weight:700;}

.cta-section{background:linear-gradient(120deg,var(--coral),var(--yellow));text-align:center;border-radius:var(--radius-lg);padding:3.5rem 2rem;margin:0 2rem;}
.cta-section h3{font-family:var(--display);font-size:2.1rem;color:#fff;margin-bottom:0.8rem;}
.cta-section p{color:rgba(255,255,255,0.9);margin-bottom:1.8rem;}
.cta-section .btn{background:#fff;color:var(--coral);}

.footer{padding:3.5rem 0 0;border-top:1px solid var(--line);margin-top:4rem;}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:3rem;padding-bottom:2.2rem;}
.footer-col h4{font-size:0.8rem;text-transform:uppercase;letter-spacing:1.3px;margin-bottom:1rem;color:var(--ink-dim);}
.footer-col a,.footer-col p{display:block;color:var(--ink-dim);font-size:0.88rem;margin-bottom:0.7rem;}
.footer-col a:hover{color:var(--active);}
.footer-bottom{border-top:1px solid var(--line);padding:1.2rem 2rem;display:flex;justify-content:space-between;font-size:0.82rem;color:var(--ink-dim);}

.reveal{opacity:0;transform:translateY(24px);transition:all 0.6s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .hero-grid{grid-template-columns:1fr;}
  .curriculum-grid,.safety-grid{grid-template-columns:1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--white);flex-direction:column;justify-content:center;gap:2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.3rem;}
  .footer-grid{grid-template-columns:1fr;}
}
@media (max-width:600px){ .footer-bottom{flex-direction:column;gap:0.6rem;text-align:center;} .cta-section{margin:0 1rem;} }
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">⚡ Spark Lab</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero">Home</a></li>
      <li><a href="#tracks">Camp Tracks</a></li>
      <li><a href="#weeks">Weekly Themes</a></li>
      <li><a href="#safety">Safety</a></li>
    </ul></nav>
    <div style="display:flex;align-items:center;gap:1rem;">
      <a href="#cta" class="btn btn-primary" style="padding:0.7rem 1.5rem;font-size:0.85rem;">Register</a>
      <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <span class="hero-label" id="hero-badge">🚀 Now Enrolling for Summer</span>
        <h1 class="hero-title">Camp where kids<br>build <span id="hero-accent-word">robots</span>, not boredom.</h1>
        <p class="hero-desc">Hands-on STEM camp for ages 6-14 — coding, robotics, and engineering, taught by real engineers who actually like kids.</p>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;">
          <a href="#cta" class="btn btn-primary">Reserve a Spot</a>
          <a href="#tracks" class="btn btn-outline">See Camp Tracks</a>
        </div>
      </div>
      <div class="hero-visual">🤖</div>
    </div>
  </div>
</section>

<section class="section" id="tracks">
  <div class="container">
    <div class="reveal" style="text-align:center;">
      <span class="section-label">Pick a Track</span>
      <h2 class="section-title">Three camps, three age groups</h2>
      <p class="section-subtitle" style="margin:0 auto;">Tap an age group to see that week's curriculum.</p>
    </div>
    <div class="track-tabs" id="track-tabs">
      <button class="track-tab active" data-track="explorers" style="background:var(--coral);color:#fff;border-color:transparent;">🔍 Explorers <span class="age-pill">6-8</span></button>
      <button class="track-tab" data-track="builders">🔧 Builders <span class="age-pill">9-11</span></button>
      <button class="track-tab" data-track="inventors">💡 Inventors <span class="age-pill">12-14</span></button>
    </div>
    <div class="curriculum-grid" id="curriculum-grid"></div>
  </div>
</section>

<section class="section" id="weeks" style="background:var(--offwhite);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">This Summer</span>
      <h2 class="section-title">Weekly themes</h2>
    </div>
    <div class="weeks-strip">
      <div class="week-card"><p class="week-num">WEEK 1</p><p class="week-theme">🚀 Space &amp; Rockets</p></div>
      <div class="week-card"><p class="week-num">WEEK 2</p><p class="week-theme">🤖 Robotics</p></div>
      <div class="week-card"><p class="week-num">WEEK 3</p><p class="week-theme">🎮 Game Design</p></div>
      <div class="week-card"><p class="week-num">WEEK 4</p><p class="week-theme">🌱 Eco Engineering</p></div>
      <div class="week-card"><p class="week-num">WEEK 5</p><p class="week-theme">⚡ Circuits &amp; Power</p></div>
    </div>
  </div>
</section>

<section class="section" id="safety">
  <div class="container">
    <div class="reveal" style="text-align:center;">
      <span class="section-label">Parents, Read This</span>
      <h2 class="section-title">Safety is non-negotiable</h2>
    </div>
    <div class="safety-grid">
      <div class="reveal"><p class="safety-stat">1:8</p><p class="safety-label">Staff-to-camper ratio</p></div>
      <div class="reveal"><p class="safety-stat">100%</p><p class="safety-label">Background-checked staff</p></div>
      <div class="reveal"><p class="safety-stat">12yrs</p><p class="safety-label">Running summer camps</p></div>
    </div>
  </div>
</section>

<section class="section" id="cta">
  <div class="container">
    <div class="cta-section reveal">
      <h3>Spots fill by early May</h3>
      <p>Register now to lock in your child's preferred week and track.</p>
      <a href="#" class="btn">Start Registration</a>
    </div>
  </div>
</section>

<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-col"><h4>Spark Lab Camps</h4><p>Hands-on STEM summer camp for kids 6-14, run by real engineers.</p></div>
    <div class="footer-col"><h4>Camp</h4><a href="#tracks">Camp Tracks</a><a href="#weeks">Weekly Themes</a><a href="#safety">Safety Info</a></div>
    <div class="footer-col"><h4>Families</h4><a href="#">FAQ</a><a href="#">Financial Aid</a><a href="#">Contact Us</a></div>
  </div>
  <div class="container footer-bottom"><p>© 2026 Spark Lab Camps.</p><p>Building curious minds since 2014.</p></div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function(){
  const tracks = {
    explorers: { color:'#FF6B5B', word:'robots', curriculum:[
      { icon:'🧱', title:'LEGO Robotics', desc:'Build and program simple robots using block-based coding.' },
      { icon:'🔬', title:'Mini Science Lab', desc:'Hands-on experiments with everyday kitchen-cabinet materials.' },
      { icon:'🎨', title:'Design Thinking', desc:'Invent solutions to silly problems using the engineering process.' },
    ]},
    builders: { color:'#3EC1D3', word:'apps', curriculum:[
      { icon:'💻', title:'Intro to Scratch Coding', desc:'Build playable games and animations with visual block coding.' },
      { icon:'⚙️', title:'Circuit Building', desc:'Wire real circuits and learn how electricity actually moves.' },
      { icon:'🏗️', title:'Bridge Engineering', desc:'Design, build, and stress-test bridges out of recycled materials.' },
    ]},
    inventors: { color:'#4CAF6D', word:'inventions', curriculum:[
      { icon:'🐍', title:'Python Fundamentals', desc:'Write real, text-based code to build small games and tools.' },
      { icon:'🦾', title:'Advanced Robotics', desc:'Program sensor-driven robots to navigate mazes autonomously.' },
      { icon:'🚀', title:'Capstone Invention', desc:'Design an original invention and pitch it on Demo Day.' },
    ]}
  };

  function renderCurriculum(trackKey){
    const t = tracks[trackKey];
    const grid = document.getElementById('curriculum-grid');
    grid.innerHTML = '';
    t.curriculum.forEach((c,i)=>{
      const card = document.createElement('div');
      card.className = 'curriculum-card reveal';
      card.style.transitionDelay = (i*70)+'ms';
      card.innerHTML = `<div class="curriculum-icon">${c.icon}</div><h4>${c.title}</h4><p>${c.desc}</p>`;
      grid.appendChild(card);
      revealObserver.observe(card);
    });
    document.getElementById('hero-accent-word').textContent = t.word;
    document.documentElement.style.setProperty('--active', t.color);
    document.documentElement.style.setProperty('--active-dim', t.color + '1F');
  }

  document.querySelectorAll('.track-tab').forEach(tab=>{
    tab.addEventListener('click', ()=>{
      document.querySelectorAll('.track-tab').forEach(tb=>{ tb.classList.remove('active'); tb.style.background=''; tb.style.color=''; tb.style.borderColor=''; });
      tab.classList.add('active');
      const color = tracks[tab.dataset.track].color;
      tab.style.background = color; tab.style.color = '#fff'; tab.style.borderColor = 'transparent';
      renderCurriculum(tab.dataset.track);
    });
  });

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

  renderCurriculum('explorers');
});
</script>
</body>
</html>
```
