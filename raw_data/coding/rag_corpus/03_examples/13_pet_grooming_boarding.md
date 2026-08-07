# Example — Pet Grooming & Boarding (Tailwind Architecture)

Tags: example, full-site, pet-grooming, pet-boarding, pets, local-service, tailwind, light-theme, coral, cream, service-tiers, booking-widget

Niche: neighborhood pet grooming and boarding service.
Architecture: Tailwind CDN utility classes, light mode (an exception to the
dark-theme-heavy default in this corpus — proves Tailwind works fine for light too).
Palette: cream canvas (#FFF8F2), warm coral accent (#FF7E5F), soft and friendly.
Signature element: a service-tier comparison table plus a lightweight booking-request
widget (date + service-type selector) that produces a confirmation summary without a
real backend.
Sections: header, hero, service tiers, booking widget, gallery/testimonials, FAQ,
footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Waggle &amp; Co. | Pet Grooming &amp; Boarding</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#FFF8F2',light:'#FFFFFF',card:'#FFFFFF'}, ink:{DEFAULT:'#2E2A26',dim:'#7A7269'}, accent:{DEFAULT:'#FF7E5F',hover:'#FF9579',glow:'rgba(255,126,95,0.25)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], display:['Quicksand','sans-serif'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Quicksand:wght@500;600;700&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;background:#FFF8F2;color:#2E2A26;}
  .font-display{font-family:'Quicksand',sans-serif;}
  ::selection{background:rgba(255,126,95,0.25);}
  .hero-title{font-size:clamp(2.4rem,5.5vw,4.6rem);line-height:1.05;}
  .reveal{opacity:0;transform:translateY(26px);transition:all .65s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .tier-card.featured{box-shadow:0 20px 45px rgba(255,126,95,0.18);}
  .faq-content{max-height:0;overflow:hidden;transition:max-height .3s cubic-bezier(.16,1,.3,1);}
  .faq-item.open .faq-content{max-height:160px;}
  .faq-item.open .faq-chevron{transform:rotate(180deg);}
  .faq-chevron{transition:transform .3s ease;}
  input:focus,select:focus,button:focus-visible{outline:2px solid #FF7E5F;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500 bg-canvas/80 backdrop-blur-sm">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <a href="#" class="font-display text-xl font-bold flex items-center gap-2">🐾 Waggle &amp; Co.</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#services" class="text-sm text-ink-dim hover:text-ink font-medium">Services</a>
        <a href="#booking" class="text-sm text-ink-dim hover:text-ink font-medium">Book Now</a>
        <a href="#faq" class="text-sm text-ink-dim hover:text-ink font-medium">FAQ</a>
      </nav>
      <a href="#booking" class="bg-accent hover:bg-accent-hover text-white font-bold text-sm px-5 py-2.5 rounded-full transition-colors">Book a Visit</a>
    </div>
  </div>
</header>

<section class="relative min-h-[88vh] flex items-center pt-24 overflow-hidden">
  <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse at 80% 20%, rgba(255,126,95,0.1) 0%, transparent 55%);"></div>
  <div class="max-w-7xl mx-auto px-6 lg:px-8 relative z-10 grid lg:grid-cols-2 gap-16 items-center">
    <div class="space-y-7">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-accent/10">
        <span class="text-xs font-bold text-accent uppercase tracking-wide">🐶 5-Star Rated on Google</span>
      </div>
      <h1 class="hero-title font-display font-bold">
        Your dog's <span class="text-accent">second</span> favorite place.
      </h1>
      <p class="text-lg text-ink-dim max-w-md leading-relaxed">
        Grooming, daycare, and overnight boarding from a team that actually remembers
        your pet's name — and their favorite treat.
      </p>
      <div class="flex flex-col sm:flex-row gap-4">
        <a href="#booking" class="bg-accent hover:bg-accent-hover text-white font-bold px-8 py-4 rounded-xl transition-all hover:-translate-y-0.5">Book a Visit</a>
        <a href="#services" class="border border-ink/15 hover:border-ink/30 font-semibold px-8 py-4 rounded-xl transition-all hover:bg-white">See Services</a>
      </div>
    </div>
    <div class="relative hidden lg:flex items-center justify-center">
      <div class="w-full max-w-md aspect-square rounded-3xl bg-white border border-ink/5 shadow-xl flex items-center justify-center text-8xl">🐕</div>
    </div>
  </div>
</section>

<section id="services" class="py-24 lg:py-32 bg-white border-t border-ink/5">
  <div class="max-w-7xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs font-bold uppercase tracking-[0.2em] mb-3">Our Services</p>
      <h2 class="font-display text-3xl lg:text-4xl font-bold">Pick what your pet needs</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="tier-card reveal bg-canvas rounded-2xl p-8 border border-ink/5">
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2 font-semibold">Grooming</p>
        <p class="font-display text-4xl font-bold mb-4">$45+</p>
        <ul class="space-y-2 text-sm text-ink-dim mb-6"><li>Bath &amp; brush-out</li><li>Nail trim &amp; ear cleaning</li><li>Breed-specific cut</li></ul>
        <a href="#booking" class="block text-center border border-ink/15 hover:border-accent hover:text-accent font-bold py-3 rounded-xl transition-all">Book Grooming</a>
      </div>
      <div class="tier-card featured reveal bg-canvas rounded-2xl p-8 border-2 border-accent relative">
        <span class="absolute -top-3 left-8 bg-accent text-white text-xs font-bold px-3 py-1 rounded-full">Most Booked</span>
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2 font-semibold">Daycare</p>
        <p class="font-display text-4xl font-bold mb-4">$38<span class="text-base text-ink-dim">/day</span></p>
        <ul class="space-y-2 text-sm text-ink-dim mb-6"><li>Supervised play groups</li><li>Indoor &amp; outdoor space</li><li>Webcam access</li></ul>
        <a href="#booking" class="block text-center bg-accent hover:bg-accent-hover text-white font-bold py-3 rounded-xl transition-all">Book Daycare</a>
      </div>
      <div class="tier-card reveal bg-canvas rounded-2xl p-8 border border-ink/5">
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2 font-semibold">Boarding</p>
        <p class="font-display text-4xl font-bold mb-4">$65<span class="text-base text-ink-dim">/night</span></p>
        <ul class="space-y-2 text-sm text-ink-dim mb-6"><li>Private suite</li><li>Daily walks &amp; playtime</li><li>Nightly photo update</li></ul>
        <a href="#booking" class="block text-center border border-ink/15 hover:border-accent hover:text-accent font-bold py-3 rounded-xl transition-all">Book Boarding</a>
      </div>
    </div>
  </div>
</section>

<section id="booking" class="py-24 lg:py-32">
  <div class="max-w-2xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-12 reveal">
      <p class="text-accent text-xs font-bold uppercase tracking-[0.2em] mb-3">Request a Booking</p>
      <h2 class="font-display text-3xl lg:text-4xl font-bold">Let's get something on the calendar</h2>
    </div>
    <div class="reveal bg-white rounded-2xl p-8 border border-ink/5 shadow-lg">
      <div class="space-y-5 mb-6">
        <div>
          <label class="block text-sm font-semibold mb-2">Service</label>
          <select id="service-select" class="w-full border border-ink/15 rounded-xl px-4 py-3 text-sm">
            <option value="Grooming">Grooming — from $45</option>
            <option value="Daycare">Daycare — $38/day</option>
            <option value="Boarding">Boarding — $65/night</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-semibold mb-2">Preferred Date</label>
          <input type="date" id="date-input" class="w-full border border-ink/15 rounded-xl px-4 py-3 text-sm">
        </div>
        <div>
          <label class="block text-sm font-semibold mb-2">Pet's Name</label>
          <input type="text" id="pet-name" placeholder="e.g. Biscuit" class="w-full border border-ink/15 rounded-xl px-4 py-3 text-sm">
        </div>
      </div>
      <button id="booking-submit" class="w-full bg-accent hover:bg-accent-hover text-white font-bold py-4 rounded-xl transition-all">Request Booking</button>
      <div id="booking-confirmation" class="hidden mt-5 bg-accent/10 border border-accent/30 rounded-xl p-4 text-sm">
        <p class="font-semibold mb-1">Request received! 🎉</p>
        <p class="text-ink-dim" id="confirmation-text"></p>
      </div>
    </div>
  </div>
</section>

<section class="py-20 bg-white border-t border-ink/5">
  <div class="max-w-3xl mx-auto px-6 text-center reveal">
    <p class="text-2xl font-medium text-ink/85 leading-relaxed mb-6">"They send a photo update every single night my dog boards. It's the little things — I never worry when she's there."</p>
    <p class="text-sm text-ink-dim">Priya M. &amp; Biscuit (Golden Retriever)</p>
  </div>
</section>

<section id="faq" class="py-24 lg:py-32">
  <div class="max-w-2xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-12 reveal"><h2 class="font-display text-3xl font-bold">Common questions</h2></div>
    <div class="space-y-3">
      <div class="faq-item reveal bg-white border border-ink/5 rounded-xl">
        <button class="faq-trigger w-full flex items-center justify-between p-5 text-left font-semibold"><span>Do you require vaccination records?</span><span class="faq-chevron">▾</span></button>
        <div class="faq-content px-5"><p class="text-sm text-ink-dim pb-5">Yes — current rabies, DHPP, and bordetella records are required before any stay.</p></div>
      </div>
      <div class="faq-item reveal bg-white border border-ink/5 rounded-xl">
        <button class="faq-trigger w-full flex items-center justify-between p-5 text-left font-semibold"><span>Can I tour the facility first?</span><span class="faq-chevron">▾</span></button>
        <div class="faq-content px-5"><p class="text-sm text-ink-dim pb-5">Absolutely — drop by anytime during business hours, no appointment needed.</p></div>
      </div>
      <div class="faq-item reveal bg-white border border-ink/5 rounded-xl">
        <button class="faq-trigger w-full flex items-center justify-between p-5 text-left font-semibold"><span>What breeds do you groom?</span><span class="faq-chevron">▾</span></button>
        <div class="faq-content px-5"><p class="text-sm text-ink-dim pb-5">All breeds and sizes, including breed-specific cuts for show standards.</p></div>
      </div>
    </div>
  </div>
</section>

<footer class="border-t border-ink/5 py-12 bg-white">
  <div class="max-w-7xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-ink-dim">
    <p>© 2026 Waggle &amp; Co.</p>
    <div class="flex gap-6"><a href="#" class="hover:text-ink">Vaccination Policy</a><a href="#" class="hover:text-ink">Contact</a></div>
  </div>
</footer>

<script>
document.getElementById('booking-submit').addEventListener('click', ()=>{
  const service = document.getElementById('service-select').value;
  const date = document.getElementById('date-input').value;
  const pet = document.getElementById('pet-name').value || 'your pet';
  const confirmation = document.getElementById('booking-confirmation');
  const text = document.getElementById('confirmation-text');
  if (!date) {
    text.textContent = 'Please select a preferred date before submitting.';
    confirmation.classList.remove('hidden');
    confirmation.classList.replace('bg-accent/10','bg-red-50');
    return;
  }
  confirmation.classList.replace('bg-red-50','bg-accent/10');
  const formattedDate = new Date(date + 'T00:00:00').toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric' });
  text.textContent = `We'll text you to confirm ${service} for ${pet} on ${formattedDate}.`;
  confirmation.classList.remove('hidden');
});

document.querySelectorAll('.faq-trigger').forEach(trigger=>{
  trigger.addEventListener('click', ()=>trigger.closest('.faq-item').classList.toggle('open'));
});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));
</script>
</body>
</html>
```
