# Example — Boxing & MMA Gym (Tailwind Architecture)

Tags: example, full-site, boxing, mma, gym, fitness, combat-sports, tailwind, dark-theme, blood-orange, fighter-roster, aggressive

Niche: boxing and MMA training gym with a competitive fight team.
Architecture: Tailwind CDN utility classes.
Palette: matte black canvas (#0C0C0C), blood orange accent (#FF4422), heavy condensed
display type for aggression.
Signature element: a fighter roster grid showing each athlete's record (W-L-D) as a
bold stat block, with a hover state revealing their next fight date.
Sections: header, hero, class types, fighter roster, membership tiers, schedule,
testimonial, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ironclad Combat Club | Boxing &amp; MMA Training</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#0C0C0C',light:'#161616',card:'#1C1C1C'}, accent:{DEFAULT:'#FF4422',hover:'#FF6644',glow:'rgba(255,68,34,0.3)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], display:['Oswald','sans-serif'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Oswald:wght@500;600;700;800&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
  .font-display{font-family:'Oswald',sans-serif;text-transform:uppercase;}
  ::selection{background:rgba(255,68,34,0.35);}
  .hero-title{font-size:clamp(3rem,8vw,7rem);line-height:0.92;letter-spacing:-0.01em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .fighter-card{transition:transform .35s cubic-bezier(.25,.46,.45,.94);}
  .fighter-card:hover{transform:translateY(-6px);}
  .fighter-overlay{opacity:0;transition:opacity .3s ease;}
  .fighter-card:hover .fighter-overlay{opacity:1;}
  input:focus,button:focus-visible{outline:2px solid #FF4422;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <button id="mobile-menu-btn" class="lg:hidden p-2 -ml-2" aria-label="Open menu">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <a href="#" class="font-display text-xl font-bold tracking-wide">IRONCLAD</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#classes" class="font-display text-sm text-white/60 hover:text-white tracking-wide">Classes</a>
        <a href="#fighters" class="font-display text-sm text-white/60 hover:text-white tracking-wide">Fight Team</a>
        <a href="#membership" class="font-display text-sm text-white/60 hover:text-white tracking-wide">Membership</a>
      </nav>
      <a href="#membership" class="bg-accent hover:bg-accent-hover font-display font-bold text-sm px-5 py-2.5 transition-colors">Free Trial Class</a>
    </div>
  </div>
  <div id="mobile-nav" class="hidden lg:hidden bg-canvas-light border-b border-white/5">
    <div class="px-6 py-6 flex flex-col gap-4 font-display">
      <a href="#classes">Classes</a><a href="#fighters">Fight Team</a><a href="#membership">Membership</a>
    </div>
  </div>
</header>

<section class="relative min-h-[94vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 75% 30%, rgba(255,68,34,0.1) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
    <p class="text-accent font-display font-bold tracking-widest mb-6">EST. 2014 · BOXING · MUAY THAI · MMA</p>
    <h1 class="hero-title font-display font-bold text-white mb-8">
      TRAIN LIKE<br>YOU FIGHT.
    </h1>
    <p class="text-lg text-white/50 max-w-md mb-10 leading-relaxed">
      No mirrors, no fluff — just coaches who've competed, a fight team that trains
      next to you, and a heavy bag room that never closes early.
    </p>
    <div class="flex flex-col sm:flex-row gap-4">
      <a href="#membership" class="bg-accent hover:bg-accent-hover font-display font-bold px-8 py-4 transition-all hover:-translate-y-0.5">Claim Free Trial Class</a>
      <a href="#classes" class="border border-white/15 hover:border-white/30 font-display font-semibold px-8 py-4 transition-all hover:bg-white/5">View Class Schedule</a>
    </div>
  </div>
</section>

<section id="classes" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent font-display font-bold tracking-widest mb-3">DISCIPLINES</p>
      <h2 class="font-display text-3xl lg:text-5xl font-bold">Three ways to get hit</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="reveal bg-canvas-card border border-white/5 p-8"><div class="text-4xl mb-4">🥊</div><h3 class="font-display text-xl font-bold mb-2">Boxing</h3><p class="text-sm text-white/45">Footwork, combinations, and pad work — fundamentals first, sparring earned.</p></div>
      <div class="reveal bg-canvas-card border border-white/5 p-8" style="transition-delay:.1s"><div class="text-4xl mb-4">🦵</div><h3 class="font-display text-xl font-bold mb-2">Muay Thai</h3><p class="text-sm text-white/45">Clinch work, elbows, and the eight-limb game from coaches trained in Thailand.</p></div>
      <div class="reveal bg-canvas-card border border-white/5 p-8" style="transition-delay:.2s"><div class="text-4xl mb-4">🤼</div><h3 class="font-display text-xl font-bold mb-2">MMA</h3><p class="text-sm text-white/45">Striking-to-grappling transitions for those building toward amateur competition.</p></div>
    </div>
  </div>
</section>

<section id="fighters" class="py-24 lg:py-32">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent font-display font-bold tracking-widest mb-3">OUR FIGHT TEAM</p>
      <h2 class="font-display text-3xl lg:text-5xl font-bold">The ones who compete</h2>
    </div>
    <div id="fighter-grid" class="grid grid-cols-2 sm:grid-cols-4 gap-5"></div>
  </div>
</section>

<section id="membership" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent font-display font-bold tracking-widest mb-3">MEMBERSHIP</p>
      <h2 class="font-display text-3xl lg:text-5xl font-bold">No contracts, no excuses</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="reveal bg-canvas-card border border-white/5 p-8">
        <p class="font-display text-sm text-white/40 tracking-widest mb-2">DROP-IN</p>
        <p class="font-display text-4xl font-bold mb-4">$25</p>
        <ul class="space-y-2 text-sm text-white/55 mb-6"><li>Single class</li><li>Glove rental included</li></ul>
        <button class="w-full border border-white/15 hover:border-accent hover:text-accent font-display font-bold py-3 transition-all">Book a Class</button>
      </div>
      <div class="reveal bg-canvas-card border border-accent p-8 relative">
        <span class="absolute -top-3 left-8 bg-accent font-display text-xs font-bold px-3 py-1">MOST JOIN THIS</span>
        <p class="font-display text-sm text-white/40 tracking-widest mb-2">UNLIMITED</p>
        <p class="font-display text-4xl font-bold mb-4">$159<span class="text-base text-white/40">/mo</span></p>
        <ul class="space-y-2 text-sm text-white/55 mb-6"><li>All classes, all disciplines</li><li>Open mat access</li><li>No contract</li></ul>
        <button class="w-full bg-accent hover:bg-accent-hover font-display font-bold py-3 transition-all">Start Membership</button>
      </div>
      <div class="reveal bg-canvas-card border border-white/5 p-8">
        <p class="font-display text-sm text-white/40 tracking-widest mb-2">FIGHT TEAM</p>
        <p class="font-display text-4xl font-bold mb-4">By Invite</p>
        <ul class="space-y-2 text-sm text-white/55 mb-6"><li>Competition-track training</li><li>Corner support at events</li></ul>
        <button class="w-full border border-white/15 hover:border-accent hover:text-accent font-display font-bold py-3 transition-all">Inquire</button>
      </div>
    </div>
  </div>
</section>

<section class="py-20 border-t border-white/5">
  <div class="max-w-3xl mx-auto px-6 text-center reveal">
    <p class="text-2xl font-medium text-white/85 leading-relaxed mb-6">"I walked in soft and scared of the bag. A year later I had my first amateur fight. This place doesn't coddle you, and that's exactly why it works."</p>
    <p class="text-sm text-white/40 font-display">— DEVON R., MEMBER SINCE 2023</p>
  </div>
</section>

<footer class="border-t border-white/5 py-12 bg-canvas-light">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p class="font-display">© 2026 IRONCLAD COMBAT CLUB</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Waiver</a><a href="#" class="hover:text-white/60">Contact</a></div>
  </div>
</footer>

<script>
const fighters = [
  { name:'Marcus Reyes', weight:'Welterweight', record:'8-1-0', next:'Sept 14' },
  { name:'Tia Nakamura', weight:'Bantamweight', record:'6-0-1', next:'Oct 3' },
  { name:'Diego Ferreira', weight:'Lightweight', record:'11-2-0', next:'Aug 29' },
  { name:'Sam Okafor', weight:'Middleweight', record:'4-1-0', next:'Sept 21' },
];
function renderFighters(){
  const grid = document.getElementById('fighter-grid');
  grid.innerHTML = '';
  fighters.forEach((f,i)=>{
    const card = document.createElement('div');
    card.className = 'fighter-card reveal relative bg-canvas-card border border-white/5 aspect-[3/4] overflow-hidden cursor-pointer';
    card.style.transitionDelay = (i*60)+'ms';
    card.innerHTML = `
      <div class="absolute inset-0 bg-gradient-to-br from-accent/10 to-transparent flex items-center justify-center">
        <span class="font-display text-5xl font-bold text-white/10">${f.name.split(' ').map(n=>n[0]).join('')}</span>
      </div>
      <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
        <p class="font-display font-bold text-sm">${f.name}</p>
        <p class="text-xs text-white/50">${f.weight}</p>
        <p class="font-display text-accent font-bold text-sm mt-1">${f.record}</p>
      </div>
      <div class="fighter-overlay absolute inset-0 bg-black/85 flex flex-col items-center justify-center text-center p-4">
        <p class="text-xs text-white/40 uppercase tracking-wide mb-2">Next Fight</p>
        <p class="font-display text-xl font-bold text-accent">${f.next}</p>
      </div>
    `;
    grid.appendChild(card);
    revealObserver.observe(card);
  });
}

const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileNav = document.getElementById('mobile-nav');
mobileMenuBtn.addEventListener('click', ()=>mobileNav.classList.toggle('hidden'));
mobileNav.querySelectorAll('a').forEach(l=>l.addEventListener('click', ()=>mobileNav.classList.add('hidden')));

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(12,12,12,0.9)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

renderFighters();
</script>
</body>
</html>
```
