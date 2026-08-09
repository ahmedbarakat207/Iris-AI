import json
import time
import os
import re
import io
from contextlib import redirect_stdout
from typing import Dict, List, Optional, Tuple


def _extract_python_code(raw: str) -> str:

    m = re.search(r"```(?:python)?\n(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    if m:
        code = m.group(1)
    else:

        raw_stripped = raw.strip()
        if raw_stripped.startswith("```"):
            lines = raw_stripped.split("\n")
            if len(lines) > 1:
                code = "\n".join(lines[1:]).strip("`")
            else:
                code = raw_stripped.strip("`")
        else:
            code = raw_stripped

    cleaned_lines = []
    in_block = False
    for line in code.splitlines():
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue

        if not in_block and line.startswith(" "):
            line = line.lstrip()

        cleaned_lines.append(line)

        if stripped.endswith(":"):
            in_block = True
        elif in_block and not line.startswith(" "):

            in_block = False

    return "\n".join(cleaned_lines).strip()


def _make_driver(headless: bool = False):

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    profile_dir = os.path.join(os.path.dirname(__file__), "..", "browser_profile")
    opts.add_argument(f"--user-data-dir={os.path.abspath(profile_dir)}")
    opts.add_argument("--profile-directory=Default")

    if headless:
        opts.add_argument("--headless=new")

    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    import platform

    sys_name = platform.system()
    if sys_name == "Windows":
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    elif sys_name == "Linux":
        ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    else:
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

    opts.add_argument(f"user-agent={ua}")

    try:
        driver = webdriver.Chrome(options=opts)
    except Exception:
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=opts,
            )
        except Exception as e:
            raise RuntimeError(
                f"Could not start Chrome WebDriver: {e}\n"
                "Make sure Google Chrome is installed and run:\n  pip install selenium"
            )
    driver.implicitly_wait(6)
    return driver


def _page_snapshot(driver) -> dict:

    js_code = """
    window.findIrisElement = function(id) {
        function search(root) {
            let el = root.querySelector('[data-iris-id="' + id + '"]');
            if (el) return el;
            for (let child of root.querySelectorAll('*')) {
                if (child.shadowRoot) { let found = search(child.shadowRoot); if (found) return found; }
            }
            return null;
        }
        return search(document);
    };
    function extractDOM() {
        let irisIdCounter = 1; const items = [];
        function isVisible(el) {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0 && window.getComputedStyle(el).visibility !== 'hidden';
        }
        const sel = 'a, button, input, textarea, select, [role="button"], [role="link"], [tabindex]:not([tabindex="-1"])';
        function traverse(root) {
            for (let el of root.querySelectorAll(sel)) {
                if (!isVisible(el)) continue;
                let id = el.getAttribute('data-iris-id');
                if (!id) { id = irisIdCounter++; el.setAttribute('data-iris-id', id); }
                let tag = el.tagName.toLowerCase();
                let text = (el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || '').trim();
                if (text.length > 60) text = text.substring(0, 57) + '...';
                let obj = { id: parseInt(id), tag: tag };
                if (text) obj.text = text;
                let type = el.getAttribute('type'); if (type) obj.type = type;
                let name = el.getAttribute('name'); if (name) obj.name = name;
                if (text || tag === 'input' || tag === 'textarea' || tag === 'select') items.push(obj);
            }
            for (let el of root.querySelectorAll('*')) { if (el.shadowRoot) traverse(el.shadowRoot); }
        }
        traverse(document);
        return items;
    }
    return extractDOM();
    """
    try:
        elements = driver.execute_script(js_code)
        return {"title": driver.title, "url": driver.current_url, "elements": elements}
    except Exception as e:
        return {"title": driver.title, "url": driver.current_url, "elements": []}


_MAX_RETRIES = 3
_RETRY_DELAY = 1.5
_ACTION_TIMEOUT = 10


def _retry(fn, name: str = "action"):

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            return fn()
        except Exception as e:
            if attempt == _MAX_RETRIES:
                raise
            print(f"  [Browser] {name} attempt {attempt} failed: {e} — retrying...")
            time.sleep(_RETRY_DELAY * attempt)


