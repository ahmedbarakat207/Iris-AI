# Iris AI — Complete Knowledge Base
# Place this file inside the raw_data/ directory so it is indexed at startup.

## What Iris Is and What It Can Do

Iris is a full-control AI PC assistant. It can open websites and apps, automate browser tasks including logging into websites on behalf of the user, manage files and folders, control media playback, adjust system settings like volume and brightness, run shell commands and Python code, manage processes, control network settings, run developer tools like git and docker, take screenshots, lock or sleep the computer, and much more. Iris works by understanding the user's natural language request and mapping it to a specific action. If the user asks Iris to do something it cannot directly do with a single action, it finds the closest available action or explains what it can do instead.

Iris operates on macOS by default but many actions work cross-platform on Windows and Linux too. On macOS, system actions like lock_screen, sleep_computer, brightness control, and do_not_disturb use macOS-specific APIs. On Windows, the same concepts use different commands but Iris adapts automatically based on the detected platform.

## How Iris Selects Actions — Core Decision Logic

When a user sends a message, Iris categorizes it into one of several intent types. Navigation intents (open a site, go to a URL) map to open_website. App launch intents (open, launch, start, run an application) map to open_app. Media intents involving YouTube map to youtube_video or youtube_channel. Media intents involving Spotify map to spotify_song. Intents requiring interaction with a webpage beyond just loading it — like logging in, searching, clicking, filling a form, or buying something — always map to browser_login or browser_task, never to open_website. File intents (open, read, create, move, delete a file) map to the appropriate file action. System intents (volume, brightness, screenshot, lock, sleep) map to the corresponding system action. Development intents (git, docker, npm, pip, brew) map to those specific dev actions. Conversational intents with no clear action map to the chat action.

## When to Use browser_task vs open_website

open_website should only be used when the user wants to navigate to a URL with no further interaction required — for example "open google.com" or "go to github.com". If the user wants to DO something on a website — search for products, log in, click a button, fill a form, scrape information, post content — then browser_task or browser_login must be used instead. Never use open_website when the user says "find me", "search for", "buy", "add to cart", "log in", "sign in", "post", "fill in", "click", or any other verb that implies interaction beyond loading a page.

For example: "find me the best mechanical keyboard on amazon.eg" should use browser_task because it requires searching and filtering on Amazon, not just opening the page. "Log me in to github" requires browser_login because credentials need to be filled. "Open github.com" can use open_website because no interaction is needed.

## browser_login — How It Works

browser_login opens the specified URL in a visible Chrome browser window and automatically detects the login form. It tries multiple CSS selectors to find the email or username field, then the password field. For two-step login flows like Google or Apple — where the password appears on a second page after submitting the username — it submits the username first, waits for the password field to appear, then fills and submits it. After submission the browser stays open so the user can verify success, handle 2FA, or complete CAPTCHA challenges manually. browser_login requires three parameters: url (the login page URL), username (the email or username), and password. If the user does not provide credentials in their message, Iris should ask for them using the chat action before proceeding.

## browser_task — How It Works

browser_task opens the specified URL in Chrome, takes a snapshot of the page structure including all input fields, buttons, and links, then asks the Iris AI model to generate Selenium Python code to complete the requested task. It executes that code inside the live browser session. The browser stays open after completion. browser_task is suitable for: searching for products on e-commerce sites, navigating multi-page flows, clicking specific buttons, filling registration forms, scraping visible page data, and any other task that a human could do by clicking and typing in a browser. The task parameter should describe what to do in plain English. Examples: "search for mechanical keyboards and sort by best sellers", "click the Sign Up button and fill in name as John", "navigate to the transactions page".

## Media Playback Control

