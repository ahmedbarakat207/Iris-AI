# الرمز التعريفي للمحادثة: Convo_901

User:
How do I implement a GDPR-compliant cookie consent banner that respects user preferences across multiple subdomains while maintaining session persistence for my portfolio site's contact form functionality?

---

Bot
For a GDPR-compliant cookie consent banner across subdomains, you'll need to implement a shared cookie policy that persists across your main domain and all subdomains.

Set up a central cookie consent management system using JavaScript or a third-party solution like Cookiebot or OneTrust. Create a persistent cookie on your primary domain (e.g., example.com) that stores user preferences. This cookie should be set with the Domain attribute pointing to your main domain, not individual subdomains.

For session persistence on your contact form, you'll want to use a separate approach:

1. Store form data in localStorage or sessionStorage during the user's browsing session
2. Use a unique session identifier that persists through page reloads but expires after a reasonable time (like 30 minutes)
3. Set up a backend session management system if needed for longer-term storage

To handle the cookie banner specifically:

- Create a single banner that appears once per user
- Store consent preferences in localStorage or cookies
- Make sure your implementation properly sets and reads cookies across all subdomains using the same domain attribute

For your portfolio site, you can use a simple JavaScript solution to:
1. Check if consent has been given for analytics/other cookies
2. Set appropriate cookies based on user choices
3. Ensure that session data persists through navigation

The key is that your cookie consent system should be stateless and maintain a consistent user experience across all subdomains, while session management remains separate from the cookie preferences but still respects the user's choice to continue using the contact form functionality.

Your approach should prioritize user control over cookie settings while maintaining functional aspects of your site.

---

User:
Whoa, that sounds pretty complicated. What if I just wanna use something free and not deal with third-party stuff? Is there a basic code snippet or something?

---

Bot
Absolutely, let's simplify this. You can build a basic GDPR-compliant cookie consent banner using vanilla JavaScript—no third-party libraries or services required. This approach uses cookies set on your main domain (e.g., .example.com) to share preferences across subdomains, and localStorage for session persistence on your contact form. It's free, lightweight, and gives you full control.

I'll break it down step by step: first, the high-level setup; then, a basic code snippet you can copy-paste into your site's HTML; and finally, how to handle the contact form. I'll assume your site uses a main domain like example.com with subdomains (e.g., blog.example.com, portfolio.example.com). If your setup differs, adjust the domain references accordingly.

### Step 1: Understanding the Basics
- **Cookie Consent**: We'll create a banner that asks for consent. User preferences will be stored in a cookie on the parent domain (.example.com), making it accessible across all subdomains. This cookie will track if they've accepted or declined cookies.
- **Cross-Subdomain Sharing**: Cookies must be set with the `domain` attribute to include the leading dot (e.g., `.example.com`) for subdomain sharing. Avoid setting them on specific subdomains.
- **Session Persistence for Contact Form**: Use localStorage to save form data temporarily (e.g., during navigation). Add a timestamp to expire it after 30 minutes, simulating a session. This keeps form data without relying on cookies, respecting user preferences.
- **GDPR Compliance**: The banner will explain cookie use, allow opting in/out, and store only essential data (no PII). Always link to your full privacy policy.
- **Potential Confusion**: Browsers may block third-party cookies, but since this is on your domain, it should work. Test in incognito mode to ensure cookies persist across page loads. If a user clears cookies, they'll see the banner again—that's expected.

Does this setup align with your site? If you have multiple unrelated domains, this won't work without adjustments.

### Step 2: Basic Code Snippet
Add this to your site's `<head>` or just before the closing `</body>` tag on every page (across all subdomains). It checks for an existing consent cookie on load. If none exists, it shows the banner.

```html
<!-- Cookie Consent Banner Script -->
<script>
  // Function to set a cookie across subdomains
  function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = name + "=" + value + ";expires=" + date.toGMTString() + ";path=/;domain=.example.com;secure"; // Replace .example.com with your domain
  }

  // Function to get a cookie
  function getCookie(name) {
    const value = "; " + document.cookie;
    const parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }

  // Check if consent has been given
  const consent = getCookie("gdpr_consent");
  if (!consent) {
    // Show banner if no consent
    const banner = document.createElement("div");
    banner.id = "consent-banner";
    banner.innerHTML = `
      <div style="position:fixed;bottom:0;left:0;right:0;background:#333;color:#fff;padding:20px;z-index:1000;text-align:center;">
        <p>We use cookies to improve your experience. <a href="/privacy-policy" style="color:#add8e6;">Learn more</a>.</p>
        <button id="accept-cookies" style="margin-right:10px;padding:10px;background:#4CAF50;color:white;border:none;cursor:pointer;">Accept</button>
        <button id="decline-cookies" style="padding:10px;background:#f44336;color:white;border:none;cursor:pointer;">Decline</button>
      </div>
    `;
    document.body.appendChild(banner);

    // Handle accept button
    document.getElementById("accept-cookies").onclick = function() {
      setCookie("gdpr_consent", "accepted", 365); // Store for 1 year
      banner.style.display = "none";
      // Add code here to enable tracking/analytics if accepted
    };

    // Handle decline button
    document.getElementById("decline-cookies").onclick = function() {
      setCookie("gdpr_consent", "declined", 365);
      banner.style.display = "none";
      // Ensure no non-essential cookies are set
    };
  } else {
    // If consent exists, proceed (e.g., enable tracking if accepted)
    if (consent === "accepted") {
      // Your analytics code here, e.g., load Google Analytics
    }
  }
</script>
```

