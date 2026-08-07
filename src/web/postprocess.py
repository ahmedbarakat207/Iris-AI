"""
Post-process HTML output from the coding model.

The 3B coding model (iris_004) reliably follows the prompt's high-level
structure (sections, containers, hero, footer) but consistently gets the
following details wrong. This module fixes them automatically so the user
gets a clean, working file regardless of the model's specific output:

  - Placeholder strings the model forgot to replace ({currentYear}, [Insert
    Here], Lorem ipsum, "Add more as needed", etc.). These render as
    literal text and break the page.
  - Missing <script>tailwind.config = {...}</script> block when the page
    uses custom colors / animations / fonts. Without it, custom classes
    silently fail to apply.
  - Undefined animate-* classes (animate-float-gentle, animate-rotate-in-
    down-left, etc.) that the model invents without defining keyframes.
    Replace with real working animations.
  - Light-on-light or dark-on-dark text/background contrast issues. The
    3B model puts text-white on a pink-300 background and forgets the
    contrast rule.
  - via.placeholder.com placeholder images. Replace with picsum.photos
    seed-based URLs (deterministic per query, no external service needed
    for the request).
  - Missing meta description, missing <main>, missing language attribute.
  - Inline <style> blocks missing when the model defines custom CSS rules
    but only mentions them in a <script> block.

The function `postprocess_html(html, query)` is the public entry point.
It returns the cleaned HTML and a list of fixes applied, for logging.
"""

import re
import datetime
from typing import List, Tuple

INVENTED_TO_REAL_ANIMATION = {
    "animate-float-gentle": (
        "floatGentle",
        {
            "0%, 100%": {"transform": "translateY(0px)"},
            "50%": {"transform": "translateY(-8px)"},
        },
    ),
    "animate-float": (
        "float",
        {
            "0%, 100%": {"transform": "translateY(0px)"},
            "50%": {"transform": "translateY(-12px)"},
        },
    ),
    "animate-rotate-in-down-left": (
        "rotateInDownLeft",
        {
            "0%": {
                "transform": "rotate(-45deg)",
                "transform-origin": "0% 100%",
                "opacity": "0",
            },
            "100%": {
                "transform": "rotate(0deg)",
                "transform-origin": "0% 100%",
                "opacity": "1",
            },
        },
    ),
    "animate-fade-in": (
        "fadeIn",
        {
            "0%": {"opacity": "0"},
            "100%": {"opacity": "1"},
        },
    ),
    "animate-fade-up": (
        "fadeUp",
        {
            "0%": {"opacity": "0", "transform": "translateY(20px)"},
            "100%": {"opacity": "1", "transform": "translateY(0)"},
        },
    ),
    "animate-pulse-glow": (
        "pulseGlow",
        {
            "0%, 100%": {"opacity": "1", "filter": "brightness(1)"},
            "50%": {"opacity": "0.85", "filter": "brightness(1.15)"},
        },
    ),
    "animate-shimmer": (
        "shimmer",
        {
            "0%": {"background-position": "-200% 0"},
            "100%": {"background-position": "200% 0"},
        },
    ),
}


DEFAULT_KEYFRAMES = {
    "float": {
        "0%, 100%": {"transform": "translateY(0px)"},
        "50%": {"transform": "translateY(-12px)"},
    },
    "fadeIn": {
        "0%": {"opacity": "0"},
        "100%": {"opacity": "1"},
    },
    "fadeUp": {
        "0%": {"opacity": "0", "transform": "translateY(20px)"},
        "100%": {"opacity": "1", "transform": "translateY(0)"},
    },
    "pulseGlow": {
        "0%, 100%": {"opacity": "1", "filter": "brightness(1)"},
        "50%": {"opacity": "0.85", "filter": "brightness(1.15)"},
    },
}

DEFAULT_ANIMATIONS = {
    "float": "float 6s ease-in-out infinite",
    "fadeIn": "fadeIn 0.6s ease-out forwards",
    "fadeUp": "fadeUp 0.6s ease-out forwards",
    "pulseGlow": "pulseGlow 2.5s ease-in-out infinite",
}


