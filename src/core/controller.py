<<<<<<< HEAD
import os
import platform
import sys


def _ensure_open_interpreter():
    try:
        import interpreter as _test
    except ImportError:
        import subprocess as _sp

        print("\n[Iris] Installing open-interpreter — one-time setup...", flush=True)
        pip_args = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-q",
            "--upgrade",
            "open-interpreter",
        ]
        if platform.system() == "Linux":
            pip_args.append("--break-system-packages")
        env = os.environ.copy()
        env["PYO3_USE_ABI3_FORWARD_COMPATIBILITY"] = "1"
        _sp.run(pip_args, check=True, env=env)
        print("[Iris] open-interpreter installed ✓\n", flush=True)


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.logger import get_logger
from src.iris.engine import (
    detect_user_language,
    translate_text,
    _model_pool,
    load_model,
    ModelRole,
    get_hardware_profile,
    get_device,
)

logger = get_logger("controller")


import json
import platform
import re
import shutil
import smtplib
import subprocess
import subprocess as _subprocess
import time
from pathlib import Path
from typing import Optional, Generator, Dict, Any, List, Tuple, Union

OI_AVAILABLE = False
_oi = None
_oi_initialized = False
_oi_step_counter = 0


def _get_oi_system_message() -> str:
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "skills",
        "prompts",
        "oi_system_message.txt",
    )
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning(f"[WARNING] Prompt file not found: {path}")
        return "You are an AI PC assistant. Please write and execute code."


def _init_oi():
    global _oi, OI_AVAILABLE, _oi_initialized
    if _oi_initialized:
        if _oi is not None:
            _oi.system_message = _get_oi_system_message()
        return
    _oi_initialized = True

    _ensure_open_interpreter()

    try:
        from interpreter import interpreter as open_interpreter

        _oi = open_interpreter

        _oi.auto_run = True
        _oi.verbose = False
        _oi.max_output = 4000
        _oi.offline = True
        _oi.sync_computer = False
        _oi.loop = False

        _oi.llm.supports_functions = False
        _oi.llm.supports_vision = False

        def _iris_native_oi_llm(*args, **kwargs):

            global _oi_step_counter
            _oi_step_counter += 1
            if _oi_step_counter > 1:
                yield {
                    "choices": [
                        {
                            "delta": {"content": "Stopped after executing 1 step."},
                            "finish_reason": "stop",
                        }
                    ]
                }
                return

            try:
                load_model(ModelRole.CODE)
            except FileNotFoundError:
                yield {
                    "choices": [
                        {
                            "delta": {
                                "content": "Controller disabled: Code model not found."
                            },
                            "finish_reason": "stop",
                        }
                    ]
                }
                return

            model_obj = _model_pool[ModelRole.CODE.value]

            clean_kwargs = {
                "messages": kwargs.get("messages", []),
                "stream": True,
                "max_tokens": 1024,
                "temperature": 0.1,
                "stop": [
                    "<|im_end|>",
                    "<|im_start|>",
                    "<|endoftext|>",
                    "</s>",
                    "## Conversation",
                    "<step_end>",
                ],
            }

            for chunk in model_obj.create_chat_completion(**clean_kwargs):
                yield chunk

        _oi.llm.completions = _iris_native_oi_llm
        _oi.llm.api_base = None
        _oi.llm.model = "iris-native"
        _oi.llm.context_window = 8192
        _oi.llm.max_tokens = 1024

        _oi.system_message = _get_oi_system_message()

        OI_AVAILABLE = True
        logger.info("[OI] Open Interpreter ready (offline mode) ✓")

    except Exception as _oi_err:
        OI_AVAILABLE = False
        logger.warning(f"[OI] Open Interpreter unavailable: {_oi_err}")


class _FakeResult:

    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def _shell(cmd, **kw) -> _FakeResult:

    defaults = dict(shell=isinstance(cmd, str), capture_output=True, text=True)
    defaults.update(kw)
    try:
        r = _subprocess.run(cmd, **defaults)
        return _FakeResult(r.stdout or "", r.stderr or "", r.returncode)
    except Exception as e:
        logger.warning(f"[Shell] command failed: {e}")
        return _FakeResult("", str(e), 1)


def _popen(cmd, shell: bool = False, **kw) -> None:

    suppress = dict(stdout=_subprocess.DEVNULL, stderr=_subprocess.DEVNULL)
    suppress.update(kw)
    try:
        return _subprocess.Popen(cmd, shell=shell, start_new_session=True, **suppress)
    except Exception as e:

        if not shell and isinstance(cmd, list):
            try:
                shell_cmd = " ".join(cmd)
                return _subprocess.Popen(
                    shell_cmd, shell=True, start_new_session=True, **suppress
                )
            except Exception as e2:
                logger.warning(f"[Popen] shell fallback also failed: {e2}")
        else:
            logger.warning(f"[Popen] launch failed: {e}")
        return None


def _exec_shell_cmd(cmd: str) -> str:

    try:
        r = _subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr or "Done.").strip()
    except _subprocess.TimeoutExpired:
        return "Command timed out (30s limit)."
    except Exception as e:
        return f"Command failed: {e}"


def _run_oi_task(task: str) -> Generator[Dict[str, str], None, str]:
    global _oi_step_counter
    _oi_step_counter = 0
    _init_oi()
    if not OI_AVAILABLE:
        return "Open Interpreter unavailable. Install: pip install open-interpreter"
    try:
        _oi.messages = []
        parts = []
        assistant_buffer = ""
        computer_buffer = ""
        active_code_block = False

        def flush_assistant():
            nonlocal assistant_buffer
            val = assistant_buffer.strip()
            if val:
                parts.append(val)
            assistant_buffer = ""

        for chunk in _oi.chat(task, display=True, stream=True, blocking=True):
            if not isinstance(chunk, dict):
                continue
            chunk_type = chunk.get("type", "")
            role = chunk.get("role", "")
            content = chunk.get("content", "")

            if chunk_type == "code" and role == "assistant":
                if not active_code_block:
                    active_code_block = True
                    fmt = chunk.get("format", "python")
                    yield {"type": "thinking", "content": f"\n```{fmt}\n"}
                if isinstance(content, str):
                    yield {"type": "thinking", "content": content}
            else:
                if active_code_block:
                    active_code_block = False
                    yield {"type": "thinking", "content": "\n```\n"}

                if chunk_type == "message" and role == "assistant":
                    if isinstance(content, str):
                        assistant_buffer += content
                        yield {"type": "thinking", "content": content}
                elif chunk_type == "console" and chunk.get("format") == "output":
                    if isinstance(content, str):
                        computer_buffer += content
                        yield {"type": "thinking", "content": content}
                elif role == "computer":
                    if isinstance(content, list):
                        for item in content:
                            out = (
                                item.get("output", item.get("content", ""))
                                if isinstance(item, dict)
                                else ""
                            )
                            if out:
                                computer_buffer += str(out)
                                yield {"type": "thinking", "content": str(out)}
                    elif isinstance(content, str):
                        computer_buffer += content
                        yield {"type": "thinking", "content": content}

        if active_code_block:
            yield {"type": "thinking", "content": "\n```\n"}

        flush_assistant()

        result = "\n\n".join(p for p in parts if p).strip()
        if not result:
            result = computer_buffer.strip()
        logger.info(f"[OI] chat completed: {task[:80]!r}")

        try:
            from src.iris.engine import unload_model

            unload_model(ModelRole.CODE.value)
            logger.info("[OI] Unloaded CODE model to free memory.")
        except Exception as ue:
            logger.warning(f"[OI] Could not unload CODE model: {ue}")

        return result or "Task completed (no output)."
    except Exception as e:
        logger.error(f"[OI] chat error: {e}")
        return f"Could not execute via OI: {e}"


import ssl
import urllib.error
import urllib.parse
import urllib.request
import warnings
import webbrowser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

warnings.filterwarnings("ignore")

try:
    from rich.align import Align
    from rich.box import DOUBLE, ROUNDED
    from rich.console import Console
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text

    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

IS_INTERACTIVE = True

ROUTER_KEYWORDS: dict = {
    "medical": [
        "symptom",
        "symptoms",
        "diagnosis",
        "diagnose",
        "treatment",
        "medicine",
        "medication",
        "doctor",
        "health",
        "disease",
        "pain",
        "hospital",
        "surgery",
        "patient",
        "clinical",
        "therapy",
        "drug",
        "prescription",
        "fever",
        "injury",
        "chronic",
        "infection",
        "vaccine",
        "anatomy",
        "blood",
        "heart",
        "lung",
    ],
    "coding": [
        "python",
        "javascript",
        "typescript",
        "function",
        "code",
        "debug",
        "error",
        "import",
        "class",
        "algorithm",
        "variable",
        "loop",
        "array",
        "api",
        "sql",
        "database",
        "framework",
        "library",
        "bug",
        "syntax",
        "compile",
        "runtime",
        "async",
        "thread",
        "git",
        "docker",
        "linux",
        "bash",
        "script",
        "regex",
        "html",
        "css",
        "react",
        "node",
        "flask",
        "django",
        "mlx",
        "pytorch",
        "c++",
        "cpp",
        "codeforces",
        "leetcode",
        "competitive",
    ],
    "finance": [
        "tax",
        "taxes",
        "budget",
        "expense",
        "expenses",
        "investment",
        "invest",
        "stock",
        "stocks",
        "money",
        "salary",
        "income",
        "profit",
        "loss",
        "revenue",
        "accounting",
        "bank",
        "loan",
        "mortgage",
        "interest",
        "rate",
        "crypto",
        "bitcoin",
        "portfolio",
        "dividend",
        "inflation",
        "economy",
        "financial",
    ],
}


def route_category(text: str) -> Optional[str]:
    lower = text.lower()
    scores: dict = {}
    for cat, keywords in ROUTER_KEYWORDS.items():
        score = sum(
            1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", lower)
        )
        if score:
            scores[cat] = score
    if not scores:
        return None
    best = max(scores, key=scores.__getitem__)
    logger.info(f"[Router] Category='{best}' (scores={scores})")
    return best


import html as _html

_WEB_SEARCH_TRIGGERS = re.compile(
    r"""(?xi)
    \b(
      what | who  | when | where | why  | how  | which | whose |
      latest | recent | current | today | news | update | price |
      weather | score | result | explain | define | meaning | tell\s+me |
      search | look\s+up | find\s+out | is\s+it | are\s+there |
      difference\s+between | compare | vs\.?
    )\b
    |
    \?$                         # ends with a question mark
    """,
    re.IGNORECASE,
)


def should_web_search(text: str) -> bool:
    """Determine if web search is likely beneficial based on trigger words."""
    if len(text.split()) < 3:
        return False
    return bool(_WEB_SEARCH_TRIGGERS.search(text))


def web_search(query: str, max_results: int = 5) -> str:

    try:
        lang = detect_user_language(query)
        if lang and lang != "English":
            translated = translate_text(query, "English")
            if translated and translated != query:
                logger.info(
                    f"[Controller WebSearch] Translated search query '{query}' to English: '{translated}'"
                )
                query = translated
    except Exception as e:
        logger.warning(f"[Controller WebSearch] Failed to translate query: {e}")

    try:
        q = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={q}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="ignore")

        titles = re.findall(
            r'class=["\']result__a["\'][^>]*>(.*?)</a>',
            body,
            re.DOTALL,
        )

        snippets = re.findall(
            r'class=["\']result__snippet["\'][^>]*>(.*?)</(?:a|span)>',
            body,
            re.DOTALL,
        )

        def clean(s: str) -> str:
            s = re.sub(r"<[^>]+>", "", s)
            return _html.unescape(s).strip()

        results = []
        for i, (t, s) in enumerate(zip(titles[:max_results], snippets[:max_results])):
            t, s = clean(t), clean(s)
            if t or s:
                results.append(f"[Result {i + 1}] {t}\n{s}")

        if not results:
            return "(No web results found for this query.)"

        return "\n\n".join(results)

    except Exception as exc:
        return f"(Web search unavailable: {exc})"


CLIPBOARD_AVAILABLE = True
try:
    from src.iris.iris import ask_stream
    from src.iris.rag import BookRetriever
    from src.iris.vision import analyze_image

    IRIS_AVAILABLE = True
except ImportError:
    IRIS_AVAILABLE = False
    logger.warning(
        "[WARNING] iris.py not found or dependencies missing. Running in rule-only mode."
    )

MLX_MODEL_ID = os.environ.get("IRIS_MODEL_ID", "")
if not MLX_MODEL_ID:
    try:
        with open("./config/iris.conf") as f:
            cfg = json.load(f)
        MLX_MODEL_ID = cfg.get("size", "medium") + " tier"
    except:
        MLX_MODEL_ID = "Iris AI"

