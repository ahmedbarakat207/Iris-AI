# الرمز التعريفي للمحادثة: Convo_173

User:
How can I dynamically change multiple CSS custom properties across different elements at once using vanilla JavaScript without affecting the page's performance?

---

Bot
You can efficiently update multiple CSS custom properties across different elements using a single JavaScript approach that maintains performance:

**Method 1: Direct DOM manipulation with a loop**
```javascript
// Define your custom properties and values
const customProperties = {
  '--primary-color': '#ff6b6b',
  '--secondary-color': '#4ecdc4',
  '--font-size': '1.2rem'
};

// Apply to multiple elements
const elements = document.querySelectorAll('.themeable');
Object.entries(customProperties).forEach(([property, value]) => {
  elements.forEach(el => el.style.setProperty(property, value));
});
```

**Method 2: Using a CSS variable on a root element**
```javascript
// Set all properties at once on :root
document.documentElement.style.setProperty('--primary-color', '#ff6b6b');
document.documentElement.style.setProperty('--secondary-color', '#4ecdc4');
// etc.
```

**Method 3: Batch updates with documentFragment**
```javascript
const fragment = document.createDocumentFragment();
const elements = document.querySelectorAll('.themeable');

elements.forEach(el => {
  Object.entries(customProperties).forEach(([prop, value]) => {
    el.style.setProperty(prop, value);
  });
});
```

To avoid performance issues:
- Use `style.setProperty()` instead of modifying `cssText`
- Batch updates when possible
- Avoid frequent DOM queries in loops
- Consider using CSS classes with pre-defined variables for complex themes

The key is minimizing DOM interactions and applying changes efficiently across your elements.

---

User:
Wait, so if I'm using Method 2 on the root, does that automatically update all elements that use those variables, or do I still need to touch each one?

---

Bot
Yes, that's exactly the beauty of CSS custom properties (also known as CSS variables)—they cascade just like other CSS properties. When you set a variable on the root element (using `document.documentElement.style.setProperty()` as in Method 2), it automatically updates all descendant elements that reference that variable via `var()`. You don't need to manually "touch" each individual element; the browser handles the cascading for you, which is efficient and performant.

### How It Works Step-by-Step
1. **Define the Variable on :root**: This sets the variable at the highest level in the document tree. For example:
   ```javascript
   document.documentElement.style.setProperty('--primary-color', '#ff6b6b');
   ```

2. **Reference It in CSS**: In your stylesheet, any element can use this variable. For instance:
   ```css
   .button {
     background-color: var(--primary-color);
   }
   h1 {
     color: var(--primary-color);
   }
   ```
   - When the JavaScript updates `--primary-color` on :root, the new value cascades down to all elements using `var(--primary-color)`, updating them instantly without DOM manipulation on each one.

3. **No Manual Updates Needed**: Unlike Method 1 (which loops over elements and sets styles directly), this doesn't require querying or iterating through elements. It's a single setProperty call.

### Potential Confusion Points
- **Scope and Overrides**: If an element has its own local definition of the variable (e.g., via inline styles or a more specific selector), that will take precedence due to CSS specificity. The root value won't override it unless you remove the local one.
- **Fallbacks**: You can define fallbacks in `var()` like `var(--primary-color, #default-value)` to handle cases where the variable isn't set.
- **Inheritance**: Variables only inherit down the tree; they don't bubble up. So, setting on :root affects everything below it.

To verify: Does this clarify how the cascading works for you? Try it out—set a variable on :root in your browser's console and watch how it propagates to elements referencing it.

As a next step, experiment by creating a simple HTML page with multiple elements using `var(--color)`, then use JavaScript to change it on :root and observe the updates. If you run into issues with overrides, share your CSS for more targeted advice!

---

