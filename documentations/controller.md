# Iris AI — PC Controller

## Overview

The PC Controller is a natural-language interface for controlling your computer. Available in **Python** (`controller.py`) and **C++** (`controller.cpp`), both with identical functionality.

```
⚡ iris> open spotify
  [app] Launching: spotify
Launching spotify.

⚡ iris> play lofi hip hop on youtube
  [youtube] Searching for video: 'lofi hip hop'
Opening YouTube video: https://www.youtube.com/watch?v=...

⚡ iris> volume up
  [system] Adjusting volume: up
```

## Build (C++ Binary)

```bash
g++ -std=c++17 -O2 controller.cpp -lcurl -o controller
```

A **405KB** native binary — no Python interpreter, no dependencies except libcurl.

## Actions Reference

### App & File Operations
| Command | Action |
|---------|--------|
| `open <app>` | Launch application by name |
| `open <url>` | Open website in browser |
| `read file <path>` | Display file contents |
| `create file <path> with <content>` | Create new file |
| `append to <path> <content>` | Append to file |
| `replace <find> with <replace> in <path>` | Find and replace in file |
| `delete file <path>` | Move to Trash (macOS) or delete |
| `create folder <path>` | Create directory |
| `move <src> to <dst>` | Move/rename file |
| `copy <src> to <dst>` | Copy file or directory |
| `download <url> to <path>` | Download file from URL |
| `search for <query> in <folder>` | Search files by name |

### Media & System
| Command | Action |
|---------|--------|
| `play <query> on youtube` | Find and open YouTube video |
| `play <query> on spotify` | Search Spotify |
| `open <name> channel on youtube` | Open YouTube channel |
| `volume up / down / mute` | Adjust system volume |
| `volume set <pct>` | Set exact volume |
| `brightness up / down` | Adjust screen brightness |
| `brightness set <pct>` | Set exact brightness |
| `media play / pause / next / stop` | Control media playback |
| `say <text>` | Text-to-speech |

### Window & Display
| Command | Action |
|---------|--------|
| `lock screen` | Lock workstation |
| `sleep` | Suspend computer |
| `restart` | Reboot |
| `shutdown` | Power off |
| `dark mode on / off` | Toggle dark mode (macOS) |
| `set wallpaper <path>` | Change desktop background |
| `screenshot` | Take screenshot |
| `close / minimize / maximize window` | Window management |

### Network & Connectivity
| Command | Action |
|---------|--------|
| `wifi on / off` | Toggle WiFi |
| `bluetooth on / off` | Toggle Bluetooth |
| `flush dns` | Clear DNS cache |
| `speed test` | Run speedtest |

### Email
| Command | Action |
|---------|--------|
| `send email to <contact> about <subject> saying <body>` | Compose and send email |

Configure SMTP in `config/control.conf`:
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_address": "you@gmail.com",
    "sender_password": "your_app_password",
    "contacts": {
      "mom": "mom@example.com",
      "boss": "manager@company.com"
    }
  }
}
```

### System Commands
| Command | Action |
|---------|--------|
| `run <command>` | Execute shell command |
| `terminal` | Open terminal window |
| `kill <process>` | Terminate process by name or PID |
| `clipboard` | Read clipboard contents |
| `copy <text> to clipboard` | Copy text to clipboard |
| `system info` | Display hardware/OS information |
| `empty trash` | Empty recycle bin |

## Slash Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help menu |
| `/status` | System resource overview |
| `/config` | Print current configuration |
| `/history` | Show conversation history |
| `/model` | Show active model details |
| `/clear` | Clear screen and history |
| `/exit`, `/quit` | Close controller |

## Intent Detection

The controller uses regex-based intent detection (same patterns in both Python and C++):

```cpp
// YouTube video: "play <query> on youtube"
regex yt_v1("(?:play|open|watch|show|find|search|look\\s+up)\\s+(.+?)\\s+"
            "(?:on\\s+(?:youtube|yt)|on\\s+yt|youtube|yt)", icase);

// Spotify: "play <query> on spotify"
regex spot("(?:play|open|search|listen\\s+to|show)\\s+(.+?)\\s+(?:on\\s+)?spotify", icase);

// Email: "send email to <recipient> about <subject> saying <body>"
regex email("(?:send|write|compose|draft)\\s+(?:an?\\s+)?e?mail"
            "(?:\\s+to\\s+([^\\s,]+))?(?:[\\s,]+(?:about|subject|re:?)\\s+(.+?))?"
            "(?:\\s+(?:saying|body|message|content|with)\\s+(.+))?$", icase);

// Website: "open <url>"
regex web("(?:open|go\\s+to|visit|navigate\\s+to|browse\\s+to|load|show)\\s+"
          "(https?://\\S+|www\\.\\S+|\\S+\\.[a-z]{2,6}(?:\\/\\S*)?)", icase);
```

## Web Search

The controller automatically triggers DuckDuckGo search for informational queries:

```python
def should_web_search(text):
    if len(text.split()) < 5: return False        # Skip short queries
    if SKIP_PATTERN.search(text): return False    # "open", "launch", "play"
    return TRIGGER_PATTERN.search(text)           # "what", "who", "latest"
```

## Platform Support

| Feature | macOS | Windows | Linux |
|---------|-------|---------|-------|
| App launching | [SUCCESS] `open -a` | [SUCCESS] `start` | [SUCCESS] native |
| File operations | [SUCCESS] | [SUCCESS] | [SUCCESS] |
| Volume control | [SUCCESS] osascript | ⚠️ nircmd | [SUCCESS] amixer |
| Brightness | [SUCCESS] osascript | ⚠️ | ⚠️ |
| Window control | [SUCCESS] osascript | [ERROR] | [ERROR] |
| Media control | [SUCCESS] osascript | [ERROR] | [ERROR] |
| Lock/sleep/restart | [SUCCESS] | [SUCCESS] | [SUCCESS] |
| Dark mode | [SUCCESS] osascript | [ERROR] | [ERROR] |
| Wallpaper | [SUCCESS] osascript | [ERROR] | [ERROR] |
| Screenshot | [SUCCESS] screencapture | [ERROR] | [SUCCESS] |
| Type text | [SUCCESS] osascript | [ERROR] | [ERROR] |
| Press keys | [SUCCESS] osascript | [ERROR] | [ERROR] |
| Focus app | [SUCCESS] osascript | [ERROR] | [ERROR] |

## Configuration

```json
// config/control.conf
{
  "email": { "smtp_server": "...", "sender_address": "..." },
  "apps": { "spotify": "spotify", "vscode": "code", ... },
  "browser": "default"
}
```

## Python vs C++

| Feature | Python | C++ |
|---------|--------|-----|
| Binary size | N/A (interpreter) | 405KB |
| Startup | ~200ms | ~5ms |
| Memory | ~30MB | ~3MB |
| Rich UI | [SUCCESS] | [ERROR] (plain text) |
| Iris LLM integration | [SUCCESS] (full) | [ERROR] (standalone) |
| RAG integration | [SUCCESS] | [ERROR] |
| All actions | 105 functions | 89 functions |
| Build required | No | `g++ -O2 -lcurl` |