def _make_helpers(driver):

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys

    def click_element(iris_id):
        def _do():
            el = driver.execute_script(f"return window.findIrisElement('{iris_id}')")
            if not el:
                raise Exception(f"Element iris_id={iris_id} not found")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            el.click()
            time.sleep(0.5)

        _retry(_do, f"click #{iris_id}")

    def fill_element(iris_id, text: str):
        def _do():
            el = driver.execute_script(f"return window.findIrisElement('{iris_id}')")
            if not el:
                raise Exception(f"Element iris_id={iris_id} not found")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            el.clear()
            el.send_keys(text)
            time.sleep(0.3)

        _retry(_do, f"fill #{iris_id}")

    def upload_file(iris_id, file_path: str):

        def _do():
            el = driver.execute_script(f"return window.findIrisElement('{iris_id}')")
            if not el:
                raise Exception(f"Element iris_id={iris_id} not found")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                raise Exception(f"File not found: {abs_path}")
            el.send_keys(abs_path)
            time.sleep(1.0)

        _retry(_do, f"upload #{iris_id}")

    def select_option(iris_id, option_text: str):

        def _do():
            el = driver.execute_script(f"return window.findIrisElement('{iris_id}')")
            if not el:
                raise Exception(f"Element iris_id={iris_id} not found")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.3)
            from selenium.webdriver.support.ui import Select

            Select(el).select_by_visible_text(option_text)
            time.sleep(0.3)

        _retry(_do, f"select #{iris_id}")

    return {
        "driver": driver,
        "By": By,
        "WebDriverWait": WebDriverWait,
        "EC": EC,
        "Keys": Keys,
        "time": time,
        "json": json,
        "click_element": click_element,
        "fill_element": fill_element,
        "upload_file": upload_file,
        "select_option": select_option,
    }


