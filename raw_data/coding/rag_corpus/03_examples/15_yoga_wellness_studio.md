# Example — Yoga & Wellness Studio (Tailwind Architecture, Light/Airy)

Tags: example, full-site, yoga, wellness, studio, fitness, tailwind, light-theme, sand, dusty-rose, airy, class-schedule, calm

Niche: boutique yoga and wellness studio.
Architecture: Tailwind CDN utility classes, light/airy mode — demonstrates that
Tailwind isn't only for dark, dense, glassy designs; restraint and whitespace work
just as well as a utility-class strategy.
Palette: warm sand canvas (#FAF6F1), dusty rose accent (#C98B82), generous whitespace,
thin weights, slow gentle motion only.
Signature element: a weekly class-schedule grid (days × time slots) that highlights
the current day and lets you filter by class type.
Sections: header, hero, class-type filter + weekly schedule grid, instructor intro,
membership, footer.

```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Still Water Yoga | Studio &amp; Wellness Classes</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = { theme:{extend:{
  colors:{ canvas:{DEFAULT:'#FAF6F1',light:'#FFFFFF',card:'#FFFFFF'}, ink:{DEFAULT:'#332B28',dim:'#8C7F77'}, accent:{DEFAULT:'#C98B82',hover:'#D6A097',glow:'rgba(201,139,130,0.2)'} },
  fontFamily:{ sans:['Inter','system-ui','sans-serif'], display:['Cormorant Garamond','serif'] }
}}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Cormorant+Garamond:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  body{font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased;background:#FAF6F1;color:#332B28;font-weight:300;}
  .font-display{font-family:'Cormorant Garamond',serif;}
  ::selection{background:rgba(201,139,130,0.2);}
  .hero-title{font-size:clamp(2.4rem,5.5vw,4.4rem);line-height:1.1;letter-spacing:-0.01em;}
  .reveal{opacity:0;transform:translateY(20px);transition:all .8s cubic-bezier(.16,1,.3,1);}
  .reveal.visible{opacity:1;transform:translateY(0);}
  .schedule-cell.hidden-by-filter{opacity:0.15;}
  input:focus,select:focus,button:focus-visible{outline:2px solid #C98B82;outline-offset:2px;}
  @media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important;}}
</style>
</head>
<body class="min-h-screen">

<header id="site-header" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500 bg-canvas/85 backdrop-blur-sm">
  <div class="max-w-6xl mx-auto px-6 lg:px-8">
    <div class="flex items-center justify-between h-20">
      <a href="#" class="font-display text-2xl">Still Water</a>
      <nav class="hidden lg:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
        <a href="#schedule" class="text-sm text-ink-dim hover:text-ink">Schedule</a>
        <a href="#instructors" class="text-sm text-ink-dim hover:text-ink">Instructors</a>
        <a href="#membership" class="text-sm text-ink-dim hover:text-ink">Membership</a>
      </nav>
      <a href="#membership" class="border border-accent text-accent hover:bg-accent hover:text-white text-sm px-5 py-2.5 rounded-full transition-colors">Try a Free Class</a>
    </div>
  </div>
</header>

<section class="relative min-h-[86vh] flex items-center pt-24">
  <div class="max-w-6xl mx-auto px-6 lg:px-8 grid lg:grid-cols-2 gap-16 items-center">
    <div class="space-y-7">
      <p class="text-accent text-xs uppercase tracking-[0.2em]">A Quiet Studio in the City</p>
      <h1 class="hero-title font-display">
        Slow down.<br>Breathe deeper.
      </h1>
      <p class="text-lg text-ink-dim max-w-md leading-relaxed">
        Twelve weekly classes across vinyasa, restorative, and sound bath — taught
        by instructors who studied for years before they ever taught a single class.
      </p>
      <div class="flex flex-col sm:flex-row gap-4">
        <a href="#schedule" class="bg-accent hover:bg-accent-hover text-white font-medium px-8 py-4 rounded-full transition-all">View Class Schedule</a>
        <a href="#membership" class="border border-ink/15 hover:border-ink/30 font-medium px-8 py-4 rounded-full transition-all">See Membership</a>
      </div>
    </div>
    <div class="relative hidden lg:flex items-center justify-center">
      <div class="w-full max-w-sm aspect-[3/4] rounded-3xl bg-gradient-to-br from-accent/10 to-canvas-light border border-ink/5 flex items-center justify-center text-7xl">🧘</div>
    </div>
  </div>
</section>

<section id="schedule" class="py-24 lg:py-32 bg-white border-t border-ink/5">
  <div class="max-w-6xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-12 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">This Week</p>
      <h2 class="font-display text-3xl lg:text-4xl">Class schedule</h2>
    </div>
    <div class="flex justify-center gap-3 mb-10 flex-wrap" id="class-filters">
      <button class="filter-chip active px-5 py-2 rounded-full border border-accent bg-accent text-white text-sm font-medium" data-type="all">All Classes</button>
      <button class="filter-chip px-5 py-2 rounded-full border border-ink/15 text-sm font-medium" data-type="Vinyasa">Vinyasa</button>
      <button class="filter-chip px-5 py-2 rounded-full border border-ink/15 text-sm font-medium" data-type="Restorative">Restorative</button>
      <button class="filter-chip px-5 py-2 rounded-full border border-ink/15 text-sm font-medium" data-type="Sound Bath">Sound Bath</button>
    </div>
    <div class="overflow-x-auto">
      <div id="schedule-grid" class="grid gap-2" style="grid-template-columns: 100px repeat(7, minmax(110px,1fr)); min-width:880px;"></div>
    </div>
  </div>
</section>

<section id="instructors" class="py-24 lg:py-32">
  <div class="max-w-5xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Meet the Team</p>
      <h2 class="font-display text-3xl lg:text-4xl">Our instructors</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-10 text-center">
      <div class="reveal"><div class="w-28 h-28 mx-auto rounded-full bg-accent/10 flex items-center justify-center text-3xl mb-4">🌿</div><h3 class="font-display text-xl mb-1">Anaya Patel</h3><p class="text-sm text-ink-dim">Vinyasa &amp; Restorative, 11 years teaching</p></div>
      <div class="reveal" style="transition-delay:.1s"><div class="w-28 h-28 mx-auto rounded-full bg-accent/10 flex items-center justify-center text-3xl mb-4">🌙</div><h3 class="font-display text-xl mb-1">Noah Bergström</h3><p class="text-sm text-ink-dim">Sound Bath &amp; Meditation, trained in Bali</p></div>
      <div class="reveal" style="transition-delay:.2s"><div class="w-28 h-28 mx-auto rounded-full bg-accent/10 flex items-center justify-center text-3xl mb-4">🌸</div><h3 class="font-display text-xl mb-1">Wren Okafor</h3><p class="text-sm text-ink-dim">Restorative &amp; Prenatal Yoga</p></div>
    </div>
  </div>
</section>

<section id="membership" class="py-24 lg:py-32 bg-white border-t border-ink/5">
  <div class="max-w-4xl mx-auto px-6 lg:px-8">
    <div class="text-center mb-16 reveal">
      <p class="text-accent text-xs uppercase tracking-[0.2em] mb-3">Membership</p>
      <h2 class="font-display text-3xl lg:text-4xl">Find your rhythm</h2>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <div class="reveal text-center border border-ink/10 rounded-2xl p-8">
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2">Drop-In</p>
        <p class="font-display text-3xl mb-4">$28</p>
        <p class="text-sm text-ink-dim">Single class, any style</p>
      </div>
      <div class="reveal text-center border-2 border-accent rounded-2xl p-8 relative">
        <span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-accent text-white text-xs px-3 py-1 rounded-full">Most Popular</span>
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2">Unlimited</p>
        <p class="font-display text-3xl mb-4">$149<span class="text-base text-ink-dim">/mo</span></p>
        <p class="text-sm text-ink-dim">Every class, every week</p>
      </div>
      <div class="reveal text-center border border-ink/10 rounded-2xl p-8">
        <p class="text-sm text-ink-dim uppercase tracking-wide mb-2">10-Class Pack</p>
        <p class="font-display text-3xl mb-4">$220</p>
        <p class="text-sm text-ink-dim">Never expires</p>
      </div>
    </div>
  </div>
</section>

<footer class="py-12 border-t border-ink/5">
  <div class="max-w-6xl mx-auto px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-ink-dim">
    <p>© 2026 Still Water Yoga</p>
    <div class="flex gap-6"><a href="#" class="hover:text-ink">Studio Etiquette</a><a href="#" class="hover:text-ink">Contact</a></div>
  </div>
</footer>

<script>
const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
const todayIndex = (new Date().getDay() + 6) % 7; // Mon=0
const schedule = {
  '7:00 AM':  ['Vinyasa','','Restorative','','Vinyasa','',''],
  '9:00 AM':  ['','Sound Bath','','Sound Bath','','Vinyasa',''],
  '12:00 PM': ['Restorative','Vinyasa','','Vinyasa','Restorative','',''],
  '5:30 PM':  ['Vinyasa','','Vinyasa','','','','Restorative'],
  '7:00 PM':  ['','Restorative','Sound Bath','','Vinyasa','',''],
};
let activeType = 'all';

function renderSchedule(){
  const grid = document.getElementById('schedule-grid');
  grid.innerHTML = '';
  grid.innerHTML += `<div></div>`;
  days.forEach((d,i)=>{
    grid.innerHTML += `<div class="text-center text-xs font-semibold uppercase tracking-wide py-2 ${i===todayIndex ? 'text-accent' : 'text-ink-dim'}">${d}</div>`;
  });
  Object.entries(schedule).forEach(([time, classes])=>{
    grid.innerHTML += `<div class="text-xs text-ink-dim flex items-center pr-2">${time}</div>`;
    classes.forEach((cls,i)=>{
      const isToday = i===todayIndex;
      const cell = document.createElement('div');
      cell.className = `schedule-cell rounded-lg p-2 text-center text-xs min-h-[44px] flex items-center justify-center ${cls ? 'bg-accent/10 text-accent font-medium' : 'bg-ink/[0.02] text-ink-dim/30'} ${isToday ? 'ring-1 ring-accent/40' : ''}`;
      cell.textContent = cls || '—';
      if (cls) cell.dataset.type = cls;
      grid.appendChild(cell);
    });
  });
  applyFilter();
}
function applyFilter(){
  document.querySelectorAll('.schedule-cell').forEach(cell=>{
    if (!cell.dataset.type) return;
    cell.classList.toggle('hidden-by-filter', activeType !== 'all' && cell.dataset.type !== activeType);
  });
}
document.querySelectorAll('.filter-chip').forEach(chip=>{
  chip.addEventListener('click', ()=>{
    document.querySelectorAll('.filter-chip').forEach(c=>{ c.classList.remove('active','bg-accent','text-white','border-accent'); c.classList.add('border-ink/15'); });
    chip.classList.add('active','bg-accent','text-white','border-accent');
    chip.classList.remove('border-ink/15');
    activeType = chip.dataset.type;
    applyFilter();
  });
});

const header = document.getElementById('site-header');
window.addEventListener('scroll', ()=>{
  header.style.boxShadow = window.scrollY > 40 ? '0 2px 20px rgba(51,43,40,0.06)' : 'none';
}, {passive:true});

const revealObserver = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{ if(entry.isIntersecting){ entry.target.classList.add('visible'); revealObserver.unobserve(entry.target); } });
}, {threshold:0.1, rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));

renderSchedule();
</script>
</body>
</html>
```
