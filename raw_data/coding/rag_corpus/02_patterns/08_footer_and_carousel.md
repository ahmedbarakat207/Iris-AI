# Pattern — Footer & Testimonial Carousel

Tags: pattern, footer, testimonials, carousel, social-links, sitemap

## Footer anatomy

A complete footer (not just a copyright line) usually has: a brand recap column, 2-3
link columns (sitemap-style), a newsletter or contact column, a bottom bar with
copyright + legal links + social icons.

```html
<footer class="footer">
  <div class="container footer-grid">
    <div class="footer-brand">
      <div class="logo"><div class="logo-icon">B</div><span>Brand</span></div>
      <p class="footer-tagline">One sentence restating the brand's core promise.</p>
      <div class="social-links">
        <a href="#" aria-label="Instagram" class="social-icon"><!-- svg --></a>
        <a href="#" aria-label="Twitter" class="social-icon"><!-- svg --></a>
      </div>
    </div>
    <div class="footer-col">
      <h4>Shop</h4>
      <a href="#">New Arrivals</a>
      <a href="#">Best Sellers</a>
      <a href="#">Sale</a>
    </div>
    <div class="footer-col">
      <h4>Company</h4>
      <a href="#">About</a>
      <a href="#">Careers</a>
      <a href="#">Press</a>
    </div>
    <div class="footer-col footer-newsletter">
      <h4>Stay Updated</h4>
      <p>Get early access to drops and members-only pricing.</p>
      <form class="newsletter-form"><!-- see 07_forms_and_validation.md --></form>
    </div>
  </div>
  <div class="footer-bottom">
    <p>© 2026 Brand. All rights reserved.</p>
    <div class="footer-legal"><a href="#">Privacy</a><a href="#">Terms</a></div>
  </div>
</footer>
```

```css
.footer { background: var(--dark-gray); border-top: 1px solid var(--light-gray); padding: 5rem 0 0; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr; gap: 3rem; padding-bottom: 4rem; }
.footer-col h4 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1.25rem; color: var(--off-white); }
.footer-col a { display: block; color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.85rem; }
.footer-col a:hover { color: var(--accent); }
.social-icon { display: inline-flex; width: 38px; height: 38px; border-radius: 50%; background: var(--medium-gray); align-items: center; justify-content: center; margin-right: 0.6rem; }
.social-icon:hover { background: var(--accent); color: var(--black); }
.footer-bottom { border-top: 1px solid var(--light-gray); padding: 1.5rem 0; display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted); }
.footer-legal { display: flex; gap: 1.5rem; }
@media (max-width: 900px) { .footer-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 600px) { .footer-grid { grid-template-columns: 1fr; } .footer-bottom { flex-direction: column; gap: 1rem; text-align: center; } }
```

## Testimonial carousel (autoplay + manual dots + pause-on-hover)

```html
<div class="testimonial-carousel" id="testimonial-carousel">
  <div class="testimonial-track" id="testimonial-track">
    <div class="testimonial-slide active">
      <p class="testimonial-quote">"Specific, real-sounding quote about the actual product experience, not generic praise."</p>
      <p class="testimonial-author">Person Name <span>— Role / Context</span></p>
    </div>
    <!-- more .testimonial-slide -->
  </div>
  <div class="testimonial-dots" id="testimonial-dots"></div>
</div>
```

```css
.testimonial-carousel { position: relative; max-width: 700px; margin: 0 auto; text-align: center; }
.testimonial-slide { display: none; animation: fadeIn 0.5s ease; }
.testimonial-slide.active { display: block; }
.testimonial-quote { font-size: 1.4rem; font-weight: 300; line-height: 1.6; font-style: italic; margin-bottom: 1.5rem; color: var(--off-white); }
.testimonial-author { font-size: 0.9rem; font-weight: 600; }
.testimonial-author span { color: var(--text-muted); font-weight: 400; }
.testimonial-dots { display: flex; justify-content: center; gap: 0.5rem; margin-top: 2rem; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--lighter-gray); border: none; transition: var(--transition); }
.dot.active { background: var(--accent); width: 24px; border-radius: 4px; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
```

```js
const slides = document.querySelectorAll('.testimonial-slide');
const dotsContainer = document.getElementById('testimonial-dots');
let currentSlide = 0;
let autoplayInterval;

slides.forEach((_, i) => {
  const dot = document.createElement('button');
  dot.className = 'dot' + (i === 0 ? ' active' : '');
  dot.setAttribute('aria-label', `Go to testimonial ${i + 1}`);
  dot.addEventListener('click', () => goToSlide(i));
  dotsContainer.appendChild(dot);
});

function goToSlide(index) {
  slides[currentSlide].classList.remove('active');
  dotsContainer.children[currentSlide].classList.remove('active');
  currentSlide = index;
  slides[currentSlide].classList.add('active');
  dotsContainer.children[currentSlide].classList.add('active');
}

function nextSlide() { goToSlide((currentSlide + 1) % slides.length); }

function startAutoplay() { autoplayInterval = setInterval(nextSlide, 5000); }
function stopAutoplay() { clearInterval(autoplayInterval); }

startAutoplay();
const carousel = document.getElementById('testimonial-carousel');
carousel.addEventListener('mouseenter', stopAutoplay);
carousel.addEventListener('mouseleave', startAutoplay);
```

## Rules

- Footer link columns should reflect the actual site's sections/sitemap, not generic
  filler links — if there's no "Careers" page concept for this brief, don't include
  the link.
- Carousel autoplay must pause on hover/focus so a reader can actually finish reading
  a longer quote, and must offer manual dot navigation as an escape from the timer.
- Testimonial copy should sound like a specific person describing a specific moment,
  not a generic "Great product, highly recommend!" line.
- The footer's newsletter or CTA column should not duplicate the header's signup if
  the site already has a prominent one elsewhere — pick one primary capture point.