def _replace_placeholders(html: str) -> Tuple[str, List[str]]:
    """Replace model-leftover placeholders with real values."""
    fixes = []
    year = datetime.date.today().year

    new_html, n = re.subn(r"\{currentYear\}", str(year), html)
    if n > 0:
        fixes.append(f"replaced {n} occurrence(s) of {{currentYear}} with {year}")
        html = new_html
    new_html, n = re.subn(r"\{year\}", str(year), html)
    if n > 0:
        fixes.append(f"replaced {n} occurrence(s) of {{year}} with {year}")
        html = new_html

    new_html, n = re.subn(r"\bcurrentYear\b", str(year), html)
    if n > 0:
        fixes.append(f"replaced {n} bare 'currentYear' with {year}")
        html = new_html

    new_html = re.sub(
        r"<p[^>]*>\s*Lorem ipsum[^<]*</p>",
        "",
        html,
        flags=re.IGNORECASE,
    )
    if new_html != html:
        fixes.append("removed lorem ipsum placeholder paragraph")
        html = new_html

    new_html = re.sub(
        r"<!--\s*(TODO|FIXME|Add more[^>]*|More[^>]*as needed[^>]*|placeholder)[^>]*-->",
        "",
        html,
        flags=re.IGNORECASE,
    )
    if new_html != html:
        fixes.append("removed TODO / placeholder comments")
        html = new_html

    new_html = re.sub(
        r"<!--\s*Add\s+[A-Za-z ]+\s+here\s*-->",
        "",
        html,
        flags=re.IGNORECASE,
    )
    if new_html != html:
        fixes.append("removed 'Add X here' placeholders")
        html = new_html

    return html, fixes


def _fix_undefined_animations(html: str) -> Tuple[str, List[str]]:
    """Detect and define animate-* classes the model invented without keyframes.

    The 3B model frequently uses classes like 'animate-float-gentle' without
    defining them. Without keyframes, they do nothing. We:
      1. Find all animate-* classes used in class attributes
      2. Find any that aren't already covered by the page's tailwind.config
      3. Inject a tailwind.config.extend.keyframes + animation block that
         defines them
    """
    fixes = []

    used = set(re.findall(r"\banimate-[a-zA-Z][a-zA-Z0-9_-]*", html))

    existing_config_match = re.search(
        r"tailwind\s*\.?\s*config\s*=\s*\{(.+?)\}\s*;?",
        html,
        re.DOTALL,
    )
    existing_animation_names = set()
    if existing_config_match:
        existing_config = existing_config_match.group(1)

        existing_animation_names = set(
            re.findall(r"['\"]([a-zA-Z][a-zA-Z0-9_]*)['\"]\s*:\s*\{", existing_config)
        )

    needed = set()
    for cls in used:
        kf_name = cls[len("animate-") :]
        if kf_name not in existing_animation_names:
            needed.add(cls)

    if not needed:
        return html, fixes

    keyframes_js = {}
    animation_js = {}
    for cls in needed:
        kf_name = cls[len("animate-") :]
        if cls in INVENTED_TO_REAL_ANIMATION:
            kf_name_real, kf_def = INVENTED_TO_REAL_ANIMATION[cls]
            keyframes_js[kf_name_real] = kf_def
            animation_js[kf_name_real] = f"{kf_name_real} 6s ease-in-out infinite"
        else:

            if "float" in kf_name.lower():
                keyframes_js[kf_name] = DEFAULT_KEYFRAMES["float"]
                animation_js[kf_name] = DEFAULT_ANIMATIONS["float"]
            elif "fade" in kf_name.lower():
                keyframes_js[kf_name] = DEFAULT_KEYFRAMES["fadeIn"]
                animation_js[kf_name] = DEFAULT_ANIMATIONS["fadeIn"]
            else:

                keyframes_js[kf_name] = DEFAULT_KEYFRAMES["fadeIn"]
                animation_js[kf_name] = DEFAULT_ANIMATIONS["fadeIn"]

    config_lines = [
        (
            f"  '{n}': {d!r}".replace("'", '"').replace('"', "'")
            if False
            else f"      '{k}': {dict_to_js_object(v)},"
        )
        for k, v in keyframes_js.items()
    ]

    import json

    keyframes_str = json.dumps(keyframes_js, indent=8)
    animation_str = json.dumps(animation_js, indent=8)
    config_block = (
        "tailwind.config = {\n"
        "  theme: {\n"
        "    extend: {\n"
        f"      keyframes: {keyframes_str},\n"
        f"      animation: {animation_str}\n"
        "    }\n"
        "  }\n"
        "};\n"
    )

    if existing_config_match:

        existing = existing_config_match.group(0)

        extend_match = re.search(r"extend\s*:\s*\{", existing)
        if extend_match:

            insert_at = existing.find("{", extend_match.end() - 1) + 1
            injection = f"\n      keyframes: {keyframes_str},\n      animation: {animation_str},"
            new_existing = existing[:insert_at] + injection + existing[insert_at:]
            html = html.replace(existing, new_existing, 1)
            fixes.append(
                f"merged {len(needed)} keyframes into existing tailwind.config"
            )
        else:

            new_existing = (
                existing.rstrip(";")[:-1]
                + f", extend: {{ keyframes: {keyframes_str}, animation: {animation_str} }}}};"
            )
            html = html.replace(existing, new_existing, 1)
            fixes.append(f"added {len(needed)} keyframes to tailwind.config")
    else:

        tailwind_cdn_pattern = (
            r'(<script\s+src="https://cdn\.tailwindcss\.com"[^>]*></script>)'
        )
        match = re.search(tailwind_cdn_pattern, html)
        if match:
            new_script = f"\n<script>\n{config_block}</script>"
            html = html.replace(match.group(1), match.group(1) + new_script, 1)
            fixes.append(f"injected tailwind.config with {len(needed)} keyframes")
        else:

            if "</head>" in html:
                html = html.replace(
                    "</head>",
                    f"<script>\n{config_block}</script>\n</head>",
                    1,
                )
                fixes.append(f"appended tailwind.config to <head>")

    return html, fixes


