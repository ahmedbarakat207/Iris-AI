# Example — Craft Cocktail Bar (Tailwind Architecture)

Tags: example, full-site, cocktail-bar, nightlife, bar, hospitality, tailwind, dark-theme, plum, neon-pink, flip-cards, menu

Niche: craft cocktail bar with a rotating seasonal menu.
Architecture: Tailwind CDN utility classes.
Palette: deep plum canvas (#1A0E1A), neon pink accent (#FF3D9A), moody and saturated.
Signature element: cocktail menu flip cards — each card flips on click/hover to
reveal the ingredient list and glassware on the back face, using a 3D CSS transform.
Sections: header, hero, menu flip-card grid, atmosphere/about, reservations CTA,
hours/location, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Velvet Hour | Craft Cocktail Bar</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#1A0E1A',light:'#241327',card:'#2C1730'}, accent:{DEFAULT:'#FF3D9A',hover:'#FF66AE',glow:'rgba(255,61,154,0.3)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], display:['Cormorant Garamond','serif'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Cormorant+Garamond:wght@500;600;700&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
  .font-display{font-family:'Cormorant Garamond',serif;}
  ::selection{background:rgba(255,61,154,0.3);}
  .hero-title{font-size:clamp(2.8rem,6.5vw,5.6rem);line-height:1.0;letter-spacing:-0.01em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .flip-card{perspective:1200px;height:340px;cursor:pointer;}
  .flip-inner{position:relative;width:100%;height:100%;transition:transform .6s cubic-bezier(.25,.8,.25,1);transform-style:preserve-3d;}
  .flip-card.flipped .flip-inner{transform:rotateY(180deg);}
  .flip-face{position:absolute;inset:0;backface-visibility:hidden;border-radius:1rem;}
  .flip-back{transform:rotateY(180deg);}
  input:focus,button:focus-visible{outline:2px solid #FF3D9A;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <a href="#" class="font-display text-2xl">Velvet Hour</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#menu" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">Menu</a>
        <a href="#about" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">About</a>
        <a href="#visit" class="text-sm text-white/60 hover:text-white uppercase tracking-wide">Visit</a>
      </nav>
      <a href="#visit" class="bg-accent hover:bg-accent-hover text-white font-semibold text-sm px-5 py-2.5 rounded-full transition-colors">Reserve a Table</a>
    </div>
  </div>
</header>

<section class="relative min-h-[92vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 75% 25%, rgba(255,61,154,0.1) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10 text-center">
    <p class="text-accent text-sm uppercase tracking-[0.2em] mb-6">A Speakeasy on Elm Street</p>
    <h1 class="hero-title font-display text-white mb-8">
      Drinks built for<br><span class="text-accent">slow nights.</span>
    </h1>
    <p class="text-lg text-white/50 max-w-md mx-auto mb-10 leading-relaxed">
      A seasonal cocktail menu, low light, and a bar team that asks what you actually
      like before they pour anything.
    </p>
    <a href="#menu" class="inline-flex items-center gap-2 bg-accent hover:bg-accent-hover text-white font-semibold px-8 py-4 rounded-full transition-all hover:-translate-y-0.5">View the Menu</a>
  </div>
</section>

<section id="menu" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">This Season</p>
      <h2 class="font-display text-4xl">Tap a card to flip it</h2>
    </div>
    <div id="menu-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"></div>
  </div>
</section>

<section id="about" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-4xl mx-auto px-6 lg:px-8 text-center reveal">
    <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">About Us</p>
    <h2 class="font-display text-3xl lg:text-4xl mb-6">No TVs. No top-40. No rush.</h2>
    <p class="text-white/50 leading-relaxed">
      Velvet Hour opened in 2019 behind an unmarked door, on the idea that a bar could
      be a place you actually talk to people. The menu changes with the seasons, the
      lighting stays low, and the only soundtrack is a vinyl record someone on staff
      picked that night.
    </p>
  </div>
</section>

<section id="visit" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-5xl mx-auto px-6 lg:px-8 grid sm:grid-cols-2 gap-12">
    <div class="reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Hours</p>
      <h2 class="font-display text-3xl mb-6">When we're open</h2>
      <div class="space-y-2 text-white/60 text-sm">
        <div class="flex justify-between border-b border-white/5 py-2"><span>Tue – Thu</span><span>6pm – 1am</span></div>
        <div class="flex justify-between border-b border-white/5 py-2"><span>Fri – Sat</span><span>6pm – 2am</span></div>
        <div class="flex justify-between border-b border-white/5 py-2"><span>Sun – Mon</span><span>Closed</span></div>
      </div>
    </div>
    <div class="reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Reservations</p>
      <h2 class="font-display text-3xl mb-6">Book a table</h2>
      <p class="text-white/50 mb-6 text-sm">Walk-ins welcome at the bar; tables of 4+ recommended to reserve ahead.</p>
      <a href="#" class="inline-flex items-center gap-2 bg-accent hover:bg-accent-hover text-white font-semibold px-7 py-3.5 rounded-full transition-all">Reserve Now</a>
    </div>
  </div>
</section>

<footer class="border-t border-white/5 py-12 bg-canvas-light">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p>© 2026 Velvet Hour</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Private Events</a><a href="#" class="hover:text-white/60">Contact</a></div>
  </div>
</footer>

<script>
const cocktails = [
  { name:'Smoke & Mirrors', front:'🥃', notes:'Mezcal · Smoked Cherry · Lime', ingredients:'2oz mezcal, 0.75oz smoked cherry syrup, 0.75oz lime, dash mole bitters', glass:'Rocks glass, smoked' },
  { name:'Midnight Fig', front:'🍸', notes:'Gin · Fig · Black Pepper', ingredients:'2oz gin, 0.5oz fig liqueur, 0.5oz lemon, black pepper tincture', glass:'Coupe' },
  { name:'Velvet Old Fashioned', front:'🥃', notes:'Bourbon · Demerara · Orange', ingredients:'2oz bourbon, 0.25oz demerara syrup, orange bitters, orange peel', glass:'Rocks glass' },
  { name:'Paper Crane', front:'🍹', notes:'Vodka · Yuzu · Elderflower', ingredients:'1.5oz vodka, 0.5oz yuzu, 0.5oz elderflower, soda top', glass:'Highball' },
  { name:'Last Light', front:'🍷', notes:'Rye · Aperitivo · Grapefruit', ingredients:'1.5oz rye, 1oz bitter aperitivo, 0.5oz grapefruit, soda', glass:'Wine glass' },
  { name:'Honey & Ash', front:'🥃', notes:'Scotch · Honey · Lapsang', ingredients:'2oz scotch, 0.5oz honey syrup, lapsang tea reduction', glass:'Rocks glass, smoked' },
];

function renderMenu(){
  const grid = document.getElementById('menu-grid');
  grid.innerHTML = '';
  cocktails.forEach((c,i)=>{
    const card = document.createElement('div');
    card.className = 'flip-card reveal';
    card.style.transitionDelay = (i*60)+'ms';
    card.innerHTML = `
      <div class="flip-inner">
        <div class="flip-face flip-front bg-canvas-card border border-white/10 flex flex-col items-center justify-center text-center p-6">
          <div class="text-5xl mb-4">${c.front}</div>
          <h3 class="font-display text-2xl mb-2">${c.name}</h3>
          <p class="text-sm text-white/40">${c.notes}</p>
          <p class="text-xs text-white/25 mt-6">Tap to see recipe</p>
        </div>
        <div class="flip-face flip-back bg-accent flex flex-col items-center justify-center text-center p-6 text-white">
          <p class="text-xs uppercase tracking-wide opacity-75 mb-3">Recipe</p>
          <p class="text-sm leading-relaxed mb-4">${c.ingredients}</p>
          <p class="text-xs uppercase tracking-wide opacity-75">Served In</p>
          <p class="font-display text-lg">${c.glass}</p>
        </div>
      </div>
    `;
    card.addEventListener('click', ()=>card.classList.toggle('flipped'));
    grid.appendChild(card);
    revealObserver.observe(card);
  });
}

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(26,14,26,0.85)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

renderMenu();
</script>
</body>
</html>
```
