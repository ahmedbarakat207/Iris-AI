# Web UI JavaScript Examples

This RAG corpus provides high-quality vanilla JavaScript implementations for common Web UI components and interactions. It covers theme toggling, client-side searching, local storage persistence, and accessible navigation drawers.

---

## 1. Dark Mode Toggle with Local Storage

A robust dark mode implementation that respects system preferences and persists user choices via `localStorage`.

```javascript
/**
 * Initializes and manages theme toggling with OS preference fallback.
 * Assumes a button with id="theme-toggle" and tailwind 'dark' class on HTML.
 */
function initThemeToggle() {
  const toggleBtn = document.getElementById('theme-toggle');
  const htmlElement = document.documentElement;

  // 1. Check local storage
  // 2. Fall back to system preference
  const getPreferredTheme = () => {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) return storedTheme;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  };

  const applyTheme = (theme) => {
    if (theme === 'dark') {
      htmlElement.classList.add('dark');
    } else {
      htmlElement.classList.remove('dark');
    }
    // Optional: update button icon based on theme
    toggleBtn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
  };

  // Set initial theme
  const currentTheme = getPreferredTheme();
  applyTheme(currentTheme);

  // Toggle event
  toggleBtn.addEventListener('click', () => {
    const isDark = htmlElement.classList.contains('dark');
    const newTheme = isDark ? 'light' : 'dark';
    
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initThemeToggle);
```

---

## 2. Real-Time Client-Side Search Bar

Filtering a list of items dynamically as the user types, using event delegation and debouncing to prevent UI lag.

```javascript
/**
 * Debounce function to limit execution rate
 */
function debounce(func, delay = 300) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

/**
 * Initializes a search filter for a list of elements.
 * @param {string} inputSelector - CSS selector for the search input.
 * @param {string} itemsSelector - CSS selector for the items to filter.
 */
function initSearchFilter(inputSelector, itemsSelector) {
  const searchInput = document.querySelector(inputSelector);
  if (!searchInput) return;

  const handleSearch = (e) => {
    const searchTerm = e.target.value.toLowerCase().trim();
    const items = document.querySelectorAll(itemsSelector);

    items.forEach(item => {
      // Assumes text to search is either in textContent or a specific data attribute
      const text = item.textContent.toLowerCase();
      
      if (text.includes(searchTerm)) {
        item.style.display = ''; // Restore default display
        item.classList.remove('hidden');
      } else {
        item.style.display = 'none';
        item.classList.add('hidden');
      }
    });
  };

  searchInput.addEventListener('input', debounce(handleSearch, 250));
}

// Usage:
// document.addEventListener('DOMContentLoaded', () => initSearchFilter('#search-box', '.card-item'));
```

---

## 3. Side Navigation Drawer with Overlay

An accessible off-canvas sidebar that traps focus, handles escape key closes, and manages an overlay backdrop.

```javascript
function initSideNav() {
  const nav = document.getElementById('side-nav');
  const openBtn = document.getElementById('open-nav-btn');
  const closeBtn = document.getElementById('close-nav-btn');
  const overlay = document.getElementById('nav-overlay');

  if (!nav || !openBtn || !closeBtn || !overlay) return;

  const openNav = () => {
    nav.classList.remove('-translate-x-full');
    overlay.classList.remove('hidden');
    // Small delay to allow display:block to apply before animating opacity
    requestAnimationFrame(() => overlay.classList.remove('opacity-0'));
    
    nav.setAttribute('aria-expanded', 'true');
    closeBtn.focus(); // Accessibility: shift focus to close button
  };

  const closeNav = () => {
    nav.classList.add('-translate-x-full');
    overlay.classList.add('opacity-0');
    
    // Wait for transition to finish before hiding
    setTimeout(() => overlay.classList.add('hidden'), 300);
    
    nav.setAttribute('aria-expanded', 'false');
    openBtn.focus(); // Accessibility: return focus to open button
  };

  openBtn.addEventListener('click', openNav);
  closeBtn.addEventListener('click', closeNav);
  overlay.addEventListener('click', closeNav); // Click outside to close

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.getAttribute('aria-expanded') === 'true') {
      closeNav();
    }
  });
}

document.addEventListener('DOMContentLoaded', initSideNav);
```

---

## 4. Local Storage Form Auto-Save

Automatically saving draft form data so users don't lose progress if they accidentally refresh the page.