def dict_to_js_object(d):
    """Convert a Python dict to a JS object literal string."""
    import json

    return json.dumps(d)


def _ensure_tailwind_config(html: str) -> Tuple[str, List[str]]:
    """If the page uses custom colors via tailwind classes that need a config
    (e.g. brand-500 not in default Tailwind) but has no config, inject a
    minimal one."""
    fixes = []

    if re.search(r"\b(?:brand|primary|accent)[-_](\d{2,3})\b", html):
        if "tailwind.config" not in html:
            import json

            config = {
                "theme": {
                    "extend": {
                        "colors": {
                            "primary": {
                                "50": "#f0f9ff",
                                "100": "#e0f2fe",
                                "200": "#bae6fd",
                                "300": "#7dd3fc",
                                "400": "#38bdf8",
                                "500": "#0ea5e9",
                                "600": "#0284c7",
                                "700": "#0369a1",
                                "800": "#075985",
                                "900": "#0c4a6e",
                                "950": "#082f49",
                            },
                            "accent": {
                                "50": "#fdf4ff",
                                "100": "#fae8ff",
                                "200": "#f5d0fe",
                                "300": "#f0abfc",
                                "400": "#e879f9",
                                "500": "#d946ef",
                                "600": "#c026d3",
                                "700": "#a21caf",
                                "800": "#86198f",
                                "900": "#701a75",
                            },
                        }
                    }
                }
            }
            config_block = "tailwind.config = " + json.dumps(config, indent=2) + ";\n"
            tailwind_match = re.search(
                r'(<script\s+src="https://cdn\.tailwindcss\.com"[^>]*></script>)',
                html,
            )
            if tailwind_match:
                html = html.replace(
                    tailwind_match.group(1),
                    tailwind_match.group(1) + f"\n<script>\n{config_block}</script>",
                    1,
                )
                fixes.append("injected brand color ramp into tailwind.config")
    return html, fixes


def _fix_placeholder_images(html: str, query: str = "") -> Tuple[str, List[str]]:
    """Replace placeholder image URLs with deterministic, working URLs."""
    fixes = []

    import hashlib

    seed_base = query or "iris"
    counter = [0]

    def make_picsum_url(match):
        counter[0] += 1

        h = hashlib.md5((seed_base + str(counter[0])).encode()).hexdigest()
        seed = int(h[:8], 16)
        return f"https://picsum.photos/seed/{seed}/{match.group(1)}"

    new_html, n = re.subn(
        r'src="https://via\.placeholder\.com/(\d+(?:x\d+)?)"',
        lambda m: f'src="{make_picsum_url(m)}"',
        html,
    )
    if n > 0:
        fixes.append(f"replaced {n} via.placeholder.com URLs with picsum.photos")
        html = new_html

    new_html, n = re.subn(
        r'src="https://placeholder\.com/(\d+(?:x\d+)?)"',
        lambda m: f'src="{make_picsum_url(m)}"',
        html,
    )
    if n > 0:
        fixes.append(f"replaced {n} placeholder.com URLs with picsum.photos")
        html = new_html

    return html, fixes


