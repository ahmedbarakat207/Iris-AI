SYSTEM: You are an AI PC assistant capable of controlling macOS, Windows, and Ubuntu/Linux systems. The user will ask you to perform tasks. 
Before providing the final JSON action, you MUST think about the request inside <think>...</think> tags. 
In your thinking, analyze the intent, identify the correct tool, consider the operating system if relevant, and verify any parameters.
Finally, respond with a single JSON object that describes the action to take.

Available actions:
- open_website(url)
- open_app(name)
- close_app(name)
- youtube_video(query)
- youtube_channel(name)
- spotify_song(query)
- send_email(to, subject, body)
- open_file(path)
- search_files(query, folder)
- run_command(command)
- open_terminal(command)
- volume_up, volume_down, volume_mute
- volume_set(percent)
- brightness_up, brightness_down, brightness_set(percent)
- system_info(what)
- clipboard_copy(text)
- clipboard_read
- chat(response)

# --- General & Identity ---
USER: who are you?
BOT: <think>
The user asked: 'who are you?'. I'll reply conversationally to assist them.
</think>
{"action": "chat", "response": "I am Iris AI."}

USER: what can you do?
BOT: <think>
The user asked: 'what can you do?'. I'll reply conversationally to assist them.
</think>
{"action": "chat", "response": "I can help you open websites and apps, play music on Spotify, find videos on YouTube, send emails, search for files, and troubleshoot system performance or network issues on macOS, Windows, or Ubuntu."}

# --- Entertainment (YouTube & Spotify) ---
USER: play no one noticed on youtube
BOT: <think>
The user wants to watch 'no one noticed' on YouTube. I will trigger the youtube_video action to open their browser directly to the search results or video.
</think>
{"action": "youtube_video", "query": "no one noticed"}

USER: listen to linkin park on spotify
BOT: <think>
The user wants to listen to 'linkin park'. I'll use the spotify_song action to launch Spotify and start playing it.
</think>
{"action": "spotify_song", "query": "linkin park"}

USER: open the MrBeast channel
BOT: <think>
The user is looking for the YouTube channel 'MrBeast'. I will use the youtube_channel tool to open it.
</think>
{"action": "youtube_channel", "name": "MrBeast"}

# --- Productivity (Files & Email) ---
USER: find my resume pdf
BOT: <think>
The user is searching for 'resume.pdf' in 'Documents'. I'll use the search_files tool to scan the directories and present the results.
</think>
{"action": "search_files", "query": "resume.pdf", "folder": "Documents"}

USER: email the boss about the project update
BOT: <think>
Analyzing the user request: 'email the boss about the project update'. I've identified 'send_email' as the most appropriate tool to fulfill this task.
</think>
{"action": "send_email", "to": "boss", "subject": "Project Update", "body": "Hi, here is the update on the project."}

# --- Cross-Platform System Control ---
USER: my internet is slow
BOT: <think>
The user is experiencing network issues. I'll run `ping -c 4 google.com` to diagnose their connection.
</think>
{"action": "run_command", "command": "ping -c 4 google.com"}

USER: open the terminal and run htop
BOT: <think>
The user wants to run a command visibly in a terminal. I'll open a new terminal window and execute `htop`.
</think>
{"action": "open_terminal", "command": "htop"}

USER: volume up
BOT: <think>
The user wants to adjust their system audio. I will use the volume_up tool to change the volume natively.
</think>
{"action": "volume_up"}

USER: make the screen brighter
BOT: <think>
The user wants to adjust their screen brightness. I will trigger the brightness_up tool to modify the display settings.
</think>
{"action": "brightness_up"}

USER: show me my current IP address
BOT: <think>
The user is requesting hardware or system metrics. I'll use the system_info action to fetch and display this data.
</think>
{"action": "system_info", "what": "ip"}

USER: what is my computer's hostname?
BOT: <think>
The user is requesting hardware or system metrics. I'll use the system_info action to fetch and display this data.
</think>
{"action": "system_info", "what": "hostname"}

USER: copy "Meeting at 3pm" to the clipboard
BOT: <think>
Analyzing the user request: 'copy "Meeting at 3pm" to the clipboard'. I've identified 'clipboard_copy' as the most appropriate tool to fulfill this task.
</think>
{"action": "clipboard_copy", "text": "Meeting at 3pm"}

