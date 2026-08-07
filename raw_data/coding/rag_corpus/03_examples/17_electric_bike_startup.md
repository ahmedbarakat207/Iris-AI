# Example — Electric Bike Startup (Tailwind Architecture)

Tags: example, full-site, ebike, electric-bike, startup, product-launch, tailwind, dark-theme, electric-blue, spec-comparison, range-slider, tech

Niche: direct-to-consumer electric bike company launching a new model.
Architecture: Tailwind CDN utility classes.
Palette: near-black canvas (#0A0B0D), electric blue accent (#3D8BFF), crisp technical
feel with mono accents for spec numbers.
Signature element: an interactive range/spec comparison — a slider that adjusts
"rider weight" and live-updates an estimated range number, plus a model comparison
table (this model vs. previous generation).
Sections: header, hero, live range calculator, spec comparison table, gallery (icon
grid standing in for photos), reserve/preorder CTA, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Volt Cycles | The All-New Volt One E-Bike</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#0A0B0D',light:'#121317',card:'#181A1F'}, accent:{DEFAULT:'#3D8BFF',hover:'#5C9DFF',glow:'rgba(61,139,255,0.3)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], mono:['JetBrains Mono','monospace'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;}
  .font-mono{font-family:'JetBrains Mono',monospace;}
  ::selection{background:rgba(61,139,255,0.3);}
  .hero-title{font-size:clamp(2.6rem,6.5vw,5.6rem);line-height:0.98;letter-spacing:-0.02em;}
  .reveal{opacity:0;transform:translateY(28px);transition:all .7s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  input[type=range]{-webkit-appearance:none;height:6px;background:#23252B;border-radius:3px;}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:22px;height:22px;border-radius:50%;background:#3D8BFF;cursor:pointer;box-shadow:0 0 0 6px rgba(61,139,255,0.15);}
  input:focus,button:focus-visible{outline:2px solid #3D8BFF;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <a href="#" class="font-bold text-xl tracking-tight">VOLT</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#range" class="text-sm text-white/60 hover:text-white">Range Calculator</a>
        <a href="#specs" class="text-sm text-white/60 hover:text-white">Specs</a>
        <a href="#preorder" class="text-sm text-white/60 hover:text-white">Preorder</a>
      </nav>
      <a href="#preorder" class="bg-accent hover:bg-accent-hover text-white font-semibold text-sm px-5 py-2.5 rounded-lg transition-colors">Reserve — $99</a>
    </div>
  </div>
</header>

<section class="relative min-h-[94vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 25% 25%, rgba(61,139,255,0.08) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
    <p class="text-accent text-sm font-mono uppercase tracking-widest mb-6">INTRODUCING VOLT ONE</p>
    <h1 class="hero-title font-extrabold text-white mb-8 max-w-4xl">
      75 miles per charge.<br><span class="text-accent">Zero compromises.</span>
    </h1>
    <p class="text-lg text-white/50 max-w-md mb-10 leading-relaxed">
      A torque sensor that actually feels human, a battery that lasts a week of
      commutes, and a frame that doesn't look like a science project.
    </p>
    <div class="flex flex-col sm:flex-row gap-4">
      <a href="#preorder" class="bg-accent hover:bg-accent-hover text-white font-semibold px-8 py-4 rounded-xl transition-all hover:-translate-y-0.5">Reserve Yours — $99</a>
      <a href="#range" class="border border-white/15 hover:border-white/30 font-medium px-8 py-4 rounded-xl transition-all hover:bg-white/5">Calculate Your Range</a>
    </div>
  </div>
</section>

<section id="range" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-3xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-14 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Range Calculator</p>
      <h2 class="text-3xl lg:text-4xl font-bold">How far will you go?</h2>
    </div>
    <div class="reveal bg-canvas-card border border-white/10 rounded-2xl p-8 lg:p-10">
      <div class="mb-8">
        <div class="flex justify-between mb-3">
          <label class="text-sm text-white/60">Rider Weight</label>
          <span class="font-mono text-accent font-bold" id="weight-display">165 lbs</span>
        </div>
        <input type="range" id="weight-slider" min="100" max="280" value="165" class="w-full">
      </div>
      <div class="mb-8">
        <div class="flex justify-between mb-3">
          <label class="text-sm text-white/60">Assist Mode</label>
          <span class="font-mono text-accent font-bold" id="mode-display">Eco</span>
        </div>
        <input type="range" id="mode-slider" min="0" max="2" value="0" step="1" class="w-full">
      </div>
      <div class="pt-6 border-t border-white/10 text-center">
        <p class="text-xs text-white/40 uppercase tracking-wide mb-2">Estimated Range</p>
        <p class="font-mono text-5xl font-bold text-accent" id="range-result">75 mi</p>
      </div>
    </div>
  </div>
</section>

<section id="specs" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-14 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Spec Comparison</p>
      <h2 class="text-3xl lg:text-4xl font-bold">Volt One vs. Gen 1</h2>
    </div>
    <div class="reveal overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-white/10">
            <th class="text-left py-4 text-white/40 font-medium">Spec</th>
            <th class="text-left py-4 text-white/60 font-medium">Gen 1</th>
            <th class="text-left py-4 text-accent font-bold">Volt One</th>
          </tr>
        </thead>
        <tbody class="font-mono">
          <tr class="border-b border-white/5"><td class="py-4 text-white/50">Range</td><td class="py-4">42 mi</td><td class="py-4 text-accent font-bold">75 mi</td></tr>
          <tr class="border-b border-white/5"><td class="py-4 text-white/50">Top Speed</td><td class="py-4">20 mph</td><td class="py-4 text-accent font-bold">28 mph</td></tr>
          <tr class="border-b border-white/5"><td class="py-4 text-white/50">Charge Time</td><td class="py-4">5.5 hrs</td><td class="py-4 text-accent font-bold">3.2 hrs</td></tr>
          <tr class="border-b border-white/5"><td class="py-4 text-white/50">Weight</td><td class="py-4">52 lbs</td><td class="py-4 text-accent font-bold">44 lbs</td></tr>
          <tr><td class="py-4 text-white/50">Motor Torque</td><td class="py-4">65 Nm</td><td class="py-4 text-accent font-bold">85 Nm</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="py-24 lg:py-32">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Engineering</p>
      <h2 class="text-3xl lg:text-4xl font-bold">Built different, on purpose</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8 text-center"><div class="text-4xl mb-4">🔋</div><h3 class="font-semibold mb-2">Removable Battery</h3><p class="text-sm text-white/45">Pull it out and charge inside — no more dragging an extension cord to the garage.</p></div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8 text-center" style="transition-delay:.1s"><div class="text-4xl mb-4">⚙️</div><h3 class="font-semibold mb-2">Torque Sensor Pedal Assist</h3><p class="text-sm text-white/45">Responds to how hard you're pedaling, not just whether you are — it feels like a bike, not a scooter.</p></div>
      <div class="reveal bg-canvas-card border border-white/5 rounded-2xl p-8 text-center" style="transition-delay:.2s"><div class="text-4xl mb-4">🔒</div><h3 class="font-semibold mb-2">Integrated GPS Lock</h3><p class="text-sm text-white/45">Built-in tracking and remote motor lock if it's ever moved without your phone nearby.</p></div>
    </div>
  </div>
</section>

<section id="preorder" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-2xl mx-auto px-6 lg:px-8 text-center">
    <div class="reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Limited First Run</p>
      <h2 class="text-3xl lg:text-4xl font-bold mb-4">Reserve your Volt One</h2>
      <p class="text-white/50 mb-8">$99 fully refundable deposit. First deliveries ship in October.</p>
      <a href="#" class="inline-flex items-center gap-2 bg-accent hover:bg-accent-hover text-white font-semibold px-10 py-4 rounded-xl transition-all hover:-translate-y-0.5">Reserve Now — $99</a>
      <p class="text-xs text-white/30 mt-4">No payment until your build slot is confirmed.</p>
    </div>
  </div>
</section>

<footer class="border-t border-white/5 py-12">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-white/35">
    <p>© 2026 Volt Cycles, Inc.</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Warranty</a><a href="#" class="hover:text-white/60">Support</a></div>
  </div>
</footer>

<script>
const weightSlider = document.getElementById('weight-slider');
const modeSlider = document.getElementById('mode-slider');
const modes = ['Eco', 'Trail', 'Boost'];
const baseRangeByMode = [75, 58, 42];

function updateRange(){
  const weight = parseInt(weightSlider.value);
  const modeIndex = parseInt(modeSlider.value);
  document.getElementById('weight-display').textContent = weight + ' lbs';
  document.getElementById('mode-display').textContent = modes[modeIndex];
  const weightPenalty = Math.max(0, (weight - 165) * 0.12);
  const range = Math.max(18, Math.round(baseRangeByMode[modeIndex] - weightPenalty));
  document.getElementById('range-result').textContent = range + ' mi';
}
weightSlider.addEventListener('input', updateRange);
modeSlider.addEventListener('input', updateRange);
updateRange();

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(10,11,13,0.85)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));
</script>
</body>
</html>
```
