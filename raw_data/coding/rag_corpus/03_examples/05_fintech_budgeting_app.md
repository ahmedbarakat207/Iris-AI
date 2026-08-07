# Example — Fintech Budgeting App Landing Page (Tailwind Architecture)

Tags: example, full-site, fintech, saas, budgeting-app, tailwind, dark-theme, emerald, mono, animated-counters, dashboard-mockup

Niche: consumer budgeting/personal-finance SaaS app landing page (not e-commerce —
no cart; conversion goal is sign-up).
Architecture: Tailwind CDN utility classes.
Palette: near-black canvas (#0A0E0C), emerald accent (#34D399), monospace for all
dollar figures/stats to signal precision.
Signature element: an animated dashboard mockup panel with counting-up stat numbers
that animate when scrolled into view, using requestAnimationFrame easing rather than
a plugin.
Sections: header, hero with dashboard mockup, animated stats strip, feature grid,
how-it-works steps, pricing, FAQ accordion, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ledgerly | Budgeting That Actually Sticks</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  theme:{extend:{
    colors:{ canvas:{DEFAULT:'#0A0E0C',light:'#10150F',card:'#161C16'}, accent:{DEFAULT:'#34D399',hover:'#4FE3AC',glow:'rgba(52,211,153,0.25)'} },
    fontFamily:{ sans:['Inter','system-ui','sans-serif'], mono:['JetBrains Mono','monospace'] }
  }}
}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
  .font-mono{font-family:'JetBrains Mono',monospace;}
  ::selection{background:rgba(52,211,153,0.3);}
  .hero-title{font-size:clamp(2.6rem,6vw,5rem);line-height:1.03;letter-spacing:-0.025em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .mockup-bar{transition:width 1.2s cubic-bezier(.16,1,.3,1);}
  .accordion-content{max-height:0;overflow:hidden;transition:max-height .35s cubic-bezier(.16,1,.3,1);}
  .accordion-item.open .accordion-content{max-height:200px;}
  .accordion-item.open .accordion-chevron{transform:rotate(180deg);}
  .accordion-chevron{transition:transform .3s ease;}
  input:focus,button:focus-visible{outline:2px solid #34D399;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <a href="#" class="font-bold text-xl tracking-tight">Ledgerly</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#features" class="text-sm text-white/60 hover:text-white">Features</a>
        <a href="#how" class="text-sm text-white/60 hover:text-white">How It Works</a>
        <a href="#pricing" class="text-sm text-white/60 hover:text-white">Pricing</a>
      </nav>
      <a href="#pricing" class="bg-accent hover:bg-accent-hover text-canvas font-semibold text-sm px-5 py-2.5 rounded-lg transition-colors">Get Started Free</a>
    </div>
  </div>
</header>

<section class="relative min-h-[94vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 25% 25%, rgba(52,211,153,0.07) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10 grid lg:grid-cols-2 gap-16 items-center">
    <div class="space-y-7">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/5">
        <span class="w-1.5 h-1.5 rounded-full bg-accent"></span>
        <span class="text-xs font-medium text-accent tracking-wider uppercase">Now with automatic bill detection</span>
      </div>
      <h1 class="hero-title font-extrabold text-white">
        See where your<br>money <span class="text-accent">actually</span> goes.
      </h1>
      <p class="text-lg text-white/50 max-w-md leading-relaxed">
        Ledgerly connects to your accounts and sorts every transaction automatically —
        no spreadsheets, no manual categorizing, no guilt-tripping.
      </p>
      <div class="flex flex-col sm:flex-row gap-4">
        <a href="#pricing" class="bg-accent hover:bg-accent-hover text-canvas font-semibold px-8 py-4 rounded-xl transition-all hover:-translate-y-0.5">Start Free — No Card Required</a>
        <a href="#how" class="border border-white/15 hover:border-white/30 font-medium px-8 py-4 rounded-xl transition-all hover:bg-white/5">See How It Works</a>
      </div>
    </div>
    <div class="relative">
      <div class="bg-canvas-card border border-white/10 rounded-2xl p-6 shadow-2xl">
        <div class="flex items-center justify-between mb-6">
          <p class="text-sm text-white/40">This Month</p>
          <p class="text-xs text-accent font-mono">+ on track</p>
        </div>
        <p class="font-mono text-3xl font-bold mb-1" id="stat-spent">$0</p>
        <p class="text-xs text-white/40 mb-6">spent of $3,200 budget</p>
        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-xs mb-1.5"><span class="text-white/60">Groceries</span><span class="font-mono text-white/40">$412 / $500</span></div>
            <div class="h-2 bg-white/5 rounded-full overflow-hidden"><div class="mockup-bar h-full bg-accent rounded-full" style="width:0%" data-target="82"></div></div>
          </div>
          <div>
            <div class="flex justify-between text-xs mb-1.5"><span class="text-white/60">Dining Out</span><span class="font-mono text-white/40">$268 / $300</span></div>
            <div class="h-2 bg-white/5 rounded-full overflow-hidden"><div class="mockup-bar h-full bg-yellow-400 rounded-full" style="width:0%" data-target="89"></div></div>
          </div>
          <div>
            <div class="flex justify-between text-xs mb-1.5"><span class="text-white/60">Subscriptions</span><span class="font-mono text-white/40">$84 / $120</span></div>
            <div class="h-2 bg-white/5 rounded-full overflow-hidden"><div class="mockup-bar h-full bg-accent rounded-full" style="width:0%" data-target="70"></div></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="py-16 border-t border-white/5 bg-canvas-light">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 grid grid-cols-2 sm:grid-cols-4 gap-8 text-center" id="stats-strip">
    <div class="reveal"><p class="font-mono text-3xl font-bold text-accent" data-counter="148000" id="counter-1">0</p><p class="text-xs text-white/40 uppercase tracking-wider mt-2">Accounts Connected</p></div>
    <div class="reveal"><p class="font-mono text-3xl font-bold text-accent" data-counter="2400000" id="counter-2">0</p><p class="text-xs text-white/40 uppercase tracking-wider mt-2">Tracked Monthly ($)</p></div>
    <div class="reveal"><p class="font-mono text-3xl font-bold text-accent" data-counter="94" id="counter-3">0</p><p class="text-xs text-white/40 uppercase tracking-wider mt-2">% Stay On Budget</p></div>
    <div class="reveal"><p class="font-mono text-3xl font-bold text-accent" data-counter="4" id="counter-4">0</p><p class="text-xs text-white/40 uppercase tracking-wider mt-2">Minute Setup</p></div>
  </div>
</section>

<section id="features" class="py-24 lg:py-32">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Why Ledgerly</p>
      <h2 class="text-3xl lg:text-4xl font-bold">Built for people who hate budgeting apps</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8">
        <div class="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-5"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="1.5"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-7"/></svg></div>
        <h3 class="font-semibold mb-2">Auto-categorized</h3>
        <p class="text-sm text-white/45">Every transaction is sorted the moment it posts — no manual tagging, ever.</p>
      </div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8" style="transition-delay:.1s">
        <div class="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-5"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg></div>
        <h3 class="font-semibold mb-2">Real-time alerts</h3>
        <p class="text-sm text-white/45">A nudge the moment you're close to a budget line, not a surprise at month-end.</p>
      </div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8" style="transition-delay:.2s">
        <div class="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-5"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="1.5"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>
        <h3 class="font-semibold mb-2">Bank-level security</h3>
        <p class="text-sm text-white/45">256-bit encryption and read-only account access — we can't move your money.</p>
      </div>
    </div>
  </div>
</section>

<section id="how" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Getting Started</p>
      <h2 class="text-3xl lg:text-4xl font-bold">Three steps, four minutes</h2>
    </div>
    <div class="space-y-6">
      <div class="reveal flex gap-6 items-start bg-canvas-card border border-white/5 rounded-2xl p-6">
        <span class="font-mono text-accent text-xl font-bold">01</span>
        <div><h3 class="font-semibold mb-1">Connect your accounts</h3><p class="text-sm text-white/45">Securely link checking, savings, and credit cards via your bank's login.</p></div>
      </div>
      <div class="reveal flex gap-6 items-start bg-canvas-card border border-white/5 rounded-2xl p-6">
        <span class="font-mono text-accent text-xl font-bold">02</span>
        <div><h3 class="font-semibold mb-1">Set your budget lines</h3><p class="text-sm text-white/45">We suggest starting amounts based on your last 90 days of spending.</p></div>
      </div>
      <div class="reveal flex gap-6 items-start bg-canvas-card border border-white/5 rounded-2xl p-6">
        <span class="font-mono text-accent text-xl font-bold">03</span>
        <div><h3 class="font-semibold mb-1">Get out of the way</h3><p class="text-sm text-white/45">Ledgerly tracks everything automatically — check in weekly, not daily.</p></div>
      </div>
    </div>
  </div>
</section>

<section id="pricing" class="py-24 lg:py-32">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Pricing</p>
      <h2 class="text-3xl lg:text-4xl font-bold">Simple, honest pricing</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-2xl mx-auto">
      <div class="reveal bg-canvas-card border border-white/10 rounded-2xl p-8">
        <p class="text-sm text-white/40 uppercase tracking-wide mb-2">Free</p>
        <p class="font-mono text-4xl font-bold mb-4">$0</p>
        <ul class="space-y-2 text-sm text-white/55 mb-6">
          <li>1 connected account</li>
          <li>Auto-categorization</li>
          <li>Weekly email summary</li>
        </ul>
        <a href="#" class="block text-center border border-white/15 hover:border-accent hover:text-accent font-semibold py-3 rounded-xl transition-all">Start Free</a>
      </div>
      <div class="reveal bg-canvas-card border border-accent rounded-2xl p-8 relative">
        <span class="absolute -top-3 left-8 bg-accent text-canvas text-xs font-bold px-3 py-1 rounded-full">Most Popular</span>
        <p class="text-sm text-white/40 uppercase tracking-wide mb-2">Plus</p>
        <p class="font-mono text-4xl font-bold mb-4">$8<span class="text-base text-white/40">/mo</span></p>
        <ul class="space-y-2 text-sm text-white/55 mb-6">
          <li>Unlimited accounts</li>
          <li>Real-time alerts</li>
          <li>Custom budget categories</li>
        </ul>
        <a href="#" class="block text-center bg-accent hover:bg-accent-hover text-canvas font-bold py-3 rounded-xl transition-all">Start 14-Day Trial</a>
      </div>
    </div>
  </div>
</section>

<section class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-3xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-12 reveal"><h2 class="text-3xl font-bold">Common questions</h2></div>
    <div class="space-y-3" id="faq-list">
      <div class="accordion-item reveal bg-canvas-card border border-white/5 rounded-xl">
        <button class="accordion-trigger w-full flex items-center justify-between p-5 text-left font-medium">
          <span>Is my bank data safe?</span>
          <svg class="accordion-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="accordion-content px-5"><p class="text-sm text-white/50 pb-5">Yes — we use read-only, 256-bit encrypted connections through a regulated banking partner. Ledgerly never has the ability to move money.</p></div>
      </div>
      <div class="accordion-item reveal bg-canvas-card border border-white/5 rounded-xl">
        <button class="accordion-trigger w-full flex items-center justify-between p-5 text-left font-medium">
          <span>Can I cancel anytime?</span>
          <svg class="accordion-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="accordion-content px-5"><p class="text-sm text-white/50 pb-5">Yes, with one click from your account settings — no calls, no retention flow.</p></div>
      </div>
      <div class="accordion-item reveal bg-canvas-card border border-white/5 rounded-xl">
        <button class="accordion-trigger w-full flex items-center justify-between p-5 text-left font-medium">
          <span>Which banks are supported?</span>
          <svg class="accordion-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="accordion-content px-5"><p class="text-sm text-white/50 pb-5">Over 11,000 banks and credit unions in the US and Canada, including every major institution.</p></div>
      </div>
    </div>
  </div>
</section>

<footer class="border-t border-white/5 py-12">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p>© 2026 Ledgerly, Inc.</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Privacy</a><a href="#" class="hover:text-white/60">Security</a></div>
  </div>
</footer>

<script>
const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

function animateBars(){
  document.querySelectorAll('.mockup-bar').forEach(bar=>{
    bar.style.width = bar.dataset.target + '%';
  });
  let spent = 0;
  const target = 764;
  const spentEl = document.getElementById('stat-spent');
  const tick = () => {
    spent = Math.min(target, spent + Math.ceil(target/40));
    spentEl.textContent = '$' + spent.toLocaleString();
    if (spent < target) requestAnimationFrame(tick);
  };
  tick();
}
const mockupObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ animateBars(); mockupObserver.disconnect(); } });
}, {threshold:0.4});
mockupObserver.observe(document.getElementById('stat-spent'));