USER: read what's on my clipboard
BOT: <think>
Analyzing the user request: 'read what's on my clipboard'. I've identified 'clipboard_read' as the most appropriate tool to fulfill this task.
</think>
{"action": "clipboard_read"}

USER: set the volume to 45%
BOT: <think>
The user wants to adjust their system audio. I will use the volume_set tool to change the volume natively.
</think>
{"action": "volume_set", "percent": 45}

USER: turn brightness down to half
BOT: <think>
The user wants to adjust their screen brightness. I will trigger the brightness_set tool to modify the display settings.
</think>
{"action": "brightness_set", "percent": 50}

USER: open the website https://developer.apple.com/documentation
BOT: <think>
The user wants to navigate to 'https://developer.apple.com/documentation'. I'll use the open_website tool to launch it in their default browser.
</think>
{"action": "open_website", "url": "https://developer.apple.com/documentation"}

# --- Windows Full Control ---
USER: clear my dns cache on Windows
BOT: <think>
The user needs a system operation performed. I will execute `ipconfig /flushdns` using the run_command tool.
</think>
{"action": "run_command", "command": "ipconfig /flushdns"}

USER: open task manager
BOT: <think>
The user needs a system operation performed. I will execute `taskmgr` using the run_command tool.
</think>
{"action": "run_command", "command": "taskmgr"}

USER: show me my Windows system info
BOT: <think>
The user needs a system operation performed. I will execute `systeminfo` using the run_command tool.
</think>
{"action": "run_command", "command": "systeminfo"}

USER: force quit the calculator app on Windows
BOT: <think>
The user is asking to close or force quit 'calculator'. I will use the close_app action to find the active process and terminate it securely.
</think>
{"action": "close_app", "name": "calculator"}

USER: restart my Windows PC in 10 minutes
BOT: <think>
The user needs a system operation performed. I will execute `shutdown /r /t 600` using the run_command tool.
</think>
{"action": "run_command", "command": "shutdown /r /t 600"}

USER: check my hard drive for errors
BOT: <think>
The user needs a system operation performed. I will execute `chkdsk C:` using the run_command tool.
</think>
{"action": "run_command", "command": "chkdsk C:"}

USER: what processes are using the most memory on Windows?
BOT: <think>
The user needs a system operation performed. I will execute `powershell -Command "Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10"` using the run_command tool.
</think>
{"action": "run_command", "command": "powershell -Command \"Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10\""}

USER: check my active TCP connections
BOT: <think>
The user needs a system operation performed. I will execute `netstat -an | findstr ESTABLISHED` using the run_command tool.
</think>
{"action": "run_command", "command": "netstat -an | findstr ESTABLISHED"}

# --- Ubuntu & Linux Full Control ---
USER: update my ubuntu system packages
BOT: <think>
The user needs a system operation performed. I will execute `sudo apt update && sudo apt upgrade -y` using the run_command tool.
</think>
{"action": "run_command", "command": "sudo apt update && sudo apt upgrade -y"}

USER: check the systemd service status for nginx
BOT: <think>
The user needs a system operation performed. I will execute `systemctl status nginx` using the run_command tool.
</think>
{"action": "run_command", "command": "systemctl status nginx"}

USER: clear the linux dns cache
BOT: <think>
The user needs a system operation performed. I will execute `sudo systemd-resolve --flush-caches` using the run_command tool.
</think>
{"action": "run_command", "command": "sudo systemd-resolve --flush-caches"}

USER: show me disk usage on ubuntu
BOT: <think>
The user needs a system operation performed. I will execute `df -h` using the run_command tool.
</think>
{"action": "run_command", "command": "df -h"}

USER: display the last 50 lines of the system log
BOT: <think>
The user needs a system operation performed. I will execute `journalctl -n 50 --no-pager` using the run_command tool.
</think>
{"action": "run_command", "command": "journalctl -n 50 --no-pager"}

USER: what's using my memory on linux?
BOT: <think>
The user needs a system operation performed. I will execute `free -m` using the run_command tool.
</think>
{"action": "run_command", "command": "free -m"}

USER: configure ufw firewall to allow port 22
BOT: <think>
The user needs a system operation performed. I will execute `sudo ufw allow 22/tcp` using the run_command tool.
</think>
{"action": "run_command", "command": "sudo ufw allow 22/tcp"}

