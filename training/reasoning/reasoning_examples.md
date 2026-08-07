SYSTEM: You are an AI PC assistant. The user will ask you to perform tasks. Before providing the final JSON action, you MUST think about the request inside <think>...</think> tags.

USER: find my resume and open it
BOT: <think>
The user wants to find and open a file named "resume".
I should first search for it in common folders like Documents or Downloads.
Action: search_files
Query: resume
</think>
{"action": "search_files", "query": "resume", "folder": "Documents"}

USER: check why my internet is slow
BOT: <think>
Slow internet can be caused by latency or bandwidth issues.
I should run a ping command to check for latency and packet loss.
Target: google.com
</think>
{"action": "run_command", "command": "ping -c 4 google.com"}

USER: play bohemian rhapsody on spotify
BOT: <think>
Intent: Music playback.
Service: Spotify.
Song: Bohemian Rhapsody.
I'll use the spotify_song action.
</think>
{"action": "spotify_song", "query": "Bohemian Rhapsody"}

USER: what is 25 * 12?
BOT: <think>
This is a math question, not a PC control task.
I should answer conversationally using the chat action.
Calculation: 25 * 10 = 250, 25 * 2 = 50. Total = 300.
</think>
{"action": "chat", "response": "25 * 12 is 300."}

USER: who are you?
BOT: <think>
Identity question.
I am Iris AI.
</think>
{"action": "chat", "response": "I am Iris AI."}

USER: write a fast prime checker in python
BOT: <think>
The user wants a function to check if a number is prime, optimized for speed.
Common optimizations:
1. Handle small numbers (<=3).
2. Skip even numbers and multiples of 3.
3. Check only up to sqrt(n).
4. Use 6k +/- 1 rule.
This is a coding task, so I'll provide the code inside the chat response.
</think>
{"action": "chat", "response": "Here is an optimized prime checker in Python:\n\n```python\ndef is_prime(n):\n    if n <= 3: return n > 1\n    if n % 2 == 0 or n % 3 == 0: return False\n    i = 5\n    while i * i <= n:\n        if n % i == 0 or n % (i + 2) == 0: return False\n        i += 6\n    return True\n```"}

USER: create a script to monitor cpu and email me if it hits 90%
BOT: <think>
Task: Monitor CPU and send email.
Requirements:
1. Check CPU usage (psutil or top).
2. Condition: usage > 90.
3. Action: send email.
I should provide a complete Python script using my send_email tool logic or a standalone script.
Actually, I'll explain how to set it up as a background task.
</think>
{"action": "chat", "response": "You can use this Python script. Run it in the background with `nohup`:\n\n```python\nimport psutil, time\nimport os\n\ndef monitor():\n    while True:\n        usage = psutil.cpu_percent(interval=1)\n        if usage > 90:\n            print(f'Alert: CPU at {usage}%')\n            # You can tell me to: send email to you subject Alert body CPU High\n        time.sleep(60)\n\nmonitor()\n```"}

USER: refactor this code to be more readable: [x*x for x in range(10) if x%2==0]
BOT: <think>
Input: A list comprehension.
Goal: Readability.
The comprehension is already quite standard, but for beginners or for complex logic, a loop might be clearer.
However, I can also suggest using a named function or explaining what it does.
</think>
{"action": "chat", "response": "Your code is already very efficient! To make it even more readable, you could use a descriptive variable name or split it:\n\n```python\n# Even squares from 0 to 9\neven_squares = [x**2 for x in range(10) if x % 2 == 0]\n```"}

USER: send a quick message to Sam about the meeting
BOT: <think>
The user wants to send an email to a contact named "Sam". I need to check contacts for "Sam". If not found, I'll prompt. Subject is "meeting". Body is empty.
Action: send_email.
</think>
{"action": "send_email", "to": "Sam", "subject": "meeting", "body": ""}

USER: my screen is too bright at night, reduce it to 20%
BOT: <think>
Intent: lower brightness.
Value: 20%.
Action: brightness_set with percent 20.
</think>
{"action": "brightness_set", "percent": 20}

USER: turn the sound off completely
BOT: <think>
Intent: mute audio.
Action: volume_mute.
</think>
{"action": "volume_mute"}

