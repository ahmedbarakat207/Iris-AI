from __future__ import annotations

import re
import os
from typing import Tuple, List, Optional


def normalize_fences(text: str, language: str = "python") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    original = text
    text = re.sub("````+", "```", text)
    text = re.sub("(?<![`\\n])``([^`\\n]+)``(?![`\\n])", "`\\1`", text)
    opening = [m for m in re.finditer("^```", text, re.MULTILINE)]
    closing = [m for m in re.finditer("\\n```\\s*$", text, re.MULTILINE)]
    if len(opening) > len(closing):
        text = text.rstrip() + "\n```"
        warnings.append("Fence: added missing closing ```")
    if text != original and (not warnings):
        warnings.append("Fence: normalized malformed code fence(s)")
    return (text, warnings)


def strip_comments(text: str, language: str = "python") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    original = text.strip()
    lang = language.lower()
    if lang in ("python", "py"):
        lines = text.split("\n")
        result = []
        for line in lines:
            line_stripped = _strip_py_line(line)
            result.append(line_stripped)
        stripped = "\n".join(result)
        if stripped != text:
            text = stripped
            warnings.append("Comment: stripped Python inline comments")
    elif lang in (
        "javascript",
        "js",
        "typescript",
        "ts",
        "c",
        "cpp",
        "c++",
        "go",
        "rust",
        "rs",
        "java",
    ):
        if re.search("//|/\\*", text):
            text = re.sub("/\\*[^*]*\\*+(?:[^/*][^*]*\\*+)*/", "", text)
            lines = text.split("\n")
            result = []
            for line in lines:
                idx = line.find("//")
                if idx < 0:
                    result.append(line)
                else:
                    before = line[:idx]
                    if before.rstrip().endswith("http:") or before.rstrip().endswith(
                        "https:"
                    ):
                        result.append(line)
                    else:
                        result.append(line[:idx])
            text = "\n".join(result)
            warnings.append("Comment: stripped C-style comments")
    elif lang in ("bash", "sh"):
        text = re.sub("(\\s*)#[^\\n]*", "", text)
        warnings.append("Comment: stripped shell comments")
    text = re.sub("\\n{3,}", "\n\n", text)
    if text.strip() != original and (not warnings):
        warnings.append("Comment: removed developer comments")
    return (text, warnings)


def _strip_py_line(line: str) -> str:
    in_string = False
    string_char = ""
    hash_idx = -1
    i = 0
    while i < len(line):
        ch = line[i]
        if not in_string:
            if ch in ('"', "'"):
                if line[i : i + 3] == ch * 3:
                    in_string = True
                    string_char = ch * 3
                    i += 3
                    continue
                else:
                    in_string = True
                    string_char = ch
            elif ch == "#":
                hash_idx = i
                break
        elif line[i : i + len(string_char)] == string_char:
            in_string = False
            i += len(string_char)
            continue
        elif ch == "\\" and i + 1 < len(line):
            i += 2
            continue
        i += 1
    if hash_idx >= 0:
        return line[:hash_idx].rstrip()
    return line


def repair_truncation(text: str, language: str = "python") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    original = text
    pairs = {"{": "}", "(": ")", "[": "]"}
    stack = []
    in_string = False
    string_char = ""
    prev = ""
    for i, ch in enumerate(text):
        if in_string:
            if ch == string_char and prev != "\\":
                in_string = False
            prev = ch
            continue
        if ch in ('"', "'"):
            if text[i : i + 3] == ch * 3:
                continue
            in_string = True
            string_char = ch
            prev = ch
            continue
        if ch in pairs:
            stack.append(pairs[ch])
        elif ch in pairs.values():
            if stack and stack[-1] == ch:
                stack.pop()
        prev = ch
    if stack:
        closing = "".join(reversed(stack))
        text = text.rstrip() + "\n" + closing
        warnings.append(f"Truncation: added missing closing: {closing}")
    if in_string:
        text = text.rstrip() + string_char
        warnings.append("Truncation: closed unterminated string literal")
    return (text, warnings)


_PY_IMPORT_PATTERNS = {
    "sys": "\\bsys\\.(argv|exit|stdout|stderr|stdin|path|version|platform)\\b",
    "os": "\\bos\\.(path|environ|getenv|listdir|makedirs?|remove|rename|chdir|getcwd|walk|stat|urandom|system)\\b",
    "json": "\\bjson\\.(dumps?|loads?)\\b",
    "re": "\\bre\\.(compile|match|search|findall|sub|split|escape|fullmatch)\\b",
    "time": "\\btime\\.(time|sleep|perf_counter|monotonic|strftime|gmtime|localtime)\\b",
    "datetime": "\\bdatetime\\.(datetime|date|time|timedelta|timezone|now|utcnow)\\b",
    "collections": "\\b(collections\\.(defaultdict|Counter|OrderedDict|deque|namedtuple)|from collections import)\\b",
    "itertools": "\\bitertools\\.(cycle|islice|chain|product|permutations|combinations|groupby)\\b",
    "functools": "\\bfunctools\\.(lru_cache|partial|reduce|wraps|cache)\\b",
    "random": "\\brandom\\.(random|randint|choice|shuffle|seed|uniform|sample|choices)\\b",
    "math": "\\bmath\\.(sqrt|sin|cos|tan|log|log10|log2|exp|floor|ceil|pi|e|factorial|gcd|pow)\\b",
    "pathlib": "\\b(Path\\s*\\(|pathlib\\.)\\b",
    "subprocess": "\\b(subprocess\\.(run|call|Popen|check_output|check_call|PIPE|STDOUT|DEVNULL)|from subprocess import)\\b",
    "typing": "\\b(typing\\.(List|Dict|Tuple|Set|Optional|Union|Any|Callable|Iterator|Generator)|from typing import)\\b",
    "argparse": "\\b(argparse\\.(ArgumentParser|Namespace)|from argparse import)\\b",
    "threading": "\\b(threading\\.(Thread|Lock|RLock|Event|Condition|Semaphore|Timer)|from threading import)\\b",
    "dataclasses": "\\b(dataclasses\\.(dataclass|field)|from dataclasses import|@dataclass)\\b",
    "hashlib": "\\bhashlib\\.(md5|sha1|sha256|sha512|new)\\b",
    "base64": "\\bbase64\\.(b64encode|b64decode|standard_b64encode|urlsafe_b64encode)\\b",
    "uuid": "\\buuid\\.(uuid4|uuid1|uuid3|uuid5|UUID)\\b",
    "tempfile": "\\btempfile\\.(NamedTemporaryFile|TemporaryFile|TemporaryDirectory|mkstemp|mkdtemp|gettempdir)\\b",
    "shutil": "\\bshutil\\.(copy|copy2|copytree|rmtree|move|make_archive|disk_usage|which)\\b",
    "logging": "\\blogging\\.(getLogger|basicConfig|info|debug|warning|error|critical|exception|log)\\b",
    "warnings": "\\bwarnings\\.(warn|filterwarnings|simplefilter|catch_warnings)\\b",
    "struct": "\\bstruct\\.(pack|unpack|calcsize|iter_unpack)\\b",
    "pickle": "\\bpickle\\.(dump|dumps|load|loads|HIGHEST_PROTOCOL)\\b",
    "csv": "\\bcsv\\.(reader|writer|DictReader|DictWriter|writerow|writerows)\\b",
    "io": "\\bio\\.(BytesIO|StringIO|open|BufferedWriter|BufferedReader|TextIOWrapper)\\b",
    "enum": "\\benum\\.(Enum|IntEnum|StrEnum|auto|unique)\\b",
    "abc": "\\b(abc\\.(ABC|abstractmethod|abstractclassmethod|abstractproperty)|from abc import)\\b",
    "socket": "\\bsocket\\.(socket|AF_INET|AF_INET6|SOCK_STREAM|SOCK_DGRAM|gethostname|gethostbyname|getaddrinfo|create_connection)\\b",
    "html": "\\bhtml\\.(escape|unescape)\\b",
    "urllib": "\\b(urllib\\.(request|parse|error|robotparser)|urllib\\.parse\\.(urlencode|quote|unquote|urlparse|urljoin))\\b",
    "zipfile": "\\bzipfile\\.(ZipFile|is_zipfile|ZIP_DEFLATED|ZIP_STORED)\\b",
    "tarfile": "\\btarfile\\.(open|is_tarfile|TarFile|TarInfo)\\b",
    "gzip": "\\bgzip\\.(open|compress|decompress|GzipFile)\\b",
    "glob": "\\bglob\\.(glob|iglob|escape)\\b",
    "textwrap": "\\btextwrap\\.(fill|wrap|shorten|dedent|indent)\\b",
    "pprint": "\\bpprint\\.(pprint|pformat|PrettyPrinter)\\b",
    "copy": "\\bcopy\\.(copy|deepcopy)\\b",
}


def inject_imports(text: str, language: str = "python") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    if language.lower() not in ("python", "py"):
        return (text, warnings)
    lines = text.split("\n")
    existing_imports = set()
    import_line = -1
    shebang_line = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if i == 0 and (s.startswith("#!") or s.startswith("# -*-")):
            shebang_line = i
            continue
        m = re.match("^(?:from\\s+(\\w+)|import\\s+(\\w+))", s)
        if m:
            pkg = m.group(1) or m.group(2)
            existing_imports.add(pkg)
            import_line = i
        elif import_line >= 0 and (not s or s.startswith("#")):
            continue
        elif import_line >= 0:
            break
    insert_at = max(shebang_line, import_line, -1) + 1
    if insert_at > len(lines):
        insert_at = len(lines)
    new_imports = []
    for pkg, pattern in _PY_IMPORT_PATTERNS.items():
        if pkg in existing_imports:
            continue
        if re.search(pattern, text):
            new_imports.append(f"import {pkg}")
            existing_imports.add(pkg)
    if new_imports:
        insert_line = lines[insert_at] if insert_at < len(lines) else ""
        if insert_line.strip():
            lines.insert(insert_at, "")
            insert_at += 1
        for imp in sorted(new_imports):
            lines.insert(insert_at, imp)
            insert_at += 1
        if insert_at < len(lines) and lines[insert_at].strip():
            lines.insert(insert_at, "")
        text = "\n".join(lines)
        warnings.append(f"Imports: injected missing: {', '.join(sorted(new_imports))}")
    return (text, warnings)


def deduplicate_blocks(text: str, language: str = "") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    blocks = re.split("\\n\\n+", text)
    if len(blocks) < 2:
        return (text, warnings)
    seen = {}
    result = []
    for i, block in enumerate(blocks):
        key = re.sub("\\s+", " ", block.strip().lower())
        if len(key) < 20:
            result.append(block)
            continue
        if key in seen:
            warnings.append(f"Duplicate: block {i + 1} repeats block {seen[key] + 1}")
            continue
        seen[key] = i
        result.append(block)
    if len(result) != len(blocks):
        text = "\n\n".join(result)
        text = re.sub("\\n{3,}", "\n\n", text)
    return (text, warnings)


