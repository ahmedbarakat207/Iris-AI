# الرمز التعريفي للمحادثة: Convo_900

User:
How do I set up basic cookies for user preferences on my portfolio website?

---

Bot
To set up basic cookies for user preferences on your portfolio website, you'll need to work with JavaScript since cookies are handled at the client-side level.

Here's a simple approach:

1. Create a cookie management function:
```javascript
function setCookie(name, value, days) {
  const expires = days ? `; expires=${new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString()}` : '';
  document.cookie = `${name}=${value}${expires}; path=/`;
}

function getCookie(name) {
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') {
      c = c.substring(1, c.length);
    }
    if (c.indexOf(nameEQ) === 0) {
      return c.substring(nameEQ.length, c.length);
    }
  }
  return null;
}
```

2. Use it for simple preferences like theme or language:
```javascript
// Set a preference
setCookie('theme', 'dark', 30); // Store for 30 days

// Read a preference
const savedTheme = getCookie('theme');
if (savedTheme) {
  document.body.className = savedTheme;
}
```

3. Add a simple UI to let users choose their preferences:
```html
<div id="preferences">
  <label>
    <input type="checkbox" id="dark-mode-toggle"> Dark Mode
  </label>
</div>

<script>
document.getElementById('dark-mode-toggle').addEventListener('change', function() {
  const theme = this.checked ? 'dark' : 'light';
  setCookie('theme', theme, 30);
  document.body.className = theme;
});
</script>
```

The key is to store user choices in the cookie and read them when the page loads. Keep it simple with just a few preferences to avoid overwhelming visitors.

---

User:
Wait, so this code goes right into my HTML file or what? I'm kinda new to this JS stuff.

---

Bot
Yes, the code snippets I provided can go directly into your HTML file—that's a great starting point for beginners dipping into JavaScript. I'll break this down step by step, assuming you have a basic HTML structure already set up for your portfolio (like an index.html file). This way, we can keep things simple and practical without jumping into too many files right away.

### Step 1: Understand Where JavaScript Fits in HTML
JavaScript (JS) code runs in the browser and needs to be included in your HTML to work. You can put it:
- **Inline**: Right inside the HTML file, wrapped in `<script>` tags. This is easiest for testing small bits of code.
- **In an external file**: A separate `.js` file linked to your HTML. This is better for larger projects to keep things organized, but we'll save that for later.

For your portfolio, start with inline scripts. Place them near the end of your HTML, just before the closing `</body>` tag. This ensures the HTML loads first, then the JS runs.

### Step 2: Add the Code to Your HTML File
Open your portfolio's HTML file (e.g., index.html) in a code editor like VS Code or Notepad++. Here's how to integrate the cookie functions and example:

1. **Add the cookie functions**: Paste this inside `<script>` tags. If your HTML doesn't have a `<script>` section yet, add one at the end of the `<body>`.

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <title>Your Portfolio</title>
       <!-- Your CSS and other head stuff here -->
   </head>
   <body>
       <!-- Your portfolio content here, like header, nav, etc. -->
       
       <!-- Add the cookie functions here -->
       <script>
       function setCookie(name, value, days) {
         const expires = days ? `; expires=${new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString()}` : '';
         document.cookie = `${name}=${value}${expires}; path=/`;
       }

       function getCookie(name) {
         const nameEQ = name + "=";
         const ca = document.cookie.split(';');
         for(let i = 0; i < ca.length; i++) {
           let c = ca[i];
           while (c.charAt(0) === ' ') {
             c = c.substring(1, c.length);
           }
           if (c.indexOf(nameEQ) === 0) {
             return c.substring(nameEQ.length, c.length);
           }
         }
         return null;
       }
       </script>
   </body>
   </html>
   ```

   This defines the `setCookie` and `getCookie` functions. The `setCookie` creates or updates a cookie, and `getCookie` reads it.

2. **Add the preference logic**: Right after the functions, or in a separate `<script>` block, add code to set and read preferences. For example, to remember a theme:

   ```html
   <script>
   // On page load, check for saved theme and apply it
   const savedTheme = getCookie('theme');
   if (savedTheme) {
     document.body.className = savedTheme; // Applies 'dark' or 'light' class to the body
   }

   // Example: Set theme on a button click (you'll add the button in HTML)
   function toggleTheme() {
     const currentTheme = document.body.className || 'light';
     const newTheme = currentTheme === 'light' ? 'dark' : 'light';
     setCookie('theme', newTheme, 30);
     document.body.className = newTheme;
   }
   </script>
   ```

   To make this interactive, add a button in your HTML (inside the `<body>`, maybe in a footer or preferences section):

   ```html
   <button onclick="toggleTheme()">Toggle Theme</button>
   ```

   Clicking this will switch between light and dark themes and save the choice in a cookie for 30 days.

### Step 3: Test It Out
- Save your HTML file and open it in a browser (double-click the file or use a local server like Live Server in VS Code).
- Click the toggle button—notice how the page "remembers" the theme even after refreshing or closing/reopening the browser.
- Check your browser's developer tools (press F12, go to the Console tab) to see if there are any errors. If something doesn't work, it might be a typo in the code.

A common confusion point: If your theme doesn't apply visually, make sure you have CSS classes defined (e.g., in a `<style>` tag or separate CSS file) like `.dark { background: black; color: white; }` and `.light { background: white; color: black; }`.

Does this placement make sense, or are you running into any specific errors when trying it? If it works, try expanding it by adding more preferences, like a language selector. As a next step, once you're comfortable, we can move the JS to a separate file to keep your HTML cleaner. Let me know how it goes!

---