USER: show me the pdf file 'annual_report' in my Downloads
BOT: <think>
User wants to open a file named 'annual_report' likely in the Downloads folder. I'll combine search and open? I can only do one action. Better to search for it, then user can open. Or I can directly open if I'm sure about the path? The request says "show me", which might mean open or locate. I'll search for 'annual_report' in Downloads.
Action: search_files.
</think>
{"action": "search_files", "query": "annual_report", "folder": "Downloads"}

USER: run npm install for this project
BOT: <think>
The user wants to execute a command in the current directory.
Command: npm install.
I'll use run_command.
</think>
{"action": "run_command", "command": "npm install"}

USER: I need to see what's on my clipboard right now
BOT: <think>
Request to read clipboard.
Action: clipboard_read.
</think>
{"action": "clipboard_read"}

USER: open my music player
BOT: <think>
Ambiguous: which music player? Default could be Spotify or Apple Music. I'll try the app named "Spotify" as a common choice. If not configured, the controller might prompt.
Action: open_app, name "Spotify".
</think>
{"action": "open_app", "name": "spotify"}

USER: search youtube for relaxing jazz music
BOT: <think>
YouTube search for a specific genre.
Query: "relaxing jazz music".
Action: youtube_video.
</think>
{"action": "youtube_video", "query": "relaxing jazz music"}

USER: what's the full path of the current working directory?
BOT: <think>
User wants to know the current directory.
I'll run 'pwd' to print it.
Action: run_command with command "pwd".
</think>
{"action": "run_command", "command": "pwd"}

USER: copy that file path to clipboard
BOT: <think>
But I don't have the file path from previous context. I could ask for the path, but as a fallback I'll reply that I need the path.
Action: chat to inform user.
</think>
{"action": "chat", "response": "Which file path would you like me to copy? Please provide it."}

USER: the computer is sluggish; check memory usage
BOT: <think>
Sluggishness often relates to high memory usage. I'll get memory info via system_info.
</think>
{"action": "system_info", "what": "memory"}

USER: launch terminal and run 'htop' to see processes
BOT: <think>
User wants to open a terminal with the command "htop". I can use open_terminal action.
</think>
{"action": "open_terminal", "command": "htop"}

USER: open the project's README.md in Documents
BOT: <think>
User implies there's a file "README.md" inside the Documents folder. I'll open it directly.
Path: Documents/README.md
</think>
{"action": "open_file", "path": "Documents/README.md"}

USER: go to the apple developer website
BOT: <think>
URL: developer.apple.com
Action: open_website.
</think>
{"action": "open_website", "url": "developer.apple.com"}

USER: make the computer brighter; I can't see in sunlight
BOT: <think>
User wants increased brightness.
Action: brightness_up.
</think>
{"action": "brightness_up"}

USER: send an email to john@doe.com with the subject "Invoice" and body "Please find the invoice attached."
BOT: <think>
Complete email request.
To: john@doe.com, Subject: Invoice, Body: Please find the invoice attached.
Action: send_email.
</think>
{"action": "send_email", "to": "john@doe.com", "subject": "Invoice", "body": "Please find the invoice attached."}

USER: I want to listen to 'Imagine Dragons' on Spotify
BOT: <think>
Spotify search for artist or song. Query: "Imagine Dragons".
Action: spotify_song.
</think>
{"action": "spotify_song", "query": "Imagine Dragons"}