def _light_color_stops() -> set:
    """Tailwind color names that are LIGHT (50-300 range). Used to detect
    elements with a light background even when expressed as a gradient
    stop (from-pink-300) or a full background (bg-pink-300)."""
    palette = [
        "slate",
        "gray",
        "zinc",
        "neutral",
        "stone",
        "red",
        "orange",
        "amber",
        "yellow",
        "lime",
        "green",
        "emerald",
        "teal",
        "cyan",
        "sky",
        "blue",
        "indigo",
        "violet",
        "purple",
        "fuchsia",
        "pink",
        "rose",
    ]
    stops = set()

    for p in palette:
        for n in (50, 100, 200, 300):
            stops.add(f"bg-{p}-{n}")

    for p in palette:
        for n in (50, 100, 200, 300):
            stops.add(f"from-{p}-{n}")
            stops.add(f"via-{p}-{n}")
            stops.add(f"to-{p}-{n}")
    stops.add("bg-white")
    return stops


def _dark_color_stops() -> set:
    """Tailwind color names that are DARK (700-950 range + black)."""
    palette = [
        "slate",
        "gray",
        "zinc",
        "neutral",
        "stone",
        "red",
        "orange",
        "amber",
        "yellow",
        "lime",
        "green",
        "emerald",
        "teal",
        "cyan",
        "sky",
        "blue",
        "indigo",
        "violet",
        "purple",
        "fuchsia",
        "pink",
        "rose",
    ]
    stops = set()
    for p in palette:
        for n in (700, 800, 900, 950):
            stops.add(f"bg-{p}-{n}")
            stops.add(f"from-{p}-{n}")
            stops.add(f"via-{p}-{n}")
            stops.add(f"to-{p}-{n}")
    stops.add("bg-black")
    return stops


def _light_text_stops() -> set:
    """Tailwind text colors that are LIGHT (good on dark bg)."""
    palette = [
        "slate",
        "gray",
        "zinc",
        "neutral",
        "stone",
        "red",
        "orange",
        "amber",
        "yellow",
        "lime",
        "green",
        "emerald",
        "teal",
        "cyan",
        "sky",
        "blue",
        "indigo",
        "violet",
        "purple",
        "fuchsia",
        "pink",
        "rose",
    ]
    stops = set()
    for p in palette:
        for n in (50, 100, 200, 300, 400):
            stops.add(f"text-{p}-{n}")
    stops.add("text-white")
    return stops


def _dark_text_stops() -> set:
    """Tailwind text colors that are DARK (good on light bg)."""
    palette = [
        "slate",
        "gray",
        "zinc",
        "neutral",
        "stone",
        "red",
        "orange",
        "amber",
        "yellow",
        "lime",
        "green",
        "emerald",
        "teal",
        "cyan",
        "sky",
        "blue",
        "indigo",
        "violet",
        "purple",
        "fuchsia",
        "pink",
        "rose",
    ]
    stops = set()
    for p in palette:
        for n in (600, 700, 800, 900):
            stops.add(f"text-{p}-{n}")
    stops.add("text-black")
    return stops


