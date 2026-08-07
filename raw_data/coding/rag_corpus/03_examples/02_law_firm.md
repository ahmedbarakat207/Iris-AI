# Example — Boutique Law Firm (Vanilla CSS Architecture)

Tags: example, full-site, law-firm, legal, professional-services, vanilla-css, light-and-dark-mix, navy, gold, serif, editorial

Niche: boutique litigation law firm.
Architecture: vanilla CSS with custom properties, no external dependencies.
Palette: deep navy canvas (#0E1525), warm ivory text, brass gold accent (#B08D4F).
Signature element: a results ticker (case outcomes) that auto-scrolls horizontally,
plus a serif-led editorial typographic system.
Sections: header, hero, results ticker, practice areas, attorney profiles,
process/timeline, testimonial, contact form, footer.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ashworth &amp; Cole LLP | Civil Litigation Counsel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
:root{
  --navy:#0E1525; --navy-light:#16203A; --navy-lighter:#1F2D4D; --line:#2B3A5E;
  --ivory:#F4F1E8; --ivory-dim:#A9B0C2; --gold:#B08D4F; --gold-hover:#C7A567;
  --radius:6px; --radius-lg:10px;
  --transition: all 0.35s cubic-bezier(0.25,0.46,0.45,0.94);
  --shadow-lg: 0 20px 50px rgba(0,0,0,0.4);
  --serif:'Playfair Display', serif; --sans:'Source Sans 3', sans-serif;
}
html{scroll-behavior:smooth;}
body{font-family:var(--sans);background:var(--navy);color:var(--ivory);line-height:1.7;overflow-x:hidden;}
a{text-decoration:none;color:inherit;}
img{max-width:100%;display:block;}
button{cursor:pointer;font-family:inherit;}
.container{max-width:1180px;margin:0 auto;padding:0 2rem;}
.section{padding:6.5rem 0;}
.section-label{display:block;text-transform:uppercase;letter-spacing:3px;font-size:0.78rem;color:var(--gold);margin-bottom:1rem;font-weight:600;}
.section-title{font-family:var(--serif);font-size:2.6rem;font-weight:600;line-height:1.2;margin-bottom:1rem;}
.section-subtitle{color:var(--ivory-dim);font-size:1.05rem;max-width:600px;}
.btn{display:inline-flex;align-items:center;gap:0.5rem;padding:0.9rem 2.1rem;border:none;border-radius:var(--radius);font-size:0.9rem;font-weight:600;letter-spacing:0.5px;transition:var(--transition);text-transform:uppercase;}
.btn-primary{background:var(--gold);color:var(--navy);}
.btn-primary:hover{background:var(--gold-hover);transform:translateY(-2px);box-shadow:0 10px 24px rgba(176,141,79,0.3);}
.btn-outline{background:transparent;color:var(--ivory);border:1px solid var(--line);}
.btn-outline:hover{border-color:var(--gold);color:var(--gold);}

.header{position:fixed;top:0;left:0;width:100%;z-index:1000;padding:1.4rem 0;transition:var(--transition);}
.header.scrolled{background:rgba(14,21,37,0.95);backdrop-filter:blur(16px);padding:1rem 0;box-shadow:0 2px 30px rgba(0,0,0,0.4);}
.header-inner{display:flex;align-items:center;justify-content:space-between;}
.logo{font-family:var(--serif);font-size:1.4rem;font-weight:700;letter-spacing:0.5px;}
.logo span{color:var(--gold);}
.nav-list{display:flex;list-style:none;gap:2.3rem;align-items:center;}
.nav-list a{font-size:0.85rem;font-weight:500;letter-spacing:1px;text-transform:uppercase;position:relative;padding:0.25rem 0;}
.nav-list a::after{content:"";position:absolute;bottom:-2px;left:0;width:0;height:1.5px;background:var(--gold);transition:var(--transition);}
.nav-list a:hover::after,.nav-list a.active::after{width:100%;}
.menu-toggle{display:none;flex-direction:column;gap:5px;background:none;border:none;padding:4px;z-index:1001;}
.menu-toggle span{width:24px;height:2px;background:var(--ivory);transition:var(--transition);}
.menu-toggle.active span:nth-child(1){transform:translateY(7px) rotate(45deg);}
.menu-toggle.active span:nth-child(2){opacity:0;}
.menu-toggle.active span:nth-child(3){transform:translateY(-7px) rotate(-45deg);}

.overlay{position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:900;opacity:0;pointer-events:none;transition:opacity 0.3s ease;}
.overlay.active{opacity:1;pointer-events:auto;}

.hero{min-height:92vh;display:flex;align-items:center;position:relative;padding-top:6rem;background:linear-gradient(160deg,var(--navy) 0%, var(--navy-light) 60%, var(--navy) 100%);}
.hero::before{content:"";position:absolute;top:-30%;right:-10%;width:60%;height:160%;background:radial-gradient(ellipse, rgba(176,141,79,0.07) 0%, transparent 60%);pointer-events:none;}
.hero-grid{display:grid;grid-template-columns:1.1fr 0.9fr;gap:4rem;align-items:center;}
.hero-label{display:inline-block;padding:0.4rem 1rem;border:1px solid rgba(176,141,79,0.4);border-radius:30px;font-size:0.78rem;letter-spacing:2.5px;text-transform:uppercase;color:var(--gold);margin-bottom:2rem;}
.hero-title{font-family:var(--serif);font-size:3.6rem;font-weight:700;line-height:1.15;margin-bottom:1.5rem;letter-spacing:-0.5px;}
.hero-title em{font-style:italic;color:var(--gold);font-weight:400;}
.hero-desc{font-size:1.1rem;color:var(--ivory-dim);max-width:480px;margin-bottom:2.2rem;}
.hero-actions{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:3rem;}
.hero-stats{display:flex;gap:2.5rem;padding-top:2rem;border-top:1px solid var(--line);flex-wrap:wrap;}
.hero-stat h4{font-family:var(--serif);font-size:2rem;color:var(--gold);line-height:1;margin-bottom:0.3rem;}
.hero-stat p{font-size:0.8rem;color:var(--ivory-dim);text-transform:uppercase;letter-spacing:1px;}
.hero-visual{background:var(--navy-light);border:1px solid var(--line);border-radius:var(--radius-lg);padding:3rem 2.5rem;}
.hero-visual-quote{font-family:var(--serif);font-style:italic;font-size:1.3rem;line-height:1.5;margin-bottom:1.5rem;color:var(--ivory);}
.hero-visual-meta{font-size:0.85rem;color:var(--ivory-dim);border-top:1px solid var(--line);padding-top:1.2rem;}

.ticker-wrap{background:var(--navy-light);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:1.4rem 0;overflow:hidden;position:relative;}
.ticker-track{display:flex;gap:3.5rem;white-space:nowrap;animation:tickerScroll 28s linear infinite;width:max-content;}
.ticker-item{display:flex;align-items:center;gap:0.7rem;font-size:0.95rem;color:var(--ivory-dim);}
.ticker-item strong{color:var(--gold);font-family:var(--serif);}
@keyframes tickerScroll{from{transform:translateX(0);}to{transform:translateX(-50%);}}
.ticker-wrap:hover .ticker-track{animation-play-state:paused;}

.practice-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;margin-top:3rem;}
.practice-card{background:var(--navy-light);border-radius:var(--radius-lg);padding:2.3rem;transition:var(--transition);border:1px solid transparent;}
.practice-card:hover{transform:translateY(-6px);border-color:var(--gold);box-shadow:var(--shadow-lg);}
.practice-num{font-family:var(--serif);font-size:0.9rem;color:var(--gold);margin-bottom:1.2rem;letter-spacing:1px;}
.practice-title{font-family:var(--serif);font-size:1.35rem;margin-bottom:0.8rem;}
.practice-desc{color:var(--ivory-dim);font-size:0.92rem;}

