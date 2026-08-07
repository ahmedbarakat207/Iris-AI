# Example — Indoor Bouldering Gym (Tailwind Architecture)

Tags: example, full-site, climbing, bouldering, gym, fitness, tailwind, dark-theme, lime, charcoal, route-grades

Niche: indoor bouldering gym with graded routes and day passes/memberships.
Architecture: Tailwind CDN utility classes.
Palette: charcoal canvas (#16181A), chalky off-white text, electric lime accent (#C8FF4D).
Signature element: an interactive route-grade legend with a live "today's resets" grid
that color-codes difficulty.
Sections: header, hero, grade legend / today's resets grid, membership tiers,
class schedule, community/testimonial, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Crux Bouldering Co. | Climb. Reset. Repeat.</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  theme: { extend: {
    colors: { canvas:{DEFAULT:'#16181A',light:'#1F2123',card:'#26282A'}, accent:{DEFAULT:'#C8FF4D',hover:'#D7FF77',glow:'rgba(200,255,77,0.25)'} },
    fontFamily: { sans:['Inter','system-ui','sans-serif'], display:['Archivo Black','sans-serif'] }
  }}
}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Archivo+Black&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
  .font-display{font-family:'Archivo Black',sans-serif;}
  ::selection{background:rgba(200,255,77,0.3);}
  .hero-title{font-size:clamp(2.8rem,7vw,6.2rem);line-height:0.95;letter-spacing:-0.02em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .grade-cell{transition:all .25s cubic-bezier(.34,1.56,.64,1);}
  .grade-cell:hover{transform:scale(1.08);}
  .tier-card{transition:all .3s cubic-bezier(.25,.46,.45,.94);}
  .tier-card.featured{transform:scale(1.04);}
  input:focus,button:focus-visible{outline:2px solid #C8FF4D;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <button id="mobile-menu-btn" class="lg:hidden p-2 -ml-2" aria-label="Open menu">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <a href="#" class="font-display text-xl tracking-tight">CRUX</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#grades" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">Today's Resets</a>
        <a href="#membership" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">Membership</a>
        <a href="#schedule" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">Schedule</a>
      </nav>
      <a href="#membership" class="bg-accent text-canvas font-bold text-sm px-5 py-2.5 rounded-full hover:bg-accent-hover transition-colors">Day Pass</a>
    </div>
  </div>
  <div id="mobile-nav" class="hidden lg:hidden bg-canvas-light border-b border-white/5">
    <div class="px-6 py-6 flex flex-col gap-4">
      <a href="#grades">Today's Resets</a><a href="#membership">Membership</a><a href="#schedule">Schedule</a>
    </div>
  </div>
</header>

<section class="relative min-h-[92vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 80% 30%, rgba(200,255,77,0.06) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
    <p class="text-accent text-sm font-bold uppercase tracking-widest mb-6">42 New Routes This Week</p>
    <h1 class="hero-title font-display text-white mb-8">
      SEND<br><span class="text-accent">HARDER.</span>
    </h1>
    <p class="text-lg text-white/50 max-w-md mb-10 leading-relaxed">
      18,000 sq ft of bouldering, 9 wall angles, and a reset crew that never lets the
      board go stale.
    </p>
    <div class="flex flex-col sm:flex-row gap-4">
      <a href="#membership" class="bg-accent hover:bg-accent-hover text-canvas font-bold px-8 py-4 rounded-xl transition-all hover:-translate-y-0.5">Get a Day Pass — $22</a>
      <a href="#grades" class="border border-white/15 hover:border-white/30 font-semibold px-8 py-4 rounded-xl transition-all hover:bg-white/5">See Today's Sets</a>
    </div>
  </div>
</section>

<section id="grades" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="reveal mb-12">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Live Board</p>
      <h2 class="font-display text-3xl lg:text-4xl">Today's Resets by Grade</h2>
      <p class="text-white/45 mt-2 max-w-lg">Tap a grade to see how many problems are live on the floor right now.</p>
    </div>
    <div id="grade-legend" class="grid grid-cols-3 sm:grid-cols-6 gap-3 mb-10"></div>
    <div class="bg-canvas-card border border-white/5 rounded-2xl p-6 flex items-center justify-between reveal">
      <div>
        <p class="text-sm text-white/40">Selected grade</p>
        <p id="selected-grade-label" class="font-display text-2xl text-accent">V0–V2</p>
      </div>
      <div class="text-right">
        <p id="selected-grade-count" class="font-display text-3xl">14</p>
        <p class="text-sm text-white/40">live problems</p>
      </div>
    </div>
  </div>
</section>

<section id="membership" class="py-24 lg:py-32">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Membership</p>
      <h2 class="font-display text-3xl lg:text-4xl">Pick your commitment</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="tier-card reveal bg-canvas-card border border-white/5 rounded-2xl p-8">
        <p class="text-sm text-white/40 uppercase tracking-wide mb-2">Drop In</p>
        <p class="font-display text-4xl mb-4">$22</p>
        <ul class="space-y-2 text-sm text-white/55 mb-6">
          <li>Single day access</li>
          <li>Shoe rental included</li>
          <li>No commitment</li>
        </ul>
        <button class="w-full border border-white/15 hover:border-accent hover:text-accent font-semibold py-3 rounded-xl transition-all">Buy Pass</button>
      </div>
      <div class="tier-card featured reveal bg-canvas-card border border-accent rounded-2xl p-8 relative">
        <span class="absolute -top-3 left-8 bg-accent text-canvas text-xs font-bold px-3 py-1 rounded-full">Most Popular</span>
        <p class="text-sm text-white/40 uppercase tracking-wide mb-2">Monthly</p>
        <p class="font-display text-4xl mb-4">$89<span class="text-base text-white/40">/mo</span></p>
        <ul class="space-y-2 text-sm text-white/55 mb-6">
          <li>Unlimited climbing</li>
          <li>2 free guest passes/mo</li>
          <li>10% off gear &amp; rentals</li>
        </ul>
        <button class="w-full bg-accent hover:bg-accent-hover text-canvas font-bold py-3 rounded-xl transition-all">Join Now</button>
      </div>
      <div class="tier-card reveal bg-canvas-card border border-white/5 rounded-2xl p-8">
        <p class="text-sm text-white/40 uppercase tracking-wide mb-2">Annual</p>
        <p class="font-display text-4xl mb-4">$799<span class="text-base text-white/40">/yr</span></p>
        <ul class="space-y-2 text-sm text-white/55 mb-6">
          <li>Everything in Monthly</li>
          <li>2 months free vs. monthly</li>
          <li>Locked-in rate</li>
        </ul>
        <button class="w-full border border-white/15 hover:border-accent hover:text-accent font-semibold py-3 rounded-xl transition-all">Join Now</button>
      </div>
    </div>
  </div>
</section>

<section id="schedule" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-14 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">This Week</p>
      <h2 class="font-display text-3xl lg:text-4xl">Class schedule</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="reveal bg-canvas-card border border-white/5 rounded-xl p-5"><p class="text-xs text-accent uppercase tracking-wide mb-2">Mon, 6:30pm</p><p class="font-semibold">Movement Fundamentals</p></div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-xl p-5"><p class="text-xs text-accent uppercase tracking-wide mb-2">Wed, 7:00pm</p><p class="font-semibold">Comp Training Squad</p></div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-xl p-5"><p class="text-xs text-accent uppercase tracking-wide mb-2">Fri, 6:00pm</p><p class="font-semibold">Women's Climb Night</p></div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-xl p-5"><p class="text-xs text-accent uppercase tracking-wide mb-2">Sat, 10:00am</p><p class="font-semibold">Youth Climb Club</p></div>
    </div>
  </div>
</section>

<section class="py-20 border-t border-white/5">
  <div class="max-w-3xl mx-auto px-6 text-center reveal">
    <p class="text-2xl font-medium text-white/85 leading-relaxed mb-6">"I came for one drop-in and never left. The reset crew here keeps the board honest — nothing feels stale after week one."</p>
    <p class="text-sm text-white/40">Jordan P. — member since 2023</p>
  </div>
</section>

<footer class="border-t border-white/5 py-12 bg-canvas-light">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p>© 2026 Crux Bouldering Co.</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Waiver</a><a href="#" class="hover:text-white/60">Contact</a></div>
  </div>
</footer>

<script>
const grades = [
  { label:'V0–V2', count:14, color:'#C8FF4D' },
  { label:'V3–V4', count:22, color:'#9FE85C' },
  { label:'V5–V6', count:17, color:'#F5D547' },
  { label:'V7–V8', count:9, color:'#F2994A' },
  { label:'V9–V10', count:5, color:'#EB5757' },
  { label:'V11+', count:2, color:'#9B51E0' },
];

function renderGrades(){
  const wrap = document.getElementById('grade-legend');
  wrap.innerHTML = '';
  grades.forEach((g,i) => {
    const cell = document.createElement('button');
    cell.className = 'grade-cell reveal bg-canvas-card border border-white/5 rounded-xl p-4 text-left hover:border-white/20';
    cell.style.transitionDelay = (i*50)+'ms';
    cell.innerHTML = `
      <div class="w-3 h-3 rounded-full mb-3" style="background:${g.color}"></div>
      <p class="font-display text-sm mb-1">${g.label}</p>
      <p class="text-xs text-white/40">${g.count} live</p>
    `;
    cell.addEventListener('click', () => selectGrade(g));
    wrap.appendChild(cell);
    revealObserver.observe(cell);
  });
}
function selectGrade(g){
  document.getElementById('selected-grade-label').textContent = g.label;
  document.getElementById('selected-grade-label').style.color = g.color;
  const countEl = document.getElementById('selected-grade-count');
  countEl.textContent = g.count;
  countEl.style.animation = 'none'; countEl.offsetHeight; countEl.style.animation = 'pop .3s cubic-bezier(.34,1.56,.64,1)';
}

const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileNav = document.getElementById('mobile-nav');
mobileMenuBtn.addEventListener('click', () => mobileNav.classList.toggle('hidden'));
mobileNav.querySelectorAll('a').forEach(l => l.addEventListener('click', () => mobileNav.classList.add('hidden')));

const header = document.getElementById('site-header');
window.addEventListener('scroll', () => {
  if (window.scrollY>80){ header.style.background='rgba(22,24,26,0.85)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

renderGrades();
</script>

<style>
@keyframes pop { 0%{transform:scale(0.7);opacity:0.5;} 100%{transform:scale(1);opacity:1;} }
</style>
</body>
</html>
```