CONFIG_FILE = "./config/control.conf"

DEFAULT_CONFIG = {
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_address": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "contacts": {},
    },
    "browser": "default",
}


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        logger.info(f"[INFO] Created config template at {CONFIG_FILE}")
        logger.info(
            "       Edit it with your email credentials and app paths before sending mail."
        )
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception as e:
        logger.error(
            f"[ERROR] Failed to load {CONFIG_FILE}: {e}. Using default config."
        )
        return DEFAULT_CONFIG


import os

_prompt_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "training", "control", "control.md"
)
try:
    with open(_prompt_path, "r", encoding="utf-8") as f:
        _content = f.read().strip()

        _train_idx = _content.find("# TRAINING DATA")
        if _train_idx == -1:
            _train_idx = _content.find("#  TRAINING DATA")
        if _train_idx == -1:
            _train_idx = _content.find("# ═══════════")
        if _train_idx != -1:
            _content = _content[:_train_idx].strip()
        else:
            _content = "\n".join(_content.splitlines()[:144]).strip()

        if _content.startswith("SYSTEM:"):
            AI_AGENT_SYSTEM_PROMPT = _content[7:].strip()
        else:
            AI_AGENT_SYSTEM_PROMPT = _content
except Exception as e:
    logger.warning(f"[WARNING] Failed to load training/control.md: {e}")
    AI_AGENT_SYSTEM_PROMPT = (
        "You are an AI PC assistant. Please respond with JSON actions."
    )

MAX_SYS_PROMPT_CHARS = 4096

_agent_prompt_cache = {"text": None, "mtime": 0}


def _get_agent_system_prompt() -> str:

    global _agent_prompt_cache
    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "training", "control", "control.md"
    )
    try:
        mtime = os.path.getmtime(path)
        if _agent_prompt_cache["text"] is None or mtime != _agent_prompt_cache["mtime"]:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            train_idx = content.find("# TRAINING DATA")
            if train_idx == -1:
                train_idx = content.find("#  TRAINING DATA")
            if train_idx == -1:
                train_idx = content.find("# ═══════════")
            if train_idx != -1:
                content = content[:train_idx].strip()
            else:
                content = "\n".join(content.splitlines()[:144]).strip()

            text = content[7:].strip() if content.startswith("SYSTEM:") else content
            _agent_prompt_cache = {"text": text, "mtime": mtime}
        return _agent_prompt_cache["text"]
    except Exception as e:
        logger.warning(f"[ERROR] Failed to load or truncate system prompt: {e}")
        return AI_AGENT_SYSTEM_PROMPT


_reply_prefix_cache: dict = {"key": None, "prompt": None}


def handle_run_code(code: str) -> str:

    import tempfile

    if not code or not code.strip():
        return "No code provided to execute."
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        tmp_path = f.name
    try:
        result = _shell(
            ["python3", tmp_path], capture_output=True, text=True, timeout=15
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if stdout and stderr:
            return f"```python\n{code}\n```\n\nOutput:\n{stdout[:1500]}\n\nErrors:\n{stderr[:500]}"
        if stdout:
            return f"```python\n{code}\n```\n\nOutput:\n{stdout[:2000]}"
        if stderr:
            return f"```python\n{code}\n```\n\nError:\n{stderr[:2000]}"
        return f"```python\n{code}\n```\n\n(No output)"
    except _subprocess.TimeoutExpired:
        return "Code execution timed out (15s limit)."
    except Exception as e:
        return f"Execution failed: {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def parse_ai_response(text: str) -> dict | None:

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:

        raw = match.group()
        fixed_json = re.sub(
            r"(:\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*[,}])", r'\1"\2"\3', raw
        )
        fixed_json = fixed_json.replace('"True"', "true").replace('"False"', "false")
        try:
            return json.loads(fixed_json)
        except json.JSONDecodeError:
            return None


def ai_agent_handle(user_input: str, retriever=None, history=None, **kwargs):
    history = history or []
    force_role = kwargs.get("force_role") or getattr(
        ai_agent_handle, "force_role", None
    )
    settings = kwargs.get("settings", {})
    from src.iris.iris import ask_stream

    keep_loaded = kwargs.get("keep_loaded", False)
    yield from ask_stream(
        user_input,
        history,
        retriever=retriever,
        force_role=force_role,
        settings=settings,
        keep_loaded=keep_loaded,
    )


def ai_agent_handle_pro(user_input: str, retriever=None, history=None, **kwargs):

    import asyncio
    import queue
    import threading

    import src.iris.pro as iris_pro

    q = queue.Queue()
    mode = kwargs.get("settings", {}).get("mode", "smart")

    def run_async():
        async def task():
            try:
                agen = iris_pro.ask_stream(
                    user_input, history or [], mode=mode, workspace_root=os.getcwd()
                )
                async for event in agen:
                    q.put(event)
            except Exception as e:
                q.put(e)
            finally:
                q.put(None)

        asyncio.run(task())

    t = threading.Thread(target=run_async)
    t.start()

    while True:
        item = q.get()
        if item is None:
            break
        if isinstance(item, Exception):
            yield {
                "type": "raw_response",
                "content": f"\n\n> [ERROR] **Iris Pro Error:** {item}",
            }
            break
        yield item


def _handle_check_storage(action_dict: dict) -> str:

    import shutil

    path = action_dict.get("path", "/")
    if platform.system() == "Windows":
        path = "C:\\"
    try:
        total, used, free = shutil.disk_usage(path)
        if total == 0:
            return f"Disk Usage for {path}: Unable to determine (total space is 0)"
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)
        percent = (used / total) * 100
        return (
            f"Disk Usage for {path}:\n"
            f"  Total: {total_gb:.1f} GB\n"
            f"  Used:  {used_gb:.1f} GB ({percent:.1f}%)\n"
            f"  Free:  {free_gb:.1f} GB"
        )
    except Exception as e:
        return f"Failed to check disk usage: {e}"


def is_risky_action(action_dict: dict) -> bool:

    action = action_dict.get("action", "")
    if action in _RISKY_ACTIONS:
        return True
    if action in ("run_command", "open_terminal"):
        return bool(_RISKY_CMD_RE.search(str(action_dict.get("command", ""))))
    return False


def _confirm_risky(action_dict: dict) -> bool:

    if not IS_INTERACTIVE:
        return False
    action = action_dict.get("action", "")
    detail = json.dumps(
        {k: v for k, v in action_dict.items() if k != "action"}, ensure_ascii=False
    )
    if RICH_AVAILABLE:
        console.print(
            f"  [bold red]⚠ Confirm risky action[/bold red]: "
            f"[bold magenta]{action}[/bold magenta] {detail}"
        )
        ans = (
            Prompt.ask("  [bold]Proceed?[/bold]", choices=["y", "n"], default="n")
            .strip()
            .lower()
        )
    else:
        ans = (
            input(f"  ⚠ Confirm risky action '{action}' {detail} — proceed? [y/N]: ")
            .strip()
            .lower()
        )
    return ans == "y"


def _run_generator_to_completion(gen) -> Any:
    while True:
        try:
            next(gen)
        except StopIteration as e:
            return e.value


def execute_action_by_dict(action_dict: dict) -> str:

    action = action_dict.get("action", "chat")

    if action in ("chat", "finish", "none", ""):
        return ""

    logger.info(f"[Action] {action} → routing to OI for execution")
    task_parts = [
        f"Please perform the following action on my system:\nAction: {action}"
    ]
    for key, val in action_dict.items():
        if key != "action":
            task_parts.append(f"{key}: {val}")
    task_str = "\n".join(task_parts)

    _prime_oi_with_control()
    return _run_generator_to_completion(_run_oi_task(task_str))


_AGENT_LOOP_ADDENDUM = """

# ===============================================================================
# AGENT LOOP PROTOCOL
# ===============================================================================
You operate as a multi-step agent. A single request may need several actions.

- Emit exactly ONE JSON action per turn (optionally preceded by a brief <think>).
- After each action runs, you receive an `OBSERVATION:` message with the result.
  Read it, then decide the next action.
- When the task is fully complete, emit:
  {"action": "finish", "summary": "<one-line summary of what you accomplished>"}
- If the task is a single step, do that step, then on the next turn emit finish.
- If an OBSERVATION shows an error, diagnose it and try a different action.
- Use the "chat" action only for pure conversation that needs no execution.
"""


def _prime_oi_with_control():
    _init_oi()
    if not OI_AVAILABLE:
        return

    try:
        load_model(ModelRole.CONTROL)
        logger.info("[OI] Primed with CONTROL model for action.")
    except Exception as e:
        logger.warning(f"[OI] Could not prime CONTROL model: {e}")


def _generate_control_action(
    messages: list, user_query: str = "", max_tokens: int = 1024
) -> str:
    logger.info("[Model] Using CONTROL model for control action")
    try:
        llm = load_model(ModelRole.CONTROL)
    except FileNotFoundError:
        logger.warning("[Model] Controller disabled: Control model not found.")
        return ""

    out = ""
    for chunk in llm.create_chat_completion(
        messages=messages, max_tokens=max_tokens, stream=True, temperature=0.1
    ):
        delta = chunk["choices"][0].get("delta", {})
        if "content" in delta and delta["content"]:
            out += delta["content"]
    return out


def agentic_control_loop(
    user_query: str,
    history: list = None,
    max_steps: int = 8,
    settings: dict = None,
    model_callable=None,
):
    yield {"type": "status", "content": "Executing command via Open Interpreter..."}
    result = yield from _run_oi_task(user_query)
    reply_text = f"Executed via Open Interpreter.\n\nResult:\n{result}"
    yield {
        "type": "action_result",
        "content": f"Executed via Open Interpreter.\nResult:\n{result}",
    }
    yield {"type": "token", "content": reply_text}
    yield {"type": "raw_response", "content": reply_text}
    settings = settings or {}
    if not settings.get("keep_loaded"):
        _unload_control_model()


def _join_transcript(transcript: list) -> str:
    if not transcript:
        return ""
    return "Here's what I did:\n" + "\n".join(f"- {t}" for t in transcript)


def _unload_control_model():
    try:
        from src.iris.iris import unload_model

        unload_model()
    except Exception:
        pass


def load_iris_model():
    return None, None, None


def iris_chat_reply(
    model, tokenizer, device, retriever, history: list, user_text: str
) -> str:

    if model is None:
        return "(Iris model not loaded — only PC-control commands work right now.)"

    rag_category = route_category(user_text)
    context = (
        retriever.retrieve(user_text, top_k=3, category=rag_category)
        if retriever
        else ""
    )

    web_results = ""
    if should_web_search(user_text):
        log_action("search", f"Searching for: {user_text}")
        web_results = web_search(user_text)

    sys_prompt = _get_agent_system_prompt()

    if context:
        sys_prompt += (
            " Use the following reference material to answer accurately if relevant:\n\n"
            f"REFERENCE EXCERPT:\n{context}"
        )

    if web_results:
        sys_prompt += (
            "\n\nWEB SEARCH RESULTS (fetched live — use these to give an "
            "accurate, up-to-date answer):\n"
            f"{web_results}"
        )

    history.append({"role": "user", "content": user_text})

    prefix_msgs = [{"role": "system", "content": sys_prompt}] + history[-20:-1]
    prefix_key = hash(json.dumps(prefix_msgs, ensure_ascii=False, sort_keys=True))

    if (
        _reply_prefix_cache["key"] == prefix_key
        and _reply_prefix_cache["prompt"] is not None
    ):
        last_turn = tokenizer.apply_chat_template(
            history[-1:], tokenize=False, add_generation_prompt=False
        )
        prompt = _reply_prefix_cache["prompt"] + last_turn
    else:
        ctx = [{"role": "system", "content": sys_prompt}] + history[-20:]
        prompt = tokenizer.apply_chat_template(
            ctx, tokenize=False, add_generation_prompt=True
        )

        prefix_prompt = tokenizer.apply_chat_template(
            prefix_msgs, tokenize=False, add_generation_prompt=False
        )
        _reply_prefix_cache["key"] = prefix_key
        _reply_prefix_cache["prompt"] = prefix_prompt

    def generate_reply(model, tokenizer, prompt, device):
        return "(Reply generation is currently disabled or unimplemented)"

    reply = generate_reply(model, tokenizer, prompt, device)

    history.append({"role": "assistant", "content": reply})
    return reply