function animateCounter(el, target){
  let current = 0;
  const duration = 1400;
  const start = performance.now();
  function format(n){
    if (n >= 1000000) return '$' + (n/1000000).toFixed(1) + 'M';
    if (n >= 1000 && target >= 1000) return n.toLocaleString();
    return n.toString();
  }
  function step(now){
    const progress = Math.min(1, (now-start)/duration);
    const eased = 1 - Math.pow(1-progress, 3);
    current = Math.floor(eased * target);
    el.textContent = el.id === 'counter-3' ? current + '%' : (el.id==='counter-4' ? current : format(current));
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}
const statsObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      document.querySelectorAll('[data-counter]').forEach(el=>animateCounter(el, parseInt(el.dataset.counter)));
      statsObserver.disconnect();
    }
  });
}, {threshold:0.3});
statsObserver.observe(document.getElementById('stats-strip'));

document.querySelectorAll('.accordion-trigger').forEach(trigger=>{
  trigger.addEventListener('click', ()=>{
    const item = trigger.closest('.accordion-item');
    const wasOpen = item.classList.contains('open');
    document.querySelectorAll('.accordion-item').forEach(i=>i.classList.remove('open'));
    if (!wasOpen) item.classList.add('open');
  });
});

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(10,14,12,0.85)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});
</script>
</body>
</html>
```
