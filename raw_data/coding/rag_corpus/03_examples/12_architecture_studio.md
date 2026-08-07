# Example — Architecture & Interior Design Studio (Vanilla CSS Architecture)

Tags: example, full-site, architecture, interior-design, studio, portfolio, vanilla-css, light-theme, concrete-gray, minimal, before-after-slider

Niche: architecture and interior design studio portfolio.
Architecture: vanilla CSS, custom properties, light/minimal mode.
Palette: warm white canvas (#FAFAF8), concrete gray accent (#7A7670), near-black text.
Signature element: a draggable before/after renovation slider (mouse + touch) using a
clip-path reveal, no library.
Sections: header, hero, before/after slider, project grid, philosophy statement,
services list, contact, footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Halden Studio | Architecture &amp; Interior Design</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Neue+Montreal:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --white:#FAFAF8; --white-card:#FFFFFF; --line:#E2E0D9;
  --ink:#191815; --ink-dim:#6E6A62; --concrete:#7A7670; --concrete-dark:#5C594F;
  --radius:2px; --radius-lg:4px;
  --transition: all 0.4s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow-lg: 0 24px 60px rgba(25,24,21,0.1);
  --sans:'Inter', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--white);color:var(--ink);line-height:1.7;overflow-x:hidden;font-weight:300;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;} button{cursor:pointer;font-family:inherit;}
.container{max-width:1240px;margin:0 auto;padding:0 2.5rem;}
.section{padding:7rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.72rem;color:var(--concrete-dark);margin-bottom:1.2rem;font-weight:600;}
.section-title{font-size:2.4rem;font-weight:300;line-height:1.2;margin-bottom:1rem;letter-spacing:-0.5px;}
.section-title strong{font-weight:600;}
.section-subtitle{color:var(--ink-dim);font-size:1rem;max-width:520px;}
.btn{display:inline-flex;align-items:center;gap:0.6rem;padding:0.95rem 2rem;border:1px solid var(--ink);font-size:0.82rem;font-weight:500;letter-spacing:0.8px;text-transform:uppercase;transition:var(--transition);}
.btn-primary{background:var(--ink);color:var(--white);}
.btn-primary:hover{background:var(--concrete-dark);border-color:var(--concrete-dark);}
.btn-outline{background:transparent;color:var(--ink);}
.btn-outline:hover{background:var(--ink);color:var(--white);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.6rem 0;transition:var(--transition);mix-blend-mode:normal;}
.header.scrolled{background:rgba(250,250,248,0.95);backdrop-filter:blur(10px);padding:1.2rem 0;box-shadow:0 1px 0 var(--line);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-size:1.15rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;}
.nav-list{display:flex;list-style:none;gap:2.5rem;align-items:center;}
.nav-list a{font-size:0.78rem;letter-spacing:1px;text-transform:uppercase;font-weight:500;}
.nav-list a:hover{color:var(--concrete-dark);}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:22px;height:1.5px;background:var(--ink);transition:var(--transition);}
.overlay{position:fixed;inset:0;background:rgba(25,24,21,0.4);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:88vh;display:flex;align-items:center;padding-top:6rem;}
.hero-title{font-size:3.6rem;font-weight:300;line-height:1.1;letter-spacing:-1px;margin-bottom:1.6rem;max-width:780px;}
.hero-title strong{font-weight:600;}
.hero-desc{font-size:1.05rem;color:var(--ink-dim);max-width:480px;margin-bottom:2.2rem;}