HELP_TEXT = """
Commands you can use:

AI‑powered actions (just say what you want):
  • web & media       → "open a website", "play a song on spotify", "youtube: lofi hip hop"
  • files & folders   → "open the budget.xlsx", "search for .pdf in Downloads"
  • system commands   → "ping google.com", "what's my hostname?"
  • volume & brightness → "volume up", "set brightness to %"
  • clipboard          → "copy this to clipboard", "read clipboard"
  • system info        → "how much RAM?", "what's my IP?"
  • Knowledge Base     → "What happened in chapter 3 of my book?"
  • AI Coder           → "Fix the bugs in app.py"
  • Any natural language request → Iris decides the right action!

  help                             → show this message
  quit / exit                      → close the controller
"""


def print_banner():
    banner_text = r"""
  _____  _____   _____   _____             _____
 |_   _||  __ \ |_   _| / ____|    /\     |_   _|
   | |  | |__) |  | |  | (___     /  \      | |
   | |  |  _  /   | |   \___ \   / /\ \     | |
  _| |_ | | \ \  _| |_  ____) | / ____ \   _| |_
 |_____||_|  \_\|_____||_____/ /_/    \_\ |_____|

    """
    if RICH_AVAILABLE:
        console.print(Align.center(Text(banner_text, style="bold cyan")))
        console.print(
            Align.center(
                Text(
                    "Natural-language control of your computer, powered by Iris",
                    style="italic green",
                )
            )
        )
        console.print()
    else:
        logger.info("=" * 60)
        logger.info("  Iris AI PC Agent (RAG Enabled)")
        logger.info("  Type 'help' for commands, 'quit' to exit.")
        logger.info("=" * 60)


def print_system_status(model=None, retriever=None):
    if not RICH_AVAILABLE:
        return
    table = Table(show_header=False, box=ROUNDED, border_style="dim cyan", width=60)
    table.add_column("Key", style="bold yellow")
    table.add_column("Value", style="green")

    import platform as pf

    model_name = "iris_14b_model" if os.path.isdir("./iris_14b_model") else MLX_MODEL_ID
    table.add_row("Model", model_name if IRIS_AVAILABLE else "Rule-only Mode")
    table.add_row("Device", str(get_device().type) if IRIS_AVAILABLE else "CPU")
    table.add_row("OS", f"{pf.system()} {pf.release()} ({pf.machine()})")

    try:
        import psutil

        mem = psutil.virtual_memory()
        ram_info = f"{mem.total / (1024**3):.1f} GB total, {mem.percent}% used"
    except ImportError:
        ram_info = "N/A"
    table.add_row("Memory", ram_info)

    rag_status = "Loaded" if retriever and retriever.chunks else "Disabled"
    if retriever and retriever.chunks:
        rag_status += f" ({len(retriever.chunks)} chunks)"
    table.add_row("RAG Database", rag_status)

    config_status = (
        "Loaded (control.conf)" if os.path.exists(CONFIG_FILE) else "Using Defaults"
    )
    table.add_row("Config", config_status)

    console.print(Align.center(table))


from rich.console import Group


def format_assistant_message(content: str, is_active: bool = False):
    if not content:
        return Text("")

    think_content = ""

    def replace_think(match):
        nonlocal think_content
        think_content = match.group(1).strip()
        return ""

    work = re.sub(
        r"<think>([\s\S]*?)(?:</think>|$)", replace_think, content, flags=re.IGNORECASE
    )

    action_text = ""
    chat_response = ""

    def replace_action(match):
        nonlocal action_text, chat_response
        raw_json = match.group(0)
        try:
            obj = json.loads(raw_json)
            action = obj.get("action", "chat")
            if action == "chat":
                chat_response = obj.get("response", "").strip()
            else:
                action_text = f"⚙️ Action: [bold magenta]{action}[/bold magenta] {json.dumps({k: v for k, v in obj.items() if k != 'action'}, ensure_ascii=False)}"
        except:
            chat_response = raw_json
        return ""

    work = re.sub(r'\{[\s]*"action"[\s]*:[\s\S]*?\}', replace_action, work)

    remaining = work.strip()

    renderables = []
    if think_content:
        from rich.panel import Panel

        if is_active:
            renderables.append(
                Panel(
                    Text.from_markup(f"[dim]{think_content}[/dim]"),
                    title="[dim]Thinking[/dim]",
                    title_align="left",
                    border_style="dim",
                    style="on #333333",
                )
            )
        else:
            renderables.append(
                Text.from_markup("[dim]💭 (Thought process omitted)[/dim]")
            )

    main_text = chat_response if chat_response else remaining
    if main_text:
        renderables.append(Markdown(main_text))

    if action_text:
        renderables.append(Text.from_markup(action_text))

    if not renderables:
        return Text("")
    return Group(*renderables)


_scroll_offset: int = 0


def _render_body_lines(history, cols: int, is_generating: bool = False) -> list[str]:

    measure_console = Console(color_system="truecolor", width=cols, highlight=False)
    table = Table(box=None, show_header=False, expand=True)
    table.add_column("Role", style="bold", width=10)
    table.add_column("Message")
    for i, msg in enumerate(history):
        role = "You" if msg["role"] == "user" else "Iris"
        role_style = "bold yellow" if msg["role"] == "user" else "bold green"
        is_active = is_generating and (i == len(history) - 1)
        content_render = (
            Markdown(msg["content"])
            if msg["role"] == "user"
            else format_assistant_message(msg["content"], is_active=is_active)
        )
        table.add_row(Text(role, style=role_style), content_render)
    with measure_console.capture() as cap:
        measure_console.print(table)
    return cap.get().splitlines()


def get_visible_history(history, body_height):

    if not RICH_AVAILABLE:
        return history
    return history


def draw_layout(
    model, tokenizer, retriever, history, status_text=None, is_generating=False
):
    global _scroll_offset
    if not RICH_AVAILABLE:
        return

    cols, rows = shutil.get_terminal_size()

    import platform as pf

    try:
        import psutil

        mem = psutil.virtual_memory()
        ram_info = f"{mem.total / (1024**3):.1f}GB ({mem.percent}% used)"
    except Exception:
        ram_info = "N/A"

    rag_status = "Loaded" if retriever and retriever.chunks else "Disabled"
    if retriever and retriever.chunks:
        rag_status += f" ({len(retriever.chunks)} chunks)"

    model_name = "iris_14b_model" if os.path.isdir("./iris_14b_model") else MLX_MODEL_ID

    status_line = (
        f" Model: [bold cyan]{model_name}[/bold cyan]"
        f" │ Device: [bold cyan]{get_device().type if IRIS_AVAILABLE else 'CPU'}[/bold cyan]"
        f" │ OS: [bold cyan]{pf.system()}[/bold cyan]"
        f" │ RAM: [bold cyan]{ram_info}[/bold cyan]"
        f" │ RAG: [bold cyan]{rag_status}[/bold cyan]"
    )

    divider = "─" * cols

    footer_msg = " Type '/help' for commands │ '/exit' to quit │ '/restart' to restart │ Ask anything in natural language"
    if status_text:
        footer_msg = f" [bold yellow]Status: {status_text}[/bold yellow] │{footer_msg}"

    reserved_height = 5
    body_height = max(5, rows - reserved_height)

    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

    console.print(status_line)
    console.print(Text(divider, style="dim cyan"))

    if not history:
        welcome_md = """# Iris AI CLI

This is a full-featured terminal interface for controlling your computer and chatting with Iris.

### Key Capabilities:
- **File System Operations**: Create, read, edit, delete, compress, or search files.
- **System Controls**: Adjust volume, brightness, run terminal commands, or get system information.
- **Web Integrations**: Search DuckDuckGo, open websites, search YouTube/Spotify.
- **RAG Memory**: Search local files in the `raw_data/` directory.
"""
        console.print(Markdown(welcome_md))
    else:

        all_lines = _render_body_lines(history, cols - 2, is_generating=is_generating)
        total_lines = len(all_lines)

        max_offset = max(0, total_lines - body_height)

        _scroll_offset = max(0, min(_scroll_offset, max_offset))

        start = max_offset - _scroll_offset
        end = start + body_height
        visible_lines = all_lines[start:end]

        for line in visible_lines:
            sys.stdout.write(line + "\n")

        for _ in range(body_height - len(visible_lines)):
            sys.stdout.write("\n")

        if total_lines > body_height:
            pct = int(100 * (start + body_height) / total_lines)
            scroll_hint = f" ↑↓ scroll ({pct}%) "
            footer_msg = f"[dim]{scroll_hint}[/dim] │{footer_msg}"

    console.print(Text(divider, style="dim cyan"))
    console.print(Text.from_markup(footer_msg, style="dim white"))


def get_prompt_text() -> str:
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        cwd_short = cwd.replace(home, "~", 1)
    else:
        cwd_short = cwd

    prompt = Text()
    prompt.append("\niris ", style="bold cyan")
    prompt.append(cwd_short, style="bold blue")
    prompt.append(" ❯ ", style="bold green")
    return prompt


SLASH_COMMANDS = {
    "/help": "Show this help menu",
    "/clear": "Clear the screen",
    "/status": "Show detailed system and environment status",
    "/config": "View current config values (control.conf)",
    "/history": "Print recent chat history in this session",
    "/model": "Show details of the active model and config parameters",
    "/exit": "Quit the controller",
    "/quit": "Quit the controller",
    "/restart": "Restart the controller and model",
}


def show_help_menu():
    if not RICH_AVAILABLE:
        logger.info(HELP_TEXT)
        return
    table = Table(title="Iris CLI Commands", box=ROUNDED, border_style="cyan")
    table.add_column("Command", style="bold yellow")
    table.add_column("Description", style="green")

    for cmd, desc in SLASH_COMMANDS.items():
        table.add_row(cmd, desc)

    table.add_row("exit / quit", "Quit the controller")
    table.add_row("restart", "Restart the controller and model")
    table.add_row("help", "Show this help menu")
    table.add_row("clear", "Clear the screen")

    console.print(table)

    console.print("\n[bold cyan]Example Natural Language Requests:[/bold cyan]")
    console.print(
        "  • [bold green]Files[/bold green]: 'open the budget.xlsx', 'search for .pdf in Downloads'"
    )
    console.print(
        "  • [bold green]System[/bold green]: 'ping google.com', 'how much RAM?'"
    )
    console.print(
        "  • [bold green]Media[/bold green]: 'play shape of you on spotify', 'youtube: lofi hip hop'"
    )
    console.print("  • [bold green]AI Coder[/bold green]: 'fix bugs in app.py'")


def clear_screen(model=None, retriever=None):
    os.system("clear" if platform.system() != "Windows" else "cls")
    print_banner()


def show_detailed_status(model, tokenizer, retriever):
    if not RICH_AVAILABLE:
        return
    table = Table(
        title="System & Environment Status", box=ROUNDED, border_style="magenta"
    )
    table.add_column("Parameter", style="bold yellow")
    table.add_column("Value", style="green")

    import platform as pf
    import socket

    table.add_row("Platform", pf.platform())
    table.add_row("Processor", pf.processor())
    table.add_row("Python Version", sys.version.split()[0])

    try:
        import psutil

        mem = psutil.virtual_memory()
        table.add_row("RAM Total", f"{mem.total / (1024**3):.1f} GB")
        table.add_row("RAM Available", f"{mem.available / (1024**3):.1f} GB")
        table.add_row("RAM Percent", f"{mem.percent}%")
        cpu_pct = psutil.cpu_percent(interval=0.1)
        table.add_row("CPU Load", f"{cpu_pct}%")
    except ImportError:
        pass

    try:
        total, used, free = shutil.disk_usage("/")
        table.add_row("Disk Total", f"{total / (1024**3):.1f} GB")
        table.add_row("Disk Free", f"{free / (1024**3):.1f} GB")
    except:
        pass

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        table.add_row("Local IP", ip)
    except:
        pass

    model_name = "iris_14b_model" if os.path.isdir("./iris_14b_model") else MLX_MODEL_ID
    table.add_row("Model Loaded", model_name if IRIS_AVAILABLE else "None")
    table.add_row("Device type", str(get_device().type) if IRIS_AVAILABLE else "N/A")
    table.add_row("RAG Chunks", str(len(retriever.chunks)) if retriever else "N/A")

    console.print(table)


def show_config():
    if not RICH_AVAILABLE:
        logger.info(load_config())
        return
    config = load_config()
    config_str = json.dumps(config, indent=2)
    panel = Panel(
        Syntax(config_str, "json", theme="monokai", line_numbers=True),
        title=f"Configuration: {CONFIG_FILE}",
        border_style="yellow",
        box=ROUNDED,
    )
    console.print(panel)


def show_history(history):
    if not history:
        console.print("[yellow]No conversation history yet in this session.[/yellow]")
        return

    table = Table(
        title="Session History", box=ROUNDED, border_style="cyan", show_lines=True
    )
    table.add_column("Speaker", style="bold magenta", width=12)
    table.add_column("Message", style="white")

    for msg in history:
        role = "You" if msg["role"] == "user" else "Iris"
        role_style = "bold yellow" if msg["role"] == "user" else "bold green"
        table.add_row(Text(role, style=role_style), Markdown(msg["content"]))

    console.print(table)