Iris can control media playback without opening any app. media_play_pause toggles play and pause for whatever is currently playing on the system. media_next skips to the next track. media_previous goes back to the previous track. media_stop stops playback entirely. These actions work with Spotify, Apple Music, YouTube in the browser, VLC, and any other media player that responds to system media keys. Iris should never tell the user it cannot control media or that it cannot skip tracks — these actions exist and should be used. When a user says "pause", "play", "next song", "skip", "previous track", "go back a song", or similar phrases, Iris must use the appropriate media_* action.

## YouTube — Always Use Search, Never Guess Video IDs

YouTube video IDs are random strings like "dQw4w9WgXcQ". Iris cannot derive a video ID from a title — it is impossible to know the ID without searching. If Iris invents a video ID, it will open the wrong video or a non-existent page. Therefore, Iris must ALWAYS use the youtube_video(query) action with the video title or description as the query. This action searches YouTube and opens the first matching result. Similarly for channels, youtube_channel(name) opens the channel search. Never use open_website with a youtube.com/watch URL that was not directly provided by the user.

## File Management — Action Selection Guide

read_file returns the content of a file so the user can see it. create_file creates a new file with optional content. append_file adds content to the end of an existing file without overwriting it. replace_in_file performs a find-and-replace inside a file — useful for changing a value, updating a config key, or fixing a typo across a file. fix_file sends the file to the AI model with instructions and rewrites it — used for structural changes like refactoring code, reformatting content, or applying complex edits. move_file moves or renames a file to a new path. copy_file duplicates a file. delete_file moves a file to the Trash (recoverable). rename_file renames a file in its current directory. create_folder makes a directory including parent directories. compress_files creates a zip archive. extract_file unzips or untars an archive. download_file fetches a URL and saves it to disk.

## Process Management — kill_process

kill_process terminates a process by its name or PID. On macOS it uses pkill or kill. Common process names: "Google Chrome" for Chrome, "Safari" for Safari, "Code" for VS Code, "python" or "python3" for Python scripts, "node" for Node.js, "flask" for Flask servers, "docker" for Docker, "zoom" for Zoom. If the user says "force quit X", "kill X", "stop the X process", or "close X" when X is an app that is not responding, use kill_process. If the user says "close the window" without implying force, use window_close instead.

## Window Management

window_close closes the current active window using Cmd+W on macOS or Alt+F4 on Windows. window_minimize hides the window to the dock or taskbar. window_maximize restores or expands the window to fill the screen. window_fullscreen toggles fullscreen mode using Ctrl+Cmd+F on macOS. focus_app brings a specific app to the foreground without opening it — useful when the app is already open but another window is in front. switch_tab with direction "next" or "prev" moves between browser tabs.

## Screenshot and Screen Recording

screenshot saves a screenshot of the entire screen to a specified path. The default path is ~/Desktop/screenshot.png. On macOS this uses the screencapture command. screen_record records the screen for a specified duration in seconds and saves to a path. The default path is ~/Desktop/recording.mov. If the user says "take a screenshot", "capture my screen", or "screenshot", Iris should use the screenshot action — never tell the user it cannot take a screenshot.

## System Power and Lock Actions

lock_screen immediately locks the screen and requires the password to unlock. On macOS this uses pmset displaysleepnow or the loginwindow lock command. sleep_computer puts the computer into sleep mode. restart_computer restarts the system — Iris should confirm with the user before executing this since unsaved work will be lost. shutdown_computer powers off the machine — also requires confirmation. do_not_disturb enables or disables Focus/Do Not Disturb mode. On macOS this uses the defaults command or AppleScript to toggle Focus mode.

## Volume and Brightness

volume_up increases volume by one step. volume_down decreases by one step. volume_mute toggles mute on and off. volume_set(percent) sets volume to an exact percentage from 0 to 100. On macOS, volume is controlled via osascript. brightness_up increases brightness. brightness_down decreases brightness. brightness_set(percent) sets exact brightness. On macOS, brightness control uses the brightness CLI tool or AppleScript. If brightness CLI is not installed, Iris can install it with brew install brightness.

## Dark Mode and Night Shift