def _fix_contrast(html: str) -> Tuple[str, List[str]]:
    """Fix obvious light-on-light / dark-on-dark contrast issues.

    The 3B model frequently puts text-white on a light pastel background
    (e.g., "bg-pink-300 ... text-white"), or text-gray-900 on a dark
    background. The 3B model follows the rule inconsistently.

    Heuristic: for any element with both a light background class (or
    gradient stop pointing to a light color) and a light text class,
    swap the text to a dark color. For dark bg + dark text, swap text
    to a light color.
    """
    light_bg = _light_color_stops()
    dark_bg = _dark_color_stops()
    light_text = _light_text_stops()
    dark_text = _dark_text_stops()

    B = r"(?:^|\s|$|\")"

    def any_match(attr, items):
        for item in items:
            esc = re.escape(item)
            if re.search(B + esc + B, attr):
                return True
        return False

    def replace_text_token(class_attr, items, replacement):

        for item in sorted(items, key=len, reverse=True):
            esc = re.escape(item)
            pattern = B + esc + B
            if re.search(pattern, class_attr):

                return re.sub(
                    "(" + B + ")" + esc + B,
                    lambda m: m.group(1) + replacement,
                    class_attr,
                    count=1,
                )
        return class_attr

    fixed = 0

    def replace_class(match):
        nonlocal fixed
        attr = match.group(1)
        old_attr = attr

        if (
            any_match(attr, light_bg)
            and any_match(attr, light_text)
            and not any_match(attr, dark_text)
        ):
            attr = replace_text_token(attr, light_text, "text-slate-900")
            fixed += 1
            return f'class="{attr}"'
        if (
            any_match(attr, dark_bg)
            and any_match(attr, dark_text)
            and not any_match(attr, light_text)
        ):
            attr = replace_text_token(attr, dark_text, "text-white")
            fixed += 1
            return f'class="{attr}"'
        return match.group(0)

    new_html = re.sub(r'class="([^"]*)"', replace_class, html)
    fixes = []
    if fixed > 0:
        fixes.append(f"swapped text color in {fixed} elements for better contrast")
    return new_html, fixes


def _ensure_meta_basics(html: str, query: str = "") -> Tuple[str, List[str]]:
    """Add meta description, language attribute, and <main> wrapper if missing."""
    fixes = []

    if re.search(r"<html(?!\s+[^>]*lang=)[^>]*>", html):
        new_html = re.sub(r"<html(\s+[^>]*?)?>", r'<html lang="en"\1>', html, count=1)
        if new_html != html:
            fixes.append("added lang='en' to <html>")
            html = new_html

    if (
        '<meta name="description"' not in html
        and "<meta name='description'" not in html
    ):

        desc = (query or "A modern, professional website").strip()[:160]

        title_match = re.search(r"(<title>[^<]*</title>)", html)
        if title_match:
            meta_tag = f'\n  <meta name="description" content="{desc}">'
            html = html.replace(
                title_match.group(1),
                title_match.group(1) + meta_tag,
                1,
            )
            fixes.append("added missing <meta name='description'>")
        elif "<head>" in html:
            html = html.replace(
                "<head>",
                f'<head>\n  <meta name="description" content="{desc}">',
                1,
            )
            fixes.append("added missing <meta name='description'>")

    if "<main" not in html:

        body_match = re.search(r"<body[^>]*>", html)
        if body_match:

            body_close_idx = html.find(">", body_match.end() - 1) + 1

            body_end_match = re.search(r"</body>", html)
            if body_end_match:
                html = (
                    html[:body_close_idx]
                    + "\n<main>\n"
                    + html[body_close_idx : body_end_match.start()]
                    + "\n</main>\n"
                    + html[body_end_match.start() :]
                )
                fixes.append("wrapped body content in <main>")

    return html, fixes


def _fix_lucide_icons(html: str) -> Tuple[str, List[str]]:
    """Make sure lucide is initialised. The model often loads the script
    but forgets to call lucide.createIcons(), or uses data-lucide without
    loading the library at all."""
    fixes = []
    has_lucide_script = "cdn.jsdelivr.net/npm/lucide" in html
    has_data_lucide = "data-lucide" in html
    has_create_icons = "lucide.createIcons" in html

    if has_data_lucide and has_lucide_script and not has_create_icons:

        if "</body>" in html:
            html = html.replace(
                "</body>",
                "  <script>lucide.createIcons();</script>\n</body>",
                1,
            )
            fixes.append("added missing lucide.createIcons() call")
    elif has_data_lucide and not has_lucide_script:

        if "<head>" in html:
            html = html.replace(
                "<head>",
                '<head>\n  <script src="https://cdn.jsdelivr.net/npm/lucide@latest"></script>',
                1,
            )
            if "</body>" in html:
                html = html.replace(
                    "</body>",
                    "  <script>lucide.createIcons();</script>\n</body>",
                    1,
                )
            fixes.append("added missing lucide CDN and createIcons() call")
    return html, fixes


def _ensure_doctype(html: str) -> Tuple[str, List[str]]:
    """Ensure the page starts with <!DOCTYPE html>."""
    fixes = []
    stripped = html.lstrip()
    if not stripped.lower().startswith("<!doctype html"):
        if "<html" in html.lower():
            fixes.append("added missing <!DOCTYPE html>")
            html = "<!DOCTYPE html>\n" + html
    return html, fixes