def show_model_details():
    if not IRIS_AVAILABLE:
        console.print("[red]Iris model is not available or not loaded.[/red]")
        return

    from src.iris.iris import load_generation_config

    cfg = load_generation_config()

    table = Table(title="Active Model Settings", box=ROUNDED, border_style="green")
    table.add_column("Setting", style="bold yellow")
    table.add_column("Value", style="green")

    model_name = "iris_14b_model" if os.path.isdir("./iris_14b_model") else MLX_MODEL_ID
    table.add_row("Model ID", model_name)
    table.add_row("Max New Tokens", str(cfg.get("max_new_tokens", 256)))
    table.add_row("Temperature", str(cfg.get("temperature", 0.7)))
    table.add_row("Top P", str(cfg.get("top_p", 0.9)))
    table.add_row("Repetition Penalty", str(cfg.get("repetition_penalty", 1.0)))
    table.add_row("RAG Disabled", str(cfg.get("disable_rag", False)))

    console.print(table)


def _read_input_with_scroll(prompt_str, model, tokenizer, retriever, history) -> str:

    global _scroll_offset

    import os
    import sys

    try:
        import termios
        import tty
    except ImportError:

        console.print(prompt_str, end="")
        return input()

    cols, rows = shutil.get_terminal_size()
    reserved_height = 5
    body_height = max(5, rows - reserved_height)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    buf = []
    try:
        tty.setraw(fd)

        console.print(prompt_str, end="")
        sys.stdout.flush()

        while True:
            ch = sys.stdin.read(1)

            if ch == "\r" or ch == "\n":

                sys.stdout.write("\r\n")
                sys.stdout.flush()
                break

            elif ch == "\x03":

                raise KeyboardInterrupt

            elif ch == "\x04":

                raise EOFError

            elif ch == "\x7f" or ch == "\x08":

                if buf:
                    buf.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()

            elif ch == "\x1b":

                seq = sys.stdin.read(2)
                if seq in ("[A", "OA"):

                    _scroll_offset = min(_scroll_offset + (body_height // 3), 9999)
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    draw_layout(model, tokenizer, retriever, history)
                    tty.setraw(fd)
                    console.print(prompt_str, end="")
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                elif seq in ("[B", "OB"):

                    _scroll_offset = max(_scroll_offset - (body_height // 3), 0)
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    draw_layout(model, tokenizer, retriever, history)
                    tty.setraw(fd)
                    console.print(prompt_str, end="")
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                elif seq == "[5":

                    sys.stdin.read(1)
                    _scroll_offset = min(_scroll_offset + body_height, 9999)
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    draw_layout(model, tokenizer, retriever, history)
                    tty.setraw(fd)
                    console.print(prompt_str, end="")
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                elif seq == "[6":

                    sys.stdin.read(1)
                    _scroll_offset = max(_scroll_offset - body_height, 0)
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    draw_layout(model, tokenizer, retriever, history)
                    tty.setraw(fd)
                    console.print(prompt_str, end="")
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()

            elif ch >= " ":

                buf.append(ch)
                sys.stdout.write(ch)
                sys.stdout.flush()

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    _scroll_offset = 0
    return "".join(buf)


def main():
    import argparse

    from src.iris.iris import ModelRole

    parser = argparse.ArgumentParser(description="Iris AI PC Agent")
    parser.add_argument(
        "--model",
        choices=[m.value for m in ModelRole],
        default=None,
        help="Force using a single specific model role for all queries (bypasses routing).",
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use Iris Pro (cloud models) instead of local Iris.",
    )
    args, _ = parser.parse_known_args()

    global PRO_MODE
    PRO_MODE = args.pro
    if args.model:
        ai_agent_handle.force_role = ModelRole(args.model)

    config = load_config()

    if RICH_AVAILABLE:
        sys.stdout.write("\033[?1049h")
        sys.stdout.write("\033[H")
        sys.stdout.flush()

    try:
        if not PRO_MODE:
            if RICH_AVAILABLE:
                console.print("[bold yellow]Loading Iris LLM Core...[/bold yellow]")
            else:
                logger.info("[INFO] Loading Iris LLM Core...")
            model, tokenizer, device = load_iris_model()
        else:
            model, tokenizer, device = None, None, None
            if RICH_AVAILABLE:
                console.print("[bold cyan]Using Iris Pro (Cloud API)...[/bold cyan]")
            else:
                logger.info("[INFO] Using Iris Pro (Cloud API)...")

        retriever = None
        if IRIS_AVAILABLE:
            if RICH_AVAILABLE:
                console.print(
                    "[bold yellow]Initializing RAG Knowledge Base...[/bold yellow]"
                )
                try:
                    retriever = BookRetriever(raw_data_dir="raw_data")
                    retriever.load_and_index()
                except Exception as e:
                    console.print(f"[red][WARNING] Failed to load RAG: {e}[/red]")
            else:
                logger.info("[INFO] Initializing RAG Knowledge Base...")
                try:
                    retriever = BookRetriever(raw_data_dir="raw_data")
                    retriever.load_and_index()
                except Exception as e:
                    logger.warning(f"[WARNING] Failed to load RAG: {e}")
        history: list = []

        while True:
            if RICH_AVAILABLE:
                draw_layout(model, tokenizer, retriever, history)
                prompt_str = get_prompt_text()
                try:
                    raw = _read_input_with_scroll(
                        prompt_str, model, tokenizer, retriever, history
                    ).strip()
                except (EOFError, KeyboardInterrupt):
                    break
            else:
                try:
                    raw = input("\nYou: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

            if not raw:
                continue

            lower = raw.lower()

            if (raw.startswith("/") and not lower.startswith("/route ")) or lower in (
                "help",
                "clear",
                "exit",
                "quit",
                "status",
                "config",
                "history",
                "model",
                "restart",
            ):
                cmd = raw.split()[0].lower()
                if cmd == "/exit" or cmd == "/quit" or cmd in ("exit", "quit"):
                    break
                elif cmd == "/restart" or cmd == "restart":
                    if RICH_AVAILABLE:
                        console.print("[bold yellow]Restarting Iris...[/bold yellow]")
                    else:
                        logger.info("Restarting Iris...")
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                elif cmd == "/help" or cmd in ("help", "?"):
                    show_help_menu()
                    if RICH_AVAILABLE:
                        console.input("\nPress Enter to return to chat...")
                    continue
                elif cmd == "/clear" or cmd == "clear":
                    history.clear()
                    continue
                elif cmd == "/status" or cmd == "status":
                    show_detailed_status(model, tokenizer, retriever)
                    if RICH_AVAILABLE:
                        console.input("\nPress Enter to return to chat...")
                    continue
                elif cmd == "/config" or cmd == "config":
                    show_config()
                    if RICH_AVAILABLE:
                        console.input("\nPress Enter to return to chat...")
                    continue
                elif cmd == "/history" or cmd == "history":
                    show_history(history)
                    if RICH_AVAILABLE:
                        console.input("\nPress Enter to return to chat...")
                    continue
                elif cmd == "/model" or cmd == "model":
                    show_model_details()
                    if RICH_AVAILABLE:
                        console.input("\nPress Enter to return to chat...")
                    continue
                else:
                    if RICH_AVAILABLE:
                        console.print(
                            f"[red]Unknown command: {cmd}. Type /help for assistance.[/red]"
                        )
                        console.input("\nPress Enter to return to chat...")
                    else:
                        logger.info(f"Unknown command: {cmd}")
                    continue

            try:
                display_history = list(history)
                display_history.append({"role": "user", "content": raw})
                display_history.append({"role": "assistant", "content": ""})

                status_text = "Thinking..."
                if RICH_AVAILABLE:
                    draw_layout(
                        model,
                        tokenizer,
                        retriever,
                        display_history,
                        status_text=status_text,
                        is_generating=True,
                    )

                reply_parts = []
                final_reply = None

                agent_gen = (
                    ai_agent_handle_pro(raw, retriever, history)
                    if PRO_MODE
                    else ai_agent_handle(raw, retriever, history)
                )

                in_thinking_stream = False
                for event in agent_gen:
                    ev_type = event.get("type")
                    content = event.get("content", "")

                    if ev_type == "status":
                        status_text = content
                        if RICH_AVAILABLE:
                            draw_layout(
                                model,
                                tokenizer,
                                retriever,
                                display_history,
                                status_text=status_text,
                                is_generating=True,
                            )
                        else:
                            logger.info(f"[{status_text}]")
                    elif ev_type == "clear":
                        reply_parts.clear()
                        in_thinking_stream = False
                        display_history[-1]["content"] = ""
                        if RICH_AVAILABLE:
                            draw_layout(
                                model,
                                tokenizer,
                                retriever,
                                display_history,
                                status_text="Refining...",
                                is_generating=True,
                            )
                        else:
                            logger.info("\n--- Clearing generation buffer ---")
                    elif ev_type == "thinking":
                        if not in_thinking_stream:
                            reply_parts.append("\n<think>\n")
                            in_thinking_stream = True
                        reply_parts.append(content)
                        display_history[-1]["content"] = "".join(reply_parts)
                        if RICH_AVAILABLE:
                            draw_layout(
                                model,
                                tokenizer,
                                retriever,
                                display_history,
                                status_text="Thinking...",
                                is_generating=True,
                            )
                        else:
                            logger.info(content, end="", flush=True)
                    elif ev_type == "token":
                        if in_thinking_stream:
                            reply_parts.append("\n</think>\n")
                            in_thinking_stream = False
                        reply_parts.append(content)
                        display_history[-1]["content"] = "".join(reply_parts)
                        if RICH_AVAILABLE:
                            draw_layout(
                                model,
                                tokenizer,
                                retriever,
                                display_history,
                                status_text="Responding...",
                                is_generating=True,
                            )
                        else:
                            logger.info(content, end="", flush=True)
                    elif ev_type == "action_result":
                        if in_thinking_stream:
                            reply_parts.append("\n</think>\n")
                            in_thinking_stream = False
                        display_history.insert(
                            -1,
                            {
                                "role": "assistant",
                                "content": f"Running action returned:\n{content.strip()}",
                            },
                        )
                        if RICH_AVAILABLE:
                            draw_layout(
                                model,
                                tokenizer,
                                retriever,
                                display_history,
                                status_text="Executing action...",
                                is_generating=True,
                            )
                        else:
                            logger.info(f"\n[Action Output]\n{content}")
                    elif ev_type == "raw_response":
                        final_reply = content

                if in_thinking_stream:
                    reply_parts.append("\n</think>\n")
                    in_thinking_stream = False

                if final_reply is None:
                    final_reply = "".join(reply_parts)
                history.append({"role": "user", "content": raw})
                history.append({"role": "assistant", "content": final_reply})

                try:
                    code_blocks = re.findall(r"```(\w*)\n([\s\S]*?)```", final_reply)
                    for i, (lang, code) in enumerate(code_blocks):
                        filename = None
                        for line in code.splitlines()[:3]:
                            m = re.search(
                                r"^\s*(?://|#|/\*|<!--)\s*([a-zA-Z0-9_\-\./\\]+\.[a-zA-Z0-9]+)",
                                line,
                            )
                            if m:
                                filename = m.group(1).strip()
                                break
                        if not filename:
                            ext = lang.strip().lower() or "txt"
                            ext_map = {
                                "python": "py",
                                "javascript": "js",
                                "typescript": "ts",
                                "cpp": "cpp",
                                "c": "c",
                                "java": "java",
                                "html": "html",
                                "css": "css",
                                "bash": "sh",
                                "sh": "sh",
                            }
                            ext = ext_map.get(ext, ext)
                            filename = f"generated_code_{i + 1}.{ext}"

                        file_path = os.path.join(
                            os.getcwd(), os.path.basename(filename)
                        )
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(code.strip() + "\n")

                        if RICH_AVAILABLE:
                            console.print(
                                f"[dim green]Auto-saved code block to: {file_path}[/dim green]"
                            )
                        else:
                            logger.info(f"Auto-saved code to: {file_path}")
                except Exception as save_err:
                    if not RICH_AVAILABLE:
                        logger.warning(f"Failed to auto-save code block: {save_err}")

            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[red]Error: {e}[/red]")
                    console.input("\nPress Enter to return to chat...")
                else:
                    logger.warning(f"Error: {e}")
    finally:
        if RICH_AVAILABLE:
            sys.stdout.write("\033[?1049l")
            sys.stdout.flush()
        logger.info("Goodbye!")


if __name__ == "__main__":
    main()
=======
import os
import platform
import sys


def _ensure_open_interpreter():
    try:
        import interpreter as _test
    except ImportError:
        import subprocess as _sp

        print("\n[Iris] Installing open-interpreter — one-time setup...", flush=True)
        pip_args = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-q",
            "--upgrade",
            "open-interpreter",
        ]
        if platform.system() == "Linux":
            pip_args.append("--break-system-packages")
        env = os.environ.copy()
        env["PYO3_USE_ABI3_FORWARD_COMPATIBILITY"] = "1"
        _sp.run(pip_args, check=True, env=env)
        print("[Iris] open-interpreter installed ✓\n", flush=True)


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.logger import get_logger
from src.iris.engine import (
    detect_user_language,
    translate_text,
    _model_pool,
    load_model,
    ModelRole,
    get_hardware_profile,
    get_device,
)

logger = get_logger("controller")


import json
import platform
import re
import shutil
import smtplib
import subprocess
import subprocess as _subprocess
import time
from pathlib import Path
from typing import Optional, Generator, Dict, Any, List, Tuple, Union

OI_AVAILABLE = False
_oi = None
_oi_initialized = False
_oi_step_counter = 0


def _get_oi_system_message() -> str:
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "skills",
        "prompts",
        "oi_system_message.txt",
    )
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning(f"[WARNING] Prompt file not found: {path}")
        return "You are an AI PC assistant. Please write and execute code."


def _init_oi():
    global _oi, OI_AVAILABLE, _oi_initialized
    if _oi_initialized:
        if _oi is not None:
            _oi.system_message = _get_oi_system_message()
        return
    _oi_initialized = True

    _ensure_open_interpreter()

    try:
        from interpreter import interpreter as open_interpreter

        _oi = open_interpreter

        _oi.auto_run = True
        _oi.verbose = False
        _oi.max_output = 4000
        _oi.offline = True
        _oi.sync_computer = False
        _oi.loop = False

        _oi.llm.supports_functions = False
        _oi.llm.supports_vision = False

        def _iris_native_oi_llm(*args, **kwargs):

            global _oi_step_counter
            _oi_step_counter += 1
            if _oi_step_counter > 1:
                yield {
                    "choices": [
                        {
                            "delta": {"content": "Stopped after executing 1 step."},
                            "finish_reason": "stop",
                        }
                    ]
                }
                return

            try:
                load_model(ModelRole.CODE)
            except FileNotFoundError:
                yield {
                    "choices": [
                        {
                            "delta": {
                                "content": "Controller disabled: Code model not found."
                            },
                            "finish_reason": "stop",
                        }
                    ]
                }
                return

            model_obj = _model_pool[ModelRole.CODE.value]

            clean_kwargs = {
                "messages": kwargs.get("messages", []),
                "stream": True,
                "max_tokens": 1024,
                "temperature": 0.1,
                "stop": [
                    "<|im_end|>",
                    "<|im_start|>",
                    "<|endoftext|>",
                    "</s>",
                    "## Conversation",
                    "<step_end>",
                ],
            }

            for chunk in model_obj.create_chat_completion(**clean_kwargs):
                yield chunk

        _oi.llm.completions = _iris_native_oi_llm
        _oi.llm.api_base = None
        _oi.llm.model = "iris-native"
        _oi.llm.context_window = 8192
        _oi.llm.max_tokens = 1024

        _oi.system_message = _get_oi_system_message()

        OI_AVAILABLE = True
        logger.info("[OI] Open Interpreter ready (offline mode) ✓")

    except Exception as _oi_err:
        OI_AVAILABLE = False
        logger.warning(f"[OI] Open Interpreter unavailable: {_oi_err}")


class _FakeResult:

    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def _shell(cmd, **kw) -> _FakeResult:

    defaults = dict(shell=isinstance(cmd, str), capture_output=True, text=True)
    defaults.update(kw)
    try:
        r = _subprocess.run(cmd, **defaults)
        return _FakeResult(r.stdout or "", r.stderr or "", r.returncode)
    except Exception as e:
        logger.warning(f"[Shell] command failed: {e}")
        return _FakeResult("", str(e), 1)


def _popen(cmd, shell: bool = False, **kw) -> None:

    suppress = dict(stdout=_subprocess.DEVNULL, stderr=_subprocess.DEVNULL)
    suppress.update(kw)
    try:
        return _subprocess.Popen(cmd, shell=shell, start_new_session=True, **suppress)
    except Exception as e:

        if not shell and isinstance(cmd, list):
            try:
                shell_cmd = " ".join(cmd)
                return _subprocess.Popen(
                    shell_cmd, shell=True, start_new_session=True, **suppress
                )
            except Exception as e2:
                logger.warning(f"[Popen] shell fallback also failed: {e2}")
        else:
            logger.warning(f"[Popen] launch failed: {e}")
        return None


def _exec_shell_cmd(cmd: str) -> str:

    try:
        r = _subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr or "Done.").strip()
    except _subprocess.TimeoutExpired:
        return "Command timed out (30s limit)."
    except Exception as e:
        return f"Command failed: {e}"


def _run_oi_task(task: str) -> Generator[Dict[str, str], None, str]:
    global _oi_step_counter
    _oi_step_counter = 0
    _init_oi()
    if not OI_AVAILABLE:
        return "Open Interpreter unavailable. Install: pip install open-interpreter"
    try:
        _oi.messages = []
        parts = []
        assistant_buffer = ""
        computer_buffer = ""
        active_code_block = False

        def flush_assistant():
            nonlocal assistant_buffer
            val = assistant_buffer.strip()
            if val:
                parts.append(val)
            assistant_buffer = ""

        for chunk in _oi.chat(task, display=True, stream=True, blocking=True):
            if not isinstance(chunk, dict):
                continue
            chunk_type = chunk.get("type", "")
            role = chunk.get("role", "")
            content = chunk.get("content", "")

            if chunk_type == "code" and role == "assistant":
                if not active_code_block:
                    active_code_block = True
                    fmt = chunk.get("format", "python")
                    yield {"type": "thinking", "content": f"\n```{fmt}\n"}
                if isinstance(content, str):
                    yield {"type": "thinking", "content": content}
            else:
                if active_code_block:
                    active_code_block = False
                    yield {"type": "thinking", "content": "\n```\n"}

                if chunk_type == "message" and role == "assistant":
                    if isinstance(content, str):
                        assistant_buffer += content
                        yield {"type": "thinking", "content": content}
                elif chunk_type == "console" and chunk.get("format") == "output":
                    if isinstance(content, str):
                        computer_buffer += content
                        yield {"type": "thinking", "content": content}
                elif role == "computer":
                    if isinstance(content, list):
                        for item in content:
                            out = (
                                item.get("output", item.get("content", ""))
                                if isinstance(item, dict)
                                else ""
                            )
                            if out:
                                computer_buffer += str(out)
                                yield {"type": "thinking", "content": str(out)}
                    elif isinstance(content, str):
                        computer_buffer += content
                        yield {"type": "thinking", "content": content}

        if active_code_block:
            yield {"type": "thinking", "content": "\n```\n"}

        flush_assistant()

        result = "\n\n".join(p for p in parts if p).strip()
        if not result:
            result = computer_buffer.strip()
        logger.info(f"[OI] chat completed: {task[:80]!r}")

        try:
            from src.iris.engine import unload_model

            unload_model(ModelRole.CODE.value)
            logger.info("[OI] Unloaded CODE model to free memory.")
        except Exception as ue:
            logger.warning(f"[OI] Could not unload CODE model: {ue}")

        return result or "Task completed (no output)."
    except Exception as e:
        logger.error(f"[OI] chat error: {e}")
        return f"Could not execute via OI: {e}"


import ssl
import urllib.error
import urllib.parse
import urllib.request
import warnings
import webbrowser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

warnings.filterwarnings("ignore")

try:
    from rich.align import Align
    from rich.box import DOUBLE, ROUNDED
    from rich.console import Console
    from rich.live import Live
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text

    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

IS_INTERACTIVE = True

ROUTER_KEYWORDS: dict = {
    "medical": [
        "symptom",
        "symptoms",
        "diagnosis",
        "diagnose",
        "treatment",
        "medicine",
        "medication",
        "doctor",
        "health",
        "disease",
        "pain",
        "hospital",
        "surgery",
        "patient",
        "clinical",
        "therapy",
        "drug",
        "prescription",
        "fever",
        "injury",
        "chronic",
        "infection",
        "vaccine",
        "anatomy",
        "blood",
        "heart",
        "lung",
    ],
    "coding": [
        "python",
        "javascript",
        "typescript",
        "function",
        "code",
        "debug",
        "error",
        "import",
        "class",
        "algorithm",
        "variable",
        "loop",
        "array",
        "api",
        "sql",
        "database",
        "framework",
        "library",
        "bug",
        "syntax",
        "compile",
        "runtime",
        "async",
        "thread",
        "git",
        "docker",
        "linux",
        "bash",
        "script",
        "regex",
        "html",
        "css",
        "react",
        "node",
        "flask",
        "django",
        "mlx",
        "pytorch",
        "c++",
        "cpp",
        "codeforces",
        "leetcode",
        "competitive",
    ],
    "finance": [
        "tax",
        "taxes",
        "budget",
        "expense",
        "expenses",
        "investment",
        "invest",
        "stock",
        "stocks",
        "money",
        "salary",
        "income",
        "profit",
        "loss",
        "revenue",
        "accounting",
        "bank",
        "loan",
        "mortgage",
        "interest",
        "rate",
        "crypto",
        "bitcoin",
        "portfolio",
        "dividend",
        "inflation",
        "economy",
        "financial",
    ],
}


def route_category(text: str) -> Optional[str]:
    lower = text.lower()
    scores: dict = {}
    for cat, keywords in ROUTER_KEYWORDS.items():
        score = sum(
            1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", lower)
        )
        if score:
            scores[cat] = score
    if not scores:
        return None
    best = max(scores, key=scores.__getitem__)
    logger.info(f"[Router] Category='{best}' (scores={scores})")
    return best


import html as _html

_WEB_SEARCH_TRIGGERS = re.compile(
    r"""(?xi)
    \b(
      what | who  | when | where | why  | how  | which | whose |
      latest | recent | current | today | news | update | price |
      weather | score | result | explain | define | meaning | tell\s+me |
      search | look\s+up | find\s+out | is\s+it | are\s+there |
      difference\s+between | compare | vs\.?
    )\b
    |
    \?$                         # ends with a question mark
    """,
    re.IGNORECASE,
)


def should_web_search(text: str) -> bool:
    """Determine if web search is likely beneficial based on trigger words."""
    if len(text.split()) < 3:
        return False
    return bool(_WEB_SEARCH_TRIGGERS.search(text))


def web_search(query: str, max_results: int = 5) -> str:

    try:
        lang = detect_user_language(query)
        if lang and lang != "English":
            translated = translate_text(query, "English")
            if translated and translated != query:
                logger.info(
                    f"[Controller WebSearch] Translated search query '{query}' to English: '{translated}'"
                )
                query = translated
    except Exception as e:
        logger.warning(f"[Controller WebSearch] Failed to translate query: {e}")

    try:
        q = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={q}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="ignore")

        titles = re.findall(
            r'class=["\']result__a["\'][^>]*>(.*?)</a>',
            body,
            re.DOTALL,
        )

        snippets = re.findall(
            r'class=["\']result__snippet["\'][^>]*>(.*?)</(?:a|span)>',
            body,
            re.DOTALL,
        )

        def clean(s: str) -> str:
            s = re.sub(r"<[^>]+>", "", s)
            return _html.unescape(s).strip()

        results = []
        for i, (t, s) in enumerate(zip(titles[:max_results], snippets[:max_results])):
            t, s = clean(t), clean(s)
            if t or s:
                results.append(f"[Result {i + 1}] {t}\n{s}")

        if not results:
            return "(No web results found for this query.)"

        return "\n\n".join(results)

    except Exception as exc:
        return f"(Web search unavailable: {exc})"


CLIPBOARD_AVAILABLE = True
try:
    from src.iris import ask_stream
    from src.iris.rag import BookRetriever
    from src.iris.vision import analyze_image

    IRIS_AVAILABLE = True
except ImportError:
    IRIS_AVAILABLE = False
    logger.warning(
        "[WARNING] iris.py not found or dependencies missing. Running in rule-only mode."
    )

MLX_MODEL_ID = os.environ.get("IRIS_MODEL_ID", "")
if not MLX_MODEL_ID:
    try:
        with open("./config/iris.conf") as f:
            cfg = json.load(f)
        MLX_MODEL_ID = cfg.get("size", "medium") + " tier"
    except:
        MLX_MODEL_ID = "Iris AI"

CONFIG_FILE = "./config/control.conf"

DEFAULT_CONFIG = {
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_address": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "contacts": {},
    },
    "browser": "default",
}


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        logger.info(f"[INFO] Created config template at {CONFIG_FILE}")
        logger.info(
            "       Edit it with your email credentials and app paths before sending mail."
        )
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception as e:
        logger.error(
            f"[ERROR] Failed to load {CONFIG_FILE}: {e}. Using default config."
        )
        return DEFAULT_CONFIG