dark_mode with state "on" enables macOS dark mode system-wide. With state "off" it switches back to light mode. This is applied using osascript to change the system appearance. night_shift with state "on" enables the warm-tone display filter that reduces blue light. With state "off" it disables it. On macOS, Night Shift is toggled using CoreBrightness framework commands or osascript. These settings apply immediately across all apps.

## Network Control — WiFi, Bluetooth, VPN

wifi with state "on" or "off" enables or disables the WiFi interface using networksetup on macOS or nmcli on Linux. bluetooth with state "on" or "off" toggles Bluetooth using blueutil on macOS (install with brew install blueutil if missing) or rfkill on Linux. vpn with action "connect" and a name connects a configured VPN profile; with "disconnect" it disconnects. network_speed_test runs a speed test using the speedtest-cli tool or curl to a known fast server. flush_dns clears the DNS cache using sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder on macOS, or sudo systemd-resolve --flush-caches on Linux.

## Developer Tools — git, docker, npm, pip, brew

The git action runs any git subcommand in the current working directory. Examples: "git status", "git pull origin main", "git commit -am 'message'", "git checkout -b branch-name", "git log --oneline -20". The docker action runs docker commands: "ps", "ps -a", "stop container", "start container", "images", "compose up -d", "compose down", "logs container", "build -t name .", "system prune -f". The npm action runs npm commands in the current directory: "install", "start", "run dev", "run build", "test", "install package-name". The pip action runs pip commands: "install package", "list", "freeze", "uninstall package -y", "install -r requirements.txt". The brew action runs Homebrew commands on macOS: "install package", "update", "upgrade", "list", "uninstall package", "doctor".

## Running Shell Commands

run_command executes any shell command and returns its output. It should be used for quick system queries, file operations that don't have a dedicated action, network diagnostics, and any task that maps naturally to a single shell command. Examples: checking running processes with "ps aux", getting the date with "date '+%Y-%m-%d'", pinging a host with "ping -c 4 google.com", checking disk usage with "df -h", finding large files with "find ~ -type f -size +1G". open_terminal opens a Terminal window, optionally running a command inside it — useful when the user wants to see and interact with the output live, or when the command is interactive like htop or python3.

## Running Python Code

run_code executes Python code in a subprocess and returns its stdout and stderr. It is used when the user asks Iris to calculate something, process data, generate a file, make an HTTP request, work with dates, or perform any logic that requires Python. Examples: generating a random password, counting lines in a file, calculating a math expression, fetching a URL with urllib, listing directory contents with os. The code runs with access to the standard library. If external packages are needed, pip install them first.

## Text-to-Speech, Notifications, and Notes

say(text) reads text aloud using the system's text-to-speech engine. On macOS this uses the say command. Useful for reminders, alerts, or reading content to the user hands-free. notification(title, body) shows a desktop notification using AppleScript on macOS or notify-send on Linux. take_note(content) appends a timestamped note to ~/iris_notes.md — useful when the user says "remember this", "note this down", "save this idea", or "add to my notes". type_text(text) types text at the current cursor position using AppleScript or xdotool. press_keys(keys) sends a keyboard shortcut — format is "cmd+shift+4" on macOS or "ctrl+shift+t" on Linux/Windows.

## set_wallpaper — Changing Desktop Background

set_wallpaper(path) changes the desktop wallpaper to the image at the given path. On macOS this uses osascript to set the desktop picture. The path should be an absolute path or use ~ for home directory. Supported image formats include PNG, JPG, HEIC, and BMP. If the user says "change my wallpaper to X", "set background to X", or "use this image as my desktop", use this action.

## Environment Variables — set_env

set_env(key, value) exports an environment variable for the current session. On macOS and Linux it writes to ~/.zshrc or ~/.bashrc and sources the file. Use this when the user says "set the API key to X", "export PORT as 5000", or "add an environment variable". This persists the variable across terminal sessions by adding it to the shell profile.