- **How It Works**: On page load, it checks for a "gdpr_consent" cookie. If missing, it injects a fixed-position banner at the bottom. Clicking Accept or Decline sets the cookie on `.example.com` (change to your domain). This cookie is now readable across all subdomains.
- **Customization**: Style the banner via inline CSS (or move to an external stylesheet). Add your privacy policy link. If the user declines, avoid setting any optional cookies.
- **Testing Tip**: Load your site on the main domain and a subdomain. Accept cookies on one, then navigate to the other— the banner shouldn't reappear.

### Step 3: Integrating Session Persistence for the Contact Form
To keep form data during a session (e.g., if users navigate away and come back), store it in localStorage without cookies. Here's a simple addition:

- Add this script to your contact form page(s):

```html
<script>
  // On form load, restore data from localStorage if within session time
  window.onload = function() {
    const form = document.getElementById("contact-form"); // Replace with your form ID
    if (form) {
      const savedData = JSON.parse(localStorage.getItem("contact_session"));
      const now = new Date().getTime();
      if (savedData && (now - savedData.timestamp) < 1800000) { // 30 minutes in ms
        // Restore form fields
        Object.keys(savedData).forEach(key => {
          if (key !== "timestamp" && form[key]) form[key].value = savedData[key];
        });
      } else {
        localStorage.removeItem("contact_session"); // Clear expired data
      }
    }
  };

  // Save form data on input change
  function saveFormData() {
    const form = document.getElementById("contact-form");
    if (form) {
      const data = { timestamp: new Date().getTime() };
      const inputs = form.querySelectorAll("input, textarea");
      inputs.forEach(input => data[input.name] = input.value);
      localStorage.setItem("contact_session", JSON.stringify(data));
    }
  }

  // Attach to form inputs (example)
  document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("contact-form");
    if (form) {
      form.addEventListener("input", saveFormData);
    }
  });
</script>
```

- **How It Works**: As users type, data saves to localStorage with a timestamp. On page load, it restores if under 30 minutes. This persists across page refreshes but not across browsers or devices.
- **GDPR Note**: localStorage doesn't require consent like cookies, but if you store sensitive data, get explicit permission. On form submission, clear the localStorage entry.
- **Potential Issue**: localStorage is per-origin, so if subdomains are separate, data won't share. If needed, use the cookie method above to pass a session ID across subdomains.

### Next Steps to Apply This
1. Replace `example.com` with your actual domain in the cookie functions.
2. Implement on a test page: Add the scripts, load in a browser, and test accepting/declining cookies across subdomains.
3. Add the form persistence script to your contact form HTML.
4. Verify: Clear cookies, reload, and ensure the banner appears. Fill out your form, navigate away, come back—data should persist.

What part of this code are you testing first? Do you need help adapting it for your specific contact form structure? Let me know how it goes!

---

User:
Whoa, that's a ton of code! I'm gonna try pasting it in, but my contact form is just a simple HTML one with inputs named "name", "email", and "message"—do I still need to change anything specific for that?

---

Bot
No worries at all—that code snippet is designed to be plug-and-play, but it's totally understandable if it feels like a lot at first. Since your contact form is a simple HTML one with inputs named "name", "email", and "message", the provided session persistence script should work out of the box without major changes. I'll walk you through exactly what to check and any minor tweaks needed, assuming your form looks something like this basic structure (if it's different, just share a snippet, and I can adjust):

```html
<form id="contact-form">
  <input type="text" name="name" placeholder="Your Name">
  <input type="email" name="email" placeholder="Your Email">
  <textarea name="message" placeholder="Your Message"></textarea>
  <button type="submit">Send</button>
</form>
```

### Quick Check on the Code for Your Form
The session persistence script I gave you automatically:
- Targets the form by its ID (`contact-form`).
- Finds all inputs and textareas inside it using their `name` attributes.
- Saves and restores data based on those names ("name", "email", "message").

So, for your setup:
- **No changes needed for the field names**: It will save whatever is in inputs named "name", "email", and "message". If your message field is a `<textarea>`, that's fine—it's included in the query.
- **Ensure the form ID matches**: In the script, it looks for `document.getElementById("contact-form")`. If your form has a different ID (e.g., "my-form"), just update that line in the script to match. For example, change `document.getElementById("contact-form")` to `document.getElementById("my-form")` in both places.
- **Potential confusion**: If your form doesn't have an ID at all, add one like `<form id="contact-form">` to your HTML. Without it, the script won't attach the saving behavior.
- **Textarea handling**: If your "message" is a `<textarea>`, it should work seamlessly since `querySelectorAll("input, textarea")` includes both.

The rest of the script (like the 30-minute expiration and localStorage saving/loading) stays the same—it doesn't care about the specific field types or names beyond what's in the form.

### Step-by-Step to Implement and Test
1. **Paste the scripts**: Add the cookie consent script to your site's `<head>` or before `</body>` on all pages. Add the session persistence script specifically to your contact form page(s).
2. **Verify form setup**: Double-check your form's HTML has the ID and correct names. If you're using a CMS or template, ensure the names match exactly (case-sensitive).
3. **Test basics**: Load the page in a browser. Type something in the form, refresh the page—the data should reappear if under 30 minutes. Accept or decline cookies on one subdomain, then visit another to confirm the banner doesn't reappear.
4. **Edge case**: If users navigate to a different subdomain and back, localStorage won't carry over (it's per-origin), but the cookie consent will persist. If you need form data to carry across subdomains, we could tweak it to use a session ID in a cookie (but only if they've consented).

Does your form already have an ID of "contact-form", or do you need to add/change it? Give it a quick test-paste, and let me know what happens—does the form auto-save as you type, or is there an error popping up? We can troubleshoot from there! Once it's working, you can style the banner or add more features if needed.

---