.attorney-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;margin-top:3rem;}
.attorney-card{text-align:center;}
.attorney-photo{width:100%;aspect-ratio:1;border-radius:50%;background:linear-gradient(135deg,var(--navy-lighter),var(--navy-light));margin-bottom:1.3rem;display:flex;align-items:center;justify-content:center;font-family:var(--serif);font-size:2.5rem;color:var(--gold);border:2px solid var(--line);}
.attorney-name{font-family:var(--serif);font-size:1.2rem;margin-bottom:0.3rem;}
.attorney-role{font-size:0.85rem;color:var(--gold);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.8rem;}
.attorney-bio{font-size:0.88rem;color:var(--ivory-dim);}

.timeline{position:relative;margin-top:3.5rem;padding-left:2.5rem;}
.timeline::before{content:"";position:absolute;left:7px;top:8px;bottom:8px;width:2px;background:var(--line);}
.timeline-item{position:relative;padding-bottom:2.8rem;}
.timeline-item:last-child{padding-bottom:0;}
.timeline-item::before{content:"";position:absolute;left:-2.5rem;top:4px;width:16px;height:16px;border-radius:50%;background:var(--navy);border:2px solid var(--gold);}
.timeline-item h4{font-family:var(--serif);font-size:1.15rem;margin-bottom:0.4rem;}
.timeline-item p{color:var(--ivory-dim);font-size:0.92rem;max-width:560px;}