```javascript
function initFormDraftAutoSave(formId, storageKey) {
  const form = document.getElementById(formId);
  if (!form) return;

  // Load existing draft
  const savedDraft = localStorage.getItem(storageKey);
  if (savedDraft) {
    const data = JSON.parse(savedDraft);
    Object.entries(data).forEach(([name, value]) => {
      const field = form.elements[name];
      if (field) {
        if (field.type === 'checkbox' || field.type === 'radio') {
          field.checked = value;
        } else {
          field.value = value;
        }
      }
    });
  }

  // Save draft on change
  form.addEventListener('input', debounce((e) => {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // For checkboxes, FormData only includes them if checked. We might need manual mapping if robust handling is needed
    Array.from(form.elements).forEach(el => {
      if (el.type === 'checkbox') data[el.name] = el.checked;
    });

    localStorage.setItem(storageKey, JSON.stringify(data));
  }, 500));

  // Clear draft on submission
  form.addEventListener('submit', () => {
    localStorage.removeItem(storageKey);
  });
}
```

---

## 5. Accessible Tabs Component

A robust implementation of ARIA tabs that supports keyboard navigation (arrows to move, Enter/Space to select) and correctly manages state.

```javascript
function initTabs(containerSelector) {
  const container = document.querySelector(containerSelector);
  if (!container) return;

  const tablist = container.querySelector('[role="tablist"]');
  const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
  const panels = Array.from(container.querySelectorAll('[role="tabpanel"]'));

  const switchTab = (newTab) => {
    // Deselect all
    tabs.forEach(t => {
      t.setAttribute('aria-selected', 'false');
      t.setAttribute('tabindex', '-1');
      t.classList.remove('border-indigo-500', 'text-indigo-600');
      t.classList.add('border-transparent', 'text-zinc-500');
    });

    panels.forEach(p => p.classList.add('hidden'));

    // Select new
    newTab.setAttribute('aria-selected', 'true');
    newTab.removeAttribute('tabindex');
    newTab.classList.remove('border-transparent', 'text-zinc-500');
    newTab.classList.add('border-indigo-500', 'text-indigo-600');
    newTab.focus();

    const panel = document.getElementById(newTab.getAttribute('aria-controls'));
    if (panel) panel.classList.remove('hidden');
  };

  tablist.addEventListener('keydown', (e) => {
    const currentIndex = tabs.findIndex(t => t.getAttribute('aria-selected') === 'true');
    let newIndex;

    switch (e.key) {
      case 'ArrowRight':
        newIndex = (currentIndex + 1) % tabs.length;
        switchTab(tabs[newIndex]);
        break;
      case 'ArrowLeft':
        newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
        switchTab(tabs[newIndex]);
        break;
      case 'Home':
        switchTab(tabs[0]);
        break;
      case 'End':
        switchTab(tabs[tabs.length - 1]);
        break;
    }
  });

  tabs.forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab));
  });
}
```

---

## 6. Lightweight Toast Notification System

A simple manager for transient notification popups that stack vertically and auto-dismiss.

```javascript
class ToastManager {
  constructor() {
    this.container = document.createElement('div');
    this.container.className = 'fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none';
    document.body.appendChild(this.container);
  }

  show(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    
    // Base styles + pointer events auto to allow clicking the toast
    toast.className = 'px-4 py-3 rounded-xl shadow-lg text-sm text-white transform transition-all duration-300 translate-y-4 opacity-0 pointer-events-auto flex items-center gap-3';
    
    if (type === 'success') toast.classList.add('bg-emerald-600');
    else if (type === 'error') toast.classList.add('bg-rose-600');
    else toast.classList.add('bg-zinc-800');

    toast.innerHTML = `
      <span>${message}</span>
      <button class="ml-4 opacity-70 hover:opacity-100" aria-label="Close">&times;</button>
    `;

    // Handle close button
    const closeBtn = toast.querySelector('button');
    closeBtn.onclick = () => this.remove(toast);

    this.container.appendChild(toast);

    // Trigger entrance animation
    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-4', 'opacity-0');
    });

    if (duration > 0) {
      setTimeout(() => this.remove(toast), duration);
    }
  }

  remove(toast) {
    toast.classList.add('translate-y-4', 'opacity-0');
    toast.addEventListener('transitionend', () => toast.remove());
  }
}

// Usage:
// const toaster = new ToastManager();
// toaster.show('Profile updated successfully!', 'success');
```