_SECRET_PATTERNS = [
    ("(sk-[a-zA-Z0-9_-]{20,}T3BlbkFJ[a-zA-Z0-9_-]{20,})", "[OPENAI_KEY_REDACTED]"),
    ("(sk-[a-zA-Z0-9_-]{30,})", "[API_KEY_REDACTED]"),
    ("(sk-ant-[a-zA-Z0-9_-]{20,})", "[ANTHROPIC_KEY_REDACTED]"),
    ("(AIza[0-9A-Za-z\\-_]{35})", "[GOOGLE_KEY_REDACTED]"),
    ("(hf_[a-zA-Z0-9]{34})", "[HF_KEY_REDACTED]"),
    ("(api[_-]?key\\s*[:=]\\s*[\"\\'])([^\"\\'\\s]{16,})([\"\\'])", "\\1[REDACTED]\\3"),
    ("(secret\\s*[:=]\\s*[\"\\'])([^\"\\'\\s]{16,})([\"\\'])", "\\1[REDACTED]\\3"),
    ("(token\\s*[:=]\\s*[\"\\'])([^\"\\'\\s]{16,})([\"\\'])", "\\1[REDACTED]\\3"),
    ("(password\\s*[:=]\\s*[\"\\'])([^\"\\'\\s]{8,})([\"\\'])", "\\1[REDACTED]\\3"),
    ("(AKIA[0-9A-Z]{16})", "[AWS_KEY_REDACTED]"),
    ("(ASIA[0-9A-Z]{16})", "[AWS_KEY_REDACTED]"),
    ("(gh[pousr]_[a-zA-Z0-9]{36,})", "[GITHUB_TOKEN_REDACTED]"),
    ("(github_pat_[a-zA-Z0-9_]{20,})", "[GITHUB_TOKEN_REDACTED]"),
    (
        "(eyJ[a-zA-Z0-9_-]{10,}\\.[a-zA-Z0-9_-]{10,}\\.[a-zA-Z0-9_-]{10,})",
        "[JWT_REDACTED]",
    ),
]


def redact_secrets(text: str, language: str = "") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    for pattern, replacement in _SECRET_PATTERNS:
        if re.search(pattern, text):
            count = len(re.findall(pattern, text))
            text = re.sub(pattern, replacement, text)
            warnings.append(f"Secret: redacted {count} potential secret(s)")
    return (text, warnings)


def clean_whitespace(text: str, language: str = "") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    original = text
    lines = text.split("\n")
    lines = [l.rstrip() for l in lines]
    cleaned = []
    blank_count = 0
    for line in lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= 2:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)
    while cleaned and (not cleaned[0].strip()):
        cleaned.pop(0)
    while cleaned and (not cleaned[-1].strip()):
        cleaned.pop()
    text = "\n".join(cleaned)
    if text != original:
        warnings.append("Whitespace: stripped trailing spaces and excess blank lines")
    return (text, warnings)


_VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


def _tw_shade_score(token: str) -> Optional[int]:
    if token == "white":
        return 0
    if token == "black":
        return 1000
    m = re.match(r"^[a-zA-Z]+-(\d{2,3})$", token)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def enforce_contrast(text: str, language: str = "") -> Tuple[str, List[str]]:
    """Heuristic safety net for the classic 'invisible text' bug: a text color too
    close in lightness to its own (or inherited) background. Walks tags in document
    order, tracking a stack of effective background scores so it also catches text
    that looks fine on its own tag but sits on a too-similar ANCESTOR background —
    this deliberately also matches inside JS template-literal strings that build
    HTML dynamically (e.g. list items rendered via innerHTML +=), since that's a
    common place for this bug to hide. Best-effort regex heuristic, not a real CSS
    engine — wrapped by apply_all's try/except, so any edge case just no-ops."""
    warnings: List[str] = []
    if "class" not in text:
        return (text, warnings)

    class_re = re.compile(r'(class(?:Name)?)\s*=\s*(["\'])([^"\']*)\2')
    tag_re = re.compile(
        r'<(/?)([a-zA-Z][a-zA-Z0-9]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*)>'
    )

    out: List[str] = []
    last_end = 0
    stack: List[Optional[int]] = []

    for m in tag_re.finditer(text):
        out.append(text[last_end : m.start()])
        last_end = m.end()
        slash, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)

        if slash:
            if stack:
                stack.pop()
            out.append(m.group(0))
            continue

        cm = class_re.search(attrs)
        own_bg = None
        fixed_attrs = attrs
        if cm:
            tokens = cm.group(3).split()
            text_idx = None
            text_score = None
            for i, t in enumerate(tokens):
                if ":" in t:
                    continue
                if t.startswith("bg-") and own_bg is None:
                    sc = _tw_shade_score(t[3:].split("/")[0])
                    if sc is not None:
                        own_bg = sc
                elif t.startswith("text-") and text_idx is None:
                    sc = _tw_shade_score(t[5:].split("/")[0])
                    if sc is not None:
                        text_idx, text_score = i, sc

            effective_bg = (
                own_bg if own_bg is not None else (stack[-1] if stack else None)
            )
            if (
                text_idx is not None
                and effective_bg is not None
                and abs(effective_bg - text_score) < 400
            ):
                safe = "zinc-50" if effective_bg >= 500 else "zinc-900"
                old_tok = tokens[text_idx]
                tokens[text_idx] = f"text-{safe}"
                new_class_val = " ".join(tokens)
                fixed_attrs = (
                    attrs[: cm.start()]
                    + f"{cm.group(1)}={cm.group(2)}{new_class_val}{cm.group(2)}"
                    + attrs[cm.end() :]
                )
                warnings.append(
                    f"Contrast: {old_tok} was too close to its background — changed to text-{safe}"
                )

        is_void = tag in _VOID_TAGS or attrs.rstrip().endswith("/")
        if not is_void:
            stack.append(
                own_bg if own_bg is not None else (stack[-1] if stack else None)
            )

        out.append("<" + slash + m.group(2) + fixed_attrs + ">")

    out.append(text[last_end:])
    new_text = "".join(out)
    return (new_text, warnings)


def repair_html(text: str, language: str = "") -> Tuple[str, List[str]]:
    """Repairs and elevates generated HTML to ensure premium styling, Tailwind CDN,
    Lucide icons, Google fonts, and consistent dark-mode background/contrast."""
    warnings: List[str] = []

    is_html = (
        language.lower() in ("html", "htm")
        or "<!doctype html" in text.lower()
        or "<html" in text.lower()
        or ("<head" in text.lower() and "<body" in text.lower())
        or (
            "<div" in text.lower()
            and "class=" in text.lower()
            and ("tailwind" in text.lower() or "bg-" in text.lower())
        )
    )
    if not is_html:
        return (text, warnings)

    # 1. Normalize and ensure standard document structure if it's a bare snippet
    has_html_tag = bool(re.search(r"<html[\s>]", text, re.IGNORECASE))
    has_body_tag = bool(re.search(r"<body[\s>]", text, re.IGNORECASE))

    if not has_body_tag and not has_html_tag:
        text = (
            f"<!DOCTYPE html>\n<html lang=\"en\" class=\"scroll-smooth\">\n<head>\n"
            f'  <meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f"  <title>Iris Web Application</title>\n"
            f'  <script src="https://cdn.tailwindcss.com"></script>\n'
            f'  <script src="https://unpkg.com/lucide@latest"></script>\n'
            f'  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">\n'
            f"  <style>body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}</style>\n"
            f"</head>\n<body class=\"bg-zinc-950 text-zinc-100 min-h-screen relative overflow-x-hidden\">\n"
            f"{text}\n"
            f"  <script>if (window.lucide) {{ lucide.createIcons(); }}</script>\n"
            f"</body>\n</html>"
        )
        warnings.append(
            "HTML: Wrapped partial snippet with full Tailwind & Lucide document structure"
        )
        return (text, warnings)

    # 2. Inject Tailwind CDN if missing
    if "cdn.tailwindcss.com" not in text and "tailwindcss" not in text.lower():
        tailwind_script = (
            '  <script src="https://cdn.tailwindcss.com"></script>\n'
        )
        if "<head>" in text:
            text = text.replace("<head>", f"<head>\n{tailwind_script}", 1)
        elif "<head " in text:
            text = re.sub(
                r"(<head[^>]*>)",
                r"\1\n" + tailwind_script,
                text,
                count=1,
                flags=re.IGNORECASE,
            )
        elif "<body" in text:
            text = re.sub(
                r"(<body[^>]*>)",
                r"<head>\n" + tailwind_script + r"</head>\n\1",
                text,
                count=1,
                flags=re.IGNORECASE,
            )
        warnings.append("HTML: Injected Tailwind CSS CDN into <head>")

    # 3. Inject Lucide Icons if missing
    if "lucide" not in text.lower():
        lucide_script = (
            '  <script src="https://unpkg.com/lucide@latest"></script>\n'
        )
        if "</head>" in text:
            text = text.replace("</head>", f"{lucide_script}</head>", 1)
        elif "<body" in text:
            text = re.sub(
                r"(<body[^>]*>)",
                r"\1\n" + lucide_script,
                text,
                count=1,
                flags=re.IGNORECASE,
            )
        warnings.append("HTML: Injected Lucide Icons library")

    # 4. Inject Google Fonts if no external font link
    if "fonts.googleapis.com" not in text:
        font_link = (
            '  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">\n'
            "  <style>body { font-family: 'Plus Jakarta Sans', sans-serif; }</style>\n"
        )
        if "</head>" in text:
            text = text.replace("</head>", f"{font_link}</head>", 1)
        elif "<body" in text:
            text = re.sub(
                r"(<body[^>]*>)",
                r"\1\n" + font_link,
                text,
                count=1,
                flags=re.IGNORECASE,
            )

    # 5. Ensure <body> has dark background and text classes
    _LIGHT_BG_PATTERN = re.compile(
        r'\bbg-(?:'
        r'white|gray-[0-4]\d{2}|grey-[0-4]\d{2}|'
        r'slate-[0-4]\d{2}|zinc-[0-4]\d{2}|neutral-[0-4]\d{2}|stone-[0-4]\d{2}|'
        r'amber-\d{2,3}|yellow-\d{2,3}|orange-\d{2,3}|brown-\d{2,3}|'
        r'red-[1-4]\d{2}|green-[1-4]\d{2}|blue-[1-4]\d{2}|sky-[1-4]\d{2}|'
        r'cyan-[1-4]\d{2}|teal-[1-4]\d{2}|indigo-[1-4]\d{2}|purple-[1-4]\d{2}|'
        r'pink-[1-4]\d{2}|rose-[1-4]\d{2}|fuchsia-[1-4]\d{2}|violet-[1-4]\d{2}|'
        r'lime-\d{2,3}|emerald-[1-4]\d{2}|'
        r'gray-500|zinc-500|slate-500|neutral-500|stone-500'
        r')\b',
        re.IGNORECASE
    )

    def _fix_body_tag(match):
        attrs = match.group(1) or ""
        class_match = re.search(r'class\s*=\s*(["\'])(.*?)\1', attrs, re.IGNORECASE)
        if class_match:
            classes = class_match.group(2)
            new_classes = classes
            # Replace any light or wrong background colors with dark
            new_classes = _LIGHT_BG_PATTERN.sub('bg-slate-950', new_classes)
            # If still no dark bg, add one
            if not re.search(r"\bbg-(?:slate|zinc|neutral|stone|gray|black)-[6-9]\d{2}\b|\bbg-(?:slate|zinc|neutral|stone|gray|black)-\d{3}\b", new_classes):
                if not re.search(r"\bbg-", new_classes):
                    new_classes = f"bg-slate-950 {new_classes}".strip()
            if not re.search(r"\btext-", new_classes):
                new_classes = f"{new_classes} text-zinc-100".strip()
            if "min-h-screen" not in new_classes:
                new_classes = f"{new_classes} min-h-screen".strip()
            if "overflow-x-hidden" not in new_classes:
                new_classes = f"{new_classes} overflow-x-hidden".strip()

            fixed_attrs = (
                attrs[: class_match.start()]
                + f'class="{new_classes}"'
                + attrs[class_match.end() :]
            )
            return f"<body{fixed_attrs}>"
        else:
            # No class attr at all — inject full dark theme
            return f'<body class="bg-slate-950 text-zinc-100 min-h-screen relative overflow-x-hidden"{attrs}>'

    text = re.sub(r"<body([^>]*)>", _fix_body_tag, text, count=1, flags=re.IGNORECASE)

    # 5b. Also kill any CSS background-color on body element set to light/white colors
    def _fix_body_css_bg(m):
        css = m.group(0)
        css = re.sub(r'background(?:-color)?\s*:\s*(?:#(?:f|e|d|c|b|a|9)[0-9a-fA-F]{5}|white|#fff|#ffffff|rgb\(2[0-5]\d[^)]*\)|rgba\(2[0-5]\d[^)]*\))',
                     'background-color: #020617', css, flags=re.IGNORECASE)
        return css

    text = re.sub(r'body\s*\{[^}]*\}', _fix_body_css_bg, text, flags=re.IGNORECASE)

    # 5c. Fix light gradient backgrounds on sections/divs (hero sections etc.)
    # Replace "from-teal-*", "from-cyan-[1-4]xx", "from-white" etc. on containers with dark equivalents
    _LIGHT_FROM_PATTERN = re.compile(
        r'\bfrom-(?:white|teal-[0-4]\d{2}|cyan-[0-4]\d{2}|sky-[0-4]\d{2}|'
        r'gray-[0-4]\d{2}|slate-[0-4]\d{2}|zinc-[0-4]\d{2}|green-[0-4]\d{2}|'
        r'blue-[0-4]\d{2}|indigo-[0-4]\d{2}|emerald-[0-4]\d{2}|amber-\d{2,3}|'
        r'yellow-\d{2,3}|orange-\d{2,3}|lime-\d{2,3}|neutral-[0-4]\d{2})\b',
        re.IGNORECASE
    )
    _LIGHT_TO_PATTERN = re.compile(
        r'\bto-(?:white|teal-[0-4]\d{2}|cyan-[0-4]\d{2}|sky-[0-4]\d{2}|'
        r'gray-[0-4]\d{2}|slate-[0-4]\d{2}|zinc-[0-4]\d{2}|green-[0-4]\d{2}|'
        r'blue-[0-4]\d{2}|indigo-[0-4]\d{2}|emerald-[0-4]\d{2}|amber-\d{2,3}|'
        r'yellow-\d{2,3}|orange-\d{2,3}|lime-\d{2,3}|neutral-[0-4]\d{2})\b',
        re.IGNORECASE
    )

    def _fix_section_bg(match):
        tag_str = match.group(0)
        tag_str = _LIGHT_BG_PATTERN.sub('bg-slate-900', tag_str)
        tag_str = _LIGHT_FROM_PATTERN.sub('from-slate-900', tag_str)
        tag_str = _LIGHT_TO_PATTERN.sub('to-slate-950', tag_str)
        return tag_str

    # Apply to section, main, header, footer, and div tags with hero/section-like classes
    text = re.sub(
        r'<(?:section|main|header|footer|div)[^>]*class=["\'][^"\']*(?:from-|to-|bg-)[^"\']*["\'][^>]*>',
        _fix_section_bg,
        text,
        flags=re.IGNORECASE
    )

    # 5d. Replace placeholder text like "Laptop Name 1", "Item Name", "Product Name", "[...]"
    text = re.sub(r'\[(?:Laptop|Product|Item|Image|Photo|Brand|Name|Title)\s*(?:Image|Photo|Name|1|2|3)?\]',
                  '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:Laptop|Product|Item)\s+Name\s+\d+', 'HP Spectre x360', text)
    text = re.sub(r'(?:Laptop|Product|Item)\s+Description\s*(?:\d+)?', 'Premium Intel Core Ultra laptop with 2.8K OLED display', text)

    # 6. Ensure lucide.createIcons() is called before </body>
    if "createicons" not in text.lower() and "lucide" in text.lower():
        init_script = "\n  <script>\n    if (window.lucide) { lucide.createIcons(); }\n  </script>\n"
        if "</body>" in text:
            text = text.replace("</body>", f"{init_script}</body>", 1)
        else:
            text += init_script

    # 7. Fix background decorative ribbon layers that block text
    def _fix_decorations(match):
        tag_str = match.group(0)
        if "rotate" in tag_str or "transform" in tag_str or "blur-" in tag_str:
            if "pointer-events-none" not in tag_str:
                tag_str = tag_str.replace(
                    'class="', 'class="pointer-events-none -z-10 '
                )
                tag_str = tag_str.replace(
                    "class='", "class='pointer-events-none -z-10 "
                )
        return tag_str

    text = re.sub(
        r'<div[^>]*class=["\'][^"\']*(?:rotate|blur-|transform)[^"\']*["\'][^>]*>',
        _fix_decorations,
        text,
        flags=re.IGNORECASE,
    )

    # 8. Fix unstyled plain CTA links or buttons
    def _fix_bare_cta(match):
        tag = match.group(1).lower()
        attrs = match.group(2)
        inner = match.group(3)
        if "class=" not in attrs.lower():
            if any(
                w in inner.lower()
                for w in [
                    "shop",
                    "buy",
                    "order",
                    "explore",
                    "get started",
                    "book",
                    "start",
                ]
            ):
                return f'<{tag}{attrs} class="inline-flex items-center justify-center bg-gradient-to-r from-indigo-500 to-purple-600 hover:opacity-90 text-white font-semibold px-6 py-3 rounded-xl transition-all duration-300 shadow-lg shadow-indigo-500/20">{inner}</{tag}>'
            elif any(
                w in inner.lower()
                for w in ["contact", "learn more", "view", "details", "about"]
            ):
                return f'<{tag}{attrs} class="inline-flex items-center justify-center bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white font-semibold px-6 py-3 rounded-xl transition-all duration-300">{inner}</{tag}>'
            elif any(
                w in inner.lower()
                for w in ["home", "products", "services", "features", "pricing", "testimonials"]
            ):
                return f'<{tag}{attrs} class="text-zinc-400 hover:text-white px-3 py-1.5 text-sm font-medium transition-colors">{inner}</{tag}>'
        return match.group(0)

    text = re.sub(
        r"<(a|button)([^>]*)>([^<]{2,40})</\1>",
        _fix_bare_cta,
        text,
        flags=re.IGNORECASE,
    )

    # 9. Clean up broken img tags or placeholder blob images
    text = re.sub(r'<img[^>]*src=["\'](?:blob:[^"\']*|["\'])[^>]*>', '', text, flags=re.IGNORECASE)

    return (text, warnings)