.testimonial-block{max-width:680px;margin:0 auto;text-align:center;}
.testimonial-quote{font-family:var(--serif);font-size:1.5rem;font-style:italic;line-height:1.6;margin-bottom:1.5rem;}
.testimonial-author{font-size:0.9rem;color:var(--gold);font-weight:600;}

.contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:4rem;margin-top:2.5rem;align-items:start;}
.contact-info h3{font-family:var(--serif);font-size:1.5rem;margin-bottom:1rem;}
.contact-info p{color:var(--ivory-dim);margin-bottom:1.5rem;}
.contact-detail{display:flex;gap:0.8rem;align-items:flex-start;margin-bottom:1.2rem;font-size:0.92rem;}
.contact-detail strong{color:var(--gold);min-width:90px;display:inline-block;}
.form-group{margin-bottom:1.4rem;}
.form-group label{display:block;font-size:0.82rem;font-weight:600;margin-bottom:0.45rem;letter-spacing:0.3px;}
.form-group input,.form-group textarea{width:100%;background:var(--navy-light);border:1px solid var(--line);color:var(--ivory);padding:0.8rem 1rem;border-radius:var(--radius);font-size:0.92rem;font-family:inherit;transition:var(--transition);}
.form-group input:focus,.form-group textarea:focus{outline:none;border-color:var(--gold);box-shadow:0 0 0 3px rgba(176,141,79,0.15);}
.form-group input.invalid,.form-group textarea.invalid{border-color:#c0564a;}
.form-error{display:block;font-size:0.78rem;color:#c0564a;margin-top:0.35rem;min-height:1.1em;}
.form-status{margin-top:0.8rem;font-size:0.88rem;}
.form-status.success{color:#6fa888;}
.form-status.error{color:#c0564a;}

.footer{background:var(--navy-light);border-top:1px solid var(--line);padding:4rem 0 0;}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:3rem;padding-bottom:3rem;}
.footer-col h4{font-size:0.82rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:1.2rem;color:var(--ivory);}
.footer-col a,.footer-col p{display:block;color:var(--ivory-dim);font-size:0.88rem;margin-bottom:0.8rem;}
.footer-col a:hover{color:var(--gold);}
.footer-bottom{border-top:1px solid var(--line);padding:1.4rem 0;display:flex;justify-content:space-between;font-size:0.82rem;color:var(--ivory-dim);}

.reveal{opacity:0;transform:translateY(28px);transition:all 0.7s cubic-bezier(0.16,1,0.3,1);}
.reveal.visible{opacity:1;transform:translateY(0);}

@media (max-width:900px){
  .hero-grid,.contact-grid{grid-template-columns:1fr;}
  .practice-grid,.attorney-grid{grid-template-columns:1fr 1fr;}
  .nav-list{position:fixed;top:0;right:-100%;width:75%;height:100vh;background:var(--navy);flex-direction:column;justify-content:center;gap:2.2rem;transition:var(--transition);z-index:950;}
  .nav-list.open{right:0;}
  .menu-toggle{display:flex;}
  .hero-title{font-size:2.6rem;}
  .footer-grid{grid-template-columns:1fr;}
}
@media (max-width:600px){
  .practice-grid,.attorney-grid{grid-template-columns:1fr;}
  .footer-bottom{flex-direction:column;gap:0.8rem;text-align:center;}
}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:0.001ms!important;transition-duration:0.001ms!important;}}
</style>
</head>
<body>

<header class="header" id="header">
  <div class="container header-inner">
    <a href="#hero" class="logo">Ashworth <span>&amp;</span> Cole</a>
    <nav>
      <ul class="nav-list" id="nav-list">
        <li><a href="#hero" class="active">Home</a></li>
        <li><a href="#practice">Practice Areas</a></li>
        <li><a href="#attorneys">Attorneys</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
    </nav>
    <button class="menu-toggle" id="menu-toggle" aria-label="Toggle menu"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="overlay" id="overlay"></div>

<section class="hero" id="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <span class="hero-label">Civil Litigation &amp; Commercial Disputes</span>
        <h1 class="hero-title">Counsel for the cases<br><em>that can't be lost.</em></h1>
        <p class="hero-desc">A nine-attorney firm built for complex commercial litigation — the matters too consequential for a generalist and too specific for a mega-firm.</p>
        <div class="hero-actions">
          <a href="#contact" class="btn btn-primary">Request a Consultation</a>
          <a href="#practice" class="btn btn-outline">Our Practice Areas</a>
        </div>
        <div class="hero-stats">
          <div class="hero-stat"><h4>340+</h4><p>Matters Resolved</p></div>
          <div class="hero-stat"><h4>91%</h4><p>Favorable Outcomes</p></div>
          <div class="hero-stat"><h4>22</h4><p>Years Average Tenure</p></div>
        </div>
      </div>
      <div class="hero-visual">
        <p class="hero-visual-quote">"They treated our case like it was the only one on their desk."</p>
        <div class="hero-visual-meta">General Counsel, mid-market manufacturer</div>
      </div>
    </div>
  </div>
</section>

<div class="ticker-wrap" aria-label="Recent case results">
  <div class="ticker-track" id="ticker-track">
    <div class="ticker-item"><strong>$14.2M</strong> jury verdict — breach of contract</div>
    <div class="ticker-item"><strong>Dismissed</strong> — shareholder derivative suit</div>
    <div class="ticker-item"><strong>$6.8M</strong> settlement — trade secret dispute</div>
    <div class="ticker-item"><strong>Summary Judgment</strong> — employment class action</div>
    <div class="ticker-item"><strong>$22M</strong> arbitration award — partnership dissolution</div>
  </div>
</div>

<section class="section" id="practice">
  <div class="container">
    <div class="reveal">
      <span class="section-label">What We Handle</span>
      <h2 class="section-title">Practice areas</h2>
      <p class="section-subtitle">We take a small number of matters at a time, by design, across three core areas.</p>
    </div>
    <div class="practice-grid">
      <div class="practice-card reveal">
        <div class="practice-num">01</div>
        <h3 class="practice-title">Commercial Litigation</h3>
        <p class="practice-desc">Contract disputes, partnership dissolutions, and business torts for companies with too much at stake to settle cheap.</p>
      </div>
      <div class="practice-card reveal">
        <div class="practice-num">02</div>
        <h3 class="practice-title">Employment Defense</h3>
        <p class="practice-desc">Defending employers against class actions, wrongful termination claims, and regulatory investigations.</p>
      </div>
      <div class="practice-card reveal">
        <div class="practice-num">03</div>
        <h3 class="practice-title">Intellectual Property</h3>
        <p class="practice-desc">Trade secret misappropriation, licensing disputes, and IP-driven competitive litigation.</p>
      </div>
    </div>
  </div>
</section>

<section class="section" id="attorneys" style="background:var(--navy-light);">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Who You'll Work With</span>
      <h2 class="section-title">Lead counsel</h2>
    </div>
    <div class="attorney-grid">
      <div class="attorney-card reveal">
        <div class="attorney-photo">EA</div>
        <h4 class="attorney-name">Eleanor Ashworth</h4>
        <p class="attorney-role">Founding Partner</p>
        <p class="attorney-bio">25 years trying commercial disputes to verdict. Former federal clerk.</p>
      </div>
      <div class="attorney-card reveal">
        <div class="attorney-photo">DC</div>
        <h4 class="attorney-name">David Cole</h4>
        <p class="attorney-role">Founding Partner</p>
        <p class="attorney-bio">Focuses on IP and trade secret litigation for manufacturing clients.</p>
      </div>
      <div class="attorney-card reveal">
        <div class="attorney-photo">RM</div>
        <h4 class="attorney-name">Rosa Mendez</h4>
        <p class="attorney-role">Senior Counsel</p>
        <p class="attorney-bio">Leads the employment defense practice; former EEOC trial attorney.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="reveal">
      <span class="section-label">How We Work</span>
      <h2 class="section-title">From first call to resolution</h2>
    </div>
    <div class="timeline">
      <div class="timeline-item reveal"><h4>Initial Consultation</h4><p>A senior partner — not an associate — assesses your matter within 48 hours of first contact.</p></div>
      <div class="timeline-item reveal"><h4>Case Strategy</h4><p>We map the strongest path to resolution, including realistic settlement value, before you're billed for a single filing.</p></div>
      <div class="timeline-item reveal"><h4>Active Litigation</h4><p>The partner who pitched you stays lead counsel through trial — no quiet handoffs to junior staff.</p></div>
      <div class="timeline-item reveal"><h4>Resolution</h4><p>Settlement, verdict, or dismissal — we close the loop with a plain-English summary of what it means for your business.</p></div>
    </div>
  </div>
</section>

<section class="section" style="background:var(--navy-light);">
  <div class="container">
    <div class="testimonial-block reveal">
      <p class="testimonial-quote">"We had three other firms tell us to settle. Ashworth & Cole told us why we shouldn't — and proved it at trial."</p>
      <p class="testimonial-author">CFO, regional logistics company</p>
    </div>
  </div>
</section>

<section class="section" id="contact">
  <div class="container">
    <div class="reveal">
      <span class="section-label">Get In Touch</span>
      <h2 class="section-title">Request a consultation</h2>
    </div>
    <div class="contact-grid">
      <div class="contact-info reveal">
        <h3>Speak with a partner directly</h3>
        <p>Every inquiry is reviewed personally by a founding partner within one business day — not routed through intake staff.</p>
        <div class="contact-detail"><strong>Office</strong> 412 Exchange Place, Suite 1900</div>
        <div class="contact-detail"><strong>Phone</strong> (212) 555-0148</div>
        <div class="contact-detail"><strong>Hours</strong> Mon–Fri, 8:30am–6pm ET</div>
      </div>
      <form id="contact-form" class="reveal" novalidate>
        <div class="form-group">
          <label for="name">Full name</label>
          <input type="text" id="name" name="name" required>
          <span class="form-error" id="name-error"></span>
        </div>
        <div class="form-group">
          <label for="email">Email address</label>
          <input type="email" id="email" name="email" required>
          <span class="form-error" id="email-error"></span>
        </div>
        <div class="form-group">
          <label for="message">Briefly describe your matter</label>
          <textarea id="message" name="message" rows="4" required></textarea>
          <span class="form-error" id="message-error"></span>
        </div>
        <button type="submit" class="btn btn-primary">Send Inquiry</button>
        <p class="form-status" id="form-status"></p>
      </form>
    </div>
  </div>
</section>

<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-col">
      <h4>Ashworth &amp; Cole LLP</h4>
      <p>Civil litigation counsel for companies who can't afford to lose the matter that matters most.</p>
    </div>
    <div class="footer-col">
      <h4>Firm</h4>
      <a href="#practice">Practice Areas</a>
      <a href="#attorneys">Attorneys</a>
      <a href="#contact">Contact</a>
    </div>
    <div class="footer-col">
      <h4>Legal</h4>
      <a href="#">Privacy Policy</a>
      <a href="#">Terms of Use</a>
      <a href="#">Disclaimer</a>
    </div>
  </div>
  <div class="container footer-bottom">
    <p>© 2026 Ashworth &amp; Cole LLP. Attorney advertising.</p>
    <p>This is not legal advice. Past results do not guarantee future outcomes.</p>
  </div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function () {
  const header = document.getElementById('header');
  const menuToggle = document.getElementById('menu-toggle');
  const navList = document.getElementById('nav-list');
  const overlay = document.getElementById('overlay');

  function toggleMenu(){
    menuToggle.classList.toggle('active');
    navList.classList.toggle('open');
    overlay.classList.toggle('active');
    document.body.style.overflow = navList.classList.contains('open') ? 'hidden' : '';
  }
  menuToggle.addEventListener('click', toggleMenu);
  overlay.addEventListener('click', toggleMenu);
  navList.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    if (navList.classList.contains('open')) toggleMenu();
  }));

  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });

  const navLinks = document.querySelectorAll('.nav-list a');
  const sections = document.querySelectorAll('section[id]');
  const navObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        navLinks.forEach(link => link.classList.toggle('active', link.getAttribute('href') === `#${id}`));
      }
    });
  }, { threshold: 0.3, rootMargin: '-80px 0px -50% 0px' });
  sections.forEach(s => navObserver.observe(s));

  const revealEls = document.querySelectorAll('.reveal');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
  revealEls.forEach(el => revealObserver.observe(el));

  const form = document.getElementById('contact-form');
  const validators = {
    name: (v) => v.trim().length >= 2 || 'Please enter your full name.',
    email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Enter a valid email address.',
    message: (v) => v.trim().length >= 10 || 'Tell us a bit more about your matter.'
  };
  function validateField(fieldName){
    const field = document.getElementById(fieldName);
    const errorEl = document.getElementById(`${fieldName}-error`);
    const result = validators[fieldName](field.value);
    if (result === true) { field.classList.remove('invalid'); errorEl.textContent=''; return true; }
    field.classList.add('invalid'); errorEl.textContent = result; return false;
  }
  Object.keys(validators).forEach(fieldName => {
    const field = document.getElementById(fieldName);
    field.addEventListener('blur', () => validateField(fieldName));
    field.addEventListener('input', () => { if (field.classList.contains('invalid')) validateField(fieldName); });
  });
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const allValid = Object.keys(validators).map(validateField).every(Boolean);
    const statusEl = document.getElementById('form-status');
    if (!allValid) { statusEl.textContent = 'Please fix the highlighted fields above.'; statusEl.className = 'form-status error'; return; }
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true; submitBtn.textContent = 'Sending...';
    setTimeout(() => {
      statusEl.textContent = "Thank you — a partner will respond within one business day.";
      statusEl.className = 'form-status success';
      form.reset();
      submitBtn.disabled = false; submitBtn.textContent = 'Send Inquiry';
    }, 900);
  });
});
</script>
</body>
</html>
```
