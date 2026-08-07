# Tailwind CSS Training: Dark Mode Toggle

User:
How do I implement dark mode with Tailwind CSS using class-based strategy and a JavaScript toggle button?

---

Bot:
First configure Tailwind to use class-based dark mode in `tailwind.config.js`:

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // enables class-based dark mode
  content: ['./src/**/*.{html,js}'],
  theme: { extend: {} },
  plugins: [],
}
```

Then build your HTML with `dark:` variants:

```html
<!DOCTYPE html>
<html lang="en" class="light">
<head>
  <meta charset="UTF-8" />
  <title>Dark Mode Demo</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config = { darkMode: 'class' }</script>
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white min-h-screen transition-colors duration-300">

  <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
    <h1 class="text-xl font-bold">My App</h1>
    <button
      id="theme-toggle"
      class="p-2 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      aria-label="Toggle dark mode"
    >
      <span id="theme-icon">🌙</span>
    </button>
  </div>

  <main class="p-8">
    <div class="max-w-md mx-auto bg-gray-50 dark:bg-gray-800 rounded-2xl p-6 shadow">
      <h2 class="text-lg font-semibold mb-2">Welcome</h2>
      <p class="text-gray-600 dark:text-gray-300 text-sm">This page adapts to your preferred theme.</p>
    </div>
  </main>

  <script>
    const toggle = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    const html = document.documentElement;

    // Load saved preference
    const saved = localStorage.getItem('theme') || 'light';
    html.classList.toggle('dark', saved === 'dark');
    icon.textContent = saved === 'dark' ? '☀️' : '🌙';

    toggle.addEventListener('click', () => {
      const isDark = html.classList.toggle('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
      icon.textContent = isDark ? '☀️' : '🌙';
    });
  </script>
</body>
</html>
```

**Key Tailwind dark mode classes:**
| Light | Dark equivalent |
|---|---|
| `bg-white` | `dark:bg-gray-900` |
| `text-gray-900` | `dark:text-white` |
| `border-gray-200` | `dark:border-gray-700` |
| `bg-gray-50` | `dark:bg-gray-800` |

The `transition-colors duration-300` on `<body>` ensures a smooth animated transition between themes.
