import os
import re
import json
import logging

try:
    from rich.console import Console, Group
    from rich.text import Text
    from rich.table import Table
    from rich.align import Align
    from rich.box import ROUNDED
    from rich.prompt import Prompt

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

logger = logging.getLogger("controller")

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
        logger.info("  Iris AI PC Agent")
        logger.info("  Type 'help' for commands, 'quit' to exit.")
        logger.info("=" * 60)


def print_system_status(model_available=True, mlx_model_id=""):
    if not RICH_AVAILABLE:
        return
    table = Table(show_header=False, box=ROUNDED, border_style="dim cyan", width=60)
    table.add_column("Key", style="bold yellow")
    table.add_column("Value", style="green")

    import platform as pf

    model_name = "iris_14b_model" if os.path.isdir("./iris_14b_model") else mlx_model_id
    table.add_row("Model", model_name if model_available else "Rule-only Mode")
    table.add_row("OS", f"{pf.system()} {pf.release()} ({pf.machine()})")

    try:
        import psutil

        mem = psutil.virtual_memory()
        ram_info = f"{mem.total / (1024**3):.1f} GB total, {mem.percent}% used"
    except ImportError:
        ram_info = "N/A"
    table.add_row("Memory", ram_info)

    console.print(Align.center(table))


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
            a = obj.get("action", "")
            if a in ("talk", "request_info"):
                chat_response = obj.get("message", "")
                return ""
            if a:
                action_text = f"Action: {a} | {str(obj)[:60]}..."
        except Exception:
            pass
        return ""

    work = re.sub(r"\{[\s\S]*?\}", replace_action, work)
    work = work.strip()

    if chat_response:
        final_text = chat_response
    elif work:
        final_text = work
    elif action_text:
        final_text = f"[{action_text}]"
    elif think_content:
        final_text = "[Thinking completed]"
    else:
        final_text = ""

    if is_active:
        return Text(final_text, style="italic green")
    else:
        return Text(final_text, style="cyan")