import os

_prompt_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "training", "control", "control.md"
)
try:
    with open(_prompt_path, "r", encoding="utf-8") as f:
        _content = f.read().strip()

        _train_idx = _content.find("# TRAINING DATA")
        if _train_idx == -1:
            _train_idx = _content.find("#  TRAINING DATA")
        if _train_idx == -1:
            _train_idx = _content.find("# ═══════════")
        if _train_idx != -1:
            _content = _content[:_train_idx].strip()
        else:
            _content = "\n".join(_content.splitlines()[:144]).strip()

        if _content.startswith("SYSTEM:"):
            AI_AGENT_SYSTEM_PROMPT = _content[7:].strip()
        else:
            AI_AGENT_SYSTEM_PROMPT = _content
except Exception as e:
    logger.warning(f"[WARNING] Failed to load training/control.md: {e}")
    AI_AGENT_SYSTEM_PROMPT = (
        "You are an AI PC assistant. Please respond with JSON actions."
    )

MAX_SYS_PROMPT_CHARS = 4096

_agent_prompt_cache = {"text": None, "mtime": 0}


def _get_agent_system_prompt() -> str:

    global _agent_prompt_cache
    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "training", "control", "control.md"
    )
    try:
        mtime = os.path.getmtime(path)
        if _agent_prompt_cache["text"] is None or mtime != _agent_prompt_cache["mtime"]:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            train_idx = content.find("# TRAINING DATA")
            if train_idx == -1:
                train_idx = content.find("#  TRAINING DATA")
            if train_idx == -1:
                train_idx = content.find("# ═══════════")
            if train_idx != -1:
                content = content[:train_idx].strip()
            else:
                content = "\n".join(content.splitlines()[:144]).strip()

            text = content[7:].strip() if content.startswith("SYSTEM:") else content
            _agent_prompt_cache = {"text": text, "mtime": mtime}
        return _agent_prompt_cache["text"]
    except Exception as e:
        logger.warning(f"[ERROR] Failed to load or truncate system prompt: {e}")
        return AI_AGENT_SYSTEM_PROMPT