USER: force quit the firefox process on ubuntu
BOT: <think>
The user is asking to close or force quit 'firefox'. I will use the close_app action to find the active process and terminate it securely.
</think>
{"action": "close_app", "name": "firefox"}

USER: open the files app
BOT: <think>
The user wants to launch 'files'. I will invoke the open_app action. The controller will resolve this to the correct executable for their OS.
</think>
{"action": "open_app", "name": "files"}

USER: launch the system monitor
BOT: <think>
The user wants to launch 'system monitor'. I will invoke the open_app action. The controller will resolve this to the correct executable for their OS.
</think>
{"action": "open_app", "name": "system monitor"}

USER: open disks
BOT: <think>
The user wants to launch 'disks'. I will invoke the open_app action. The controller will resolve this to the correct executable for their OS.
</think>
{"action": "open_app", "name": "disks"}

USER: open the music player
BOT: <think>
The user wants to launch 'music'. I will invoke the open_app action. The controller will resolve this to the correct executable for their OS.
</think>
{"action": "open_app", "name": "music"}

# --- macOS Full Control ---
USER: flush my dns on mac
BOT: <think>
The user wants to forcefully terminate a process. I will execute the command `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder` natively on their OS.
</think>
{"action": "run_command", "command": "sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"}

USER: fix my desktop permissions on mac
BOT: <think>
The user needs a system operation performed. I will execute `chmod -R 755 ~/Desktop` using the run_command tool.
</think>
{"action": "run_command", "command": "chmod -R 755 ~/Desktop"}

USER: force quit the calculator app on mac
BOT: <think>
The user is asking to close or force quit 'calculator'. I will use the close_app action to find the active process and terminate it securely.
</think>
{"action": "close_app", "name": "calculator"}

USER: check if my Mac has Apple Silicon or Intel
BOT: <think>
The user needs a system operation performed. I will execute `uname -m` using the run_command tool.
</think>
{"action": "run_command", "command": "uname -m"}

USER: what version of macOS am I running?
BOT: <think>
The user needs a system operation performed. I will execute `sw_vers -productVersion` using the run_command tool.
</think>
{"action": "run_command", "command": "sw_vers -productVersion"}

USER: check if the SSH service is running on my mac
BOT: <think>
The user needs a system operation performed. I will execute `sudo systemsetup -getremotelogin` using the run_command tool.
</think>
{"action": "run_command", "command": "sudo systemsetup -getremotelogin"}

USER: take a screenshot of the entire screen and save it as 'screen.png' on Desktop
BOT: <think>
The user needs a system operation performed. I will execute `screencapture ~/Desktop/screen.png` using the run_command tool.
</think>
{"action": "run_command", "command": "screencapture ~/Desktop/screen.png"}

USER: what's the wifi network I'm connected to on mac?
BOT: <think>
The user needs a system operation performed. I will execute `networksetup -getairportnetwork en0` using the run_command tool.
</think>
{"action": "run_command", "command": "networksetup -getairportnetwork en0"}

SYSTEM: You are an AI PC assistant capable of controlling macOS, Windows, and Ubuntu/Linux systems. The user will ask you to perform tasks. 
Before providing the final JSON action, you MUST think about the request inside <think>...</think> tags. 
In your thinking, analyze the intent, identify the correct tool, consider the operating system if relevant, and verify any parameters.
Finally, respond with a single JSON object that describes the action to take.

Available actions:
- open_website(url)
- open_app(name)
- close_app(name)
- youtube_video(query)
- youtube_channel(name)
- spotify_song(query)
- send_email(to, subject, body)
- open_file(path)
- search_files(query, folder)
- run_command(command)
- open_terminal(command)
- volume_up, volume_down, volume_mute
- volume_set(percent)
- brightness_up, brightness_down, brightness_set(percent)
- system_info(what)
- clipboard_copy(text)
- clipboard_read
- chat(response)

# --- Advanced Reasoning & Multi‑step Analysis ---
USER: I'm working on a Python project and I keep getting "ModuleNotFoundError: No module named 'requests'". Help me fix it.
BOT: <think>
The user needs a system operation performed. I will execute `pip install requests` using the run_command tool.
</think>
{"action": "run_command", "command": "pip install requests"}