def parse_resume(file_path: str) -> Dict[str, str]:

    result = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "skills": "",
        "experience_years": "",
        "education": "",
        "raw_text": "",
    }

    if not os.path.exists(file_path):
        return result

    text = ""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            try:
                import subprocess, tempfile

                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
                    subprocess.run(
                        ["pdftotext", file_path, tmp.name],
                        timeout=15,
                        capture_output=True,
                    )
                    text = open(tmp.name).read()
                    os.unlink(tmp.name)
            except Exception:
                text = "[Could not extract PDF — install pypdf: pip install pypdf]"
        except Exception:
            text = "[PDF extraction failed]"

    elif ext in (".docx", ".doc"):
        try:
            from docx import Document

            doc = Document(file_path)
            text = "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            text = "[Could not extract DOCX — install python-docx: pip install python-docx]"
        except Exception:
            text = "[DOCX extraction failed]"

    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            text = f"[Could not read {ext} file]"

    result["raw_text"] = text[:8000]

    if not text or text.startswith("["):
        return result

    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    if email_match:
        result["email"] = email_match.group(0)

    phone_match = re.search(
        r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text
    )
    if phone_match:
        result["phone"] = phone_match.group(0).strip()

    lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 2]
    for line in lines[:5]:
        if "@" in line or re.search(r"\d{3}[-.]\d{3}", line):
            continue
        if re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$", line) and 5 < len(line) < 50:
            result["name"] = line
            break

    loc_match = re.search(
        r"([A-Z][a-z]+,\s*[A-Z]{2}\s*\d{5})|"
        r"([A-Z][a-z]+,\s*[A-Z]{2}(?:\s|$))|"
        r"([A-Z][a-z]+,\s*(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY))",
        text,
    )
    if loc_match:
        result["location"] = loc_match.group(0).strip()

    skills_section = re.search(
        r"(?:SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES|TECHNOLOGIES)[:\s]*(.+?)(?:\n\n|\n[A-Z][A-Z\s]{3,}|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if skills_section:
        result["skills"] = skills_section.group(1).strip()[:500]

    exp_match = re.search(
        r"(\d+)\+?\s*(?:years|yrs)(?:\s+of)?\s+experience", text, re.IGNORECASE
    )
    if exp_match:
        result["experience_years"] = exp_match.group(1)

    edu_match = re.search(
        r"(?:EDUCATION|ACADEMIC)[:\s]*(.+?)(?:\n\n|\n[A-Z][A-Z\s]{3,}|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if edu_match:
        result["education"] = edu_match.group(1).strip()[:500]

    return result


_FIELD_MAP = {
    "first_name": "first_name",
    "firstname": "first_name",
    "given_name": "first_name",
    "fname": "first_name",
    "last_name": "last_name",
    "lastname": "last_name",
    "surname": "last_name",
    "family_name": "last_name",
    "lname": "last_name",
    "full_name": "full_name",
    "email": "email",
    "email_address": "email",
    "phone": "phone",
    "phone_number": "phone",
    "mobile": "phone",
    "cell": "phone",
    "telephone": "phone",
    "location": "location",
    "city": "location",
    "address": "location",
    "country": "location",
    "resume": "resume",
    "cv": "resume",
    "upload_resume": "resume",
    "upload_cv": "resume",
    "attach_resume": "resume",
    "resume_upload": "resume",
    "file": "resume",
    "attachment": "resume",
    "cover_letter": "cover_letter",
    "coverletter": "cover_letter",
    "cover": "cover_letter",
    "linkedin": "linkedin",
    "linkedin_url": "linkedin",
    "website": "website",
    "portfolio": "website",
    "github": "website",
    "url": "website",
    "race": "demographic",
    "ethnicity": "demographic",
    "gender": "demographic",
    "pronouns": "demographic",
    "veteran": "demographic",
    "disability": "demographic",
    "work_auth": "work_auth",
    "sponsorship": "work_auth",
    "visa": "work_auth",
    "eligible": "work_auth",
    "authorized": "work_auth",
    "citizen": "work_auth",
    "school": "education",
    "university": "education",
    "college": "education",
    "degree": "education",
    "education": "education",
    "major": "education",
    "experience": "experience_years",
    "years_of_experience": "experience_years",
    "total_years": "experience_years",
    "salary": "skip",
    "compensation": "skip",
    "desired_pay": "skip",
    "expected_salary": "skip",
    "current_company": "experience",
    "current_employer": "experience",
    "company": "experience",
    "employer": "experience",
    "job_title": "experience",
    "title": "experience",
    "how_did_you_hear": "source",
    "referral": "source",
    "source": "source",
    "referred_by": "source",
    "hear_about": "source",
    "hear": "source",
}


def _infer_field_type(element: dict) -> Tuple[str, str]:

    text = (element.get("text") or "").lower()
    name = (element.get("name") or "").lower()
    tag = element.get("tag", "").lower()
    etype = (element.get("type") or "").lower()

    if etype == "file":
        return ("resume", True)

    search = f"{name} {text} {element.get('placeholder', '')} {element.get('aria-label', '')}".lower()

    search = re.sub(r"[*:·•]+", "", search)
    search = re.sub(r"\(.*?\)", "", search)
    search = re.sub(r"\breq\w*\b", "", search)

    for key, field_type in _FIELD_MAP.items():
        if key in search:
            return (field_type, False)

    if (
        tag == "input"
        and etype in ("text", "")
        and not name
        and not element.get("placeholder")
    ):
        if "first" in search or "given" in search:
            return ("first_name", False)
        if "last" in search or "sur" in search:
            return ("last_name", False)

    if tag == "textarea":
        return ("cover_letter", False)

    return ("unknown", False)


def browser_autopilot(
    url: str,
    task: str,
    resume_path: Optional[str] = None,
    max_turns: int = 15,
    existing_driver=None,
) -> str:

    from src.iris import generate_internal_code, ModelRole

    resume = {}
    if resume_path and os.path.exists(resume_path):
        print(f"[Browser] Parsing resume: {resume_path}")
        resume = parse_resume(resume_path)
        for k, v in resume.items():
            if v and k != "raw_text":
                print(f"  ✓ {k}: {v[:60]}")

    driver = existing_driver if existing_driver else _make_driver(headless=False)
    helpers = _make_helpers(driver)

    turn_log = []
    completed = False

    try:
        if url:
            print(f"[Browser] Opening: {url}")
            driver.get(url)
            time.sleep(3)

        for turn in range(1, max_turns + 1):
            print(f"\n[Browser] ── Turn {turn}/{max_turns} ──")

            snapshot = _page_snapshot(driver)
            if not snapshot.get("elements"):
                print(
                    "  [Browser] No interactable elements — page may still be loading."
                )
                time.sleep(2)
                snapshot = _page_snapshot(driver)

            field_hints = []
            upload_elements = []
            for el in snapshot.get("elements", []):
                ftype, is_upload = _infer_field_type(el)
                if ftype != "unknown":
                    val = None
                    if is_upload and resume_path:
                        val = resume_path
                        upload_elements.append(el["id"])
                    elif ftype == "first_name" and resume.get("name"):
                        parts = resume["name"].split()
                        if len(parts) >= 1:
                            val = parts[0]
                    elif ftype == "last_name" and resume.get("name"):
                        parts = resume["name"].split()
                        if len(parts) >= 2:
                            val = parts[-1]
                    elif ftype == "full_name" and resume.get("name"):
                        val = resume["name"]
                    elif ftype == "email" and resume.get("email"):
                        val = resume["email"]
                    elif ftype == "phone" and resume.get("phone"):
                        val = resume["phone"]
                    elif ftype == "location" and resume.get("location"):
                        val = resume["location"]
                    elif ftype == "experience_years" and resume.get("experience_years"):
                        val = resume["experience_years"]
                    elif ftype == "linkedin":
                        val = "https://linkedin.com/in/iris-ai"
                    elif ftype == "website":
                        val = "https://iris-ai.app"
                    elif ftype == "work_auth":
                        val = "Yes"
                    elif ftype == "demographic":
                        val = "Prefer not to say"
                    elif ftype == "source":
                        val = "LinkedIn"
                    elif ftype == "skip":
                        val = None
                    elif ftype == "education" and resume.get("education"):
                        val = resume["education"][:200]
                    elif ftype == "cover_letter":
                        val = "[Generated cover letter — see below]"

                    if val:
                        field_hints.append(
                            {
                                "iris_id": el["id"],
                                "field_type": ftype,
                                "suggested_value": str(val),
                                "element": el,
                            }
                        )

            prompt_parts = [
                "You are a Selenium automation expert. You have ONE turn to act on the current page.",
                "",
                f"TASK: {task}",
                f"TURN: {turn}/{max_turns}",
            ]

            if turn == 1:
                prompt_parts.append(
                    "PHASE: This is the FIRST turn. Navigate, search, or start filling the form."
                )

            if field_hints:
                prompt_parts.append("")
                prompt_parts.append("AUTO-DETECTED FORM FIELDS (use these values):")
                for h in field_hints:
                    prompt_parts.append(
                        f"  iris_id={h['iris_id']}  field={h['field_type']}  "
                        f"value={h['suggested_value'][:60]}  element={json.dumps(h['element'])}"
                    )

            if upload_elements:
                prompt_parts.append("")
                prompt_parts.append(
                    "FILE UPLOAD elements detected — use upload_file(id, path) for these:"
                )
                prompt_parts.append(f"  IDs: {upload_elements}")
                prompt_parts.append(f"  Resume path: {resume_path}")

            prompt_parts.append("")
            prompt_parts.append("CURRENT PAGE SNAPSHOT:")
            prompt_parts.append(
                json.dumps(snapshot.get("elements", []), indent=2, ensure_ascii=False)
            )
            prompt_parts.append("")
            prompt_parts.append("AVAILABLE FUNCTIONS:")
            prompt_parts.append("  click_element(id)    — click a button/link")
            prompt_parts.append("  fill_element(id, text) — type into a field")
            prompt_parts.append(
                "  upload_file(id, path)  — attach a file (<input type=file>)"
            )
            prompt_parts.append("  select_option(id, text)— pick from a dropdown")
            prompt_parts.append("  time.sleep(n)          — wait for page load")
            prompt_parts.append("")
            prompt_parts.append("RULES:")
            prompt_parts.append("- Do NOT import selenium.")
            prompt_parts.append(
                "- Do NOT initialize a new webdriver or create a new driver instance."
            )
            prompt_parts.append("- Do NOT call driver.get().")
            prompt_parts.append("- ONLY use the provided helper functions.")
            prompt_parts.append(
                "- The 'id' parameter in functions (e.g. click_element(id), fill_element(id, text)) MUST be the exact integer 'id' from the CURRENT PAGE SNAPSHOT elements list (e.g., click_element(5) or fill_element(12, 'value')). Do NOT invent string IDs like 'search_input' or 'search_button'."
            )
            prompt_parts.append("- Complete AS MUCH as possible this turn.")
            prompt_parts.append(
                "- If you see a submit/next/continue button AND all required fields are filled, CLICK IT."
            )
            prompt_parts.append(
                "- If you reach a confirmation page ('thank you', 'application submitted'), print('DONE')."
            )
            prompt_parts.append(
                "- After clicking, use time.sleep(3) for page transitions."
            )
            prompt_parts.append(
                "- Prefer the suggested values from AUTO-DETECTED FORM FIELDS above."
            )
            prompt_parts.append(
                "- Output ONLY raw Python. No markdown, no explanation."
            )

            code_prompt = "\n".join(prompt_parts)

            raw_code = generate_internal_code(
                system_prompt="You are a Selenium automation expert.",
                user_prompt=code_prompt,
                max_tokens=1024,
                role=ModelRole.CODE,
            )
            raw_code = _extract_python_code(raw_code)

            print(f"  [Browser] Generated {len(raw_code)} bytes of automation code")

            captured = io.StringIO()
            try:
                with redirect_stdout(captured):
                    exec(raw_code, helpers)
                output = captured.getvalue().strip()
            except Exception as exec_err:
                output = f"Error: {exec_err}\nCode was:\n{raw_code}"
                print(
                    f"  [Browser] Turn {turn} failed: {exec_err}\nGenerated Code:\n{raw_code}"
                )

            turn_log.append(
                {
                    "turn": turn,
                    "url": driver.current_url,
                    "title": driver.title,
                    "output": output,
                }
            )

            print(f"  [Browser] Turn {turn} → {driver.title}")

            page_text = (driver.title + " " + driver.page_source[:2000]).lower()
            done_signals = [
                "thank you",
                "application submitted",
                "applied successfully",
                "we've received",
                "confirmation",
                "your application has been",
                "submitted",
                "successfully applied",
            ]
            if any(sig in page_text for sig in done_signals) or "DONE" in output:
                print("[Browser] [SUCCESS] Application appears complete!")
                completed = True
                break

            time.sleep(1.5)

        if completed:
            summary = (
                f"[SUCCESS] Application submitted successfully on **{driver.title}**.\n"
            )
        else:
            summary = (
                f"⚠️ Reached turn limit ({max_turns}). The browser is open — "
                f"you can complete manually.\nLast page: **{driver.title}**\n\n"
            )

        summary += f"URL: {driver.current_url}\n"
        summary += f"Turns completed: {len(turn_log)}/{max_turns}\n"

        if turn_log:
            summary += "\nTurn log:\n"
            for t in turn_log:
                summary += (
                    f"  Turn {t['turn']}: {t['title'][:60]} — {t['output'][:80]}\n"
                )

        if resume and resume.get("raw_text"):
            fields_found = [k for k, v in resume.items() if v and k != "raw_text"]
            summary += f"\nResume parsed: {', '.join(fields_found)}"

        return summary

    finally:
        if not existing_driver:
            pass


def browser_task(url: str, task: str, existing_driver=None) -> str:

    driver = existing_driver if existing_driver else _make_driver(headless=False)
    from src.iris import generate_internal_code, ModelRole

    raw_code = ""
    try:
        if url:
            driver.get(url)
            time.sleep(2.5)
        snapshot = _page_snapshot(driver)
        helpers = _make_helpers(driver)

        code_prompt = f"""You are a Selenium automation expert.

CRITICAL RULES:
- Do NOT import selenium.
- Do NOT initialize a webdriver or create a new driver instance (e.g. no `driver = webdriver.Chrome()`).
- Do NOT call driver.get().
- Only use the provided functions: click_element, fill_element, time.sleep.
- The 'id' parameter in functions (e.g. click_element(id), fill_element(id, text)) MUST be the exact integer 'id' from the Page snapshot (for example: click_element(12) or fill_element(5, 'some text')). Do NOT invent semantic string IDs like 'search_input' or 'search_button'.
- Output ONLY raw Python code. No markdown.

Available Functions: click_element(id), fill_element(id, text), time.sleep(n)

Page snapshot:
{json.dumps(snapshot.get('elements', []), indent=2, ensure_ascii=False)}

Task: {task}"""

        raw_code = generate_internal_code(
            system_prompt="You are a Selenium automation expert.",
            user_prompt=code_prompt,
            max_tokens=512,
            role=ModelRole.CODE,
        )
        raw_code = _extract_python_code(raw_code)

        captured = io.StringIO()
        with redirect_stdout(captured):
            exec(raw_code, helpers)
        output = captured.getvalue().strip()

        return f"[SUCCESS] Browser task complete. Final page: **{driver.title}**\n\n{output}"
    except Exception as e:
        return f"[ERROR] Browser task failed: {e}\n\nGenerated Python code:\n```python\n{raw_code}\n```"


def browser_login(url: str, username: str, password: str) -> str:

    driver = _make_driver(headless=False)
    code = ""
    try:
        driver.get(url)
        time.sleep(2.5)
        helpers = _make_helpers(driver)

        from src.iris import generate_internal_code, ModelRole

        prompt = (
            f"Log into this page with username '{username}' and password '{password}'.\n"
            "CRITICAL: Do NOT import selenium or initialize a webdriver. Only use fill_element(id, text) and click_element(id).\n"
            f"Page elements: {json.dumps(_page_snapshot(driver).get('elements', []), indent=2)}\n"
            "Output raw Python only."
        )
        code = generate_internal_code(
            system_prompt="Login automation expert.",
            user_prompt=prompt,
            max_tokens=256,
            role=ModelRole.CODE,
        )
        code = _extract_python_code(code)
        exec(code, helpers)
        time.sleep(2)
        return f"[SUCCESS] Logged in. Currently at: **{driver.title}** — {driver.current_url}"
    except Exception as e:
        return f"[ERROR] Login failed: {e}\n\nGenerated Python code:\n```python\n{code}\n```"
