# الرمز التعريفي للمحادثة: Convo_903

User:
How do I implement basic cookies for tracking user preferences on my freelance portfolio website?

---

Bot
To implement basic cookies for tracking user preferences on your freelance portfolio, you'll want to use JavaScript to set and read cookie values.

Here's a straightforward approach:

**Setting cookies:**
```javascript
function setCookie(name, value, days) {
    const expires = days ? `; expires=${new Date(Date.now() + days * 864e5).toUTCString()}` : '';
    document.cookie = `${name}=${value}${expires}; path=/`;
}

// Example: remember if user prefers dark mode
setCookie('darkMode', 'enabled', 30);
```

**Reading cookies:**
```javascript
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Check for saved preference on page load
const darkModePref = getCookie('darkMode');
if (darkModePref === 'enabled') {
    document.body.classList.add('dark-mode');
}
```

**Simple implementation steps:**
1. Create functions to set and get cookies
2. Save user preferences when they change (like theme preference)
3. Check for saved preferences on page load
4. Apply the stored settings

For a portfolio site, you might track:
- Theme preference (light/dark mode)
- Language choice
- Whether they've seen a specific section

Keep cookie data minimal and focused on enhancing user experience rather than tracking behavior.

---

User:
Wait, so this code goes right into my HTML or what? I'm kinda lost on where to put it.

---

Bot
### Integrating Cookie Code into Your HTML

Don't worry—it's straightforward to add this JavaScript code to your portfolio site. Since you're working on a freelance portfolio (likely static HTML), you can place the code directly in your HTML file using a `<script>` tag, or link to an external JavaScript file for better organization. Let's break it down step by step.

#### 1. Basic Placement Options
- **Inline in HTML:** Add the code inside `<script>` tags within your HTML file. This is quick for small sites but can clutter your HTML.
- **External JavaScript file:** Create a separate `.js` file (e.g., `cookies.js`) and link it in your HTML. This keeps things clean and reusable.

I'd recommend the external file for a portfolio site, as it separates concerns and makes updates easier.

#### 2. Step-by-Step Implementation
Here's how to integrate the cookie functions we discussed:

**Option A: Inline in HTML**
- Open your main HTML file (e.g., `index.html`).
- Add the `<script>` tag just before the closing `</body>` tag. This ensures the DOM is loaded before the script runs.
  
  ```html
  <!-- In your HTML file, near the end of <body> -->
  <script>
    function setCookie(name, value, days) {
        const expires = days ? `; expires=${new Date(Date.now() + days * 864e5).toUTCString()}` : '';
        document.cookie = `${name}=${value}${expires}; path=/`;
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // Example: Apply dark mode on page load
    const darkModePref = getCookie('darkMode');
    if (darkModePref === 'enabled') {
        document.body.classList.add('dark-mode');
    }
  </script>
  ```

**Option B: External JavaScript File**
- Create a new file called `cookies.js` in the same folder as your HTML.
- Paste the functions into it:

  ```javascript
  // cookies.js
  function setCookie(name, value, days) {
      const expires = days ? `; expires=${new Date(Date.now() + days * 864e5).toUTCString()}` : '';
      document.cookie = `${name}=${value}${expires}; path=/`;
  }

  function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
  }

  // Example: Apply dark mode on page load
  const darkModePref = getCookie('darkMode');
  if (darkModePref === 'enabled') {
      document.body.classList.add('dark-mode');
  }
  ```

- In your HTML file, add this link in the `<head>` section:

  ```html
  <head>
      <!-- Other meta tags, title, etc. -->
      <script src="cookies.js" defer></script>  <!-- defer loads it after HTML parsing -->
  </head>
  ```

#### 3. Handling User Interactions
To save preferences when users interact (e.g., toggle dark mode), add event listeners. For example, if you have a button to toggle themes:

```javascript
// Add this in your cookies.js file or inline script
document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('theme-toggle');  // Assume you have this button
    toggleButton.addEventListener('click', () => {
        const isDark = document.body.classList.toggle('dark-mode');
        setCookie('darkMode', isDark ? 'enabled' : 'disabled', 30);
    });
});
```

Make sure your HTML has an element with `id="theme-toggle"` (e.g., `<button id="theme-toggle">Toggle Theme</button>`), and add CSS for the `.dark-mode` class.

Does this placement make sense for your setup, or are you using a framework like React or a static site generator? That might change things slightly.

As a next step, try adding the code to one page, test it by setting a cookie (e.g., via browser console: `setCookie('test', 'value', 1)`), and check if it persists across reloads. Then, wire it up to a real preference like theme toggling. Let me know how it goes or if you run into any errors!

---

