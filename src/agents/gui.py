import os
import time
import json
import re
import subprocess
from typing import Dict, Any

try:
    import pyautogui

    pyautogui.FAILSAFE = False
except ImportError:
    pyautogui = None

from src.iris import analyze_image


def _type_text_reliably(text: str):

    try:
        subprocess.run(
            ["xdotool", "type", "--clearmodifiers", "--", text], check=True, timeout=10
        )
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    try:
        proc = subprocess.Popen(
            ["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE
        )
        proc.communicate(input=text.encode("utf-8"))
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        return
    except (FileNotFoundError, Exception):
        pass

    pyautogui.write(text, interval=0.05)


def perform_gui_action(task: str, wait_seconds: float = 3.0) -> str:

    if pyautogui is None:
        return "[ERROR] GUI action failed: pyautogui is not installed. Please run `pip install pyautogui`."

    if wait_seconds > 0:
        print(f"  [GUI] Waiting {wait_seconds}s for app to open...")
        time.sleep(wait_seconds)

    screenshot_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "gui_screenshot.jpg")
    )
    try:
        pyautogui.screenshot(screenshot_path)
        screen_w, screen_h = pyautogui.size()
    except Exception as e:
        return f"[ERROR] GUI action failed: Could not capture screen: {e}"

    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "skills",
        "prompts",
        "gui_agent_prompt.txt",
    )
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = (
                f.read()
                .replace("{TASK}", str(task))
                .replace("{SCREEN_W}", str(screen_w))
                .replace("{SCREEN_H}", str(screen_h))
            )
    except FileNotFoundError:
        prompt = f"GUI Task: {task}. Screen: {screen_w}x{screen_h}. Return JSON array."
    try:
        print(f"\n[GUI] Analyzing screen ({screen_w}x{screen_h}) for task: '{task}'...")

        response = analyze_image(screenshot_path, prompt, unload_after=True)

        clean = re.sub(r"```(?:json)?", "", response).strip().strip("`").strip()
        m = re.search(r"\[.*\]", clean, re.DOTALL)
        if m:
            actions = json.loads(m.group(0))
        else:
            actions = json.loads(clean)

        if not isinstance(actions, list):
            actions = [actions]

        for act in actions:
            action_type = act.get("action")
            if action_type == "click":
                x, y = int(act["x"]), int(act["y"])
                print(f"  [GUI] Clicking ({x}, {y})")
                pyautogui.click(x, y)
                time.sleep(0.4)
            elif action_type == "type":
                text = act.get("text", "")
                print(f"  [GUI] Typing '{text}'")
                _type_text_reliably(text)
                time.sleep(0.4)
            elif action_type == "press":
                key = act.get("key", "")
                print(f"  [GUI] Pressing '{key}'")

                if "+" in key:
                    keys = key.split("+")
                    pyautogui.hotkey(*keys)
                else:
                    pyautogui.press(key)
                time.sleep(0.4)
            elif action_type == "sleep":
                sec = float(act.get("seconds", 1))
                print(f"  [GUI] Sleeping {sec}s")
                time.sleep(sec)

        return "[SUCCESS] GUI task executed successfully."
    except json.JSONDecodeError:
        return f"[ERROR] GUI task failed: Vision model returned non-JSON response:\n{response}"
    except Exception as e:
        return f"[ERROR] GUI task failed: {e}"