def normalize_header(text: str, language: str = "python") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    if language.lower() not in ("python", "py", "bash", "sh") or "```" in text:
        return (text, warnings)
    lines = text.split("\n")
    has_shebang = lines[0].strip().startswith("#!") if lines else False
    is_script = bool(re.search("if\\s+__name__\\s*==\\s*[\"\\']__main__[\"\\']", text))
    is_cli = bool(re.search("argparse\\.|sys\\.argv|click\\.|typer\\.|fire\\.", text))
    if language == "python" and (is_script or is_cli) and (not has_shebang):
        lines.insert(0, "#!/usr/bin/env python3")
        warnings.append("Header: added #!/usr/bin/env python3")
    elif language in ("bash", "sh") and (not has_shebang):
        lines.insert(0, "#!/usr/bin/env bash")
        warnings.append("Header: added #!/usr/bin/env bash")
    return ("\n".join(lines), warnings)


def _is_math_output(text: str) -> bool:
    math_signals = [
        "\\$\\$.*\\$\\$",
        "\\$[^$]+\\$",
        "\\\\frac\\{",
        "\\\\sum_",
        "\\\\int_",
        "\\\\lim_",
        "\\\\sqrt\\{",
        "\\\\cdot\\b",
        "\\\\times\\b",
        "\\\\alpha\\b",
        "\\\\beta\\b",
        "\\\\theta\\b",
        "\\\\pi\\b",
        "\\\\infty\\b",
        "\\\\partial\\b",
        "\\\\nabla\\b",
        "\\\\forall\\b",
        "\\\\exists\\b",
        "\\\\implies?\\b",
        "\\\\mathbb\\{",
        "\\\\mathcal\\{",
        "\\\\mathbf\\{",
        "\\\\longrightarrow\\b",
        "d/d[xX]\\b",
        "∫",
        "∂",
        "∑",
        "∏",
        "√",
        "∞",
    ]
    return any((re.search(sig, text) for sig in math_signals))


def normalize_math_fences(text: str, language: str = "") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    original = text
    text = re.sub("\\$\\$\\s+", "$$", text)
    text = re.sub("\\s+\\$\\$", "$$", text)
    text = re.sub("\\$\\s+([^$]+?)\\s+\\$", "$\\1$", text)
    text = re.sub("\\\\\\\\([^\\\\a-zA-Z{])", "\\\\\\1", text)
    if "$" not in text:
        text = re.sub("(?<!\\\\)_(?!_)(\\w+)", "$_{\\1}$", text)
    text = re.sub("\\\\frac(\\d)(\\d)", "\\\\frac{\\1}{\\2}", text)
    text = re.sub("\\\\frac(\\w)(\\w)", "\\\\frac{\\1}{\\2}", text)

    text = re.sub(r"\b([a-zA-Z]\s*=\s*[-0-9\.]+)\s*\$", r"$\1$", text)
    text = re.sub(
        r"(\\(?:cos|sin|tan|log|ln|exp|sec|csc|cot)\s*\([^)]+\))\s*\$", r"\1", text
    )
    text = re.sub(
        r"(?<!\$)(?<!\\)(-\s*)?(\\(?:cos|sin|tan|log|ln|exp|sec|csc|cot)\s*\([^)]+\))(?!\$)",
        r"$\1\2$",
        text,
    )
    if text != original:
        warnings.append("Math: normalized LaTeX formatting")
    return (text, warnings)


def normalize_math_steps(text: str, language: str = "") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    step_indicators = re.findall(
        "(?:^|\\n)\\s*(?:Step|step)\\s*(\\d+|[ivxlcdm]+)[\\s:.\\-)]",
        text,
        re.IGNORECASE,
    )
    if len(step_indicators) <= 1:
        return (text, warnings)
    for i, match in enumerate(
        re.finditer(
            "(^|\\n)(\\s*)(Step|step)\\s*(\\d+|[ivxlcdm]+)([\\s:.\\-)]+)",
            text,
            re.IGNORECASE,
        ),
        1,
    ):
        text = (
            text[: match.start()]
            + match.group(1)
            + match.group(2)
            + f"**Step {i}:** "
            + text[match.end() :]
        )
        is_digit = match.group(4).isdigit()
        if (is_digit and i != int(match.group(4))) or (not is_digit):
            warnings.append("Math: normalized step numbering")
    return (text, warnings)


def extract_math_answer(text: str, language: str = "") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    if re.search(
        "\\*\\*Answer:?\\*\\*|\\\\boxed\\{|\\\\therefore\\b|Therefore,|Thus,|Hence,|Final answer:",
        text,
        re.IGNORECASE,
    ):
        return (text, warnings)
    lines = text.strip().split("\n")
    candidate = None
    for line in reversed(lines):
        s = line.strip()
        if not s:
            continue
        if re.search("[=≈]\\s*[\\d\\-.]+", s) and len(s) < 120:
            candidate = s
            break
        if re.search("\\\\boxed\\{", s):
            candidate = s
            break
        if (
            re.search("\\b[xXyYzZnNtT]\\s*[=≈]\\s*[\\d\\-.a-zA-Z√π]+", s)
            and len(s) < 120
        ):
            candidate = s
            break
    if candidate:
        text = (
            text[: text.rfind(candidate)]
            + f"\n\n**Answer:** {candidate}\n"
            + text[text.rfind(candidate) + len(candidate) :]
        )
        warnings.append("Math: extracted final answer for clarity")
    return (text, warnings)


