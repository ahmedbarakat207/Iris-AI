# Pattern — Cart State & Stateful JS Logic

Tags: pattern, cart, state-management, vanilla-js, localStorage-free, toast

Single-file sites have no framework and no backend, so all "app" state (cart
contents, selected filters, wishlist) lives in a plain JS object/array for the
session. Do not use `localStorage`/`sessionStorage` unless the brief explicitly asks
for persistence and explicitly accepts it not working in restricted preview contexts
— default to in-memory state so the file works everywhere it's opened.

## Core cart state shape

```js
let cart = []; // [{ id, name, price, image, qty, variant }]

function addToCart(productId, variant) {
  const product = products.find(p => p.id === productId);
  if (!product) return;
  const existing = cart.find(i => i.id === productId && i.variant === variant);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ id: product.id, name: product.name, price: product.price, variant, qty: 1 });
  }
  renderCart();
  updateCartBadge();
  showToast(`${product.name} added to cart`, 'success');
  bounceCartIcon();
}

function removeFromCart(productId, variant) {
  cart = cart.filter(i => !(i.id === productId && i.variant === variant));
  renderCart();
  updateCartBadge();
}

function updateQty(productId, variant, delta) {
  const item = cart.find(i => i.id === productId && i.variant === variant);
  if (!item) return;
  item.qty = Math.max(1, item.qty + delta);
  renderCart();
  updateCartBadge();
}

function cartTotal() {
  return cart.reduce((sum, i) => sum + i.price * i.qty, 0);
}

function cartCount() {
  return cart.reduce((sum, i) => sum + i.qty, 0);
}
```

## Rendering the cart (toggle empty vs. populated state)

```js
function renderCart() {
  const container = document.getElementById('cart-items');
  const footer = document.getElementById('cart-footer');
  const emptyState = document.getElementById('cart-empty-state');

  if (cart.length === 0) {
    emptyState.style.display = 'flex';
    footer.classList.add('hidden');
    // remove any previously rendered item rows but keep the empty-state node
    container.querySelectorAll('.cart-row').forEach(el => el.remove());
    return;
  }

  emptyState.style.display = 'none';
  footer.classList.remove('hidden');
  container.querySelectorAll('.cart-row').forEach(el => el.remove());

  cart.forEach(item => {
    const row = document.createElement('div');
    row.className = 'cart-row flex gap-4 pb-4 border-b border-white/5';
    row.innerHTML = `
      <div class="flex-1">
        <p class="font-medium text-sm">${escapeHtml(item.name)}</p>
        <p class="text-xs text-white/40">${escapeHtml(item.variant || '')}</p>
        <div class="flex items-center gap-3 mt-2">
          <button class="qty-btn" data-id="${item.id}" data-variant="${item.variant}" data-delta="-1">−</button>
          <span class="text-sm w-4 text-center">${item.qty}</span>
          <button class="qty-btn" data-id="${item.id}" data-variant="${item.variant}" data-delta="1">+</button>
        </div>
      </div>
      <p class="font-semibold text-sm">$${(item.price * item.qty).toFixed(2)}</p>
    `;
    container.appendChild(row);
  });

  document.getElementById('cart-total').textContent = `$${cartTotal().toFixed(2)}`;

  container.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', () => updateQty(btn.dataset.id, btn.dataset.variant, parseInt(btn.dataset.delta)));
  });
}

function updateCartBadge() {
  const badge = document.getElementById('cart-badge');
  const count = cartCount();
  badge.textContent = count;
  badge.classList.toggle('hidden', count === 0);
  // retrigger pop animation
  badge.style.animation = 'none';
  badge.offsetHeight; // force reflow
  badge.style.animation = 'badgePop 0.3s cubic-bezier(0.34,1.56,0.64,1)';
}
```

## Toast notifications (stackable, auto-dismiss)

```html
<div id="toast-container" class="fixed top-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none"></div>
```

```css
.toast { background: #1A1714; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px 18px; display: flex; align-items: center; gap: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); transform: translateX(120%); transition: transform 0.35s cubic-bezier(0.16,1,0.3,1); pointer-events: auto; min-width: 240px; }
.toast.show { transform: translateX(0); }
.toast.success { border-left: 3px solid #4ADE80; }
.toast.error { border-left: 3px solid #F87171; }
```

```js
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 350);
  }, 2600);
}
```

## Small bounce on the cart icon when an item is added

```js
function bounceCartIcon() {
  const icon = document.getElementById('cart-icon-btn');
  icon.style.animation = 'none';
  icon.offsetHeight;
  icon.style.animation = 'cartBounce 0.4s cubic-bezier(0.34,1.56,0.64,1)';
}
```

```css
@keyframes cartBounce { 0%,100% { transform: scale(1); } 50% { transform: scale(1.2) rotate(-8deg); } }
```

## Always escape user-influenced or dynamic text before inserting via innerHTML

Even though most data in these single-file demos is hardcoded, build the habit of
escaping anything that could plausibly come from user input (search queries, form
field echoes) before interpolating into `innerHTML`:

```js
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
```

## Rules

- Every state mutation (`addToCart`, `removeFromCart`, `updateQty`) must call both the
  relevant render function AND the badge/total updater — don't let the badge drift
  out of sync with the underlying array.
- Always re-query and re-bind event listeners on dynamically rendered rows (as shown
  with `.qty-btn` above), since elements created via `innerHTML`/`createElement`
  after page load have no listeners until explicitly bound.
- Never block the UI with `alert()`/`confirm()` for cart feedback — use the toast
  pattern instead so the experience stays seamless.
