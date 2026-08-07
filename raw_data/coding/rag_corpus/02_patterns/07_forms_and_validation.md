# Pattern — Forms & Validation

Tags: pattern, forms, validation, contact-form, newsletter, error-states

Contact forms, newsletter signups, and booking forms appear in nearly every site type.
Validation should be real (not just `required` attributes with no feedback) and error
messaging should speak in the product's voice.

## Markup with inline error slots

```html
<form id="contact-form" novalidate>
  <div class="form-group">
    <label for="name">Full name</label>
    <input type="text" id="name" name="name" required>
    <span class="form-error" id="name-error"></span>
  </div>
  <div class="form-group">
    <label for="email">Email address</label>
    <input type="email" id="email" name="email" required>
    <span class="form-error" id="email-error"></span>
  </div>
  <div class="form-group">
    <label for="message">Message</label>
    <textarea id="message" name="message" rows="4" required></textarea>
    <span class="form-error" id="message-error"></span>
  </div>
  <button type="submit" class="btn btn-primary">Send Message</button>
  <p class="form-status" id="form-status"></p>
</form>
```

```css
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--off-white); letter-spacing: 0.3px; }
.form-group input, .form-group textarea { width: 100%; background: var(--medium-gray); border: 1px solid var(--lighter-gray); color: var(--white); padding: 0.85rem 1rem; border-radius: var(--radius); font-size: 0.95rem; font-family: inherit; transition: var(--transition); }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(74,124,89,0.15); }
.form-group input.invalid, .form-group textarea.invalid { border-color: var(--danger); }
.form-error { display: block; font-size: 0.8rem; color: var(--danger); margin-top: 0.4rem; min-height: 1.1em; }
.form-status { margin-top: 1rem; font-size: 0.9rem; }
.form-status.success { color: var(--success); }
.form-status.error { color: var(--danger); }
```

## Validation logic (real-time on blur, full check on submit)

```js
const form = document.getElementById('contact-form');

const validators = {
  name: (v) => v.trim().length >= 2 || 'Please enter your full name.',
  email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Enter a valid email address.',
  message: (v) => v.trim().length >= 10 || 'Tell us a little more — at least 10 characters.'
};

function validateField(fieldName) {
  const field = document.getElementById(fieldName);
  const errorEl = document.getElementById(`${fieldName}-error`);
  const result = validators[fieldName](field.value);
  if (result === true) {
    field.classList.remove('invalid');
    errorEl.textContent = '';
    return true;
  } else {
    field.classList.add('invalid');
    errorEl.textContent = result;
    return false;
  }
}

Object.keys(validators).forEach(fieldName => {
  const field = document.getElementById(fieldName);
  field.addEventListener('blur', () => validateField(fieldName));
  field.addEventListener('input', () => {
    if (field.classList.contains('invalid')) validateField(fieldName);
  });
});

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const allValid = Object.keys(validators).map(validateField).every(Boolean);
  const statusEl = document.getElementById('form-status');

  if (!allValid) {
    statusEl.textContent = 'Please fix the highlighted fields above.';
    statusEl.className = 'form-status error';
    return;
  }

  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Sending...';

  // Simulate submission (no backend in a single static file)
  setTimeout(() => {
    statusEl.textContent = "Thanks — we'll get back to you within one business day.";
    statusEl.className = 'form-status success';
    form.reset();
    submitBtn.disabled = false;
    submitBtn.textContent = 'Send Message';
  }, 900);
});
```

## Newsletter signup (compact inline variant)

```html
<form id="newsletter-form" class="newsletter-form">
  <input type="email" id="newsletter-email" placeholder="you@example.com" required aria-label="Email for newsletter">
  <button type="submit">Subscribe</button>
</form>
<p class="newsletter-note" id="newsletter-note">No spam. Unsubscribe anytime.</p>
```

```js
document.getElementById('newsletter-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const email = document.getElementById('newsletter-email').value;
  const note = document.getElementById('newsletter-note');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    note.textContent = 'That email doesn\'t look right — try again.';
    note.style.color = 'var(--danger)';
    return;
  }
  note.textContent = "You're on the list. Check your inbox to confirm.";
  note.style.color = 'var(--success)';
  e.target.reset();
});
```

## Rules

- Always call `e.preventDefault()` — there is no backend in a single static file, so
  a real form submission would navigate away/reload and lose the page.
- Validate on blur (so the user gets feedback as they go) and again on submit (so a
  user who never blurs a field, e.g. tabbing fast, still gets checked).
- Error copy is specific and instructive ("Enter a valid email address.") never just
  "Invalid input" or "Error".
- Disable and relabel the submit button during the simulated async action
  ("Sending...") so the click registers as having done something, then restore it.
- Success messaging confirms what happens next ("we'll get back to you within one
  business day") rather than a bare "Success!".