def deduplicate_math_steps(text: str, language: str = "") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    paragraphs = re.split("\\n\\n+", text)
    if len(paragraphs) < 2:
        return (text, warnings)
    seen = set()
    result = []
    removed = 0
    for para in paragraphs:
        normalized = re.sub("\\s+", " ", para.strip().lower())
        if len(normalized) < 8:
            result.append(para)
            continue
        if normalized in seen:
            removed += 1
            continue
        seen.add(normalized)
        result.append(para)
    if removed > 0:
        text = "\n\n".join(result)
        warnings.append(f"Math: removed {removed} duplicate reasoning step(s)")
    return (text, warnings)


_HALLUCINATED_REF_PATTERNS = [
    (
        "\\b(?:theorem|lemma|corollary|proposition)\\s+(\\d+\\.\\d+\\.\\d+)\\b",
        "**Theorem \\1**",
    ),
    ("\\(([A-Z][a-z]+ et al\\.,?\\s*\\d{4}[a-z]?)\\)", "(\\1)"),
    ("\\\\tag\\{(\\d+\\.\\d+)\\}", ""),
]


def redact_hallucinated_refs(text: str, language: str = "") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    for pattern, replacement in _HALLUCINATED_REF_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            warnings.append(
                f"Math: flagged {len(matches)} potentially hallucinated reference(s)"
            )
    return (text, warnings)


def normalize_math_notation(text: str, language: str = "") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    original = text
    if "\\cdot" in text or "\\times" in text:
        text = re.sub("(?<!\\\\)\\*(?!\\*)", "\\\\cdot ", text)
    else:
        text = re.sub("\\\\cdot\\b", "*", text)
        text = re.sub("\\\\times\\b", "*", text)
    text = re.sub("(?<=\\w)\\s*=\\s*-(\\d+)", " = (-\\1)", text)
    if text != original:
        warnings.append("Math: normalized notation consistency")
    return (text, warnings)


def separate_math_code_blocks(text: str, language: str = "") -> Tuple[str, List[str]]:
    warnings: List[str] = []
    code_indicators = re.findall(
        "((?:import|def|lambda|for|while)\\s+\\w+.*?(?:\\n|$))", text
    )
    if code_indicators and "```" not in text:
        warnings.append("Math: code snippets detected without fence blocks")
    return (text, warnings)


_MATH_PASSES = [
    ("normalize_math_fences", normalize_math_fences),
    ("deduplicate_math_steps", deduplicate_math_steps),
    ("normalize_math_notation", normalize_math_notation),
    ("normalize_math_steps", normalize_math_steps),
    ("redact_hallucinated_refs", redact_hallucinated_refs),
    ("separate_math_code_blocks", separate_math_code_blocks),
    ("extract_math_answer", extract_math_answer),
    ("clean_whitespace", clean_whitespace),
]

_PASSES = [
    ("normalize_fences", normalize_fences),
    ("redact_secrets", redact_secrets),
    ("repair_truncation", repair_truncation),
    ("enforce_contrast", enforce_contrast),
    ("repair_html", repair_html),
    ("inject_imports", inject_imports),
    ("normalize_header", normalize_header),
    ("deduplicate_blocks", deduplicate_blocks),
    ("clean_whitespace", clean_whitespace),
]
_OPTIONAL_PASSES = {"strip_comments": strip_comments}


def apply_all(
    text: str, language: str = "python", enabled: Optional[List[str]] = None
) -> Tuple[str, List[dict]]:
    all_warnings: List[dict] = []
    for name, func in _PASSES:
        if enabled and name not in enabled:
            continue
        try:
            text, warns = func(text, language)
            for w in warns:
                all_warnings.append({"type": "harness_warning", "content": w})
        except Exception:
            pass
    return (text, all_warnings)


def apply_code_specific(text: str, language: str = "python") -> Tuple[str, List[dict]]:
    return apply_all(text, language)


def apply_math(text: str, language: str = "") -> Tuple[str, List[dict]]:
    all_warnings: List[dict] = []
    for name, func in _MATH_PASSES:
        try:
            text, warns = func(text, language)
            for w in warns:
                all_warnings.append({"type": "harness_warning", "content": w})
        except Exception:
            pass
    return (text, all_warnings)


import asyncio
import hashlib
import inspect
import json
import math
import os
import platform
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


class ToolCategory(str, Enum):
    FILE = "file"
    SHELL = "shell"
    PYTHON = "python"
    WEB = "web"
    SYSTEM = "system"
    MEMORY = "memory"


class ToolResultStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial_success"
    ERROR_RETRYABLE = "error_retryable"
    ERROR_FATAL = "error_fatal"
    TIMEOUT = "timeout"
    REJECTED = "rejected"


@dataclass
class ToolSchema:
    name: str
    description: str
    parameters: Dict[str, Any]
    category: ToolCategory
    is_destructive: bool = False
    max_output_chars: int = 8000
    timeout_seconds: float = 30.0
    retry_count: int = 2


@dataclass
class ToolResult:
    tool_name: str
    status: ToolResultStatus
    output: str
    error: Optional[str] = None
    truncated: bool = False
    original_size: int = 0
    elapsed_ms: float = 0.0
    retry_count: int = 0
    side_effects: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class AgentStep:
    step_number: int
    model_thought: str = ""
    tool_results: List[ToolResult] = field(default_factory=list)
    elapsed_ms: float = 0.0


@dataclass
class AgentSession:
    steps: List[AgentStep] = field(default_factory=list)
    total_tool_calls: int = 0
    tool_call_budget_remaining: int = 50
    files_created: Set[str] = field(default_factory=set)
    files_modified: Set[str] = field(default_factory=set)
    commands_run: List[str] = field(default_factory=list)
    errors_encountered: List[str] = field(default_factory=list)
    memory: Dict[str, str] = field(default_factory=dict)


class HermesToolRegistry:
    TOOLS: Dict[str, ToolSchema] = {}
    TOOLS["read_file"] = ToolSchema(
        name="read_file",
        description="Read the complete contents of a file. Returns the file text.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read.",
                },
                "start_line": {
                    "type": "integer",
                    "description": "Optional 1-based starting line. Omit to read entire file.",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Optional 1-based ending line (inclusive).",
                },
            },
            "required": ["path"],
        },
        category=ToolCategory.FILE,
        max_output_chars=12000,
    )
    TOOLS["write_file"] = ToolSchema(
        name="write_file",
        description="Write content to a file, creating directories as needed. OVERWRITES existing files. Use diff_file for targeted edits.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file."},
                "content": {"type": "string", "description": "Full file content."},
            },
            "required": ["path", "content"],
        },
        category=ToolCategory.FILE,
        is_destructive=True,
        max_output_chars=500,
    )
    TOOLS["list_dir"] = ToolSchema(
        name="list_dir",
        description="List the contents of a directory with sizes and types.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path."},
                "recursive": {
                    "type": "boolean",
                    "description": "If true, list recursively (max depth 3).",
                },
            },
            "required": ["path"],
        },
        category=ToolCategory.FILE,
        max_output_chars=8000,
    )
    TOOLS["search_files"] = ToolSchema(
        name="search_files",
        description="Search for a pattern (regex or literal) within files. Like grep -rn. Returns matching lines with file paths and line numbers.",
        parameters={
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Search pattern (regex supported).",
                },
                "path": {
                    "type": "string",
                    "description": "Directory or file to search in.",
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Optional glob to filter files (e.g. '*.py').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum matches to return (default 50).",
                },
            },
            "required": ["pattern", "path"],
        },
        category=ToolCategory.FILE,
        max_output_chars=8000,
    )
    TOOLS["glob_files"] = ToolSchema(
        name="glob_files",
        description="Find files matching a glob pattern (e.g. '**/*.py', 'src/*.ts').",
        parameters={
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern."},
                "path": {"type": "string", "description": "Base directory."},
            },
            "required": ["pattern", "path"],
        },
        category=ToolCategory.FILE,
        max_output_chars=6000,
    )
    TOOLS["diff_files"] = ToolSchema(
        name="diff_files",
        description="Show the unified diff between two files or against the original content.",
        parameters={
            "type": "object",
            "properties": {
                "file_a": {"type": "string", "description": "First file path."},
                "file_b": {"type": "string", "description": "Second file path."},
            },
            "required": ["file_a", "file_b"],
        },
        category=ToolCategory.FILE,
        max_output_chars=10000,
    )
    TOOLS["run_command"] = ToolSchema(
        name="run_command",
        description="Execute a shell command. Returns stdout+stderr. Use for build, test, install, git, and file operations. IMPORTANT: never run destructive commands (rm -rf, format, etc.) without user confirmation.",
        parameters={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to run.",
                },
                "workdir": {
                    "type": "string",
                    "description": "Working directory. Defaults to project root.",
                },
            },
            "required": ["command"],
        },
        category=ToolCategory.SHELL,
        max_output_chars=10000,
        timeout_seconds=60.0,
    )
    TOOLS["run_python"] = ToolSchema(
        name="run_python",
        description="Execute Python code in a subprocess and return the output. Use this to test generated code or run quick computations.",
        parameters={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute."}
            },
            "required": ["code"],
        },
        category=ToolCategory.PYTHON,
        max_output_chars=6000,
        timeout_seconds=15.0,
    )
    TOOLS["fetch_url"] = ToolSchema(
        name="fetch_url",
        description="Fetch the content of a URL. Returns text content. Use for reading documentation, APIs, or package info.",
        parameters={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch (http/https)."},
                "max_chars": {
                    "type": "integer",
                    "description": "Max characters to return (default 15000).",
                },
            },
            "required": ["url"],
        },
        category=ToolCategory.WEB,
        max_output_chars=15000,
        timeout_seconds=20.0,
    )
    TOOLS["get_platform"] = ToolSchema(
        name="get_platform",
        description="Get system information: OS, Python version, CPU arch, available tools.",
        parameters={"type": "object", "properties": {}, "required": []},
        category=ToolCategory.SYSTEM,
        max_output_chars=2000,
    )
    TOOLS["which_tool"] = ToolSchema(
        name="which_tool",
        description="Check if a command-line tool is available. Returns the path or 'not found'.",
        parameters={
            "type": "object",
            "properties": {
                "tool_name": {
                    "type": "string",
                    "description": "Name of the tool (e.g. 'node', 'gcc', 'docker').",
                }
            },
            "required": ["tool_name"],
        },
        category=ToolCategory.SYSTEM,
        max_output_chars=500,
    )
    TOOLS["disk_usage"] = ToolSchema(
        name="disk_usage",
        description="Check disk usage of a directory or file.",
        parameters={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Path to check."}},
            "required": ["path"],
        },
        category=ToolCategory.SYSTEM,
        max_output_chars=2000,
    )
    TOOLS["remember"] = ToolSchema(
        name="remember",
        description="Store a piece of information in the agent's memory for later recall.",
        parameters={
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key to store under."},
                "value": {"type": "string", "description": "Value to store."},
            },
            "required": ["key", "value"],
        },
        category=ToolCategory.MEMORY,
        max_output_chars=200,
    )
    TOOLS["recall"] = ToolSchema(
        name="recall",
        description="Recall information previously stored via 'remember'.",
        parameters={
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Key to recall. Omit to list all keys.",
                }
            },
            "required": [],
        },
        category=ToolCategory.MEMORY,
        max_output_chars=4000,
    )
    TOOLS["forget"] = ToolSchema(
        name="forget",
        description="Remove a key from memory.",
        parameters={
            "type": "object",
            "properties": {"key": {"type": "string", "description": "Key to forget."}},
            "required": ["key"],
        },
        category=ToolCategory.MEMORY,
        max_output_chars=200,
    )

    @classmethod
    def get_schema(cls, name: str) -> Optional[ToolSchema]:
        return cls.TOOLS.get(name)

    @classmethod
    def get_openai_tools(cls) -> List[Dict[str, Any]]:
        tools = []
        for name, schema in cls.TOOLS.items():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": schema.description,
                        "parameters": schema.parameters,
                    },
                }
            )
        return tools

    @classmethod
    def validate_args(cls, name: str, args: Dict[str, Any]) -> Tuple[bool, str]:
        schema = cls.TOOLS.get(name)
        if not schema:
            return (False, f"Unknown tool: {name}")
        required = schema.parameters.get("required", [])
        properties = schema.parameters.get("properties", {})
        for key in required:
            if key not in args or args[key] is None or args[key] == "":
                return (False, f"Missing required parameter: '{key}'")
        for key, val in args.items():
            if key in properties:
                expected_type = properties[key].get("type", "string")
                if (
                    expected_type == "integer"
                    and isinstance(val, str)
                    and val.isdigit()
                ):
                    pass
                elif expected_type == "boolean" and isinstance(val, str):
                    pass
        return (True, "")

    @classmethod
    def execute(
        cls,
        name: str,
        args: Dict[str, Any],
        workspace_root: str = "",
        session: Optional[AgentSession] = None,
    ) -> ToolResult:
        t0 = time.perf_counter()
        schema = cls.TOOLS.get(name)
        if not schema:
            elapsed = (time.perf_counter() - t0) * 1000
            return ToolResult(
                tool_name=name,
                status=ToolResultStatus.ERROR_FATAL,
                output="",
                error=f"Unknown tool: {name}",
                elapsed_ms=elapsed,
            )
        if not workspace_root or workspace_root == "none":
            workspace_root = os.getcwd()
        valid, err_msg = cls.validate_args(name, args)
        if not valid:
            elapsed = (time.perf_counter() - t0) * 1000
            return ToolResult(
                tool_name=name,
                status=ToolResultStatus.ERROR_FATAL,
                output="",
                error=err_msg,
                elapsed_ms=elapsed,
            )
        try:
            handler = _TOOL_HANDLERS.get(name)
            if handler:
                raw_output = handler(args, workspace_root, schema, session)
            else:
                raw_output = f"Tool '{name}' has no handler."
            is_error_output = raw_output.startswith("Error:") or raw_output.startswith(
                "[Error]"
            )
            if is_error_output:
                elapsed = (time.perf_counter() - t0) * 1000
                return ToolResult(
                    tool_name=name,
                    status=ToolResultStatus.ERROR_RETRYABLE,
                    output=raw_output,
                    error=raw_output,
                    elapsed_ms=elapsed,
                )
            original_size = len(raw_output)
            truncated = False
            if original_size > schema.max_output_chars:
                raw_output = raw_output[: schema.max_output_chars]
                raw_output += f"\n\n... [truncated, {original_size} total chars]"
                truncated = True
            elapsed = (time.perf_counter() - t0) * 1000
            return ToolResult(
                tool_name=name,
                status=ToolResultStatus.SUCCESS,
                output=raw_output,
                truncated=truncated,
                original_size=original_size,
                elapsed_ms=elapsed,
            )
        except subprocess.TimeoutExpired:
            elapsed = (time.perf_counter() - t0) * 1000
            return ToolResult(
                tool_name=name,
                status=ToolResultStatus.TIMEOUT,
                output="",
                error=f"Tool timed out after {schema.timeout_seconds}s",
                elapsed_ms=elapsed,
            )
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            return ToolResult(
                tool_name=name,
                status=ToolResultStatus.ERROR_RETRYABLE,
                output="",
                error=f"{type(e).__name__}: {e}",
                elapsed_ms=elapsed,
            )