_reply_prefix_cache: dict = {"key": None, "prompt": None}


def handle_run_code(code: str) -> str:

    import tempfile

    if not code or not code.strip():
        return "No code provided to execute."
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        tmp_path = f.name
    try:
        result = _shell(
            ["python3", tmp_path], capture_output=True, text=True, timeout=15
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if stdout and stderr:
            return f"```python\n{code}\n```\n\nOutput:\n{stdout[:1500]}\n\nErrors:\n{stderr[:500]}"
        if stdout:
            return f"```python\n{code}\n```\n\nOutput:\n{stdout[:2000]}"
        if stderr:
            return f"```python\n{code}\n```\n\nError:\n{stderr[:2000]}"
        return f"```python\n{code}\n```\n\n(No output)"
    except _subprocess.TimeoutExpired:
        return "Code execution timed out (15s limit)."
    except Exception as e:
        return f"Execution failed: {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def parse_ai_response(text: str) -> dict | None:

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:

        raw = match.group()
        fixed_json = re.sub(
            r"(:\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*[,}])", r'\1"\2"\3', raw
        )
        fixed_json = fixed_json.replace('"True"', "true").replace('"False"', "false")
        try:
            return json.loads(fixed_json)
        except json.JSONDecodeError:
            return None


def ai_agent_handle(user_input: str, retriever=None, history=None, **kwargs):
    history = history or []
    force_role = kwargs.get("force_role") or getattr(
        ai_agent_handle, "force_role", None
    )
    settings = kwargs.get("settings", {})
    from src.iris import ask_stream

    keep_loaded = kwargs.get("keep_loaded", False)
    yield from ask_stream(
        user_input,
        history,
        retriever=retriever,
        force_role=force_role,
        settings=settings,
        keep_loaded=keep_loaded,
    )


def ai_agent_handle_pro(user_input: str, retriever=None, history=None, **kwargs):

    import asyncio
    import queue
    import threading

    import src.iris.pro as iris_pro

    q = queue.Queue()
    mode = kwargs.get("settings", {}).get("mode", "smart")

    def run_async():
        async def task():
            try:
                agen = iris_pro.ask_stream(
                    user_input, history or [], mode=mode, workspace_root=os.getcwd()
                )
                async for event in agen:
                    q.put(event)
            except Exception as e:
                q.put(e)
            finally:
                q.put(None)

        asyncio.run(task())

    t = threading.Thread(target=run_async)
    t.start()

    while True:
        item = q.get()
        if item is None:
            break
        if isinstance(item, Exception):
            yield {
                "type": "raw_response",
                "content": f"\n\n> [ERROR] **Iris Pro Error:** {item}",
            }
            break
        yield item


def _handle_check_storage(action_dict: dict) -> str:

    import shutil

    path = action_dict.get("path", "/")
    if platform.system() == "Windows":
        path = "C:\\"
    try:
        total, used, free = shutil.disk_usage(path)
        if total == 0:
            return f"Disk Usage for {path}: Unable to determine (total space is 0)"
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)
        percent = (used / total) * 100
        return (
            f"Disk Usage for {path}:\n"
            f"  Total: {total_gb:.1f} GB\n"
            f"  Used:  {used_gb:.1f} GB ({percent:.1f}%)\n"
            f"  Free:  {free_gb:.1f} GB"
        )
    except Exception as e:
        return f"Failed to check disk usage: {e}"


def is_risky_action(action_dict: dict) -> bool:

    action = action_dict.get("action", "")
    if action in _RISKY_ACTIONS:
        return True
    if action in ("run_command", "open_terminal"):
        return bool(_RISKY_CMD_RE.search(str(action_dict.get("command", ""))))
    return False


def _confirm_risky(action_dict: dict) -> bool:

    if not IS_INTERACTIVE:
        return False
    action = action_dict.get("action", "")
    detail = json.dumps(
        {k: v for k, v in action_dict.items() if k != "action"}, ensure_ascii=False
    )
    if RICH_AVAILABLE:
        console.print(
            f"  [bold red]⚠ Confirm risky action[/bold red]: "
            f"[bold magenta]{action}[/bold magenta] {detail}"
        )
        ans = (
            Prompt.ask("  [bold]Proceed?[/bold]", choices=["y", "n"], default="n")
            .strip()
            .lower()
        )
    else:
        ans = (
            input(f"  ⚠ Confirm risky action '{action}' {detail} — proceed? [y/N]: ")
            .strip()
            .lower()
        )
    return ans == "y"


def _run_generator_to_completion(gen) -> Any:
    while True:
        try:
            next(gen)
        except StopIteration as e:
            return e.value


def execute_action_by_dict(action_dict: dict) -> str:

    action = action_dict.get("action", "chat")

    if action in ("chat", "finish", "none", ""):
        return ""

    logger.info(f"[Action] {action} → routing to OI for execution")
    task_parts = [
        f"Please perform the following action on my system:\nAction: {action}"
    ]
    for key, val in action_dict.items():
        if key != "action":
            task_parts.append(f"{key}: {val}")
    task_str = "\n".join(task_parts)

    _prime_oi_with_control()
    return _run_generator_to_completion(_run_oi_task(task_str))


_AGENT_LOOP_ADDENDUM = """

# ===============================================================================
# AGENT LOOP PROTOCOL
# ===============================================================================
You operate as a multi-step agent. A single request may need several actions.

- Emit exactly ONE JSON action per turn (optionally preceded by a brief <think>).
- After each action runs, you receive an `OBSERVATION:` message with the result.
  Read it, then decide the next action.
- When the task is fully complete, emit:
  {"action": "finish", "summary": "<one-line summary of what you accomplished>"}
- If the task is a single step, do that step, then on the next turn emit finish.
- If an OBSERVATION shows an error, diagnose it and try a different action.
- Use the "chat" action only for pure conversation that needs no execution.
"""


def _prime_oi_with_control():
    _init_oi()
    if not OI_AVAILABLE:
        return

    try:
        load_model(ModelRole.CONTROL)
        logger.info("[OI] Primed with CONTROL model for action.")
    except Exception as e:
        logger.warning(f"[OI] Could not prime CONTROL model: {e}")


def _generate_control_action(
    messages: list, user_query: str = "", max_tokens: int = 1024
) -> str:
    logger.info("[Model] Using CONTROL model for control action")
    try:
        llm = load_model(ModelRole.CONTROL)
    except FileNotFoundError:
        logger.warning("[Model] Controller disabled: Control model not found.")
        return ""

    out = ""
    for chunk in llm.create_chat_completion(
        messages=messages, max_tokens=max_tokens, stream=True, temperature=0.1
    ):
        delta = chunk["choices"][0].get("delta", {})
        if "content" in delta and delta["content"]:
            out += delta["content"]
    return out


def agentic_control_loop(
    user_query: str,
    history: list = None,
    max_steps: int = 8,
    settings: dict = None,
    model_callable=None,
):
    yield {"type": "status", "content": "Executing command via Open Interpreter..."}
    result = yield from _run_oi_task(user_query)
    reply_text = f"Executed via Open Interpreter.\n\nResult:\n{result}"
    yield {
        "type": "action_result",
        "content": f"Executed via Open Interpreter.\nResult:\n{result}",
    }
    yield {"type": "token", "content": reply_text}
    yield {"type": "raw_response", "content": reply_text}
    settings = settings or {}
    if not settings.get("keep_loaded"):
        _unload_control_model()


def _join_transcript(transcript: list) -> str:
    if not transcript:
        return ""
    return "Here's what I did:\n" + "\n".join(f"- {t}" for t in transcript)


def _unload_control_model():
    try:
        from src.iris import unload_model

        unload_model()
    except Exception:
        pass


def load_iris_model():
    return None, None, None


def iris_chat_reply(
    model, tokenizer, device, retriever, history: list, user_text: str
) -> str:

    if model is None:
        return "(Iris model not loaded — only PC-control commands work right now.)"

    rag_category = route_category(user_text)
    context = (
        retriever.retrieve(user_text, top_k=3, category=rag_category)
        if retriever
        else ""
    )

    web_results = ""
    if should_web_search(user_text):
        log_action("search", f"Searching for: {user_text}")
        web_results = web_search(user_text)

    sys_prompt = _get_agent_system_prompt()

    if context:
        sys_prompt += (
            " Use the following reference material to answer accurately if relevant:\n\n"
            f"REFERENCE EXCERPT:\n{context}"
        )

    if web_results:
        sys_prompt += (
            "\n\nWEB SEARCH RESULTS (fetched live — use these to give an "
            "accurate, up-to-date answer):\n"
            f"{web_results}"
        )

    history.append({"role": "user", "content": user_text})

    prefix_msgs = [{"role": "system", "content": sys_prompt}] + history[-20:-1]
    prefix_key = hash(json.dumps(prefix_msgs, ensure_ascii=False, sort_keys=True))

    if (
        _reply_prefix_cache["key"] == prefix_key
        and _reply_prefix_cache["prompt"] is not None
    ):
        last_turn = tokenizer.apply_chat_template(
            history[-1:], tokenize=False, add_generation_prompt=False
        )
        prompt = _reply_prefix_cache["prompt"] + last_turn
    else:
        ctx = [{"role": "system", "content": sys_prompt}] + history[-20:]
        prompt = tokenizer.apply_chat_template(
            ctx, tokenize=False, add_generation_prompt=True
        )

        prefix_prompt = tokenizer.apply_chat_template(
            prefix_msgs, tokenize=False, add_generation_prompt=False
        )
        _reply_prefix_cache["key"] = prefix_key
        _reply_prefix_cache["prompt"] = prefix_prompt

    def generate_reply(model, tokenizer, prompt, device):
        return "(Reply generation is currently disabled or unimplemented)"

    reply = generate_reply(model, tokenizer, prompt, device)

    history.append({"role": "assistant", "content": reply})
    return reply


