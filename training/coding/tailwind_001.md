# Tailwind CSS Training: Responsive Card Grid

User:
How do I build a responsive 3-column card grid in Tailwind CSS that collapses to 1 column on mobile and 2 columns on tablet?

---

Bot:
Use Tailwind's responsive grid utilities with breakpoint prefixes:

```html
<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 p-6">
  <!-- Card -->
  <div class="bg-white rounded-2xl shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300">
    <img src="image.jpg" alt="Card image" class="w-full h-48 object-cover" />
    <div class="p-5">
      <h3 class="text-lg font-semibold text-gray-800 mb-2">Card Title</h3>
      <p class="text-sm text-gray-500 leading-relaxed">
        Some description text that explains what this card is about.
      </p>
      <button class="mt-4 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 active:scale-95 transition-all">
        Learn More
      </button>
    </div>
  </div>

  <!-- Repeat cards... -->
</div>
```

**Breakpoint logic:**
- `grid-cols-1` — default (mobile, < 640px)
- `sm:grid-cols-2` — tablet (≥ 640px)
- `lg:grid-cols-3` — desktop (≥ 1024px)

**Key classes used:**
- `gap-6` — 24px gap between cards
- `rounded-2xl` — large border radius
- `shadow-md hover:shadow-xl` — elevation on hover
- `transition-shadow duration-300` — smooth shadow animation
- `object-cover` — image fills container without distortion

For dark mode support, add the `dark:` variants:
```html
<div class="bg-white dark:bg-gray-800 rounded-2xl shadow-md ...">
  <h3 class="text-gray-800 dark:text-white ...">Card Title</h3>
  <p class="text-gray-500 dark:text-gray-400 ...">Description</p>
</div>
```