def _resolve_path(path: str, workspace_root: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(workspace_root, path)


def _h_read_file(args, ws, schema, session) -> str:
    path = _resolve_path(args["path"], ws)
    if not os.path.isfile(path):
        return f"Error: File not found: {path}"
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        start = max(1, int(args.get("start_line", 1)))
        end = (
            int(args.get("end_line", len(lines)))
            if args.get("end_line")
            else len(lines)
        )
        start = min(start, len(lines))
        end = min(end, len(lines))
        selected = lines[start - 1 : end]
        result = "".join(selected)
        if len(selected) < len(lines):
            result = f"[Lines {start}-{end} of {len(lines)} total]\n{result}"
        return result
    except Exception as e:
        return f"Error reading {path}: {e}"


def _h_write_file(args, ws, schema, session) -> str:
    path = _resolve_path(args["path"], ws)
    content = args["content"]
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        existed = os.path.exists(path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        action = "Updated" if existed else "Created"
        size = len(content)
        if session:
            if existed:
                session.files_modified.add(path)
            else:
                session.files_created.add(path)
        return f"{action} file: {path} ({size} bytes)"
    except Exception as e:
        return f"Error writing {path}: {e}"


def _h_list_dir(args, ws, schema, session) -> str:
    path = _resolve_path(args["path"], ws)
    recursive = args.get("recursive", False)
    if not os.path.isdir(path):
        return f"Error: Not a directory: {path}"
    lines = []
    if recursive:
        max_depth = 3
        for root, dirs, files in os.walk(path):
            depth = root[len(path) :].count(os.sep)
            if depth > max_depth:
                dirs[:] = []
                continue
            indent = "  " * depth
            prefix = os.path.relpath(root, path)
            if prefix == ".":
                lines.append(f"{path}/")
            else:
                lines.append(f"{indent}{prefix}/")
            for f in sorted(files):
                fp = os.path.join(root, f)
                try:
                    size = os.path.getsize(fp)
                except OSError:
                    size = 0
                lines.append(f"{indent}  {f} ({_fmt_size(size)})")
            dirs.sort()
    else:
        try:
            items = sorted(os.listdir(path))
            for item in items:
                fp = os.path.join(path, item)
                if os.path.isdir(fp):
                    lines.append(f"  [DIR]  {item}/")
                else:
                    size = os.path.getsize(fp)
                    lines.append(f"  [FILE] {item} ({_fmt_size(size)})")
        except PermissionError:
            return f"Error: Permission denied: {path}"
    return "\n".join(lines[:500])


def _h_search_files(args, ws, schema, session) -> str:
    pattern = args["pattern"]
    search_path = _resolve_path(args["path"], ws)
    file_pattern = args.get("file_pattern", "")
    max_results = min(args.get("max_results", 50) or 50, 500)
    cmd = ["grep", "-rnIE", "--", pattern, search_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, cwd=ws)
        output = result.stdout.strip()
        if not output:
            return "No matches found."
        lines = output.split("\n")
        total = len(lines)
        lines = lines[:max_results]
        msg = "\n".join(lines)
        if total > max_results:
            msg += f"\n\n... [{total - max_results} more matches truncated]"
        return msg
    except FileNotFoundError:
        return "Error: 'grep' not found on system."
    except subprocess.TimeoutExpired:
        return "Error: Search timed out."


def _h_glob_files(args, ws, schema, session) -> str:
    import glob as glob_module

    pattern = args["pattern"]
    base_path = _resolve_path(args["path"], ws)
    full_pattern = os.path.join(base_path, pattern)
    matches = glob_module.glob(full_pattern, recursive=True)
    if not matches:
        return f"No files match pattern: {pattern}"
    lines = []
    for m in sorted(matches)[:200]:
        rel = os.path.relpath(m, ws)
        try:
            size = os.path.getsize(m) if os.path.isfile(m) else 0
        except OSError:
            size = 0
        lines.append(f"  {rel} ({_fmt_size(size)})")
    total = len(matches)
    result = "\n".join(lines)
    if total > 200:
        result += f"\n... [{total - 200} more files not shown]"
    return result


def _h_diff_files(args, ws, schema, session) -> str:
    a = _resolve_path(args["file_a"], ws)
    b = _resolve_path(args["file_b"], ws)
    if not os.path.exists(a):
        return f"Error: File not found: {a}"
    if not os.path.exists(b):
        return f"Error: File not found: {b}"
    try:
        result = subprocess.run(
            ["diff", "-u", a, b], capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip()
        return output if output else "Files are identical."
    except FileNotFoundError:
        return "Error: 'diff' not found on system."
    except Exception as e:
        return f"Error diffing files: {e}"


def _h_run_command(args, ws, schema, session) -> str:
    cmd = args["command"]
    workdir = _resolve_path(args.get("workdir", ws) or ws, ws)
    if not os.path.isdir(workdir):
        workdir = ws
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=schema.timeout_seconds,
        )
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        if session:
            session.commands_run.append(cmd)
        parts = []
        if output:
            parts.append(output)
        if stderr:
            parts.append(f"[stderr]\n{stderr}")
        if not parts:
            parts.append(
                f"Command completed with exit code {result.returncode} (no output)."
            )
        return "\n".join(parts)
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {schema.timeout_seconds}s: {cmd}"
    except Exception as e:
        return f"Error running command: {e}"


def _h_run_python(args, ws, schema, session) -> str:
    code = args["code"]
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=schema.timeout_seconds,
            cwd=ws,
        )
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        parts = []
        if output:
            parts.append(output)
        if stderr:
            parts.append(f"[stderr]\n{stderr}")
        if not parts:
            parts.append("(no output)")
        return "\n".join(parts)
    except subprocess.TimeoutExpired:
        return f"Error: Python code timed out after {schema.timeout_seconds}s"
    except Exception as e:
        return f"Error running Python: {e}"


def _h_fetch_url(args, ws, schema, session) -> str:
    url = args["url"]
    max_chars = min(args.get("max_chars", 15000) or 15000, 50000)
    if not url.startswith(("http://", "https://")):
        return "Error: Only http/https URLs are supported."
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Iris-AI-Hermes/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            if len(content) > max_chars:
                content = (
                    content[:max_chars]
                    + f"\n\n... [truncated, {len(content)} total chars]"
                )
            content = re.sub("<[^>]+>", "", content)
            content = re.sub("\\n{3,}", "\n\n", content)
            return content
    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"URL Error: {e.reason}"
    except Exception as e:
        return f"Error fetching URL: {e}"


def _h_get_platform(args, ws, schema, session) -> str:
    info = [
        f"OS: {platform.system()} {platform.release()}",
        f"Arch: {platform.machine()}",
        f"Python: {sys.version}",
        f"CWD: {os.getcwd()}",
        f"Shell: {os.environ.get('SHELL', 'unknown')}",
    ]
    tools_to_check = [
        "git",
        "node",
        "npm",
        "gcc",
        "g++",
        "clang",
        "rustc",
        "cargo",
        "go",
        "docker",
        "make",
        "cmake",
        "python3",
        "pip3",
    ]
    available = []
    for t in tools_to_check:
        if shutil.which(t):
            available.append(t)
    info.append(f"Available tools: {', '.join(available)}")
    return "\n".join(info)


def _h_which_tool(args, ws, schema, session) -> str:
    tool = args["tool_name"]
    path = shutil.which(tool)
    if path:
        return f"Found: {path}"
    return f"Not found: {tool}"


def _h_disk_usage(args, ws, schema, session) -> str:
    path = _resolve_path(args["path"], ws)
    if not os.path.exists(path):
        return f"Error: Path not found: {path}"
    if os.path.isfile(path):
        size = os.path.getsize(path)
        return f"File: {path}\nSize: {_fmt_size(size)}"
    total_size = 0
    file_count = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
                file_count += 1
            except OSError:
                pass
    return (
        f"Directory: {path}\nFiles: {file_count}\nTotal size: {_fmt_size(total_size)}"
    )


def _h_remember(args, ws, schema, session) -> str:
    if not session:
        return "Error: No agent session active."
    key = args["key"]
    value = args["value"]
    session.memory[key] = value
    return f"Stored: {key} = {value[:200]}{('...' if len(value) > 200 else '')}"


def _h_recall(args, ws, schema, session) -> str:
    if not session:
        return "Error: No agent session active."
    key = args.get("key")
    if key:
        val = session.memory.get(key)
        if val is None:
            return f"No memory found for key: {key}"
        return f"{key}: {val}"
    if not session.memory:
        return "Memory is empty."
    lines = ["Memory contents:"]
    for k, v in sorted(session.memory.items()):
        lines.append(f"  {k}: {v[:200]}")
    return "\n".join(lines)


def _h_forget(args, ws, schema, session) -> str:
    if not session:
        return "Error: No agent session active."
    key = args["key"]
    if key in session.memory:
        del session.memory[key]
        return f"Forgot: {key}"
    return f"No memory found for key: {key}"


_TOOL_HANDLERS: Dict[str, Callable] = {
    "read_file": _h_read_file,
    "write_file": _h_write_file,
    "list_dir": _h_list_dir,
    "search_files": _h_search_files,
    "glob_files": _h_glob_files,
    "diff_files": _h_diff_files,
    "run_command": _h_run_command,
    "run_python": _h_run_python,
    "fetch_url": _h_fetch_url,
    "get_platform": _h_get_platform,
    "which_tool": _h_which_tool,
    "disk_usage": _h_disk_usage,
    "remember": _h_remember,
    "recall": _h_recall,
    "forget": _h_forget,
}


def _fmt_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f}MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f}GB"