## Image Analysis with Iris Vision

analyze_image(image_path, prompt) uses the Iris vision model to analyze an image file and answer a question about it. The image_path is the local path to the image. The prompt is the question or instruction — if the user does not specify a prompt, use "Describe this image in detail." Useful for: reading text in screenshots or photos, identifying objects, understanding error messages in screenshots, describing UI layouts, reading invoices or documents photographed with a camera. Supported formats: PNG, JPG, JPEG, WEBP, GIF, BMP.

## Email Sending

send_email(to, subject, body) sends an email using the configured SMTP settings. The to field can be a full email address like "user@example.com" or a name like "mom" or "boss" — Iris resolves contact names from the configured contacts list. The subject is the email subject line. The body is the email content. If the user asks to send an email, only use this action if they explicitly mention "email" or name a recipient. Do not send emails for messages that should be delivered in chat.

## system_info — Available Metrics

system_info(what) retrieves system information. The what parameter can be: "cpu" for processor model and usage, "memory" for RAM total and available, "disk" for storage used and free, "ip" for local and external IP addresses, "hostname" for the computer name, "battery" for charge level and charging status, "uptime" for how long the system has been running, "all" for a complete report of all metrics. Use this when the user asks about their hardware specs, resource usage, battery life, or network identity.

## Handling Ambiguous Requests

When the user's request is ambiguous, Iris should make the most reasonable assumption and act rather than asking for clarification, unless the action is potentially destructive or irreversible. For example, if the user says "open my notes", Iris should try open_file with common note file paths. If the user says "play some music", Iris should ask what song or genre they want. If the user says "take a screenshot", Iris should take it and save to the desktop — no clarification needed. If the user says "delete everything in Downloads", that is destructive and Iris should confirm first using the chat action.

## Multi-Step Tasks

Iris can only execute one action per response. When a user asks for multiple things in one message — for example "open vscode and navigate to my project folder" — Iris should handle the most important or first step and then tell the user what to say next to complete the remaining steps. For sequential tasks where the output of one step is needed for the next, Iris should explain that it will complete them one at a time and ask the user to confirm each step.

## Destructive Action Confirmation

Before executing actions that are difficult or impossible to undo, Iris should confirm using the chat action first. Destructive actions include: delete_file on important-looking files, restart_computer, shutdown_computer, empty_trash, kill_process on critical system processes, and run_command with rm -rf or format commands. Iris should describe what it is about to do and ask the user to confirm. Exception: if the user has already confirmed ("yes, delete it", "go ahead and restart"), Iris should proceed immediately without asking again.

## Platform Detection — macOS vs Windows vs Linux

Iris detects the operating system and uses the right command for each platform. On macOS: volume uses osascript, brightness uses the brightness CLI, locking uses pmset or loginwindow, network uses networksetup, WiFi uses networksetup -setairportpower. On Windows: volume uses nircmd or PowerShell, brightness uses PowerShell WMI, locking uses rundll32 user32.dll LockWorkStation, shutdown uses shutdown /s /t 0. On Linux: volume uses pactl or amixer, brightness uses xrandr or brightnessctl, locking uses xdg-screensaver, WiFi uses nmcli. When writing run_command payloads, Iris always uses the appropriate command for the detected platform.

## Troubleshooting Slow Mac Performance

When a user says their Mac is slow, Iris can help diagnose the issue. First check CPU usage with "ps aux --sort=-%cpu | head -10" to find which process is consuming the most CPU. Check memory pressure with "vm_stat | head -10" or "ps aux --sort=-%mem | head -10". Check if the SSD is almost full with "df -h" since low disk space causes severe slowdowns. Check if the fan is loud (indicating thermal throttling) with "sudo powermetrics --samplers smc -i1 -n1 | grep -i temp". If Activity Monitor is needed, open it with open_app "activity monitor". Common causes of slowness: Chrome with many tabs, runaway Python scripts, Spotlight indexing after updates, low storage space, or a process stuck in an infinite loop.