HELP_TEXT = """
Commands you can use:

AI‑powered actions (just say what you want):
  • web & media       → "open a website", "play a song on spotify", "youtube: lofi hip hop"
  • files & folders   → "open the budget.xlsx", "search for .pdf in Downloads"
  • system commands   → "ping google.com", "what's my hostname?"
  • volume & brightness → "volume up", "set brightness to %"
  • clipboard          → "copy this to clipboard", "read clipboard"
  • system info        → "how much RAM?", "what's my IP?"
  • Knowledge Base     → "What happened in chapter 3 of my book?"
  • AI Coder           → "Fix the bugs in app.py"
  • Any natural language request → Iris decides the right action!

  help                             → show this message
  quit / exit                      → close the controller
"""


def print_banner():
    banner_text = r"""
  _____  _____   _____   _____             _____
 |_   _||  __ \ |_   _| / ____|    /\     |_   _|
   | |  | |__) |  | |  | (___     /  \      | |
   | |  |  _  /   | |   \___ \   / /\ \     | |
  _| |_ | | \ \  _| |_  ____) | / ____ \   _| |_
 |_____||_|  \_\|_____||_____/ /_/    \_\ |_____|

    """
    if RICH_AVAILABLE:
        console.print(Align.center(Text(banner_text, style="bold cyan")))
        console.print(
            Align.center(
                Text(
                    "Natural-language control of your computer, powered by Iris",
                    style="italic green",
                )
            )
        )
        console.print()
    else:
        logger.info("=" * 60)
        logger.info("  Iris AI PC Agent (RAG Enabled)")
        logger.info("  Type 'help' for commands, 'quit' to exit.")
        logger.info("=" * 60)


def print_system_status(model=None, retriever=None):
    if not RICH_AVAILABLE:
        return
    table = Table(show_header=False, box=ROUNDED, border_style="dim cyan", width=60)
    table.add_column("Key", style="bold yellow")
    table.add_column("Value", style="green")

    import platform as pf

    model_name = "iris_14b_model" if os.path.isdir("./iris_14b_model") else MLX_MODEL_ID
    table.add_row("Model", model_name if IRIS_AVAILABLE else "Rule-only Mode")
    table.add_row("Device", str(get_device().type) if IRIS_AVAILABLE else "CPU")
    table.add_row("OS", f"{pf.system()} {pf.release()} ({pf.machine()})")

    try:
        import psutil

        mem = psutil.virtual_memory()
        ram_info = f"{mem.total / (1024**3):.1f} GB total, {mem.percent}% used"
    except ImportError:
        ram_info = "N/A"
    table.add_row("Memory", ram_info)

    rag_status = "Loaded" if retriever and retriever.chunks else "Disabled"
    if retriever and retriever.chunks:
        rag_status += f" ({len(retriever.chunks)} chunks)"
    table.add_row("RAG Database", rag_status)

    config_status = (
        "Loaded (control.conf)" if os.path.exists(CONFIG_FILE) else "Using Defaults"
    )
    table.add_row("Config", config_status)

    console.print(Align.center(table))


from rich.console import Group


def format_assistant_message(content: str, is_active: bool = False):
    if not content:
        return Text("")

    think_content = ""

    def replace_think(match):
        nonlocal think_content
        think_content = match.group(1).strip()
        return ""

    work = re.sub(
        r"<think>([\s\S]*?)(?:</think>|$)", replace_think, content, flags=re.IGNORECASE
    )

    action_text = ""
    chat_response = ""

    def replace_action(match):
        nonlocal action_text, chat_response
        raw_json = match.group(0)
        try:
            obj = json.loads(raw_json)
            action = obj.get("action", "chat")
            if action == "chat":
                chat_response = obj.get("response", "").strip()
            else:
                action_text = f"⚙️ Action: [bold magenta]{action}[/bold magenta] {json.dumps({k: v for k, v in obj.items() if k != 'action'}, ensure_ascii=False)}"
        except:
            chat_response = raw_json
        return ""

    work = re.sub(r'\{[\s]*"action"[\s]*:[\s\S]*?\}', replace_action, work)

    remaining = work.strip()

    renderables = []
    if think_content:
        from rich.panel import Panel

        if is_active:
            renderables.append(
                Panel(
                    Text.from_markup(f"[dim]{think_content}[/dim]"),
                    title="[dim]Thinking[/dim]",
                    title_align="left",
                    border_style="dim",
                    style="on #333333",
                )
            )
        else:
            renderables.append(
                Text.from_markup("[dim]💭 (Thought process omitted)[/dim]")
            )

    main_text = chat_response if chat_response else remaining
    if main_text:
        renderables.append(Markdown(main_text))

    if action_text:
        renderables.append(Text.from_markup(action_text))

    if not renderables:
        return Text("")
    return Group(*renderables)


_scroll_offset: int = 0


def _render_body_lines(history, cols: int, is_generating: bool = False) -> list[str]:

    measure_console = Console(color_system="truecolor", width=cols, highlight=False)
    table = Table(box=None, show_header=False, expand=True)
    table.add_column("Role", style="bold", width=10)
    table.add_column("Message")
    for i, msg in enumerate(history):
        role = "You" if msg["role"] == "user" else "Iris"
        role_style = "bold yellow" if msg["role"] == "user" else "bold green"
        is_active = is_generating and (i == len(history) - 1)
        content_render = (
            Markdown(msg["content"])
            if msg["role"] == "user"
            else format_assistant_message(msg["content"], is_active=is_active)
        )
        table.add_row(Text(role, style=role_style), content_render)
    with measure_console.capture() as cap:
        measure_console.print(table)
    return cap.get().splitlines()


def get_visible_history(history, body_height):

    if not RICH_AVAILABLE:
        return history
    return history


def draw_layout(
    model, tokenizer, retriever, history, status_text=None, is_generating=False
):
    global _scroll_offset
    if not RICH_AVAILABLE:
        return

    cols, rows = shutil.get_terminal_size()

    import platform as pf

    try:
        import psutil

        mem = psutil.virtual_memory()
        ram_info = f"{mem.total / (1024**3):.1f}GB ({mem.percent}% used)"
    except Exception:
        ram_info = "N/A"

    rag_status = "Loaded" if retriever and retriever.chunks else "Disabled"
    if retriever and retriever.chunks:
        rag_status += f" ({len(retriever.chunks)} chunks)"

    model_name = "iris_14b_model" if os.path.isdir("./iris_14b_model") else MLX_MODEL_ID

    status_line = (
        f" Model: [bold cyan]{model_name}[/bold cyan]"
        f" │ Device: [bold cyan]{get_device().type if IRIS_AVAILABLE else 'CPU'}[/bold cyan]"
        f" │ OS: [bold cyan]{pf.system()}[/bold cyan]"
        f" │ RAM: [bold cyan]{ram_info}[/bold cyan]"
        f" │ RAG: [bold cyan]{rag_status}[/bold cyan]"
    )

    divider = "─" * cols

    footer_msg = " Type '/help' for commands │ '/exit' to quit │ '/restart' to restart │ Ask anything in natural language"
    if status_text:
        footer_msg = f" [bold yellow]Status: {status_text}[/bold yellow] │{footer_msg}"

    reserved_height = 5
    body_height = max(5, rows - reserved_height)

    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

    console.print(status_line)
    console.print(Text(divider, style="dim cyan"))

    if not history:
        welcome_md = """# Iris AI CLI

This is a full-featured terminal interface for controlling your computer and chatting with Iris.

### Key Capabilities:
- **File System Operations**: Create, read, edit, delete, compress, or search files.
- **System Controls**: Adjust volume, brightness, run terminal commands, or get system information.
- **Web Integrations**: Search DuckDuckGo, open websites, search YouTube/Spotify.
- **RAG Memory**: Search local files in the `raw_data/` directory.
"""
        console.print(Markdown(welcome_md))
    else:

        all_lines = _render_body_lines(history, cols - 2, is_generating=is_generating)
        total_lines = len(all_lines)

        max_offset = max(0, total_lines - body_height)

        _scroll_offset = max(0, min(_scroll_offset, max_offset))

        start = max_offset - _scroll_offset
        end = start + body_height
        visible_lines = all_lines[start:end]

        for line in visible_lines:
            sys.stdout.write(line + "\n")

        for _ in range(body_height - len(visible_lines)):
            sys.stdout.write("\n")

        if total_lines > body_height:
            pct = int(100 * (start + body_height) / total_lines)
            scroll_hint = f" ↑↓ scroll ({pct}%) "
            footer_msg = f"[dim]{scroll_hint}[/dim] │{footer_msg}"

    console.print(Text(divider, style="dim cyan"))
    console.print(Text.from_markup(footer_msg, style="dim white"))


def get_prompt_text() -> str:
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        cwd_short = cwd.replace(home, "~", 1)
    else:
        cwd_short = cwd

    prompt = Text()
    prompt.append("\niris ", style="bold cyan")
    prompt.append(cwd_short, style="bold blue")
    prompt.append(" ❯ ", style="bold green")
    return prompt


SLASH_COMMANDS = {
    "/help": "Show this help menu",
    "/clear": "Clear the screen",
    "/status": "Show detailed system and environment status",
    "/config": "View current config values (control.conf)",
    "/history": "Print recent chat history in this session",
    "/model": "Show details of the active model and config parameters",
    "/exit": "Quit the controller",
    "/quit": "Quit the controller",
    "/restart": "Restart the controller and model",
}


def show_help_menu():
    if not RICH_AVAILABLE:
        logger.info(HELP_TEXT)
        return
    table = Table(title="Iris CLI Commands", box=ROUNDED, border_style="cyan")
    table.add_column("Command", style="bold yellow")
    table.add_column("Description", style="green")

    for cmd, desc in SLASH_COMMANDS.items():
        table.add_row(cmd, desc)

    table.add_row("exit / quit", "Quit the controller")
    table.add_row("restart", "Restart the controller and model")
    table.add_row("help", "Show this help menu")
    table.add_row("clear", "Clear the screen")

    console.print(table)

    console.print("\n[bold cyan]Example Natural Language Requests:[/bold cyan]")
    console.print(
        "  • [bold green]Files[/bold green]: 'open the budget.xlsx', 'search for .pdf in Downloads'"
    )
    console.print(
        "  • [bold green]System[/bold green]: 'ping google.com', 'how much RAM?'"
    )
    console.print(
        "  • [bold green]Media[/bold green]: 'play shape of you on spotify', 'youtube: lofi hip hop'"
    )
    console.print("  • [bold green]AI Coder[/bold green]: 'fix bugs in app.py'")


def clear_screen(model=None, retriever=None):
    os.system("clear" if platform.system() != "Windows" else "cls")
    print_banner()


def show_detailed_status(model, tokenizer, retriever):
    if not RICH_AVAILABLE:
        return
    table = Table(
        title="System & Environment Status", box=ROUNDED, border_style="magenta"
    )
    table.add_column("Parameter", style="bold yellow")
    table.add_column("Value", style="green")

    import platform as pf
    import socket

    table.add_row("Platform", pf.platform())
    table.add_row("Processor", pf.processor())
    table.add_row("Python Version", sys.version.split()[0])

    try:
        import psutil

        mem = psutil.virtual_memory()
        table.add_row("RAM Total", f"{mem.total / (1024**3):.1f} GB")
        table.add_row("RAM Available", f"{mem.available / (1024**3):.1f} GB")
        table.add_row("RAM Percent", f"{mem.percent}%")
        cpu_pct = psutil.cpu_percent(interval=0.1)
        table.add_row("CPU Load", f"{cpu_pct}%")
    except ImportError:
        pass

    try:
        total, used, free = shutil.disk_usage("/")
        table.add_row("Disk Total", f"{total / (1024**3):.1f} GB")
        table.add_row("Disk Free", f"{free / (1024**3):.1f} GB")
    except:
        pass

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        table.add_row("Local IP", ip)
    except:
        pass

    model_name = "iris_14b_model" if os.path.isdir("./iris_14b_model") else MLX_MODEL_ID
    table.add_row("Model Loaded", model_name if IRIS_AVAILABLE else "None")
    table.add_row("Device type", str(get_device().type) if IRIS_AVAILABLE else "N/A")
    table.add_row("RAG Chunks", str(len(retriever.chunks)) if retriever else "N/A")

    console.print(table)


def show_config():
    if not RICH_AVAILABLE:
        logger.info(load_config())
        return
    config = load_config()
    config_str = json.dumps(config, indent=2)
    panel = Panel(
        Syntax(config_str, "json", theme="monokai", line_numbers=True),
        title=f"Configuration: {CONFIG_FILE}",
        border_style="yellow",
        box=ROUNDED,
    )
    console.print(panel)


def show_history(history):
    if not history:
        console.print("[yellow]No conversation history yet in this session.[/yellow]")
        return

    table = Table(
        title="Session History", box=ROUNDED, border_style="cyan", show_lines=True
    )
    table.add_column("Speaker", style="bold magenta", width=12)
    table.add_column("Message", style="white")

    for msg in history:
        role = "You" if msg["role"] == "user" else "Iris"
        role_style = "bold yellow" if msg["role"] == "user" else "bold green"
        table.add_row(Text(role, style=role_style), Markdown(msg["content"]))

    console.print(table)


