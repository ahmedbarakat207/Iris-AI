# الرمز التعريفي للمحادثة: Convo_1059

User:
How do I create a responsive navigation bar using flexbox that collapses into a hamburger menu on mobile devices?

---

Bot
Create a navigation bar with flexbox by setting `display: flex` on your nav container and using `flex-direction: row` for desktop layout. For mobile, add a media query that switches to `flex-direction: column` and hides the menu items by default.

Use JavaScript or CSS to toggle a class like "active" on the menu when the hamburger icon is clicked. The hamburger menu should be a simple button with three lines that transform into an X when active.

Set your nav links to `display: none` initially, then show them when the mobile menu is open. Add `flex-wrap: wrap` to handle overflow and ensure proper spacing between items.

For the hamburger icon itself, create a container div with three horizontal bars using CSS borders or pseudo-elements. When active, rotate and position these bars to form an X shape.

Use consistent padding and margins across all screen sizes. Ensure your navigation links have appropriate touch targets on mobile devices (minimum 44px height).

Make sure to include proper ARIA attributes for accessibility and test the interaction thoroughly across different screen sizes.

---

User:
Wait, the JavaScript part sounds tricky. Can you show me a simple example of how to toggle that active class?

---

Bot
Absolutely, toggling the active class is straightforward with a bit of vanilla JavaScript. I'll walk you through a simple example step by step, assuming you have HTML elements for a hamburger button (like a `<button id="hamburger">`) and a navigation menu (like a `<nav id="nav-menu">` with a class of "nav-menu"). We'll toggle a class called "active" on the menu to show/hide it.

### Step 1: HTML Setup
Make sure your HTML includes the hamburger button and the nav menu. For example:

```html
<button id="hamburger">☰</button>
<nav id="nav-menu" class="nav-menu">
  <a href="#home">Home</a>
  <a href="#about">About</a>
  <a href="#contact">Contact</a>
</nav>
```

### Step 2: CSS for the Active State
In your CSS, hide the menu by default on mobile and show it when the "active" class is added:

```css
.nav-menu {
  display: none; /* Hidden on mobile */
}

.nav-menu.active {
  display: block; /* Or flex, depending on your layout */
}
```

### Step 3: JavaScript for Toggling
Add this JavaScript inside a `<script>` tag at the bottom of your HTML (or in a separate JS file). It listens for a click on the hamburger button and toggles the "active" class on the menu.

```javascript
document.getElementById('hamburger').addEventListener('click', function() {
  var menu = document.getElementById('nav-menu');
  menu.classList.toggle('active');
});
```

### Quick Breakdown
- `document.getElementById('hamburger')`: Grabs the hamburger button element.
- `.addEventListener('click', function() { ... })`: Runs the code inside when the button is clicked.
- `var menu = document.getElementById('nav-menu')`: Gets a reference to the nav menu.
- `menu.classList.toggle('active')`: Adds the "active" class if it's not there, or removes it if it is. This flips the menu's visibility.

This is basic and doesn't include animations or closing the menu when a link is clicked, but it's a solid starting point. If you want to enhance it (e.g., animating the hamburger icon), we can build on this.

Does this make sense, or would you like me to explain any part in more detail? Try adding this to a test HTML file and see how it works—let me know what happens!

---