USER: my git push is failing with "Permission denied (publickey)". What should I do?
BOT: <think>
The user needs a system operation performed. I will execute `ls ~/.ssh/id_*.pub` using the run_command tool.
</think>
{"action": "run_command", "command": "ls ~/.ssh/id_*.pub"}

USER: I just cloned a new repo and it's missing the .env file. Can you create one with default content?
BOT: <think>
The user asked: 'I just cloned a new repo and it's missing the .env file. Can you create one with default content?'. I'll reply conversationally to assist them.
</think>
{"action": "chat", "response": "I can create the .env file for you, but I need to know what variables to include (e.g., DATABASE_URL, SECRET_KEY). Could you provide them?"}

USER: find all python files in my home directory that import 'os' and show me their names.
BOT: <think>
The user needs a system operation performed. I will execute `grep -rl "import os" --include="*.py" ~` using the run_command tool.
</think>
{"action": "run_command", "command": "grep -rl \"import os\" --include=\"*.py\" ~"}

USER: set volume to 50% and then open Spotify
BOT: <think>
The user asked: 'set volume to 50% and then open Spotify'. I'll reply conversationally to assist them.
</think>
{"action": "chat", "response": "I can only perform one action at a time. Let's start with setting the volume to 50%. After that, ask me to open Spotify."}

USER: I need a quick count of lines of code in all .py files in the current project (excluding __pycache__).
BOT: <think>
The user needs a system operation performed. I will execute `find . -name "*.py" -not -path "./__pycache__/*" -exec cat {} + | wc -l` using the run_command tool.
</think>
{"action": "run_command", "command": "find . -name \"*.py\" -not -path \"./__pycache__/*\" -exec cat {} + | wc -l"}

USER: I keep getting certificate errors when using curl. How do I ignore SSL checks temporarily?
BOT: <think>
The user asked: 'I keep getting certificate errors when using curl. How do I ignore SSL checks temporarily?'. I'll reply conversationally to assist them.
</think>
{"action": "chat", "response": "You can use the -k or --insecure flag with curl to skip SSL verification, e.g., `curl -k https://example.com`. If you have a specific URL I can run it with that flag for you."}

USER: I need to find which process is listening on port 5000 and kill it on ubuntu.
BOT: <think>
The user needs a system operation performed. I will execute `kill -9 $(lsof -ti :5000)` using the run_command tool.
</think>
{"action": "run_command", "command": "kill -9 $(lsof -ti :5000)"}

USER: archive the /var/log directory excluding the .gz files and store it on my Desktop.
BOT: <think>
The user needs a system operation performed. I will execute `sudo tar -czf ~/Desktop/logs.tar.gz --exclude='*.gz' /var/log` using the run_command tool.
</think>
{"action": "run_command", "command": "sudo tar -czf ~/Desktop/logs.tar.gz --exclude='*.gz' /var/log"}

USER: open my resume.docx but if it doesn't exist, create a blank one.
BOT: <think>
The user wants me to open 'resume.docx'. I will use the open_file action to launch it in their default application.
</think>
{"action": "open_file", "path": "resume.docx"}

USER: monitor my CPU usage every second and log it to a file for 10 seconds.
BOT: <think>
The user needs a system operation performed. I will execute `top -b -n 10 -d 1 > ~/cpu_log.txt` using the run_command tool.
</think>
{"action": "run_command", "command": "top -b -n 10 -d 1 > ~/cpu_log.txt"}

USER: dim the screen to the lowest level without turning it off.
BOT: <think>
The user wants to adjust their screen brightness. I will trigger the brightness_set tool to modify the display settings.
</think>
{"action": "brightness_set", "percent": 0}

USER: I want to feel like a hacker; open a terminal with a Matrix rain effect.
BOT: <think>
The user wants to run a command visibly in a terminal. I'll open a new terminal window and execute `cmatrix`.
</think>
{"action": "open_terminal", "command": "cmatrix"}

USER: my terminal is stuck and won't respond to Ctrl-C. What now?
BOT: <think>
The user asked: 'my terminal is stuck and won't respond to Ctrl-C. What now?'. I'll reply conversationally to assist them.
</think>
{"action": "chat", "response": "You can force quit Terminal. Alternatively, I can open a new Terminal window for you. Would you like that?"}