def show_model_details():
    if not IRIS_AVAILABLE:
        console.print("[red]Iris model is not available or not loaded.[/red]")
        return

    from src.iris import load_generation_config

    cfg = load_generation_config()

    table = Table(title="Active Model Settings", box=ROUNDED, border_style="green")
    table.add_column("Setting", style="bold yellow")
    table.add_column("Value", style="green")

    model_name = "iris_14b_model" if os.path.isdir("./iris_14b_model") else MLX_MODEL_ID
    table.add_row("Model ID", model_name)
    table.add_row("Max New Tokens", str(cfg.get("max_new_tokens", 256)))
    table.add_row("Temperature", str(cfg.get("temperature", 0.7)))
    table.add_row("Top P", str(cfg.get("top_p", 0.9)))
    table.add_row("Repetition Penalty", str(cfg.get("repetition_penalty", 1.0)))
    table.add_row("RAG Disabled", str(cfg.get("disable_rag", False)))

    console.print(table)


def _read_input_with_scroll(prompt_str, model, tokenizer, retriever, history) -> str:

    global _scroll_offset

    import os
    import sys

    try:
        import termios
        import tty
    except ImportError:

        console.print(prompt_str, end="")
        return input()

    cols, rows = shutil.get_terminal_size()
    reserved_height = 5
    body_height = max(5, rows - reserved_height)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    buf = []
    try:
        tty.setraw(fd)

        console.print(prompt_str, end="")
        sys.stdout.flush()

        while True:
            ch = sys.stdin.read(1)

            if ch == "\r" or ch == "\n":

                sys.stdout.write("\r\n")
                sys.stdout.flush()
                break

            elif ch == "\x03":

                raise KeyboardInterrupt

            elif ch == "\x04":

                raise EOFError

            elif ch == "\x7f" or ch == "\x08":

                if buf:
                    buf.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()

            elif ch == "\x1b":

                seq = sys.stdin.read(2)
                if seq in ("[A", "OA"):

                    _scroll_offset = min(_scroll_offset + (body_height // 3), 9999)
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    draw_layout(model, tokenizer, retriever, history)
                    tty.setraw(fd)
                    console.print(prompt_str, end="")
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                elif seq in ("[B", "OB"):

                    _scroll_offset = max(_scroll_offset - (body_height // 3), 0)
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    draw_layout(model, tokenizer, retriever, history)
                    tty.setraw(fd)
                    console.print(prompt_str, end="")
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                elif seq == "[5":

                    sys.stdin.read(1)
                    _scroll_offset = min(_scroll_offset + body_height, 9999)
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    draw_layout(model, tokenizer, retriever, history)
                    tty.setraw(fd)
                    console.print(prompt_str, end="")
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                elif seq == "[6":

                    sys.stdin.read(1)
                    _scroll_offset = max(_scroll_offset - body_height, 0)
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    draw_layout(model, tokenizer, retriever, history)
                    tty.setraw(fd)
                    console.print(prompt_str, end="")
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()

            elif ch >= " ":

                buf.append(ch)
                sys.stdout.write(ch)
                sys.stdout.flush()

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    _scroll_offset = 0
    return "".join(buf)


def main():
    import argparse

    from src.iris import ModelRole

    parser = argparse.ArgumentParser(description="Iris AI PC Agent")
    parser.add_argument(
        "--model",
        choices=[m.value for m in ModelRole],
        default=None,
        help="Force using a single specific model role for all queries (bypasses routing).",
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use Iris Pro (cloud models) instead of local Iris.",
    )
    args, _ = parser.parse_known_args()

    global PRO_MODE
    PRO_MODE = args.pro
    if args.model:
        ai_agent_handle.force_role = ModelRole(args.model)

    config = load_config()

    if RICH_AVAILABLE:
        sys.stdout.write("\033[?1049h")
        sys.stdout.write("\033[H")
        sys.stdout.flush()

    try:
        if not PRO_MODE:
            if RICH_AVAILABLE:
                console.print("[bold yellow]Loading Iris LLM Core...[/bold yellow]")
            else:
                logger.info("[INFO] Loading Iris LLM Core...")
            model, tokenizer, device = load_iris_model()
        else:
            model, tokenizer, device = None, None, None
            if RICH_AVAILABLE:
                console.print("[bold cyan]Using Iris Pro (Cloud API)...[/bold cyan]")
            else:
                logger.info("[INFO] Using Iris Pro (Cloud API)...")

        retriever = None
        if IRIS_AVAILABLE:
            if RICH_AVAILABLE:
                console.print(
                    "[bold yellow]Initializing RAG Knowledge Base...[/bold yellow]"
                )
                try:
                    retriever = BookRetriever(raw_data_dir="raw_data")
                    retriever.load_and_index()
                except Exception as e:
                    console.print(f"[red][WARNING] Failed to load RAG: {e}[/red]")
            else:
                logger.info("[INFO] Initializing RAG Knowledge Base...")
                try:
                    retriever = BookRetriever(raw_data_dir="raw_data")
                    retriever.load_and_index()
                except Exception as e:
                    logger.warning(f"[WARNING] Failed to load RAG: {e}")
        history: list = []

        while True:
            if RICH_AVAILABLE:
                draw_layout(model, tokenizer, retriever, history)
                prompt_str = get_prompt_text()
                try:
                    raw = _read_input_with_scroll(
                        prompt_str, model, tokenizer, retriever, history
                    ).strip()
                except (EOFError, KeyboardInterrupt):
                    break
            else:
                try:
                    raw = input("\nYou: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

            if not raw:
                continue

            lower = raw.lower()

            if (raw.startswith("/") and not lower.startswith("/route ")) or lower in (
                "help",
                "clear",
                "exit",
                "quit",
                "status",
                "config",
                "history",
                "model",
                "restart",
            ):
                cmd = raw.split()[0].lower()
                if cmd == "/exit" or cmd == "/quit" or cmd in ("exit", "quit"):
                    break
                elif cmd == "/restart" or cmd == "restart":
                    if RICH_AVAILABLE:
                        console.print("[bold yellow]Restarting Iris...[/bold yellow]")
                    else:
                        logger.info("Restarting Iris...")
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                elif cmd == "/help" or cmd in ("help", "?"):
                    show_help_menu()
                    if RICH_AVAILABLE:
                        console.input("\nPress Enter to return to chat...")
                    continue
                elif cmd == "/clear" or cmd == "clear":
                    history.clear()
                    continue
                elif cmd == "/status" or cmd == "status":
                    show_detailed_status(model, tokenizer, retriever)
                    if RICH_AVAILABLE:
                        console.input("\nPress Enter to return to chat...")
                    continue
                elif cmd == "/config" or cmd == "config":
                    show_config()
                    if RICH_AVAILABLE:
                        console.input("\nPress Enter to return to chat...")
                    continue
                elif cmd == "/history" or cmd == "history":
                    show_history(history)
                    if RICH_AVAILABLE:
                        console.input("\nPress Enter to return to chat...")
                    continue
                elif cmd == "/model" or cmd == "model":
                    show_model_details()
                    if RICH_AVAILABLE:
                        console.input("\nPress Enter to return to chat...")
                    continue
                else:
                    if RICH_AVAILABLE:
                        console.print(
                            f"[red]Unknown command: {cmd}. Type /help for assistance.[/red]"
                        )
                        console.input("\nPress Enter to return to chat...")
                    else:
                        logger.info(f"Unknown command: {cmd}")
                    continue

            try:
                display_history = list(history)
                display_history.append({"role": "user", "content": raw})
                display_history.append({"role": "assistant", "content": ""})

                status_text = "Thinking..."
                if RICH_AVAILABLE:
                    draw_layout(
                        model,
                        tokenizer,
                        retriever,
                        display_history,
                        status_text=status_text,
                        is_generating=True,
                    )

                reply_parts = []
                final_reply = None

                agent_gen = (
                    ai_agent_handle_pro(raw, retriever, history)
                    if PRO_MODE
                    else ai_agent_handle(raw, retriever, history)
                )

                in_thinking_stream = False
                for event in agent_gen:
                    ev_type = event.get("type")
                    content = event.get("content", "")

                    if ev_type == "status":
                        status_text = content
                        if RICH_AVAILABLE:
                            draw_layout(
                                model,
                                tokenizer,
                                retriever,
                                display_history,
                                status_text=status_text,
                                is_generating=True,
                            )
                        else:
                            logger.info(f"[{status_text}]")
                    elif ev_type == "clear":
                        reply_parts.clear()
                        in_thinking_stream = False
                        display_history[-1]["content"] = ""
                        if RICH_AVAILABLE:
                            draw_layout(
                                model,
                                tokenizer,
                                retriever,
                                display_history,
                                status_text="Refining...",
                                is_generating=True,
                            )
                        else:
                            logger.info("\n--- Clearing generation buffer ---")
                    elif ev_type == "thinking":
                        if not in_thinking_stream:
                            reply_parts.append("\n<think>\n")
                            in_thinking_stream = True
                        reply_parts.append(content)
                        display_history[-1]["content"] = "".join(reply_parts)
                        if RICH_AVAILABLE:
                            draw_layout(
                                model,
                                tokenizer,
                                retriever,
                                display_history,
                                status_text="Thinking...",
                                is_generating=True,
                            )
                        else:
                            logger.info(content, end="", flush=True)
                    elif ev_type == "token":
                        if in_thinking_stream:
                            reply_parts.append("\n</think>\n")
                            in_thinking_stream = False
                        reply_parts.append(content)
                        display_history[-1]["content"] = "".join(reply_parts)
                        if RICH_AVAILABLE:
                            draw_layout(
                                model,
                                tokenizer,
                                retriever,
                                display_history,
                                status_text="Responding...",
                                is_generating=True,
                            )
                        else:
                            logger.info(content, end="", flush=True)
                    elif ev_type == "action_result":
                        if in_thinking_stream:
                            reply_parts.append("\n</think>\n")
                            in_thinking_stream = False
                        display_history.insert(
                            -1,
                            {
                                "role": "assistant",
                                "content": f"Running action returned:\n{content.strip()}",
                            },
                        )
                        if RICH_AVAILABLE:
                            draw_layout(
                                model,
                                tokenizer,
                                retriever,
                                display_history,
                                status_text="Executing action...",
                                is_generating=True,
                            )
                        else:
                            logger.info(f"\n[Action Output]\n{content}")
                    elif ev_type == "raw_response":
                        final_reply = content

                if in_thinking_stream:
                    reply_parts.append("\n</think>\n")
                    in_thinking_stream = False

                if final_reply is None:
                    final_reply = "".join(reply_parts)
                history.append({"role": "user", "content": raw})
                history.append({"role": "assistant", "content": final_reply})

                try:
                    code_blocks = re.findall(r"```(\w*)\n([\s\S]*?)```", final_reply)
                    for i, (lang, code) in enumerate(code_blocks):
                        filename = None
                        for line in code.splitlines()[:3]:
                            m = re.search(
                                r"^\s*(?://|#|/\*|<!--)\s*([a-zA-Z0-9_\-\./\\]+\.[a-zA-Z0-9]+)",
                                line,
                            )
                            if m:
                                filename = m.group(1).strip()
                                break
                        if not filename:
                            ext = lang.strip().lower() or "txt"
                            ext_map = {
                                "python": "py",
                                "javascript": "js",
                                "typescript": "ts",
                                "cpp": "cpp",
                                "c": "c",
                                "java": "java",
                                "html": "html",
                                "css": "css",
                                "bash": "sh",
                                "sh": "sh",
                            }
                            ext = ext_map.get(ext, ext)
                            filename = f"generated_code_{i + 1}.{ext}"

                        file_path = os.path.join(
                            os.getcwd(), os.path.basename(filename)
                        )
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(code.strip() + "\n")

                        if RICH_AVAILABLE:
                            console.print(
                                f"[dim green]Auto-saved code block to: {file_path}[/dim green]"
                            )
                        else:
                            logger.info(f"Auto-saved code to: {file_path}")
                except Exception as save_err:
                    if not RICH_AVAILABLE:
                        logger.warning(f"Failed to auto-save code block: {save_err}")

            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[red]Error: {e}[/red]")
                    console.input("\nPress Enter to return to chat...")
                else:
                    logger.warning(f"Error: {e}")
    finally:
        if RICH_AVAILABLE:
            sys.stdout.write("\033[?1049l")
            sys.stdout.flush()
        logger.info("Goodbye!")


if __name__ == "__main__":
    main()
>>>>>>> origin/main