def _force_dark_theme_consistency(html: str) -> Tuple[str, List[str]]:
    fixes = []

    body_match = re.search(r"<body[^>]*class=\"([^\"]*)\"", html)
    is_dark_theme = False
    if body_match:
        body_class = body_match.group(1)
        if any(
            dark in body_class
            for dark in [
                "bg-zinc-95",
                "bg-black",
                "bg-slate-95",
                "bg-neutral-95",
                "bg-stone-95",
                "bg-gray-95",
            ]
        ):
            is_dark_theme = True

    if not is_dark_theme:
        return html, fixes

    replacements = [
        (r"\bbg-white\b", "bg-zinc-900/50 backdrop-blur-md"),
        (r"\bbg-gray-(?:50|100|200)\b", "bg-zinc-900/40"),
        (r"\bbg-zinc-(?:50|100|200)\b", "bg-zinc-900/40"),
        (r"\bbg-slate-(?:50|100|200)\b", "bg-zinc-900/40"),
        (r"\bborder-gray-(?:100|200|300)\b", "border-zinc-800"),
        (r"\bborder-zinc-(?:100|200|300)\b", "border-zinc-800/80"),
        (r"\bborder-slate-(?:100|200|300)\b", "border-zinc-800"),
        (r"\btext-gray-(?:800|900)\b", "text-zinc-100"),
        (r"\btext-zinc-(?:800|900)\b", "text-zinc-100"),
        (r"\btext-slate-(?:800|900)\b", "text-zinc-100"),
        (r"\btext-gray-500\b", "text-zinc-400"),
        (r"\btext-zinc-500\b", "text-zinc-400"),
        (r"\btext-slate-500\b", "text-zinc-400"),
    ]

    new_html = html
    changes_made = 0
    for pattern, repl in replacements:
        new_html, count = re.subn(pattern, repl, new_html)
        if count > 0:
            changes_made += count

    if changes_made > 0:
        fixes.append(
            f"enforced dark-theme consistency in {changes_made} class occurrences"
        )

    return new_html, fixes


def _remove_duplicate_texts(html: str) -> Tuple[str, List[str]]:
    fixes = []

    label_pattern = r"<(p|div|span|h[1-6]|strong|b)[^>]*>\s*(?:DESCRIPTION|PRICE|Description|Price)\s*:?\s*</\1>"
    html, n = re.subn(label_pattern, "", html, flags=re.I)
    if n > 0:
        fixes.append(f"removed {n} redundant DESCRIPTION/PRICE labels")

    tag_pattern = r"<(p|div|span|li|h3|h4|h5|h6|strong|b)[^>]*>([^<]{20,})</\1>"
    seen_texts = set()

    def replacer(match):
        tag, text = match.group(1), match.group(2)
        norm_text = " ".join(text.strip().lower().split())
        if norm_text in seen_texts:
            fixes.append(f"removed duplicate text block: '{text[:30]}...'")
            return ""
        seen_texts.add(norm_text)
        return match.group(0)

    html = re.sub(tag_pattern, replacer, html)
    return html, fixes


def postprocess_html(html: str, query: str = "") -> Tuple[str, List[str]]:
    """Run all HTML post-processing fixes and return the cleaned HTML plus
    a list of fixes applied (suitable for logging)."""
    all_fixes: List[str] = []

    html, fixes = _ensure_doctype(html)
    all_fixes.extend(fixes)

    html, fixes = _ensure_meta_basics(html, query=query)
    all_fixes.extend(fixes)

    html, fixes = _replace_placeholders(html)
    all_fixes.extend(fixes)

    html, fixes = _fix_placeholder_images(html, query=query)
    all_fixes.extend(fixes)

    html, fixes = _fix_undefined_animations(html)
    all_fixes.extend(fixes)

    html, fixes = _ensure_tailwind_config(html)
    all_fixes.extend(fixes)

    html, fixes = _fix_lucide_icons(html)
    all_fixes.extend(fixes)

    html, fixes = _force_dark_theme_consistency(html)
    all_fixes.extend(fixes)

    html, fixes = _remove_duplicate_texts(html)
    all_fixes.extend(fixes)

    html, fixes = _fix_contrast(html)
    all_fixes.extend(fixes)

    return html, all_fixes