.slider-wrap{position:relative;aspect-ratio:16/9;border-radius:var(--radius-lg);overflow:hidden;margin-top:3rem;cursor:ew-resize;user-select:none;box-shadow:var(--shadow-lg);}
.slider-before,.slider-after{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:1rem;font-weight:500;letter-spacing:1px;text-transform:uppercase;color:#fff;}
.slider-before{background:linear-gradient(135deg,#4A4843,#2C2A26);}
.slider-after{background:linear-gradient(135deg,#D9D4C5,#B8B19E);color:var(--ink);clip-path:inset(0 50% 0 0);}
.slider-handle{position:absolute;top:0;bottom:0;left:50%;width:3px;background:#fff;transform:translateX(-50%);box-shadow:0 0 0 1px rgba(0,0,0,0.1);}
.slider-handle::after{content:"⇔";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:46px;height:46px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem;box-shadow:var(--shadow-lg);}
.slider-label{position:absolute;top:1.2rem;font-size:0.72rem;letter-spacing:1.5px;text-transform:uppercase;background:rgba(0,0,0,0.4);padding:0.4rem 0.9rem;border-radius:30px;}
.slider-label.before-label{left:1.2rem;}
.slider-label.after-label{right:1.2rem;background:rgba(255,255,255,0.6);color:var(--ink);}

.project-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;margin-top:3rem;}
.project-card{aspect-ratio:4/3;position:relative;overflow:hidden;background:linear-gradient(150deg,#E8E5DB,#D4D0C2);cursor:pointer;}
.project-overlay{position:absolute;inset:0;background:rgba(25,24,21,0);display:flex;flex-direction:column;justify-content:flex-end;padding:1.4rem;transition:var(--transition);}
.project-card:hover .project-overlay{background:rgba(25,24,21,0.55);}
.project-name{color:#fff;font-size:1rem;font-weight:500;opacity:0;transform:translateY(10px);transition:var(--transition);}
.project-cat{color:rgba(255,255,255,0.7);font-size:0.78rem;opacity:0;transform:translateY(10px);transition:var(--transition);transition-delay:0.05s;}
.project-card:hover .project-name,.project-card:hover .project-cat{opacity:1;transform:translateY(0);}

.philosophy-block{max-width:780px;}
.philosophy-block p{font-size:1.6rem;font-weight:300;line-height:1.5;letter-spacing:-0.3px;}
.philosophy-block strong{font-weight:600;}

.services-list{margin-top:2.5rem;}
.service-row{display:flex;justify-content:space-between;align-items:center;padding:1.8rem 0;border-bottom:1px solid var(--line);transition:var(--transition);}
.service-row:hover{padding-left:1rem;border-color:var(--ink);}
.service-row h4{font-size:1.3rem;font-weight:400;}
.service-row span{color:var(--ink-dim);font-size:0.85rem;}

.contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:4rem;margin-top:2.5rem;}
.contact-detail{margin-bottom:1.6rem;}
.contact-detail span{display:block;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;color:var(--ink-dim);margin-bottom:0.3rem;}
.contact-detail strong{font-size:1.1rem;font-weight:500;}
.form-group{margin-bottom:1.4rem;}
.form-group label{display:block;font-size:0.78rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;color:var(--ink-dim);}
.form-group input,.form-group textarea{width:100%;background:transparent;border:none;border-bottom:1px solid var(--line);padding:0.6rem 0;font-size:0.95rem;font-family:inherit;transition:var(--transition);}
.form-group input:focus,.form-group textarea:focus{outline:none;border-color:var(--ink);}
.form-error{display:block;font-size:0.76rem;color:#A85A4A;margin-top:0.4rem;min-height:1.1em;}
.form-status{margin-top:1rem;font-size:0.85rem;}

.footer{border-top:1px solid var(--line);padding:3rem 0;display:flex;justify-content:space-between;align-items:center;font-size:0.8rem;color:var(--ink-dim);}

.reveal{opacity:0;transform:translateY(24px);transition:all 0.7s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:980px){
  .project-grid{grid-template-columns:repeat(2,1fr);}
  .contact-grid{grid-template-columns:1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--white);flex-direction:column;justify-content:center;gap:2.2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.4rem;}
}
@media (max-width:600px){
  .project-grid{grid-template-columns:1fr;}
  .philosophy-block p{font-size:1.25rem;}
  .footer{flex-direction:column;gap:1rem;text-align:center;}
}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Halden Studio</a>
    <nav><ul class="nav-list" id="nav-list">
      <li><a href="#hero">Studio</a></li>
      <li><a href="#projects">Projects</a></li>
      <li><a href="#services">Services</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul></nav>
    <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <span class="section-label">Architecture &amp; Interior Design</span>
    <h1 class="hero-title">We design spaces that get <strong>quieter</strong> the longer you live in them.</h1>
    <p class="hero-desc">A 12-person studio working on residential renovation and ground-up builds across the Pacific Northwest.</p>
    <a href="#contact" class="btn btn-primary">Start a Project</a>

    <div class="slider-wrap" id="slider-wrap">
      <div class="slider-before"><span>BEFORE</span></div>
      <div class="slider-after" id="slider-after"><span>AFTER</span></div>
      <div class="slider-label before-label">Before</div>
      <div class="slider-label after-label">After</div>
      <div class="slider-handle" id="slider-handle"></div>
    </div>
  </div>
</section>

<section class="section" id="projects">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Selected Work</span>
      <h2 class="section-title">Recent <strong>projects</strong></h2>
    </div>
    <div class="project-grid">
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Residential</span><span class="project-name">Birch Hollow Residence</span></div></div>
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Renovation</span><span class="project-name">Cascade Loft</span></div></div>
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Commercial</span><span class="project-name">Foundry Coffee HQ</span></div></div>
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Residential</span><span class="project-name">Quarry House</span></div></div>
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Interior</span><span class="project-name">Linden Apartment</span></div></div>
      <div class="project-card reveal"><div class="project-overlay"><span class="project-cat">Ground-Up</span><span class="project-name">Cedar Ridge Cabin</span></div></div>
    </div>
  </div>
</section>

<section class="section" style="background:var(--white-card);border-top:1px solid var(--line);border-bottom:1px solid var(--line);">
  <div class="container">
    <div class="philosophy-block reveal">
      <span class="section-label">Our Approach</span>
      <p>We believe good design is mostly <strong>restraint</strong> — knowing which walls to remove, which materials to leave honest, and which decisions to leave for the people who'll actually live there.</p>
    </div>
  </div>
</section>

<section class="section" id="services">
  <div class="container">
    <div class="reveal">
      <span class="section-label">What We Do</span>
      <h2 class="section-title">Our <strong>services</strong></h2>
    </div>
    <div class="services-list">
      <div class="service-row reveal"><h4>Architectural Design</h4><span>Ground-up &amp; renovation</span></div>
      <div class="service-row reveal"><h4>Interior Design</h4><span>Spatial planning &amp; FF&amp;E</span></div>
      <div class="service-row reveal"><h4>Construction Administration</h4><span>On-site oversight</span></div>
      <div class="service-row reveal"><h4>Feasibility &amp; Planning</h4><span>Permitting &amp; zoning</span></div>
    </div>
  </div>
</section>

<section class="section" id="contact" style="background:var(--white-card);border-top:1px solid var(--line);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Get In Touch</span>
      <h2 class="section-title">Start a <strong>conversation</strong></h2>
    </div>
    <div class="contact-grid">
      <div class="reveal">
        <div class="contact-detail"><span>Studio</span><strong>1140 Foundry Row, Seattle, WA</strong></div>
        <div class="contact-detail"><span>Email</span><strong>studio@haldendesign.com</strong></div>
        <div class="contact-detail"><span>Phone</span><strong>(206) 555-0172</strong></div>
      </div>
      <form id="contact-form" class="reveal" novalidate>
        <div class="form-group"><label for="name">Name</label><input type="text" id="name" required><span class="form-error" id="name-error"></span></div>
        <div class="form-group"><label for="email">Email</label><input type="email" id="email" required><span class="form-error" id="email-error"></span></div>
        <div class="form-group"><label for="message">Tell us about your project</label><textarea id="message" rows="3" required></textarea><span class="form-error" id="message-error"></span></div>
        <button type="submit" class="btn btn-primary">Send Inquiry</button>
        <p class="form-status" id="form-status"></p>
      </form>
    </div>
  </div>
</section>

<footer class="container footer">
  <p>© 2026 Halden Studio</p>
  <p>Seattle, WA</p>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function(){
  const sliderWrap = document.getElementById('slider-wrap');
  const sliderAfter = document.getElementById('slider-after');
  const sliderHandle = document.getElementById('slider-handle');
  let dragging = false;

  function setSlider(percent){
    percent = Math.max(0, Math.min(100, percent));
    sliderAfter.style.clipPath = `inset(0 ${100-percent}% 0 0)`;
    sliderHandle.style.left = percent + '%';
  }
  function getPercent(clientX){
    const rect = sliderWrap.getBoundingClientRect();
    return ((clientX - rect.left) / rect.width) * 100;
  }
  sliderWrap.addEventListener('mousedown', (e)=>{ dragging = true; setSlider(getPercent(e.clientX)); });
  window.addEventListener('mousemove', (e)=>{ if(dragging) setSlider(getPercent(e.clientX)); });
  window.addEventListener('mouseup', ()=>{ dragging = false; });
  sliderWrap.addEventListener('touchstart', (e)=>{ dragging = true; setSlider(getPercent(e.touches[0].clientX)); });
  sliderWrap.addEventListener('touchmove', (e)=>{ if(dragging) setSlider(getPercent(e.touches[0].clientX)); });
  sliderWrap.addEventListener('touchend', ()=>{ dragging = false; });

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

  const form = document.getElementById('contact-form');
  const validators = {
    name: v => v.trim().length >= 2 || 'Please enter your name.',
    email: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Enter a valid email address.',
    message: v => v.trim().length >= 10 || 'Tell us a bit more about the project.'
  };
  function validateField(id){
    const field = document.getElementById(id);
    const errorEl = document.getElementById(`${id}-error`);
    const result = validators[id](field.value);
    if (result === true) { errorEl.textContent=''; return true; }
    errorEl.textContent = result; return false;
  }
  Object.keys(validators).forEach(id=>document.getElementById(id).addEventListener('blur', ()=>validateField(id)));
  form.addEventListener('submit', (e)=>{
    e.preventDefault();
    const allValid = Object.keys(validators).map(validateField).every(Boolean);
    const status = document.getElementById('form-status');
    if (!allValid) { status.textContent = 'Please fix the highlighted fields above.'; return; }
    const btn = form.querySelector('button[type=submit]');
    btn.disabled = true; btn.textContent = 'Sending...';
    setTimeout(()=>{ status.textContent = "Thank you — we'll follow up within two business days."; form.reset(); btn.disabled=false; btn.textContent='Send Inquiry'; }, 900);
  });
});
</script>
</body>
</html>
```