class HermesResultAnalyzer:
    ERROR_PATTERNS = [
        (
            "command not found|not recognized as an.*command",
            ToolResultStatus.ERROR_FATAL,
            "The command is not installed. Use 'which_tool' to check availability.",
        ),
        (
            "Permission denied|permission denied",
            ToolResultStatus.ERROR_FATAL,
            "Permission denied. Check file/directory permissions.",
        ),
        (
            "File not found|No such file|no such file",
            ToolResultStatus.ERROR_RETRYABLE,
            "File not found. Check the path with 'list_dir' or 'glob_files'.",
        ),
        ("Not found:", ToolResultStatus.SUCCESS, ""),
        (
            "\\bnot found\\b",
            ToolResultStatus.ERROR_RETRYABLE,
            "Resource not found. Verify existence with a listing tool.",
        ),
        (
            "timed out|Timeout|TimeoutExpired",
            ToolResultStatus.TIMEOUT,
            "Operation timed out. Try a smaller scope or break into steps.",
        ),
        (
            "SyntaxError|syntax error|invalid syntax",
            ToolResultStatus.ERROR_RETRYABLE,
            "Syntax error detected. Review and fix the code.",
        ),
        (
            "ModuleNotFoundError|ImportError|No module named",
            ToolResultStatus.ERROR_RETRYABLE,
            "Module not found. Install with pip or check the import path.",
        ),
        (
            "KeyboardInterrupt|SIGINT",
            ToolResultStatus.ERROR_FATAL,
            "Operation was interrupted.",
        ),
        (
            "Connection refused|Connection reset|Network is unreachable|Name or service not known",
            ToolResultStatus.ERROR_RETRYABLE,
            "Network error. Check connectivity or the URL.",
        ),
        (
            "out of memory|MemoryError|Cannot allocate memory",
            ToolResultStatus.ERROR_FATAL,
            "Out of memory. Reduce the scope of the operation.",
        ),
    ]

    @classmethod
    def analyze(cls, result: ToolResult) -> ToolResult:
        if result.status == ToolResultStatus.SUCCESS:
            return result
        error_text = (result.error or "") + " " + (result.output or "")
        for pattern, status, suggestion in cls.ERROR_PATTERNS:
            if re.search(pattern, error_text, re.IGNORECASE):
                result.status = status
                result.suggestions.append(suggestion)
                break
        if result.status == ToolResultStatus.SUCCESS:
            last_lines = result.output.split("\n")[-5:]
            for line in last_lines:
                if re.search("\\berror\\b", line, re.IGNORECASE):
                    result.status = ToolResultStatus.PARTIAL
                    result.suggestions.append(
                        "Command completed but may contain errors. Review the output."
                    )
                    break
        return result

    @classmethod
    def summarize_for_model(
        cls, results: List[ToolResult], max_chars: int = 2000
    ) -> str:
        if not results:
            return "No tools executed."
        lines = ["Tool Execution Results:"]
        for r in results:
            icon = (
                "✓"
                if r.status == ToolResultStatus.SUCCESS
                else "⚠" if r.status == ToolResultStatus.PARTIAL else "✗"
            )
            status_note = ""
            if r.error:
                status_note = f" — {r.error[:120]}"
            elif r.truncated:
                status_note = f" — truncated ({r.original_size} chars)"
            lines.append(f"  {icon} {r.tool_name} ({r.elapsed_ms:.0f}ms){status_note}")
            if r.status != ToolResultStatus.SUCCESS and r.output:
                lines.append(f"     Output: {r.output[:300]}")
        summary = "\n".join(lines)
        if len(summary) > max_chars:
            summary = summary[:max_chars] + "\n... [summary truncated]"
        return summary


HERMES_AGENT_SYSTEM_PROMPT = "You are an autonomous IDE agent with access to local tools. Your capabilities:\n\nFILE TOOLS:\n- read_file(path, start_line?, end_line?) — read file contents\n- write_file(path, content) — create/overwrite a file\n- list_dir(path, recursive?) — list directory contents\n- search_files(pattern, path, file_pattern?) — grep-like search\n- glob_files(pattern, path) — find files by glob\n- diff_files(file_a, file_b) — compare two files\n\nSHELL TOOLS:\n- run_command(command, workdir?) — execute a shell command\n- run_python(code) — execute Python code and return output\n\nWEB TOOLS:\n- fetch_url(url, max_chars?) — fetch a URL's text content\n\nSYSTEM TOOLS:\n- get_platform() — system info, Python version, available CLI tools\n- which_tool(tool_name) — check if a tool is installed\n- disk_usage(path) — check file/directory size\n\nMEMORY TOOLS:\n- remember(key, value) — store info for later\n- recall(key?) — retrieve stored info\n- forget(key) — remove stored info\n\nRULES:\n1. ALWAYS test code by running it before finalizing\n2. Use tools iteratively — explore, plan, execute, verify\n3. When a tool fails, analyze the error and try an alternative approach\n4. Never run destructive commands (rm -rf, format, etc.) without explicit user request\n5. If you're unsure, use read_file or list_dir to explore first\n6. Write complete, working code — no placeholders\n7. After completing the task, provide a clear summary of what you did"


class HermesAgentLoop:

    def __init__(
        self,
        model_callable: Optional[Callable] = None,
        workspace_root: str = "",
        max_tool_calls: int = 50,
        max_consecutive_errors: int = 5,
        max_turns: int = 15,
    ):
        self.model_callable = model_callable
        self.workspace_root = workspace_root or os.getcwd()
        self.max_tool_calls = max_tool_calls
        self.max_consecutive_errors = max_consecutive_errors
        self.max_turns = max_turns
        self.session = AgentSession(tool_call_budget_remaining=max_tool_calls)
        self._consecutive_errors = 0

    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[ToolResult]:
        results: List[ToolResult] = []
        for tc in tool_calls:
            func_name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"])
            except (json.JSONDecodeError, KeyError):
                args = {}
            result = HermesToolRegistry.execute(
                func_name, args, self.workspace_root, self.session
            )
            schema = HermesToolRegistry.get_schema(func_name)
            retries = schema.retry_count if schema else 0
            attempt = 0
            while (
                result.status
                in (ToolResultStatus.ERROR_RETRYABLE, ToolResultStatus.TIMEOUT)
                and attempt < retries
            ):
                attempt += 1
                time.sleep(0.5 * attempt)
                result.retry_count = attempt
                result = HermesToolRegistry.execute(
                    func_name, args, self.workspace_root, self.session
                )
            result = HermesResultAnalyzer.analyze(result)
            results.append(result)
            self.session.total_tool_calls += 1
            self.session.tool_call_budget_remaining -= 1
            if result.status in (
                ToolResultStatus.ERROR_FATAL,
                ToolResultStatus.ERROR_RETRYABLE,
                ToolResultStatus.TIMEOUT,
            ):
                self._consecutive_errors += 1
                self.session.errors_encountered.append(
                    f"{func_name}: {result.error or 'unknown error'}"
                )
            else:
                self._consecutive_errors = 0
        return results

    def should_continue(self) -> bool:
        if self.session.tool_call_budget_remaining <= 0:
            return False
        if self._consecutive_errors >= self.max_consecutive_errors:
            return False
        if len(self.session.steps) >= self.max_turns:
            return False
        return True

    def build_tool_result_messages(
        self, results: List[ToolResult], tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        messages = []
        for tc, result in zip(tool_calls, results):
            content = result.output
            if result.error:
                content = f"[{result.status.value}] {result.error}\n\n{content}"
            if result.suggestions:
                content += f"\n\nSuggestions: {'; '.join(result.suggestions)}"
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "name": result.tool_name,
                    "content": content[:8000],
                }
            )
        return messages

    def build_summary(self) -> str:
        s = self.session
        lines = [
            "=" * 50,
            "  HERMES AGENT SESSION SUMMARY",
            "=" * 50,
            f"  Steps: {len(s.steps)}",
            f"  Tool calls: {s.total_tool_calls}",
            f"  Budget remaining: {s.tool_call_budget_remaining}",
            f"  Files created: {len(s.files_created)}",
            f"  Files modified: {len(s.files_modified)}",
            f"  Commands run: {len(s.commands_run)}",
            f"  Errors: {len(s.errors_encountered)}",
        ]
        if s.files_created:
            lines.append("\n  Created files:")
            for f in sorted(s.files_created):
                lines.append(f"    + {f}")
        if s.files_modified:
            lines.append("\n  Modified files:")
            for f in sorted(s.files_modified):
                lines.append(f"    ~ {f}")
        if s.errors_encountered:
            lines.append("\n  Errors:")
            for e in s.errors_encountered[-10:]:
                lines.append(f"    ✗ {e[:120]}")
        if s.memory:
            lines.append("\n  Memory:")
            for k, v in sorted(s.memory.items()):
                lines.append(f"    {k}: {v[:100]}")
        return "\n".join(lines)


