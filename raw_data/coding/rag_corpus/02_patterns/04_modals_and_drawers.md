# Pattern — Modals & Slide-Out Drawers

Tags: pattern, modal, drawer, cart-drawer, dialog, overlay, escape-key

Two related but distinct UI surfaces appear constantly: a **centered modal** (item
detail, confirmation) and a **slide-out drawer** (cart, filters panel, mobile nav).
Both need an overlay, an open/close mechanism, and keyboard/click-outside dismissal.

## Centered modal (vanilla-CSS — vehicle/product detail example)

```html
<div class="modal" id="detail-modal">
  <div class="modal-overlay" id="modal-overlay"></div>
  <div class="modal-content">
    <button class="modal-close" id="modal-close" aria-label="Close">&times;</button>
    <h3 id="modal-title"></h3>
    <p id="modal-price" class="modal-price"></p>
    <div class="modal-specs">
      <div><span>Year</span><strong id="modal-year"></strong></div>
      <div><span>Mileage</span><strong id="modal-mileage"></strong></div>
      <div><span>Transmission</span><strong id="modal-trans"></strong></div>
    </div>
    <p id="modal-desc" class="modal-desc"></p>
  </div>
</div>
```

```css
.modal { position: fixed; inset: 0; z-index: 2000; display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: opacity 0.3s ease; }
.modal.active { opacity: 1; pointer-events: auto; }
.modal-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.75); backdrop-filter: blur(4px); }
.modal-content { position: relative; background: var(--dark-gray); border-radius: var(--radius-lg); padding: 2.5rem; max-width: 540px; width: 90%; max-height: 85vh; overflow-y: auto; transform: translateY(20px) scale(0.98); transition: transform 0.3s cubic-bezier(0.16,1,0.3,1); box-shadow: var(--shadow-lg); }
.modal.active .modal-content { transform: translateY(0) scale(1); }
.modal-close { position: absolute; top: 1.25rem; right: 1.25rem; background: var(--medium-gray); border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 1.5rem; line-height: 1; color: var(--white); }
.modal-close:hover { background: var(--accent); color: var(--black); }
```

```js
const modal = document.getElementById('detail-modal');
const modalOverlay = document.getElementById('modal-overlay');
const modalClose = document.getElementById('modal-close');

function openModal(item) {
  document.getElementById('modal-title').textContent = item.name;
  document.getElementById('modal-price').textContent = formatPrice(item.price);
  // ...populate remaining fields...
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}
function closeModal() {
  modal.classList.remove('active');
  document.body.style.overflow = '';
}
modalClose.addEventListener('click', closeModal);
modalOverlay.addEventListener('click', closeModal);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && modal.classList.contains('active')) closeModal();
});
```

## Slide-out drawer (utility-class — cart drawer example)

```html
<aside id="cart-drawer" class="fixed top-0 right-0 h-full w-full sm:w-[420px] bg-canvas-light z-[90] translate-x-full transition-transform duration-300 flex flex-col border-l border-white/5">
  <div class="flex items-center justify-between p-6 border-b border-white/5">
    <h3 class="font-bold text-lg">Your Cart</h3>
    <button id="cart-close-btn" class="p-2 text-white/50 hover:text-white" aria-label="Close cart">&times;</button>
  </div>
  <div id="cart-items" class="flex-1 overflow-y-auto p-6 space-y-4">
    <div id="cart-empty-state" class="flex flex-col items-center justify-center h-full text-center">
      <p class="text-sm font-medium text-white/50 mb-1">Your cart is empty</p>
      <p class="text-xs text-white/25">Browse our collection and add some items</p>
    </div>
  </div>
  <div id="cart-footer" class="border-t border-white/5 p-6 space-y-4 hidden">
    <div class="flex items-center justify-between">
      <span class="font-semibold">Total</span>
      <span id="cart-total" class="text-xl font-bold text-accent">$0.00</span>
    </div>
    <button class="btn-primary w-full bg-accent hover:bg-accent-hover text-white font-semibold py-4 rounded-xl">Checkout</button>
  </div>
</aside>
<div id="cart-backdrop" class="fixed inset-0 bg-black/60 z-[85] opacity-0 pointer-events-none transition-opacity duration-300"></div>
```

```js
function openCart() {
  document.getElementById('cart-drawer').classList.remove('translate-x-full');
  const backdrop = document.getElementById('cart-backdrop');
  backdrop.classList.remove('opacity-0', 'pointer-events-none');
  document.body.style.overflow = 'hidden';
}
function closeCart() {
  document.getElementById('cart-drawer').classList.add('translate-x-full');
  const backdrop = document.getElementById('cart-backdrop');
  backdrop.classList.add('opacity-0', 'pointer-events-none');
  document.body.style.overflow = '';
}
document.getElementById('cart-backdrop').addEventListener('click', closeCart);
document.getElementById('cart-close-btn').addEventListener('click', closeCart);
```

## Rules common to both surfaces

- Always provide three ways to dismiss: an explicit close button, clicking the
  backdrop/overlay, and the Escape key.
- Lock `document.body.style.overflow = 'hidden'` while open, restore it on close, so
  the page behind doesn't scroll.
- Animate both the overlay (opacity) and the content (transform: scale or
  translate) — animating only one of the two feels unfinished.
- Drawers slide from the edge they're conceptually attached to: cart from the right
  (matches a cart icon in the top-right), mobile filters often from the left or
  bottom (bottom sheet) on small screens.
- Always design and wire up the empty state (`cart-empty-state` above) — hide it via
  a footer/state class once there's content, don't just leave the container blank.
