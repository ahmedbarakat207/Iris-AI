# Pattern — Filters, Search & Empty States

Tags: pattern, filters, search, empty-state, inventory, dynamic-rendering

Inventory-style sites (dealerships, marketplaces, catalogs) need a filter bar that
narrows a data array and re-renders a grid, plus a designed empty state for when no
items match.

## Filter bar markup (vanilla-CSS — category chips + dropdowns)

```html
<div class="filter-bar">
  <div class="filter-chips" id="category-chips">
    <button class="chip active" data-filter="all">All</button>
    <button class="chip" data-filter="sedan">Sedan</button>
    <button class="chip" data-filter="suv">SUV</button>
    <button class="chip" data-filter="coupe">Coupe</button>
  </div>
  <div class="filter-selects">
    <select id="sort-select" class="filter-select">
      <option value="default">Sort: Featured</option>
      <option value="price-asc">Price: Low to High</option>
      <option value="price-desc">Price: High to Low</option>
    </select>
    <div class="search-box">
      <input type="text" id="search-input" placeholder="Search inventory..." aria-label="Search inventory">
    </div>
  </div>
</div>
```

```css
.filter-bar { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: space-between; align-items: center; margin-bottom: 3rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--light-gray); }
.filter-chips { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.chip { padding: 0.5rem 1.2rem; border-radius: 30px; border: 1px solid var(--lighter-gray); background: transparent; color: var(--text-muted); font-size: 0.85rem; font-weight: 500; transition: var(--transition); }
.chip:hover { border-color: var(--accent); color: var(--white); }
.chip.active { background: var(--accent); border-color: var(--accent); color: var(--black); font-weight: 600; }
.filter-select { background: var(--medium-gray); border: 1px solid var(--lighter-gray); color: var(--white); padding: 0.6rem 1rem; border-radius: var(--radius); font-size: 0.85rem; }
.search-box input { background: var(--medium-gray); border: 1px solid var(--lighter-gray); color: var(--white); padding: 0.6rem 1rem; border-radius: var(--radius); font-size: 0.85rem; width: 220px; }
.search-box input:focus { outline: none; border-color: var(--accent); }
```

## Filter + search + sort logic (combine all three reactively)

```js
let activeCategory = 'all';
let activeSort = 'default';
let searchQuery = '';

function getFilteredItems() {
  let result = items.filter(item => {
    const matchesCategory = activeCategory === 'all' || item.category === activeCategory;
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  if (activeSort === 'price-asc') result = result.sort((a, b) => a.price - b.price);
  if (activeSort === 'price-desc') result = result.sort((a, b) => b.price - a.price);

  return result;
}

function renderInventory() {
  const grid = document.getElementById('inventory-grid');
  const emptyState = document.getElementById('inventory-empty');
  const filtered = getFilteredItems();

  grid.innerHTML = '';

  if (filtered.length === 0) {
    emptyState.style.display = 'flex';
    grid.style.display = 'none';
    return;
  }

  emptyState.style.display = 'none';
  grid.style.display = 'grid';

  filtered.forEach((item, i) => {
    const card = buildCard(item); // returns a DOM node, see 03_card_grids.md
    card.style.animationDelay = `${i * 60}ms`;
    card.classList.add('card-enter');
    grid.appendChild(card);
  });
}

document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    activeCategory = chip.dataset.filter;
    renderInventory();
  });
});

document.getElementById('sort-select').addEventListener('change', (e) => {
  activeSort = e.target.value;
  renderInventory();
});

let searchDebounce;
document.getElementById('search-input').addEventListener('input', (e) => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    searchQuery = e.target.value;
    renderInventory();
  }, 200);
});
```

## Designed empty state (never leave a blank grid)

```html
<div class="inventory-empty" id="inventory-empty" style="display:none;">
  <div class="empty-icon">🔍</div>
  <h3>No matches found</h3>
  <p>Try a different category or clear your search to see the full inventory.</p>
  <button class="btn btn-outline" onclick="resetFilters()">Clear Filters</button>
</div>
```

```css
.inventory-empty { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 5rem 2rem; color: var(--text-muted); }
.empty-icon { font-size: 3rem; margin-bottom: 1.5rem; opacity: 0.6; }
.inventory-empty h3 { color: var(--white); font-size: 1.3rem; margin-bottom: 0.5rem; }
.inventory-empty p { max-width: 360px; margin-bottom: 1.5rem; line-height: 1.6; }
```

```js
function resetFilters() {
  activeCategory = 'all';
  searchQuery = '';
  document.getElementById('search-input').value = '';
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  document.querySelector('.chip[data-filter="all"]').classList.add('active');
  renderInventory();
}
```

## Card stagger-in animation referenced above

```css
.card-enter { animation: cardEnter 0.5s cubic-bezier(0.16,1,0.3,1) backwards; }
@keyframes cardEnter { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
```

## Rules

- Debounce search input (150-250ms) so re-rendering doesn't thrash on every
  keystroke.
- Filtering, sorting, and search must all compose — recompute from the full source
  array every time rather than mutating it, or repeated filtering will lose items
  permanently.
- The empty state needs a way back (a "Clear Filters" action), not just an
  apology message.
- Active filter chip state must be visually unambiguous (filled background, not just
  a thin border change) since it's the only indicator of current grid contents.
