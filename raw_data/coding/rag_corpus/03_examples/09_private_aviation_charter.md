# Example — Private Aviation Charter (Tailwind Architecture)

Tags: example, full-site, private-jet, aviation, luxury, charter, tailwind, dark-theme, obsidian, champagne-gold, route-selector, luxury-minimal

Niche: private jet charter booking service.
Architecture: Tailwind CDN utility classes.
Palette: obsidian canvas (#0B0B0D), champagne gold accent (#D4AF7A), generous
whitespace, restrained motion (luxury = quiet, not flashy).
Signature element: a city-pair route selector — two dropdowns (from/to) that update
an estimated flight time and price range live, no page reload.
Sections: header, hero, route selector, fleet cards, how-charter-works steps,
testimonial, contact/inquiry form, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aerion Charter | Private Jet Charter, On Your Schedule</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#0B0B0D',light:'#131315',card:'#191919'}, accent:{DEFAULT:'#D4AF7A',hover:'#E2C394',glow:'rgba(212,175,122,0.25)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], display:['Cormorant Garamond','serif'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Cormorant+Garamond:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;font-weight:300;}
  .font-display{font-family:'Cormorant Garamond',serif;}
  ::selection{background:rgba(212,175,122,0.25);}
  .hero-title{font-size:clamp(2.6rem,6vw,5.4rem);line-height:1.05;letter-spacing:-0.01em;}
  .reveal{opacity:0;transform:translateY(24px);transition:all .8s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  select:focus,input:focus,button:focus-visible{outline:1px solid #D4AF7A;outline-offset:2px;}
  .route-line{stroke-dasharray:4 4;animation:dash 30s linear infinite;}
  @keyframes dash{to{stroke-dashoffset:-1000;}}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="bg-canvas text-white min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-24">
      <a href="#" class="font-display text-2xl tracking-wide">AERION</a>
      <nav class="hidden lg:flex items-center gap-12 absolute left-1/2 -translate-x-1/2">
        <a href="#route" class="text-xs text-white/60 hover:text-white uppercase tracking-[0.15em]">Plan a Flight</a>
        <a href="#fleet" class="text-xs text-white/60 hover:text-white uppercase tracking-[0.15em]">Fleet</a>
        <a href="#contact" class="text-xs text-white/60 hover:text-white uppercase tracking-[0.15em]">Inquire</a>
      </nav>
      <a href="#contact" class="border border-accent/50 text-accent hover:bg-accent hover:text-canvas text-xs uppercase tracking-[0.1em] px-6 py-3 transition-all">Request Quote</a>
    </div>
  </div>
</header>

<section class="relative min-h-[94vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 70% 20%, rgba(212,175,122,0.06) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
    <p class="text-accent text-xs uppercase tracking-[0.2em] mb-8">On-Demand Private Aviation</p>
    <h1 class="hero-title font-display text-white mb-8 max-w-3xl">
      Your schedule.<br>Never the airline's.
    </h1>
    <p class="text-lg text-white/45 max-w-md mb-10 leading-relaxed font-light">
      Access over 4,000 light and midsize jets across North America, bookable in
      as little as four hours' notice.
    </p>
    <a href="#route" class="inline-flex items-center gap-3 border border-accent/50 text-accent hover:bg-accent hover:text-canvas text-xs uppercase tracking-[0.1em] px-8 py-4 transition-all">Plan Your Route</a>
  </div>
</section>

<section id="route" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-14 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Plan a Flight</p>
      <h2 class="font-display text-3xl lg:text-4xl">Where are you headed?</h2>
    </div>
    <div class="bg-canvas-card border border-white/10 p-8 lg:p-10 reveal">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
        <div>
          <label class="block text-xs text-white/40 uppercase tracking-wide mb-2">Departing From</label>
          <select id="from-select" class="w-full bg-canvas border border-white/10 px-4 py-3 text-sm">
            <option value="nyc">New York (TEB)</option>
            <option value="la">Los Angeles (VNY)</option>
            <option value="miami">Miami (OPF)</option>
            <option value="chicago">Chicago (MDW)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-white/40 uppercase tracking-wide mb-2">Flying To</label>
          <select id="to-select" class="w-full bg-canvas border border-white/10 px-4 py-3 text-sm">
            <option value="la">Los Angeles (VNY)</option>
            <option value="nyc">New York (TEB)</option>
            <option value="miami">Miami (OPF)</option>
            <option value="chicago">Chicago (MDW)</option>
            <option value="aspen">Aspen (ASE)</option>
          </select>
        </div>
      </div>
      <div class="grid grid-cols-2 gap-6 pt-6 border-t border-white/10">
        <div>
          <p class="text-xs text-white/40 uppercase tracking-wide mb-2">Estimated Flight Time</p>
          <p id="flight-time" class="font-display text-3xl text-accent">5h 10m</p>
        </div>
        <div>
          <p class="text-xs text-white/40 uppercase tracking-wide mb-2">Estimated Price Range</p>
          <p id="flight-price" class="font-display text-3xl text-accent">$24,000 – $38,000</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="fleet" class="py-24 lg:py-32 bg-canvas-light border-t border-white/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">The Fleet</p>
      <h2 class="font-display text-3xl lg:text-4xl">Three categories, one standard</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-8">
      <div class="reveal text-center">
        <div class="aspect-[4/3] bg-canvas-card border border-white/5 mb-5 flex items-center justify-center text-5xl">🛩️</div>
        <h3 class="font-display text-xl mb-2">Light Jet</h3>
        <p class="text-sm text-white/45 mb-3">Up to 6 passengers · 1,500nm range</p>
        <p class="text-accent text-sm">From $4,800/hr</p>
      </div>
      <div class="reveal text-center" style="transition-delay:.1s">
        <div class="aspect-[4/3] bg-canvas-card border border-white/5 mb-5 flex items-center justify-center text-5xl">✈️</div>
        <h3 class="font-display text-xl mb-2">Midsize Jet</h3>
        <p class="text-sm text-white/45 mb-3">Up to 9 passengers · 2,800nm range</p>
        <p class="text-accent text-sm">From $6,900/hr</p>
      </div>
      <div class="reveal text-center" style="transition-delay:.2s">
        <div class="aspect-[4/3] bg-canvas-card border border-white/5 mb-5 flex items-center justify-center text-5xl">🛫</div>
        <h3 class="font-display text-xl mb-2">Heavy Jet</h3>
        <p class="text-sm text-white/45 mb-3">Up to 14 passengers · 4,500nm range</p>
        <p class="text-accent text-sm">From $11,200/hr</p>
      </div>
    </div>
  </div>
</section>

<section class="py-24 lg:py-32">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal"><h2 class="font-display text-3xl lg:text-4xl">How charter works</h2></div>
    <div class="grid grid-cols-1 sm:grid-cols-4 gap-8 text-center">
      <div class="reveal"><p class="font-display text-3xl text-accent mb-3">01</p><p class="text-sm text-white/55">Tell us your route and travel dates</p></div>
      <div class="reveal" style="transition-delay:.1s"><p class="font-display text-3xl text-accent mb-3">02</p><p class="text-sm text-white/55">We source quotes from vetted operators</p></div>
      <div class="reveal" style="transition-delay:.2s"><p class="font-display text-3xl text-accent mb-3">03</p><p class="text-sm text-white/55">You choose the aircraft and confirm</p></div>
      <div class="reveal" style="transition-delay:.3s"><p class="font-display text-3xl text-accent mb-3">04</p><p class="text-sm text-white/55">Arrive 10 minutes before departure</p></div>
    </div>
  </div>
</section>

<section class="py-20 bg-canvas-light border-t border-white/5">
  <div class="max-w-2xl mx-auto px-6 text-center reveal">
    <p class="font-display text-2xl text-white/85 leading-relaxed mb-6">"We booked four hours before wheels-up for a family emergency. Aerion had us in the air in under three."</p>
    <p class="text-sm text-white/40 uppercase tracking-wide">Client since 2022</p>
  </div>
</section>

<section id="contact" class="py-24 lg:py-32 border-t border-white/5">
  <div class="max-w-2xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-12 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Get a Quote</p>
      <h2 class="font-display text-3xl">Request charter availability</h2>
    </div>
    <form id="contact-form" class="reveal space-y-5" novalidate>
      <div>
        <input type="text" id="name" placeholder="Full name" required class="w-full bg-canvas-card border border-white/10 px-4 py-3 text-sm">
        <span class="text-xs text-red-400 block mt-1" id="name-error"></span>
      </div>
      <div>
        <input type="email" id="email" placeholder="Email address" required class="w-full bg-canvas-card border border-white/10 px-4 py-3 text-sm">
        <span class="text-xs text-red-400 block mt-1" id="email-error"></span>
      </div>
      <div>
        <textarea id="message" placeholder="Route, dates, and passenger count" rows="3" required class="w-full bg-canvas-card border border-white/10 px-4 py-3 text-sm"></textarea>
        <span class="text-xs text-red-400 block mt-1" id="message-error"></span>
      </div>
      <button type="submit" class="w-full border border-accent/50 text-accent hover:bg-accent hover:text-canvas text-xs uppercase tracking-[0.1em] py-4 transition-all">Request Quote</button>
      <p class="text-sm text-center" id="form-status"></p>
    </form>
  </div>
</section>

<footer class="border-t border-white/5 py-12">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-white/30 uppercase tracking-wide">
    <p>© 2026 Aerion Charter</p>
    <div class="flex gap-6"><a href="#" class="hover:text-white/60">Privacy</a><a href="#" class="hover:text-white/60">Safety</a></div>
  </div>
</footer>

<script>
const routes = {
  'nyc-la':{time:'5h 25m', price:'$26,000 – $41,000'}, 'la-nyc':{time:'5h 10m', price:'$26,000 – $41,000'},
  'nyc-miami':{time:'2h 45m', price:'$12,000 – $19,000'}, 'miami-nyc':{time:'2h 50m', price:'$12,000 – $19,000'},
  'nyc-chicago':{time:'2h 10m', price:'$9,500 – $15,000'}, 'chicago-nyc':{time:'2h 15m', price:'$9,500 – $15,000'},
  'la-miami':{time:'4h 50m', price:'$24,000 – $38,000'}, 'miami-la':{time:'4h 55m', price:'$24,000 – $38,000'},
  'la-chicago':{time:'4h 05m', price:'$18,000 – $28,000'}, 'chicago-la':{time:'4h 10m', price:'$18,000 – $28,000'},
  'nyc-aspen':{time:'4h 15m', price:'$19,000 – $29,000'}, 'la-aspen':{time:'2h 05m', price:'$10,000 – $16,000'},
  'miami-aspen':{time:'4h 30m', price:'$20,000 – $31,000'}, 'chicago-aspen':{time:'2h 35m', price:'$11,500 – $18,000'},
  'miami-chicago':{time:'3h 05m', price:'$13,500 – $21,000'}, 'chicago-miami':{time:'3h 10m', price:'$13,500 – $21,000'},
};
function updateRoute(){
  const from = document.getElementById('from-select').value;
  const to = document.getElementById('to-select').value;
  if (from === to) {
    document.getElementById('flight-time').textContent = '—';
    document.getElementById('flight-price').textContent = 'Select two different cities';
    return;
  }
  const key = `${from}-${to}`;
  const reverseKey = `${to}-${from}`;
  const route = routes[key] || routes[reverseKey] || { time:'3h 30m', price:'$15,000 – $24,000' };
  document.getElementById('flight-time').textContent = route.time;
  document.getElementById('flight-price').textContent = route.price;
}
document.getElementById('from-select').addEventListener('change', updateRoute);
document.getElementById('to-select').addEventListener('change', updateRoute);
updateRoute();

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  if (window.scrollY>80){ header.style.background='rgba(11,11,13,0.9)'; header.style.backdropFilter='blur(20px)'; header.style.borderBottom='1px solid rgba(255,255,255,0.05)'; }
  else { header.style.background=''; header.style.backdropFilter=''; header.style.borderBottom=''; }
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

const form = document.getElementById('contact-form');
const validators = {
  name: v => v.trim().length >= 2 || 'Please enter your full name.',
  email: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Enter a valid email address.',
  message: v => v.trim().length >= 10 || 'Tell us a bit more about your trip.'
};
function validateField(id){
  const field = document.getElementById(id);
  const errorEl = document.getElementById(`${id}-error`);
  const result = validators[id](field.value);
  if (result === true) { errorEl.textContent=''; return true; }
  errorEl.textContent = result; return false;
}
Object.keys(validators).forEach(id=>{
  document.getElementById(id).addEventListener('blur', ()=>validateField(id));
});
form.addEventListener('submit', (e)=>{
  e.preventDefault();
  const allValid = Object.keys(validators).map(validateField).every(Boolean);
  const status = document.getElementById('form-status');
  if (!allValid) { status.textContent = 'Please fix the highlighted fields.'; status.className='text-sm text-center text-red-400'; return; }
  const btn = form.querySelector('button[type=submit]');
  btn.disabled = true; btn.textContent = 'Sending...';
  setTimeout(()=>{
    status.textContent = "Thank you — a charter specialist will respond within the hour.";
    status.className = 'text-sm text-center text-accent';
    form.reset(); btn.disabled=false; btn.textContent='Request Quote';
  }, 900);
});
</script>
</body>
</html>
```