USER: delete all .tmp files in /var/tmp
BOT: <think>
User wants to remove files with extension .tmp from /var/tmp. Command: rm /var/tmp/*.tmp.
I'll run_command. Must ensure safety.
</think>
{"action": "run_command", "command": "rm /var/tmp/*.tmp"}

USER: find large email attachments in my Mail folder
BOT: <think>
This is a search for files in a specific folder. I'll use search_files to find files by size? But search_files only has query by name. I could run a find command instead. Since the request is about mail attachments, likely they're in ~/Library/Mail. I'll run_command with find for files > 10M.
Command: find ~/Library/Mail -type f -size +10M.
</think>
{"action": "run_command", "command": "find ~/Library/Mail -type f -size +10M"}

USER: open the control panel in windows
BOT: <think>
On macOS, "control panel" maps to System Preferences or System Settings. I'll try to open the app using the name "System Preferences". If on Linux, may not exist. I'll use open_app with "System Preferences".
</think>
{"action": "open_app", "name": "System Preferences"}

USER: start a new chat in terminal with python interactive mode
BOT: <think>
User wants to open terminal and run python3 (or python) in interactive mode. I'll use open_terminal with command "python3".
</think>
{"action": "open_terminal", "command": "python3"}

USER: put the mac to sleep
BOT: <think>
Sleep command on macOS: pmset sleepnow. I'll run_command.
</think>
{"action": "run_command", "command": "pmset sleepnow"}

USER: what is 15% of 200?
BOT: <think>
Math calculation: 15% of 200 = 30. Use chat to respond.
</think>
{"action": "chat", "response": "15% of 200 is 30."}

USER: I'm trying to connect to a server; check if port 22 is open on 192.168.1.10
BOT: <think>
Port check can be done with nc (netcat) or telnet. Command: nc -zv 192.168.1.10 22.
Action: run_command.
</think>
{"action": "run_command", "command": "nc -zv 192.168.1.10 22"}

USER: show me the weather in tokyo
BOT: <think>
I don't have weather data, but I can open a weather website. I'll open weather.com with search for Tokyo.
Action: open_website with a crafted URL.
</think>
{"action": "open_website", "url": "https://weather.com/weather/today/l/Tokyo+Japan"}

USER: find the password for my wifi network "HomeWiFi"
BOT: <think>
On macOS, stored WiFi passwords can be retrieved with security find-generic-password. Command: security find-generic-password -wa "HomeWiFi". I'll use run_command.
</think>
{"action": "run_command", "command": "security find-generic-password -wa \"HomeWiFi\""}

USER: I need a QR code for the link https://example.com
BOT: <think>
I can generate a QR code using an online service and then open the image. I'll run a command that curls qrenco.de and opens the result. Command: curl qrenco.de/$(echo -n 'https://example.com' | curl -s --data-binary @- qrenco.de) -o qr.png && open qr.png
</think>
{"action": "run_command", "command": "curl qrenco.de/$(echo -n 'https://example.com' | curl -s --data-binary @- qrenco.de) -o qr.png && open qr.png"}

USER: I think my IP has changed, what is it now?
BOT: <think>
Get external IP: curl ifconfig.me. Or internal IP: ipconfig getifaddr en0. I'll give both? I'll run a command that shows the local IP. Maybe system_info for IP. But system_info returns only internal? Let's run_command with "curl ifconfig.me; ipconfig getifaddr en0".
</think>
{"action": "run_command", "command": "curl ifconfig.me; ipconfig getifaddr en0"}

USER: compress my Documents folder into a zip
BOT: <think>
I'll use zip command. I need name and location. Default: Documents.zip in home. Command: zip -r ~/Documents.zip ~/Documents.
</think>
{"action": "run_command", "command": "zip -r ~/Documents.zip ~/Documents"}

USER: open the folder containing all my bash aliases
BOT: <think>
Bash aliases are usually in ~/.bash_profile, ~/.bashrc, or ~/.aliases. I'll open the home directory and user can look. Or open file ~/.bashrc. Since it's a "folder", maybe they mean the home folder. I'll open ~.
</think>
{"action": "open_file", "path": "~"}

USER: increase the volume by a lot
BOT: <think>
"By a lot" is ambiguous; I'll set volume to 90% to be safe.
Action: volume_set percent 90.
</think>
{"action": "volume_set", "percent": 90}

USER: I have a file called 'data.csv' on my desktop, open it with Numbers
BOT: <think>
Open a specific file with a specific app. I'll use open_file first, but the file will open with default app. To open with Numbers, I could run command: open -a Numbers ~/Desktop/data.csv. So I'll use run_command.
</think>
{"action": "run_command", "command": "open -a Numbers ~/Desktop/data.csv"}

USER: check if my SSD is failing
BOT: <think>
SSD health can be checked with smartctl. Command: smartctl -a /dev/disk0 | grep -i "SMART overall-health". Or diskutil info / | grep SMART. I'll use diskutil.
</think>
{"action": "run_command", "command": "diskutil info / | grep SMART"}

USER: remember to copy the note 'buy eggs' to clipboard later
BOT: <think>
The user wants to set a reminder, but I don't have reminder capability. I can copy it to clipboard now, but "later" can't be scheduled. I'll suggest using Siri or Reminders app and copy it for now.
Actually, I'll copy it to clipboard now and tell the user.
</think>
{"action": "clipboard_copy", "text": "buy eggs"}

USER: my mouse is lagging; increase tracking speed
BOT: <think>
On macOS, change mouse scaling with defaults write. Command: defaults write -g com.apple.mouse.scaling 5; killall Dock.
But need sudo? No, user-level. I'll run that.
</think>
{"action": "run_command", "command": "defaults write -g com.apple.mouse.scaling 5; killall Dock"}

USER: show the last 20 commands I ran in terminal
BOT: <think>
Command history: history | tail -n 20. I'll run that.
</think>
{"action": "run_command", "command": "history | tail -n 20"}

USER: start the docker daemon
BOT: <think>
On Linux: sudo systemctl start docker. On macOS: open --background -a Docker. I'll assume macOS and run the app opener.
Action: open_app "Docker".
</think>
{"action": "open_app", "name": "Docker"}

USER: unlock a PDF file 'secure.pdf' (password is 1234)
BOT: <think>
I can use qpdf to decrypt. Command: qpdf --password=1234 --decrypt secure.pdf unlocked.pdf. If qpdf not installed, I might inform.
I'll use run_command.
</think>
{"action": "run_command", "command": "qpdf --password=1234 --decrypt secure.pdf unlocked.pdf"}

USER: I need to edit the crontab
BOT: <think>
Open crontab for editing: crontab -e. But that opens an editor in terminal. I'll open terminal with command "crontab -e". Or just run it? run_command won't work well with interactive editors. So open_terminal is better.
</think>
{"action": "open_terminal", "command": "crontab -e"}

USER: how many CPU cores do I have?
BOT: <think>
System info: cpu. System_info action for cpu.
</think>
{"action": "system_info", "what": "cpu"}

USER: turn on the firewall
BOT: <think>
macOS firewall command: /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on. Require sudo. I'll run_command with sudo.
</think>
{"action": "run_command", "command": "sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on"}

USER: show me all hidden files in my home directory
BOT: <think>
ls -la ~ . Action: run_command.
</think>
{"action": "run_command", "command": "ls -la ~"}

USER: play the song 'Happy' from Despicable Me on YouTube
BOT: <think>
YouTube search: "Happy Pharrell Williams".
Action: youtube_video.
</think>
{"action": "youtube_video", "query": "Happy Pharrell Williams"}

USER: I need a quick way to search for 'error' in all log files under /var/log, case insensitive
BOT: <think>
grep -ri "error" /var/log.
Action: run_command.
</think>
{"action": "run_command", "command": "grep -ri \"error\" /var/log"}

USER: open the chat app Slack
BOT: <think>
Open app "Slack".
</think>
{"action": "open_app", "name": "Slack"}

USER: you're not understanding, I want to lower the brightness gradually
BOT: <think>The user wants gradual change, but I can only do one step. I'll lower brightness by one notch (brightness_down) and tell them to repeat if needed.</think>
{"action": "brightness_down"}

USER: sort the lines in my file 'names.txt' alphabetically and save back
BOT: <think>
Command: sort names.txt -o names.txt.
Run command.
</think>
{"action": "run_command", "command": "sort names.txt -o names.txt"}

USER: stop all running docker containers
BOT: <think>
docker stop $(docker ps -q)
</think>
{"action": "run_command", "command": "docker stop $(docker ps -q)"}

USER: can you empty the trash?
BOT: <think>
On macOS: rm -rf ~/.Trash/* . But dangerous, I'll ask confirmation.
I cannot directly ask in JSON, but I can reply with chat that asks for confirmation.
So I'll use chat response asking if they really want that.
</think>
{"action": "chat", "response": "Empty the Trash will permanently delete files. Are you sure? If yes, say 'empty trash now'."}

USER: open my camera app
BOT: <think>
macOS app: Photo Booth.
Action: open_app "Photo Booth".
</think>
{"action": "open_app", "name": "Photo Booth"}

USER: I want to hear the song 'Bohemian Rhapsody' but I don't know which service
BOT: <think>
User didn't specify service; I'll default to YouTube as it's free.
</think>
{"action": "youtube_video", "query": "Bohemian Rhapsody"}

USER: the terminal is full of output, clear it
BOT: <think>
If they're in a terminal already, I can't clear it remotely, but I can run 'clear' command with open_terminal, which will open a new terminal and clear it? That's not the same. Better to chat and tell them to type 'clear'. So chat response.
</think>
{"action": "chat", "response": "If your terminal is open, just type 'clear' and press Enter. I can't clear it remotely."}

USER: search my home directory for files that contain my old phone number '555-1234'
BOT: <think>
Use grep recursively: grep -r "555-1234" ~.
Action: run_command.
</think>
{"action": "run_command", "command": "grep -r \"555-1234\" ~"}

USER: open the system clock to set time
BOT: <think>
On macOS, open Date & Time preferences: open /System/Library/PreferencePanes/DateAndTime.prefPane. Or open_app "Date & Time". I'll open the preference pane.
</think>
{"action": "open_file", "path": "/System/Library/PreferencePanes/DateAndTime.prefPane"}

USER: show me the wifi icon in the menu bar if it's hidden
BOT: <think>
Can't change menu bar items with a command easily, but I can open System Preferences with the Network pane. I'll open network settings.
Open file: /System/Library/PreferencePanes/Network.prefPane
</think>
{"action": "open_file", "path": "/System/Library/PreferencePanes/Network.prefPane"}

USER: switch audio output to headphones
BOT: <think>
I can't switch directly, but I can open Sound preferences. Open file: /System/Library/PreferencePanes/Sound.prefPane
</think>
{"action": "open_file", "path": "/System/Library/PreferencePanes/Sound.prefPane"}

USER: what's the current time?
BOT: <think>
Run date +"%T" to get time.
</think>
{"action": "run_command", "command": "date +\"%T\""}

USER: kill the process named 'python' forcefully
BOT: <think>
Use pkill -9 python.
But careful: might kill many. Use pkill -9 -f python? I'll just do pkill -9 python.
</think>
{"action": "run_command", "command": "pkill -9 python"}

USER: show all environment variables starting with PATH
BOT: <think>
env | grep ^PATH
</think>
{"action": "run_command", "command": "env | grep ^PATH"}

USER: open my photo library
BOT: <think>
App: Photos.
</think>
{"action": "open_app", "name": "Photos"}

USER: play the video 'funny cats' from YouTube on the big screen
BOT: <think>
YouTube video for "funny cats". Action: youtube_video.
</think>
{"action": "youtube_video", "query": "funny cats"}

USER: don't do anything, just tell me a joke
BOT: <think>
User wants chat. I'll provide a joke.
</think>
{"action": "chat", "response": "Why do programmers prefer dark mode? Because light attracts bugs."}

USER: my contact list is gone, where is it stored?
BOT: <think>
On macOS, contacts are in ~/Library/Application Support/AddressBook. I can open that folder.
</think>
{"action": "open_file", "path": "~/Library/Application Support/AddressBook"}

USER: check if git is installed
BOT: <think>
Run git --version.
</think>
{"action": "run_command", "command": "git --version"}

USER: I need to see my display's resolution
BOT: <think>
system_profiler SPDisplaysDataType
</think>
{"action": "run_command", "command": "system_profiler SPDisplaysDataType | grep Resolution"}

USER: search for a file that contains the phrase "secret project" in my projects folder
BOT: <think>
search_files won't search inside files. So I'll use grep in that folder: grep -rl "secret project" ~/projects.
</think>
{"action": "run_command", "command": "grep -rl \"secret project\" ~/projects"}

USER: enable remote login (SSH)
BOT: <think>
sudo systemsetup -setremotelogin on
</think>
{"action": "run_command", "command": "sudo systemsetup -setremotelogin on"}

USER: how much free space on the startup disk?
BOT: <think>
df -h /.
</think>
{"action": "run_command", "command": "df -h /"}

USER: eject all external disks
BOT: <think>
diskutil eject /dev/disk2 etc. But I don't know which. I can try diskutil list external and eject each? Complex. Safer: open Finder to eject manually? I'll chat and suggest to use Finder.
</think>
{"action": "chat", "response": "For safety, manually eject disks using Finder. I can open Finder for you?"}

USER: yes, open Finder
BOT: <think>
Open app "Finder".
</think>
{"action": "open_app", "name": "Finder"}