USER: open the biggest file in my Downloads folder on Windows.
BOT: <think>
The user needs a system operation performed. I will execute `powershell -Command "Get-ChildItem -Path ~\Downloads -File | Sort-Object Length -Descending | Select-Object -First 1 | Invoke-Item"` using the run_command tool.
</think>
{"action": "run_command", "command": "powershell -Command \"Get-ChildItem -Path ~\\Downloads -File | Sort-Object Length -Descending | Select-Object -First 1 | Invoke-Item\""}

USER: I'm learning git; show me the commit history of the current repo in a graphical view.
BOT: <think>
The user needs a system operation performed. I will execute `git log --graph --oneline --decorate --all` using the run_command tool.
</think>
{"action": "run_command", "command": "git log --graph --oneline --decorate --all"}

USER: search my Documents folder for any files modified in the last 2 days on linux.
BOT: <think>
The user needs a system operation performed. I will execute `find ~/Documents -type f -mtime -2` using the run_command tool.
</think>
{"action": "run_command", "command": "find ~/Documents -type f -mtime -2"}

USER: I need to compare two directories, 'dir1' and 'dir2', recursively and show differences.
BOT: <think>
The user needs a system operation performed. I will execute `diff -rq dir1 dir2` using the run_command tool.
</think>
{"action": "run_command", "command": "diff -rq dir1 dir2"}

USER: show me the weather forecast for the weekend.
BOT: <think>
The user wants to navigate to 'https://weather.com'. I'll use the open_website tool to launch it in their default browser.
</think>
{"action": "open_website", "url": "https://weather.com"}

USER: I'm feeling bored. Play a random popular song on Spotify.
BOT: <think>
The user wants to listen to 'Today's Top Hits'. I'll use the spotify_song action to launch Spotify and start playing it.
</think>
{"action": "spotify_song", "query": "Today's Top Hits"}

USER: I need to securely delete a file so it can't be recovered on linux.
BOT: <think>
The user asked: 'I need to securely delete a file so it can't be recovered on linux.'. I'll reply conversationally to assist them.
</think>
{"action": "chat", "response": "I can securely delete using 'shred' (on Linux). Which file would you like to erase?"}

USER: open my default Python IDE.
BOT: <think>
The user wants to launch 'IDLE'. I will invoke the open_app action. The controller will resolve this to the correct executable for their OS.
</think>
{"action": "open_app", "name": "IDLE"}

USER: clean up all .DS_Store files recursively from my home.
BOT: <think>
The user needs a system operation performed. I will execute `find ~ -name ".DS_Store" -delete` using the run_command tool.
</think>
{"action": "run_command", "command": "find ~ -name \".DS_Store\" -delete"}

USER: create a 100MB test file for benchmarking on Windows.
BOT: <think>
The user needs a system operation performed. I will execute `fsutil file createnew testfile.bin 104857600` using the run_command tool.
</think>
{"action": "run_command", "command": "fsutil file createnew testfile.bin 104857600"}

USER: I want to see a list of all installed software on my Ubuntu system.
BOT: <think>
Use apt list or dpkg to list installed software.
</think>
{"action": "run_command", "command": "dpkg --get-selections"}

# --- Extreme Advanced Automation & Diagnostics ---
USER: My kubernetes cluster is failing. Pod 'backend-api' is CrashLoopBackOff. Fetch the logs, get the exact error stack trace, and restart the deployment.
BOT: <think>
This is a multi-step Kubernetes diagnostic task. First, I need to get the logs of the failing pod to identify the crash reason. Once I have the logs, the next logical step would be to restart it. I will use run_command to fetch the logs with the `kubectl logs` command as the first action.
</think>
{"action": "run_command", "command": "kubectl logs deployment/backend-api --tail=100"}

USER: I need to migrate my database from SQLite to PostgreSQL. Parse my sqlite.db, generate the SQL dump, convert the syntax, and pipe it into the local Postgres 'prod_db'.
BOT: <think>
Database migration involves exporting, converting syntax (e.g. removing sqlite-specific pragmas), and importing. This is best done with a Python script or a specialized tool like pgloader. Since I only have one action, I'll write a Python script using run_code to handle the conversion logic safely.
</think>
{"action": "run_code", "code": "import sqlite3; conn=sqlite3.connect('sqlite.db'); dump='\\n'.join(conn.iterdump()); open('dump.sql','w').write(dump); print('Dumped SQLite to dump.sql. Next step: converting syntax for PostgreSQL.')"}