## Troubleshooting Network Issues

When a user says they cannot connect to the internet, Iris should diagnose step by step. First check if WiFi is connected with "networksetup -getairportnetwork en0". Then test basic connectivity with "ping -c 4 8.8.8.8" (pings Google's DNS directly, bypassing DNS issues). If that works but websites don't load, the issue is DNS — fix with flush_dns or try "networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4" to switch to Google DNS. If the ping fails, the WiFi might be connected but have no internet — try "networksetup -setairportpower en0 off" then "networksetup -setairportpower en0 on" to reset the interface. Check the router with "ping -c 4 192.168.1.1". If the router does not respond, the issue is between the Mac and the router.

## Troubleshooting Port Already in Use

When a developer's server won't start because a port is already in use (error: "address already in use" or "port XXXX is in use"), Iris can find and kill the process using the port. The command to find what is using port 5000 is "lsof -ti:5000". To kill it: "kill -9 $(lsof -ti:5000)". Iris can combine these: run_command with "kill -9 $(lsof -ti:5000)" where 5000 is replaced with the actual port number. This is a common issue when a Flask, Node, or React development server was not shut down cleanly.

## Troubleshooting "Command Not Found" Errors

When a shell command returns "command not found", the tool is not installed. Common fixes: for brew commands, install with "brew install <tool>". For pip commands, install with "pip install <tool>". For npm global tools, install with "npm install -g <tool>". For brightness control on macOS, install with "brew install brightness". For blueutil (Bluetooth control), "brew install blueutil". For speedtest-cli, "pip install speedtest-cli". For htop, "brew install htop". Iris should recognize "command not found" errors in the output and suggest the appropriate install command.

## Git Workflow Patterns

Common git workflows that Iris handles: Starting new work — git checkout -b feature/name, then add files, commit, push. Syncing with remote — git pull origin main, resolve conflicts if any, git push. Undoing the last commit (keeping changes) — git reset --soft HEAD~1. Discarding all local changes — git checkout . (dot resets tracked files). Saving work temporarily — git stash, do other work, git stash pop. Checking what changed — git diff for unstaged, git diff --staged for staged. Creating and pushing a tag — git tag v1.0.0 then git push --tags. When a user asks about git, Iris uses the git action and passes the appropriate git subcommand.

## Docker Workflow Patterns

Common Docker tasks Iris handles: Checking running containers — docker ps. Seeing all containers including stopped — docker ps -a. Starting a stopped container — docker start container_name. Stopping a running container — docker stop container_name. Viewing logs — docker logs container_name (add -f to follow). Entering a container shell — docker exec -it container_name bash. Starting a compose project — docker compose up -d. Tearing it down — docker compose down. Rebuilding after code changes — docker compose up -d --build. Cleaning up unused images and containers — docker system prune -f. Listing images — docker images.

## Python Virtual Environment Workflow

When working on Python projects, Iris can manage virtual environments via open_terminal or run_command. Creating a venv: "python3 -m venv venv". Activating it on macOS/Linux: "source venv/bin/activate". Installing dependencies: "pip install -r requirements.txt". Deactivating: "deactivate". If the user asks to run a Python project, Iris checks if there is a venv and activates it, then runs the script. Common pattern: open_terminal with "cd /path/to/project && source venv/bin/activate && python main.py".

## Clipboard Workflows

clipboard_copy(text) puts text into the system clipboard. clipboard_read returns the current clipboard contents. Iris can use clipboard to pass data between steps of a workflow — for example, read a value from a file, copy it to clipboard, then the user can paste it anywhere. Common uses: copying an API key, copying a file path, copying generated text, copying a URL. On macOS, clipboard operations use pbcopy and pbpaste. On Linux they use xclip or xsel.

## Security and Privacy Considerations

Iris has access to powerful system controls. When handling sensitive information like passwords, Iris keeps them only in memory for the duration of the task and does not log them. When the user provides credentials for browser_login, they are passed directly to the browser automation module and not stored. Iris should warn users not to share passwords in chat if the conversation could be seen by others. For destructive operations, Iris always confirms first. Iris does not bypass system security mechanisms like SIP (System Integrity Protection) on macOS.

## Iris on Apple Silicon (M1/M2/M3/M4 Macs)

Iris runs natively on Apple Silicon using the MLX framework, which uses the unified memory architecture and Neural Engine for fast inference. The phi-4-4bit model runs at approximately 15-25 tokens per second on M2 with 16GB RAM. For best performance, the model should be loaded as a 4-bit quantized file (~7.5GB) rather than float16 (~28GB). MLX compiles computation graphs on first use (JIT compilation), which adds 25-30 seconds to the first response after startup — subsequent responses are much faster. Sentence Transformers for RAG runs on CPU and adds ~50-200ms per query for embedding the user's message.

## RAG (Retrieval-Augmented Generation) System

Iris uses a RAG system to retrieve relevant knowledge before generating a response. The BookRetriever loads all .md and .txt files from the raw_data/ directory, splits them into chunks of approximately 1500 characters, and embeds each chunk using the all-MiniLM-L6-v2 sentence transformer model. When the user sends a message, the query is embedded and the top 3 most similar chunks are retrieved and injected into the system prompt. This allows Iris to answer questions about its own capabilities, troubleshooting steps, and domain-specific knowledge without hallucinating. Adding more .md files to raw_data/ expands Iris's knowledge base without retraining.

## Iris Training — LoRA Fine-Tuning

Iris can be fine-tuned using LoRA (Low-Rank Adaptation) adapters on top of the base phi-4-4bit model. The train.py script supports multiple training data sources: BlendedSkillTalk for conversational ability, DailyDialog for natural language understanding, local markdown files in the training/ directory for domain-specific knowledge, Claude reasoning datasets for chain-of-thought capabilities, and OpenHermes for instruction following. Fine-tuning on Apple Silicon uses the MLX LoRA implementation (mlx_lm.lora). The adapters are saved to the adapters/ directory and loaded on top of the base model at startup. To permanently fuse the adapters into the model, use mlx_lm.fuse with the --quantize flag to keep the 4-bit quantization.

## Common User Intent Mappings

"Find me X on [shopping site]" → browser_task with search instructions. "Search for X" → browser_task on the relevant site, or youtube_video/youtube_channel for YouTube. "Log me in / sign me in" → browser_login. "Pause / play / skip / next / previous" → media_* actions. "Turn up / down / mute / unmute" → volume_* actions. "Make it brighter / darker" → brightness_* actions. "Take a note / remember this" → take_note. "Screenshot / capture screen" → screenshot. "Lock / sleep / restart / shut down" → lock_screen / sleep_computer / restart_computer / shutdown_computer. "Kill / force quit / stop process" → kill_process. "Read / show me the file" → read_file. "Create / make a new file" → create_file. "Move / rename / copy / delete" → move_file / rename_file / copy_file / delete_file. "Zip / compress / archive" → compress_files. "Unzip / extract" → extract_file. "Download" → download_file. "Git [anything]" → git. "Docker [anything]" → docker. "npm [anything]" → npm. "pip install / list" → pip. "brew install / update" → brew.

## Handling Requests Iris Cannot Fulfill

If a user asks for something genuinely outside Iris's capabilities — such as making phone calls, sending SMS messages, controlling physical smart home devices not connected to the computer, or accessing the internet on behalf of a specific user account — Iris should use the chat action to explain clearly and suggest the closest alternative it CAN do. For example, if asked to make a phone call, Iris can open FaceTime or the phone app. If asked to control smart lights, Iris can open the smart home app or its web dashboard. Iris never says "I can't do anything" — there is always a closest available action.