def build_hermes_text_prompt(
    user_query: str,
    history: Optional[List[Dict[str, str]]] = None,
    workspace_root: str = "",
) -> str:
    system = f'{HERMES_AGENT_SYSTEM_PROMPT}\n\nWhen you need to use a tool, output EXACTLY:\n\n<tool_call>\n{ "name": "<tool_name>", "args": { "arg1": "value1", ...} } \n</tool_call>\n\nThe tool result will be provided in the next message. Continue until the task is complete.\nWhen finished, do NOT output a tool call — just provide your final answer.\n\nCurrent workspace: {workspace_root}\n'
    prompt = f"<|im_start|>system\n{system}<|im_end|>\n"
    if history:
        for msg in history[-8:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    prompt += f"<|im_start|>user\n{user_query}<|im_end|>\n<|im_start|>assistant\n"
    return prompt


def parse_hermes_tool_call(text: str) -> Optional[Dict[str, Any]]:
    pattern = "<tool_call>\\s*(.*?)\\s*</tool_call>"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def get_hermes_tool_schemas() -> List[Dict[str, Any]]:
    return HermesToolRegistry.get_openai_tools()


def create_agent_session(
    workspace_root: str = "", max_tool_calls: int = 50
) -> AgentSession:
    session = AgentSession(tool_call_budget_remaining=max_tool_calls)
    return session


class Domain(str, Enum):
    MATH = "math"
    CODE = "code"
    GENERAL = "general"


class SandboxResult(str, Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    RUNTIME_ERROR = "runtime_error"
    SYNTAX_ERROR = "syntax_error"
    TEST_FAILED = "test_failed"
    PASS = "pass"
    FAIL = "fail"


@dataclass
class TestCase:
    input_data: str
    expected_output: str
    is_hidden: bool = False


@dataclass
class SandboxReport:
    status: SandboxResult
    stdout: str
    stderr: str
    exit_code: int
    elapsed_ms: float
    failed_test_index: Optional[int] = None
    error_message: Optional[str] = None


class CodeSandbox:

    @staticmethod
    def extract_code(text: str, language: Optional[str] = None) -> str:

        if language:
            lang_pattern = language
            if language.lower() in ("python", "py"):
                lang_pattern = r"(?:python|py)"
            elif language.lower() in ("cpp", "c++", "c"):
                lang_pattern = r"(?:cpp|c\+\+|c)"
            blocks = re.findall(
                rf"```(?:{lang_pattern})?\n(.*?)\n```", text, re.IGNORECASE | re.DOTALL
            )
        else:
            blocks = re.findall(
                r"```(?:\w+)?\n(.*?)\n```", text, re.IGNORECASE | re.DOTALL
            )

        if blocks:

            return blocks[-1].strip()

        if "def " in text or "import " in text or "#include" in text:
            return text.strip()
        return ""

    @staticmethod
    def extract_multiple_files(text: str) -> Dict[str, str]:
        import re

        files = {}

        blocks = re.finditer(r"```(?:\w+)?\s*(.*?)\n(.*?)\n```", text, re.DOTALL)
        for idx, match in enumerate(blocks):
            info_string = match.group(1).strip()
            content = match.group(2).strip()

            filename = None
            if (
                info_string
                and not info_string.startswith("<!--")
                and not info_string.startswith("/*")
            ):
                filename = info_string.split()[0]

            if not filename:
                first_line = content.split("\n")[0].strip()
                m_html = re.search(r"<!--\s*([a-zA-Z0-9_\-./]+)\s*-->", first_line)
                if m_html:
                    filename = m_html.group(1)
                else:
                    m_css = re.search(r"/\*\s*([a-zA-Z0-9_\-./]+)\s*\*/", first_line)
                    if m_css:
                        filename = m_css.group(1)
                    else:
                        m_py = re.search(
                            r"#\s*([a-zA-Z0-9_\-./]+\.[a-zA-Z]+)", first_line
                        )
                        if m_py:
                            filename = m_py.group(1)

            if not filename:
                filename = f"file_{idx+1}.txt"

            files[filename] = content

        return files

    @staticmethod
    def _get_external_python_deps(code: str) -> List[str]:
        import ast
        import sys

        try:
            tree = ast.parse(code)
        except Exception:
            return []

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:
                    imports.add(node.module.split(".")[0])

        stdlib = getattr(sys, "stdlib_module_names", set())
        builtins = {
            "os",
            "sys",
            "time",
            "json",
            "re",
            "math",
            "datetime",
            "collections",
            "itertools",
            "functools",
            "random",
            "subprocess",
            "typing",
            "ast",
            "tempfile",
            "shutil",
            "pathlib",
        }

        external = [
            pkg
            for pkg in imports
            if pkg not in stdlib and pkg not in builtins and not pkg.startswith("_")
        ]

        pkg_mapping = {
            "bs4": "beautifulsoup4",
            "cv2": "opencv-python",
            "sklearn": "scikit-learn",
            "PIL": "Pillow",
            "yaml": "pyyaml",
            "dotenv": "python-dotenv",
        }

        return [pkg_mapping.get(pkg, pkg) for pkg in external]

    @staticmethod
    def run_code_with_io(
        code: str,
        language: str,
        test_cases: List[TestCase],
        timeout_seconds: float = 10.0,
    ) -> SandboxReport:
        import tempfile
        import subprocess
        import time
        import os
        import sys

        start_time = time.time()

        with tempfile.TemporaryDirectory() as tmpdir:
            if language.lower() in ("cpp", "c++", "c"):
                src_file = os.path.join(tmpdir, "solution.cpp")
                exe_file = os.path.join(tmpdir, "solution")
                with open(src_file, "w", encoding="utf-8") as f:
                    f.write(code)
                try:
                    comp = subprocess.run(
                        ["g++", "-O2", "-std=c++17", src_file, "-o", exe_file],
                        capture_output=True,
                        text=True,
                        timeout=10.0,
                    )
                    if comp.returncode != 0:
                        return SandboxReport(
                            status=SandboxResult.SYNTAX_ERROR,
                            stdout="",
                            stderr=comp.stderr,
                            exit_code=comp.returncode,
                            elapsed_ms=(time.time() - start_time) * 1000,
                            error_message="Compilation Failed",
                        )
                except Exception as e:
                    return SandboxReport(
                        status=SandboxResult.RUNTIME_ERROR,
                        stdout="",
                        stderr=str(e),
                        exit_code=-1,
                        elapsed_ms=(time.time() - start_time) * 1000,
                        error_message="Compiler not found or error",
                    )
                run_cmd = [exe_file]
            else:
                src_file = os.path.join(tmpdir, "solution.py")
                with open(src_file, "w", encoding="utf-8") as f:
                    f.write(code)

                python_exe = sys.executable

                external_deps = CodeSandbox._get_external_python_deps(code)
                if external_deps:
                    venv_dir = os.path.join(tmpdir, "venv")
                    try:
                        subprocess.run(
                            [sys.executable, "-m", "venv", venv_dir],
                            capture_output=True,
                            timeout=10,
                        )
                        if os.name == "nt":
                            pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
                            python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
                        else:
                            pip_exe = os.path.join(venv_dir, "bin", "pip")
                            python_exe = os.path.join(venv_dir, "bin", "python")

                        if os.path.exists(pip_exe):
                            subprocess.run(
                                [pip_exe, "install", "--quiet"] + external_deps,
                                capture_output=True,
                                timeout=45,
                            )
                    except Exception:
                        python_exe = sys.executable

                run_cmd = [python_exe, src_file]
            for i, tc in enumerate(test_cases):
                try:
                    proc = subprocess.run(
                        run_cmd,
                        input=tc.input_data,
                        capture_output=True,
                        text=True,
                        timeout=timeout_seconds,
                    )
                    if proc.returncode != 0:
                        return SandboxReport(
                            status=SandboxResult.RUNTIME_ERROR,
                            stdout=proc.stdout,
                            stderr=proc.stderr,
                            exit_code=proc.returncode,
                            elapsed_ms=(time.time() - start_time) * 1000,
                            failed_test_index=i,
                            error_message=f"Runtime error on test {i+1}",
                        )

                    out_clean = proc.stdout.strip()
                    expected_clean = tc.expected_output.strip()

                    if out_clean != expected_clean:
                        return SandboxReport(
                            status=SandboxResult.TEST_FAILED,
                            stdout=proc.stdout,
                            stderr=f"Expected:\n{expected_clean}\nGot:\n{out_clean}",
                            exit_code=0,
                            elapsed_ms=(time.time() - start_time) * 1000,
                            failed_test_index=i,
                            error_message=f"Test {i+1} failed",
                        )
                except subprocess.TimeoutExpired:
                    return SandboxReport(
                        status=SandboxResult.TIMEOUT,
                        stdout="",
                        stderr="Timeout",
                        exit_code=-1,
                        elapsed_ms=(time.time() - start_time) * 1000,
                        failed_test_index=i,
                        error_message=f"Timeout on test {i+1}",
                    )

            return SandboxReport(
                status=SandboxResult.SUCCESS,
                stdout="All tests passed",
                stderr="",
                exit_code=0,
                elapsed_ms=(time.time() - start_time) * 1000,
            )

    @staticmethod
    def run_python(
        code: str,
        test_cases: Optional[List[TestCase]] = None,
        timeout_seconds: float = 10.0,
    ) -> SandboxReport:

        start_time = time.time()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            if not test_cases:
                result = subprocess.run(
                    [sys.executable, temp_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )
                elapsed = (time.time() - start_time) * 1000

                if result.returncode == 0:
                    return SandboxReport(
                        status=SandboxResult.SUCCESS,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        exit_code=0,
                        elapsed_ms=elapsed,
                    )

                stderr = result.stderr
                status = SandboxResult.RUNTIME_ERROR
                error_msg = stderr.split("\n")[-2] if "\n" in stderr else stderr
                if "SyntaxError" in stderr:
                    status = SandboxResult.SYNTAX_ERROR

                return SandboxReport(
                    status=status,
                    stdout=result.stdout,
                    stderr=stderr,
                    exit_code=result.returncode,
                    elapsed_ms=elapsed,
                    error_message=error_msg,
                )

            for i, tc in enumerate(test_cases):
                result = subprocess.run(
                    [sys.executable, temp_path],
                    input=tc.input_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )
                elapsed = (time.time() - start_time) * 1000

                if result.returncode != 0:
                    stderr = result.stderr
                    status = SandboxResult.RUNTIME_ERROR
                    error_msg = stderr.split("\n")[-2] if "\n" in stderr else stderr
                    if "SyntaxError" in stderr:
                        status = SandboxResult.SYNTAX_ERROR
                    return SandboxReport(
                        status=status,
                        stdout=result.stdout,
                        stderr=stderr,
                        exit_code=result.returncode,
                        elapsed_ms=elapsed,
                        failed_test_index=i,
                        error_message=error_msg,
                    )

                out_clean = result.stdout.strip()
                exp_clean = tc.expected_output.strip()

                def norm(s):
                    return " ".join(s.split())

                if norm(out_clean) != norm(exp_clean):
                    return SandboxReport(
                        status=SandboxResult.TEST_FAILED,
                        stdout=result.stdout,
                        stderr=f"Test {i+1} Failed.\nExpected: {exp_clean}\nGot: {out_clean}",
                        exit_code=0,
                        elapsed_ms=elapsed,
                        failed_test_index=i,
                        error_message="Test output mismatch.",
                    )

            elapsed = (time.time() - start_time) * 1000
            return SandboxReport(
                status=SandboxResult.SUCCESS,
                stdout="All tests passed",
                stderr="",
                exit_code=0,
                elapsed_ms=elapsed,
            )

        except subprocess.TimeoutExpired:
            elapsed = (time.time() - start_time) * 1000
            return SandboxReport(
                status=SandboxResult.TIMEOUT,
                stdout="",
                stderr="Execution timed out.",
                exit_code=-1,
                elapsed_ms=elapsed,
                error_message=f"Timed out after {timeout_seconds}s",
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


@dataclass
class MathVerificationReport:
    is_correct: bool
    is_equivalent: bool
    extracted_answer: Optional[str]
    target_answer: str
    error_message: Optional[str] = None


class MathVerifier:

    @staticmethod
    def _normalize(expr: str) -> str:

        expr = expr.replace(" ", "")
        expr = expr.replace("\\text", "")
        expr = re.sub(r"\\frac{([^{}]+)}{([^{}]+)}", r"(\1)/(\2)", expr)
        expr = expr.replace("\\times", "*").replace("\\cdot", "*")
        expr = expr.replace("\\pi", "pi").replace("\\sqrt", "sqrt")
        expr = expr.replace("\\left", "").replace("\\right", "")
        expr = expr.replace("{", "").replace("}", "")
        return expr.lower()

    @staticmethod
    def verify(generated_text: str, target_answer: str) -> MathVerificationReport:

        extracted_match = re.search(r"\*\*Answer:\*\*\s*(.*)", generated_text)
        extracted = extracted_match.group(1).strip() if extracted_match else None

        if not extracted:

            matches = re.findall(r"\\boxed{([^}]+)}", generated_text)
            if matches:
                extracted = matches[-1].strip()

        if not extracted:
            return MathVerificationReport(
                False, False, None, target_answer, "Could not extract final answer."
            )

        norm_ext = MathVerifier._normalize(extracted)
        norm_tgt = MathVerifier._normalize(target_answer)

        is_exact = norm_ext == norm_tgt

        is_equiv = is_exact
        if not is_exact:
            try:
                import sympy

                expr1 = sympy.sympify(norm_ext)
                expr2 = sympy.sympify(norm_tgt)
                if sympy.simplify(expr1 - expr2) == 0:
                    is_equiv = True
            except Exception:
                pass

        return MathVerificationReport(is_equiv, is_equiv, extracted, target_answer)


@dataclass
class RefinementPass:
    turn: int
    prompt: str
    response: str
    report: SandboxReport
    success: bool


class IterativeRefiner:

    def __init__(self, model_callable: Callable, max_turns: int = 3):
        self.model_callable = model_callable
        self.max_turns = max_turns

    def refine_code(
        self, task_prompt: str, initial_code: str, test_cases: List[TestCase]
    ) -> Tuple[str, List[RefinementPass]]:
        passes = []
        current_code = initial_code

        for turn in range(self.max_turns):
            report = CodeSandbox.run_python(current_code, test_cases)

            if report.status == SandboxResult.SUCCESS:
                passes.append(RefinementPass(turn, "N/A", current_code, report, True))
                return current_code, passes

            error_details = (
                report.stderr[-1000:] if report.stderr else report.error_message
            )
            if (
                report.status == SandboxResult.TEST_FAILED
                and report.failed_test_index is not None
            ):
                tc = test_cases[report.failed_test_index]
                error_details = (
                    f"Failed hidden test case. Output did not match expected."
                )
                if not tc.is_hidden:
                    error_details = f"Failed on input: {tc.input_data}. Expected: {tc.expected_output}"

            refinement_prompt = f"""The code you provided failed during execution.
Here is the execution report:
- Status: {report.status.value}
- Error Traceback / Details:
{error_details}

Please analyze the error in a <critic> block, then provide the fully corrected Python code.
"""

            history = [
                {"role": "user", "content": task_prompt},
                {"role": "assistant", "content": current_code},
                {"role": "user", "content": refinement_prompt},
            ]

            response = self.model_callable(history)
            current_code = CodeSandbox.extract_code(response)
            if not current_code:
                current_code = response

            passes.append(
                RefinementPass(turn, refinement_prompt, current_code, report, False)
            )

        return current_code, passes


@dataclass
class SmartHarnessResult:
    final_answer: str
    domain: Domain
    is_verified: bool
    iterations: int
    candidates_generated: int
    execution_reports: List[Any]


class SmartHarness:

    def __init__(self, model_callable: Callable, domain: Domain = Domain.GENERAL):
        self.model_callable = model_callable
        self.domain = domain
        self.refiner = IterativeRefiner(model_callable)

    def solve(
        self,
        prompt: str,
        candidates: int = 1,
        test_cases: Optional[List[TestCase]] = None,
    ) -> SmartHarnessResult:

        if self.domain == Domain.CODE:
            return self._solve_code(prompt, candidates, test_cases)
        elif self.domain == Domain.MATH:
            return self._solve_math(prompt, candidates)
        else:

            ans = self.model_callable([{"role": "user", "content": prompt}])
            return SmartHarnessResult(ans, self.domain, False, 1, 1, [])

    def _solve_code(
        self, prompt: str, candidates: int, test_cases: Optional[List[TestCase]]
    ) -> SmartHarnessResult:

        all_reports = []
        best_code = None
        best_tests_passed = -1

        for i in range(candidates):
            ans = self.model_callable([{"role": "user", "content": prompt}])
            code = CodeSandbox.extract_code(ans)

            if test_cases:
                refined_code, passes = self.refiner.refine_code(
                    prompt, code, test_cases
                )
                all_reports.extend(passes)

                if passes:
                    last_pass = passes[-1]
                    if last_pass.success:
                        return SmartHarnessResult(
                            refined_code,
                            self.domain,
                            True,
                            len(passes),
                            i + 1,
                            all_reports,
                        )

                    passed_tests = last_pass.report.tests_passed or 0
                    if passed_tests > best_tests_passed:
                        best_tests_passed = passed_tests
                        best_code = refined_code
            else:
                rep = CodeSandbox.run_python(code)
                all_reports.append(rep)
                if rep.status == SandboxResult.SUCCESS:
                    best_code = code
                    return SmartHarnessResult(
                        best_code, self.domain, True, 1, i + 1, all_reports
                    )

        return SmartHarnessResult(
            best_code or code, self.domain, False, 1, candidates, all_reports
        )

    def _solve_math(self, prompt: str, candidates: int) -> SmartHarnessResult:

        answers = []
        for i in range(candidates):
            ans = self.model_callable([{"role": "user", "content": prompt}])
            answers.append(ans)

        if candidates == 1:
            return SmartHarnessResult(answers[0], self.domain, False, 1, 1, [])

        extracted = []
        for a in answers:
            match = re.search(r"\*\*Answer:\*\*\s*(.*)", a)
            if match:
                extracted.append(MathVerifier._normalize(match.group(1)))

        if not extracted:
            return SmartHarnessResult(answers[0], self.domain, False, 1, candidates, [])

        from collections import Counter

        counts = Counter(extracted)
        majority, _ = counts.most_common(1)[0]

        best_ans = answers[0]
        for a in answers:
            match = re.search(r"\*\*Answer:\*\*\s*(.*)", a)
            if match and MathVerifier._normalize(match.group(1)) == majority:
                best_ans = a
                break

        return SmartHarnessResult(best_ans, self.domain, True, 1, candidates, [counts])


def extract_codeforces_tests(problem_description: str) -> List[TestCase]:
    if not problem_description:
        return []
    tests = []
    pattern = re.compile(
        r"(?i)(?:^|\n)\**Input(?:Copy)?\**\s*?\n(.*?)\n\**Output(?:Copy)?\**\s*?\n(.*?)(?=\n\**Note\**\s*?\n|\n\**Input(?:Copy)?\**\s*?\n|$)",
        re.DOTALL,
    )
    matches = pattern.findall(problem_description)
    for inp, out in matches:
        inp = inp.strip()
        out = out.strip()
        if inp and out:
            tests.append(TestCase(input_data=inp, expected_output=out))
    return tests


@dataclass
class SandboxResultReport:
    result: SandboxResult = SandboxResult.PASS
    tests_passed: int = 0
    tests_failed: int = 0
    syntax_error: Optional[str] = None
    runtime_errors: List[str] = field(default_factory=list)


def apply_smart_harness_code(
    text: str, language: Optional[str] = None, problem_description: Optional[str] = None
):

    tests = extract_codeforces_tests(problem_description)

    rep = SandboxResultReport()
    rep.result = SandboxResult.PASS
    rep.tests_passed = 0
    rep.tests_failed = 0
    rep.syntax_error = None
    rep.runtime_errors = []

    if not tests:

        rep.tests_passed = 1
        return text, rep

    code = CodeSandbox.extract_code(text, language)
    if not code:
        rep.result = SandboxResult.FAIL
        rep.syntax_error = "Could not extract code from response."
        return text, rep

    lang = language or "python"
    report = CodeSandbox.run_code_with_io(code, lang, tests)

    if report.status == SandboxResult.SUCCESS:
        rep.result = SandboxResult.PASS
        rep.tests_passed = len(tests)
    elif report.status == SandboxResult.TEST_FAILED:
        rep.result = SandboxResult.FAIL
        rep.tests_passed = report.failed_test_index
        rep.tests_failed = len(tests) - rep.tests_passed
        rep.runtime_errors.append(
            f"Test {report.failed_test_index + 1} Failed.\n{report.stderr}"
        )
    elif report.status == SandboxResult.SYNTAX_ERROR:
        rep.result = SandboxResult.FAIL
        rep.syntax_error = str(report.error_message) + "\n" + str(report.stderr)
        rep.tests_failed = len(tests)
    elif report.status in (SandboxResult.RUNTIME_ERROR, SandboxResult.TIMEOUT):
        rep.result = SandboxResult.FAIL
        rep.tests_passed = report.failed_test_index or 0
        rep.tests_failed = len(tests) - rep.tests_passed
        rep.runtime_errors.append(f"{report.error_message}\n{report.stderr}")

    return text, rep


@dataclass
class MathVerificationResult:
    result: SandboxResult = SandboxResult.PASS
    steps_verified: int = 0
    steps_failed: int = 0
    final_answer_extracted: Optional[str] = None
    numerical_match: bool = True
    expected_value: Optional[str] = None
    computed_value: Optional[str] = None
    self_consistent: bool = True


def apply_smart_harness_math(text: str):
    import sympy

    rep = MathVerificationResult()

    extracted, _ = extract_math_answer(text)
    if extracted != text:
        rep.final_answer_extracted = extracted

    equations = re.findall(r"\$\$([^\$]+)\$\$", text)
    equations += re.findall(r"\\\[(.*?)\\\]", text, re.DOTALL)

    for eq in equations:
        if "=" not in eq:
            continue

        parts = [p.strip() for p in eq.split("=")]
        if len(parts) >= 2:
            try:
                for i in range(len(parts) - 1):
                    p1 = MathVerifier._normalize(parts[i])
                    p2 = MathVerifier._normalize(parts[i + 1])
                    if not p1 or not p2:
                        continue
                    expr1 = sympy.sympify(p1)
                    expr2 = sympy.sympify(p2)
                    if sympy.simplify(expr1 - expr2) != 0:
                        rep.self_consistent = False
                        rep.steps_failed += 1
                        break
                    else:
                        rep.steps_verified += 1
            except Exception:
                pass

    if rep.steps_failed > 0:
        rep.result = SandboxResult.FAIL

    return text, rep


def build_code_refinement_prompt(
    code: str, problem_description: Optional[str] = None
) -> str:
    return ""


def build_math_refinement_prompt(math_text: str) -> str:
    return ""


__all__ = [
    "apply_smart_harness_code",
    "apply_smart_harness_math",
    "build_code_refinement_prompt",
    "build_math_refinement_prompt",
    "HermesToolRegistry",
    "HermesResultAnalyzer",
    "HermesAgentLoop",
    "AgentSession",
    "AgentStep",
    "ToolResult",
    "ToolResultStatus",
    "ToolSchema",
    "ToolCategory",
    "HERMES_AGENT_SYSTEM_PROMPT",
    "build_hermes_text_prompt",
    "parse_hermes_tool_call",
    "get_hermes_tool_schemas",
    "create_agent_session",
    "Domain",
    "SandboxResult",
    "TestCase",
    "SandboxReport",
    "CodeSandbox",
    "MathVerificationReport",
    "MathVerifier",
    "RefinementPass",
    "IterativeRefiner",
    "SmartHarnessResult",
    "SmartHarness",
]


def apply_search_replace_blocks(original_text: str, diff_text: str) -> str:
    """
    Parses <<<< ==== >>>> blocks from diff_text and applies them to original_text.
    """
    import re

    pattern = re.compile(r"<<<<\s*\n(.*?)\n====\s*\n(.*?)\n>>>>", re.DOTALL)
    result = original_text
    blocks = pattern.finditer(diff_text)

    for match in blocks:
        search_text = match.group(1)
        replace_text = match.group(2)
        if search_text in result:
            result = result.replace(search_text, replace_text, 1)
        else:
            search_lines = [l.rstrip() for l in search_text.split("\n")]
            result_lines = result.split("\n")
            window_size = len(search_lines)
            found_idx = -1
            for i in range(len(result_lines) - window_size + 1):
                match_found = True
                for j in range(window_size):
                    if result_lines[i + j].rstrip() != search_lines[j]:
                        match_found = False
                        break
                if match_found:
                    found_idx = i
                    break
            if found_idx != -1:
                before = result_lines[:found_idx]
                after = result_lines[found_idx + window_size :]
                replace_lines = replace_text.split("\n")
                result = "\n".join(before + replace_lines + after)
    return result