USER: Run a massive parallel brute-force attack on this zip file 'secret.zip' using a dictionary attack from rockyou.txt
BOT: <think>
The user is requesting a password cracking operation. I will execute `fcrackzip` with the dictionary attack mode, assuming the tool is installed. If not, I would use john the ripper. Let's use `fcrackzip`.
</think>
{"action": "run_command", "command": "fcrackzip -u -D -p /usr/share/wordlists/rockyou.txt secret.zip"}

USER: Automatically buy the dip on Bitcoin if it drops below $50,000 using my Coinbase API keys.
BOT: <think>
This is an automated trading workflow. It requires setting up a loop or cron job that checks the BTC price via API and places an order if the condition is met. I will write a Python script using the `requests` library to demonstrate this logic, and tell the user they need to run it as a background service.
</think>
{"action": "run_code", "code": "import sys; print('This requires a persistent script checking the price. I can write a Python script for you to run via cron or a systemd service. Please provide the API keys as environment variables first.')"}

USER: My code is spaghetti. Use AST parsing to find all functions longer than 50 lines in the 'src' directory and generate a report.
BOT: <think>
The user wants advanced code analysis via Abstract Syntax Trees. I will use `run_code` to write and execute a Python script that uses the built-in `ast` module to traverse all `.py` files in `src/` and report large functions.
</think>
{"action": "run_code", "code": "import ast, os; \nfor root, _, files in os.walk('src'):\n  for file in files:\n    if file.endswith('.py'):\n      path=os.path.join(root, file)\n      tree=ast.parse(open(path).read())\n      for node in ast.walk(tree):\n        if isinstance(node, ast.FunctionDef):\n          if getattr(node, 'end_lineno', 0) - node.lineno > 50:\n            print(f'{path} - {node.name} is too long')"}

# --- Supreme Intelligence & Malware Reverse Engineering ---
USER: Decompile this suspicious binary 'malware.elf' without running it, extract all hardcoded IP addresses from the binary, and map them.
BOT: <think>
The user wants zero-shot malware analysis. I need to run a static analysis tool like `strings` or `radare2` to extract data, and pipe it through regex to find IPs. `strings malware.elf | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b"` is the most efficient and safe way to static parse IPs from the binary without executing it.
</think>
{"action": "run_command", "command": "strings malware.elf | grep -oE '\\b([0-9]{1,3}\\.){3}[0-9]{1,3}\\b' | sort | uniq"}

USER: I want to run a quantum circuit that creates a Bell State. Use Qiskit to execute this locally using a statevector simulator.
BOT: <think>
The user is requesting Quantum Computing execution. I'll use `run_code` to write a Python script using IBM's `qiskit` library to build a quantum circuit, apply a Hadamard gate and a CNOT gate, simulate it, and output the statevector.
</think>
{"action": "run_code", "code": "from qiskit import QuantumCircuit; from qiskit.quantum_info import Statevector; qc = QuantumCircuit(2); qc.h(0); qc.cx(0, 1); state = Statevector.from_instruction(qc); print('Bell State (Entangled):', state.data)"}

USER: Write a polymorphic python script that changes its own source code hash every time it runs while maintaining its payload.
BOT: <think>
The user is asking for self-modifying code concepts used in polymorphic malware/viruses. I will write a benign Python script that reads its own source file (`__file__`), appends a random comment to it, and overwrites itself.
</think>
{"action": "run_code", "code": "import os, random, string; \nwith open(__file__, 'r') as f: code = f.read(); \ncode += f'\\n# {\"\".join(random.choices(string.ascii_letters, k=10))}'\nwith open(__file__, 'w') as f: f.write(code)\nprint('Polymorphic mutation complete.')"}

USER: Analyze the memory footprint of this running process (PID 4432) and dump the memory region containing the heap into a file.
BOT: <think>
Dumping a live process's heap memory on Linux requires `gcore` (from gdb) or reading `/proc/4432/mem` utilizing the addresses from `/proc/4432/maps`. I'll use a bash command with `gdb` to attach to the process and generate a core dump for reverse engineering.
</think>
{"action": "run_command", "command": "sudo gcore -o /tmp/process_dump 4432"}