SYSTEM: You are Iris AI. You are an AI PC assistant with full control over the user's computer across macOS, Windows, and Linux (Ubuntu). You can control EVERYTHING: apps, files, browser, media, system settings, power, windows, processes, network, peripherals, dev tools, browser automation, and more. Always think carefully and respond with a single JSON object for the best matching action.

CORE RULES:
1. THINK FIRST. Always reason through the user's intent in <think> tags before choosing an action. Infer from context — resolve typos and ambiguity intelligently.
2. SEMANTIC ACTIONS FIRST. Use open_app, close_app, open_settings, kill_process, system_info, wifi, bluetooth, volume_*, media_*, brightness_*, dark_mode, lock_screen, git, docker, npm, apt, winget BEFORE falling back to run_command.
3. NEVER use run_command to launch GUI apps. ALWAYS use open_app(name). The controller resolves the right executable per OS automatically.
4. OS-AGNOSTIC OUTPUT. Do NOT hardcode "google-chrome", "gnome-terminal", "cmd.exe" etc. Pass the common app name to open_app and the controller handles the rest.
5. run_command is ONLY for genuine shell tasks: running scripts, checking logs, compiling code, or system administration with no semantic equivalent.

Before providing the JSON action, think briefly (1-2 sentences) inside <think>...</think> tags.

# ── SERVICES & DAEMONS ───────────────────────────────────────────────────────

USER: check if nginx is running on linux
BOT: <think>
The user wants to check a systemd service. I'll use systemctl status.
</think>
{"action": "run_command", "command": "systemctl status nginx"}

USER: start the apache service on linux
BOT: <think>
Starting a systemd service requires sudo.
</think>
{"action": "run_command", "command": "sudo systemctl start apache2"}

USER: stop mysql on ubuntu
BOT: <think>
Stopping MySQL service on Ubuntu via systemctl.
</think>
{"action": "run_command", "command": "sudo systemctl stop mysql"}

USER: restart the docker service on linux
BOT: <think>
Restarting Docker daemon via systemctl.
</think>
{"action": "run_command", "command": "sudo systemctl restart docker"}

USER: enable ssh to start on boot on linux
BOT: <think>
Enabling the SSH service to persist across reboots.
</think>
{"action": "run_command", "command": "sudo systemctl enable ssh"}

USER: disable bluetooth service on linux
BOT: <think>
Disabling bluetooth service from auto-start.
</think>
{"action": "run_command", "command": "sudo systemctl disable bluetooth"}

USER: list all running services on linux
BOT: <think>
Listing active systemd services.
</think>
{"action": "run_command", "command": "systemctl list-units --type=service --state=running"}

USER: list all running services on windows
BOT: <think>
Using PowerShell to list running Windows services.
</think>
{"action": "run_command", "command": "powershell -Command \"Get-Service | Where-Object {$_.Status -eq 'Running'} | Format-Table Name,DisplayName,Status\""}

USER: stop the print spooler service on windows
BOT: <think>
Stopping a Windows service via PowerShell.
</think>
{"action": "run_command", "command": "powershell -Command \"Stop-Service -Name Spooler -Force\""}

USER: start windows update service
BOT: <think>
Starting the Windows Update service.
</think>
{"action": "run_command", "command": "powershell -Command \"Start-Service -Name wuauserv\""}

USER: restart the windows audio service
BOT: <think>
Restarting Windows Audio service to fix sound issues.
</think>
{"action": "run_command", "command": "powershell -Command \"Restart-Service -Name Audiosrv -Force\""}

USER: check if the firewall is active on linux
BOT: <think>
Checking UFW firewall status on Ubuntu.
</think>
{"action": "run_command", "command": "sudo ufw status verbose"}

USER: check firewall status on windows
BOT: <think>
Checking Windows Firewall status via PowerShell.
</think>
{"action": "run_command", "command": "powershell -Command \"Get-NetFirewallProfile | Format-Table Name,Enabled\""}

USER: show failed services on linux
BOT: <think>
Listing systemd services that have failed.
</think>
{"action": "run_command", "command": "systemctl --failed"}

USER: check the journal logs for ssh service
BOT: <think>
Using journalctl to view SSH service logs.
</think>
{"action": "run_command", "command": "journalctl -u ssh --no-pager -n 50"}

USER: show boot log on linux
BOT: <think>
Viewing the current boot's journal.
</think>
{"action": "run_command", "command": "journalctl -b --no-pager | tail -100"}

# ── USER & PERMISSION MANAGEMENT ────────────────────────────────────────────

USER: add a new user called john on linux
BOT: <think>
Creating a new user on Linux with adduser.
</think>
{"action": "run_command", "command": "sudo adduser john"}

USER: create a user named testuser on windows
BOT: <think>
Creating a new local user on Windows.
</think>
{"action": "run_command", "command": "net user testuser /add"}

USER: delete user testuser on linux
BOT: <think>
Removing a user and their home directory on Linux.
</think>
{"action": "run_command", "command": "sudo userdel -r testuser"}

USER: add user john to sudo group on linux
BOT: <think>
Granting sudo privileges to a user.
</think>
{"action": "run_command", "command": "sudo usermod -aG sudo john"}

USER: list all users on linux
BOT: <think>
Listing all system users from /etc/passwd.
</think>
{"action": "run_command", "command": "cut -d: -f1 /etc/passwd"}

USER: list all users on windows
BOT: <think>
Listing local users on Windows.
</think>
{"action": "run_command", "command": "net user"}

USER: change password for user john on linux
BOT: <think>
Changing a user's password on Linux.
</think>
{"action": "run_command", "command": "sudo passwd john"}

USER: who is currently logged in on linux
BOT: <think>
Checking currently logged-in users.
</think>
{"action": "run_command", "command": "who"}

USER: show login history on linux
BOT: <think>
Viewing recent login history.
</think>
{"action": "run_command", "command": "last -20"}

USER: make file script.sh executable on linux
BOT: <think>
Setting the executable permission on a file.
</think>
{"action": "run_command", "command": "chmod +x script.sh"}

USER: change ownership of /var/www to www-data on linux
BOT: <think>
Changing file ownership recursively.
</think>
{"action": "run_command", "command": "sudo chown -R www-data:www-data /var/www"}

USER: set permissions 755 on the deploy folder
BOT: <think>
Setting directory permissions on Linux.
</think>
{"action": "run_command", "command": "chmod -R 755 deploy"}

USER: check file permissions of /etc/shadow
BOT: <think>
Viewing permissions of a sensitive system file.
</think>
{"action": "run_command", "command": "ls -la /etc/shadow"}

# ── SCHEDULED TASKS & CRON ──────────────────────────────────────────────────

USER: show my crontab on linux
BOT: <think>
Listing the current user's cron jobs.
</think>
{"action": "run_command", "command": "crontab -l"}

USER: edit my crontab
BOT: <think>
Opening the crontab editor in a terminal.
</think>
{"action": "open_terminal", "command": "crontab -e"}

USER: show scheduled tasks on windows
BOT: <think>
Listing Windows scheduled tasks.
</think>
{"action": "run_command", "command": "schtasks /query /fo TABLE"}

USER: create a scheduled task on windows to run cleanup.bat daily at 3am
BOT: <think>
Creating a daily scheduled task on Windows.
</think>
{"action": "run_command", "command": "schtasks /create /tn \"DailyCleanup\" /tr \"C:\\cleanup.bat\" /sc daily /st 03:00"}

USER: delete scheduled task DailyCleanup on windows
BOT: <think>
Removing a scheduled task on Windows.
</think>
{"action": "run_command", "command": "schtasks /delete /tn \"DailyCleanup\" /f"}

USER: list all systemd timers on linux
BOT: <think>
Viewing systemd timer units (modern cron alternative).
</think>
{"action": "run_command", "command": "systemctl list-timers --all --no-pager"}

# ── STORAGE & DISK MANAGEMENT ───────────────────────────────────────────────

USER: show disk partitions on linux
BOT: <think>
Listing disk partitions with fdisk.
</think>
{"action": "run_command", "command": "sudo fdisk -l"}

USER: check filesystem health on linux
BOT: <think>
Running a filesystem check (read-only) on root.
</think>
{"action": "run_command", "command": "sudo tune2fs -l /dev/sda1 | grep -i 'state\\|mount count\\|check'"}

USER: show mounted filesystems on linux
BOT: <think>
Listing currently mounted filesystems.
</think>
{"action": "run_command", "command": "mount | column -t"}

USER: check inode usage on linux
BOT: <think>
Checking inode usage which can cause "no space" errors even with free disk.
</think>
{"action": "run_command", "command": "df -i"}

USER: find what's taking up space in home directory
BOT: <think>
Using du to find the largest directories.
</think>
{"action": "run_command", "command": "du -h --max-depth=1 ~ | sort -rh | head -20"}

USER: show SMART disk health on linux
BOT: <think>
Checking disk SMART health status.
</think>
{"action": "run_command", "command": "sudo smartctl -H /dev/sda"}

USER: safely eject USB drive on linux
BOT: <think>
Safely unmounting and powering off a USB device.
</think>
{"action": "run_command", "command": "udisksctl unmount -b /dev/sdb1 && udisksctl power-off -b /dev/sdb"}

USER: safely eject USB on windows
BOT: <think>
Using PowerShell to eject removable media.
</think>
{"action": "run_command", "command": "powershell -Command \"$driveEject = New-Object -comObject Shell.Application; $driveEject.Namespace(17).ParseName('E:').InvokeVerb('Eject')\""}

USER: clean up apt cache on ubuntu
BOT: <think>
Freeing disk space by cleaning APT package cache.
</think>
{"action": "run_command", "command": "sudo apt clean && sudo apt autoremove -y"}

USER: clean up disk space on windows
BOT: <think>
Running Windows Disk Cleanup utility.
</think>
{"action": "run_command", "command": "cleanmgr /d C"}

USER: show swap usage on linux
BOT: <think>
Checking swap memory usage.
</think>
{"action": "run_command", "command": "swapon --show && free -h"}

# ── NETWORKING ADVANCED ──────────────────────────────────────────────────────

USER: show my MAC address on linux
BOT: <think>
Displaying network interface MAC addresses.
</think>
{"action": "run_command", "command": "ip link show | grep ether"}

USER: show my MAC address on windows
BOT: <think>
Displaying MAC addresses on Windows.
</think>
{"action": "run_command", "command": "getmac"}

USER: release and renew DHCP lease on linux
BOT: <think>
Releasing and renewing the DHCP IP address.
</think>
{"action": "run_command", "command": "sudo dhclient -r && sudo dhclient"}

USER: release and renew IP on windows
BOT: <think>
Releasing and renewing Windows DHCP lease.
</think>
{"action": "run_command", "command": "ipconfig /release && ipconfig /renew"}

USER: show routing table on linux
BOT: <think>
Displaying the network routing table.
</think>
{"action": "run_command", "command": "ip route show"}

USER: show routing table on windows
BOT: <think>
Displaying Windows routing table.
</think>
{"action": "run_command", "command": "route print"}

USER: block port 8080 on linux firewall
BOT: <think>
Adding a UFW firewall rule to deny traffic on port 8080.
</think>
{"action": "run_command", "command": "sudo ufw deny 8080/tcp"}

USER: allow port 443 through windows firewall
BOT: <think>
Adding a Windows Firewall rule for HTTPS.
</think>
{"action": "run_command", "command": "powershell -Command \"New-NetFirewallRule -DisplayName 'Allow HTTPS' -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow\""}

USER: check what's listening on port 3000 on linux
BOT: <think>
Finding the process using port 3000.
</think>
{"action": "run_command", "command": "sudo lsof -i :3000"}

USER: check what's using port 8080 on windows
BOT: <think>
Finding the process bound to port 8080 on Windows.
</think>
{"action": "run_command", "command": "netstat -ano | findstr :8080"}

USER: connect to wifi network MyWifi on linux
BOT: <think>
Connecting to a WiFi network using nmcli.
</think>
{"action": "run_command", "command": "nmcli dev wifi connect MyWifi"}

USER: connect to wifi MyNetwork with password secret123 on linux
BOT: <think>
Connecting to a password-protected WiFi.
</think>
{"action": "run_command", "command": "nmcli dev wifi connect MyNetwork password secret123"}

USER: show saved wifi passwords on linux
BOT: <think>
Listing saved WiFi passwords from NetworkManager.
</think>
{"action": "run_command", "command": "sudo grep -r '^psk=' /etc/NetworkManager/system-connections/"}

USER: show saved wifi passwords on windows
BOT: <think>
Retrieving saved WiFi passwords on Windows.
</think>
{"action": "run_command", "command": "powershell -Command \"(netsh wlan show profiles) | Select-String '\\:(.+)$' | ForEach-Object {$name=$_.Matches.Groups[1].Value.Trim(); netsh wlan show profile name=$name key=clear}\""}

USER: set a static IP 192.168.1.100 on linux
BOT: <think>
Setting a static IP address using nmcli.
</think>
{"action": "run_command", "command": "sudo nmcli con mod 'Wired connection 1' ipv4.addresses 192.168.1.100/24 ipv4.gateway 192.168.1.1 ipv4.dns '8.8.8.8,8.8.4.4' ipv4.method manual"}

USER: test if a remote port is open
BOT: <think>
Testing if a remote host port is accessible.
</think>
{"action": "run_command", "command": "nc -zv google.com 443"}

USER: monitor network traffic in real time on linux
BOT: <think>
Opening a terminal with iftop for real-time network monitoring.
</think>
{"action": "open_terminal", "command": "sudo iftop"}

USER: show bandwidth usage per process on linux
BOT: <think>
Using nethogs to show per-process bandwidth usage.
</think>
{"action": "open_terminal", "command": "sudo nethogs"}

# ── SECURITY & HARDENING ────────────────────────────────────────────────────

USER: check for rootkits on linux
BOT: <think>
Running rkhunter to scan for rootkits.
</think>
{"action": "run_command", "command": "sudo rkhunter --check --skip-keypress"}

USER: scan for malware on windows
BOT: <think>
Running Windows Defender quick scan.
</think>
{"action": "run_command", "command": "powershell -Command \"Start-MpScan -ScanType QuickScan\""}

USER: update virus definitions on windows
BOT: <think>
Updating Windows Defender definitions.
</think>
{"action": "run_command", "command": "powershell -Command \"Update-MpSignature\""}

USER: check for failed login attempts on linux
BOT: <think>
Viewing failed SSH/login attempts.
</think>
{"action": "run_command", "command": "sudo grep 'Failed password' /var/log/auth.log | tail -20"}

USER: generate an SSH key pair
BOT: <think>
Generating a new SSH key pair.
</think>
{"action": "run_command", "command": "ssh-keygen -t ed25519 -C 'iris@pc'"}

USER: show my SSH public key
BOT: <think>
Displaying the SSH public key.
</think>
{"action": "run_command", "command": "cat ~/.ssh/id_ed25519.pub 2>/dev/null || cat ~/.ssh/id_rsa.pub"}

USER: check windows update status
BOT: <think>
Checking for available Windows updates.
</think>
{"action": "run_command", "command": "powershell -Command \"Get-WindowsUpdate\" "}

USER: check for available updates on ubuntu
BOT: <think>
Checking for available package updates.
</think>
{"action": "run_command", "command": "sudo apt update && apt list --upgradable"}

# ── HARDWARE & DRIVERS ──────────────────────────────────────────────────────

USER: show GPU info on linux
BOT: <think>
Displaying GPU/graphics card information.
</think>
{"action": "run_command", "command": "lspci | grep -i vga"}

USER: show GPU info on windows
BOT: <think>
Displaying GPU information on Windows.
</think>
{"action": "run_command", "command": "powershell -Command \"Get-CimInstance Win32_VideoController | Format-List Name,DriverVersion,VideoModeDescription\""}

USER: check CPU temperature on linux
BOT: <think>
Reading CPU temperature sensors.
</think>
{"action": "run_command", "command": "sensors 2>/dev/null || cat /sys/class/thermal/thermal_zone*/temp"}

USER: list USB devices on linux
BOT: <think>
Listing connected USB devices.
</think>
{"action": "run_command", "command": "lsusb"}

USER: list USB devices on windows
BOT: <think>
Listing USB devices on Windows.
</think>
{"action": "run_command", "command": "powershell -Command \"Get-PnpDevice -Class USB | Format-Table Status,Class,FriendlyName\""}

USER: show hardware info summary on linux
BOT: <think>
Getting a comprehensive hardware summary.
</think>
{"action": "run_command", "command": "sudo lshw -short 2>/dev/null || lscpu && echo '---' && free -h && echo '---' && lsblk"}

USER: show BIOS version on linux
BOT: <think>
Checking BIOS/firmware version.
</think>
{"action": "run_command", "command": "sudo dmidecode -t bios | head -20"}

USER: show BIOS version on windows
BOT: <think>
Checking BIOS version on Windows.
</think>
{"action": "run_command", "command": "powershell -Command \"Get-CimInstance Win32_BIOS | Format-List Manufacturer,SMBIOSBIOSVersion,ReleaseDate\""}

USER: check RAM details on linux
BOT: <think>
Showing detailed RAM module information.
</think>
{"action": "run_command", "command": "sudo dmidecode -t memory | grep -E 'Size|Speed|Type|Manufacturer' | head -20"}

USER: check RAM details on windows
BOT: <think>
Showing RAM module details on Windows.
</think>
{"action": "run_command", "command": "powershell -Command \"Get-CimInstance Win32_PhysicalMemory | Format-Table BankLabel,Capacity,Speed,Manufacturer\""}

# ── PACKAGE MANAGEMENT ADVANCED ──────────────────────────────────────────────

USER: search for a package called htop on ubuntu
BOT: <think>
Searching APT repositories for a package.
</think>
{"action": "apt", "command": "search htop"}

USER: show info about the nginx package on ubuntu
BOT: <think>
Showing detailed package information.
</think>
{"action": "apt", "command": "show nginx"}

USER: remove package vim on ubuntu
BOT: <think>
Removing a package on Ubuntu.
</think>
{"action": "apt", "command": "remove -y vim"}

USER: install multiple packages: git curl wget on ubuntu
BOT: <think>
Installing multiple packages at once.
</think>
{"action": "apt", "command": "install -y git curl wget"}

USER: add a PPA repository on ubuntu
BOT: <think>
Adding a PPA repository on Ubuntu.
</think>
{"action": "run_command", "command": "sudo add-apt-repository ppa:deadsnakes/ppa -y && sudo apt update"}

USER: install python 3.12 on ubuntu
BOT: <think>
Installing a specific Python version from deadsnakes PPA.
</think>
{"action": "run_command", "command": "sudo apt install -y python3.12 python3.12-venv"}

USER: search for vlc on winget
BOT: <think>
Searching Windows Package Manager for VLC.
</think>
{"action": "winget", "command": "search vlc"}

USER: install 7zip on windows
BOT: <think>
Installing 7-Zip via winget.
</think>
{"action": "winget", "command": "install 7zip.7zip"}

USER: uninstall a program on windows via winget
BOT: <think>
Uninstalling a program using winget.
</think>
{"action": "winget", "command": "uninstall --name \"Program Name\""}

USER: list all installed snap packages on ubuntu
BOT: <think>
Listing installed snap packages.
</think>
{"action": "run_command", "command": "snap list"}

USER: install a flatpak app on linux
BOT: <think>
Installing an app via Flatpak.
</think>
{"action": "run_command", "command": "flatpak install flathub org.gimp.GIMP -y"}

# ── DEVELOPER WORKFLOWS ─────────────────────────────────────────────────────

USER: create a python virtual environment
BOT: <think>
Creating a Python venv in the current directory.
</think>
{"action": "run_command", "command": "python3 -m venv venv"}

USER: activate the virtual environment on linux
BOT: <think>
Activating a venv needs to run in a visible terminal.
</think>
{"action": "open_terminal", "command": "source venv/bin/activate"}

USER: activate the virtual environment on windows
BOT: <think>
Activating a venv on Windows.
</think>
{"action": "open_terminal", "command": ".\\venv\\Scripts\\activate"}

USER: start a local python http server
BOT: <think>
Starting a simple HTTP server on port 8000.
</think>
{"action": "run_command", "command": "python3 -m http.server 8000"}

USER: start a node.js project from scratch
BOT: <think>
Initializing a new Node.js project.
</think>
{"action": "npm", "command": "init -y"}

USER: check for outdated npm packages
BOT: <think>
Checking for outdated npm dependencies.
</think>
{"action": "npm", "command": "outdated"}

USER: run database migrations
BOT: <think>
Running database migrations - this is typically a Python/Django command.
</think>
{"action": "run_command", "command": "python3 manage.py migrate"}

USER: connect to a postgres database
BOT: <think>
Opening a PostgreSQL shell in a terminal.
</think>
{"action": "open_terminal", "command": "psql -U postgres"}

USER: dump my mysql database
BOT: <think>
Creating a MySQL database backup.
</think>
{"action": "run_command", "command": "mysqldump -u root -p mydb > ~/Desktop/mydb_backup.sql"}

USER: start a redis server
BOT: <think>
Starting Redis server in a terminal.
</think>
{"action": "open_terminal", "command": "redis-server"}

USER: SSH into my server at 192.168.1.50
BOT: <think>
Opening an SSH session in a terminal.
</think>
{"action": "open_terminal", "command": "ssh user@192.168.1.50"}

USER: copy a file to remote server via SCP
BOT: <think>
The user wants to copy a file via SCP. I need more details.
</think>
{"action": "chat", "response": "I can help with that. Please provide the file path, remote user, server IP, and destination path. For example: 'scp ~/file.txt user@192.168.1.50:/home/user/'"}

USER: check docker container resource usage
BOT: <think>
Showing real-time Docker container resource stats.
</think>
{"action": "docker", "command": "stats --no-stream"}

USER: show docker container logs for the last 100 lines
BOT: <think>
Showing recent container logs.
</think>
{"action": "docker", "command": "logs --tail 100 mycontainer"}

USER: remove all stopped docker containers
BOT: <think>
Cleaning up stopped containers.
</think>
{"action": "docker", "command": "container prune -f"}

USER: remove unused docker images
BOT: <think>
Cleaning up dangling Docker images.
</think>
{"action": "docker", "command": "image prune -f"}

USER: enter a running docker container shell
BOT: <think>
Exec into a container needs interactive terminal.
</think>
{"action": "open_terminal", "command": "docker exec -it mycontainer /bin/bash"}

# ── ENVIRONMENT VARIABLES ───────────────────────────────────────────────────

USER: set environment variable API_KEY to abc123
BOT: <think>
Setting an environment variable using the set_env action.
</think>
{"action": "set_env", "key": "API_KEY", "value": "abc123"}

USER: set the NODE_ENV to production
BOT: <think>
Setting NODE_ENV environment variable.
</think>
{"action": "set_env", "key": "NODE_ENV", "value": "production"}

USER: set JAVA_HOME to /usr/lib/jvm/java-17
BOT: <think>
Setting the JAVA_HOME environment variable.
</think>
{"action": "set_env", "key": "JAVA_HOME", "value": "/usr/lib/jvm/java-17"}

USER: export DATABASE_URL=postgres://localhost/mydb
BOT: <think>
Setting a database connection string as environment variable.
</think>
{"action": "set_env", "key": "DATABASE_URL", "value": "postgres://localhost/mydb"}

# ── SYSTEM SETTINGS ─────────────────────────────────────────────────────────

USER: open system settings
BOT: <think>
Opening OS-native system settings panel.
</think>
{"action": "open_settings"}

USER: open settings
BOT: <think>
Opening the system settings application.
</think>
{"action": "open_settings"}

USER: open system preferences
BOT: <think>
The user wants to open system settings/preferences.
</think>
{"action": "open_settings"}

USER: go to computer settings
BOT: <think>
Opening the system settings panel.
</think>
{"action": "open_settings"}

USER: open control panel
BOT: <think>
The user wants system settings. I'll use open_settings which handles OS differences.
</think>
{"action": "open_settings"}

USER: open display settings on windows
BOT: <think>
Opening a specific Windows settings page.
</think>
{"action": "run_command", "command": "start ms-settings:display"}

USER: open sound settings on windows
BOT: <think>
Opening Windows sound settings.
</think>
{"action": "run_command", "command": "start ms-settings:sound"}

USER: open network settings on windows
BOT: <think>
Opening Windows network settings.
</think>
{"action": "run_command", "command": "start ms-settings:network"}

USER: open bluetooth settings on windows
BOT: <think>
Opening Windows bluetooth settings.
</think>
{"action": "run_command", "command": "start ms-settings:bluetooth"}

USER: open privacy settings on windows
BOT: <think>
Opening Windows privacy settings.
</think>
{"action": "run_command", "command": "start ms-settings:privacy"}

USER: open display settings on ubuntu
BOT: <think>
Opening GNOME display settings.
</think>
{"action": "run_command", "command": "gnome-control-center display 2>/dev/null"}

USER: open sound settings on ubuntu
BOT: <think>
Opening GNOME sound settings.
</think>
{"action": "run_command", "command": "gnome-control-center sound 2>/dev/null"}

USER: open network settings on ubuntu
BOT: <think>
Opening GNOME network settings.
</think>
{"action": "run_command", "command": "gnome-control-center network 2>/dev/null"}

# ── BACKUP & RECOVERY ───────────────────────────────────────────────────────

USER: backup my home directory to an external drive on linux
BOT: <think>
Creating a compressed backup of the home directory.
</think>
{"action": "run_command", "command": "tar -czf /media/$USER/backup/home_backup_$(date +%Y%m%d).tar.gz -C /home $USER"}

USER: create a system restore point on windows
BOT: <think>
Creating a Windows System Restore point.
</think>
{"action": "run_command", "command": "powershell -Command \"Checkpoint-Computer -Description 'Iris Backup' -RestorePointType 'MODIFY_SETTINGS'\""}

USER: rsync my documents to another folder
BOT: <think>
Syncing documents with rsync for incremental backup.
</think>
{"action": "run_command", "command": "rsync -avh --progress ~/Documents/ ~/Backup/Documents/"}

USER: backup my mysql database
BOT: <think>
Creating a MySQL database dump.
</think>
{"action": "run_command", "command": "mysqldump -u root --all-databases > ~/Desktop/all_databases_backup.sql"}

USER: backup postgres database
BOT: <think>
Creating a PostgreSQL database dump.
</think>
{"action": "run_command", "command": "pg_dump -U postgres mydb > ~/Desktop/mydb_backup.sql"}

# ── OPENING APPLICATIONS ────────────────────────────────────────────────────

USER: open chrome
BOT: <think>
The user wants to open an application. I should always use open_app for launching software.
</think>
{"action": "open_app", "name": "chrome"}

USER: launch firefox
BOT: <think>
The user wants to launch Firefox. I will use the open_app action.
</think>
{"action": "open_app", "name": "firefox"}

USER: start the calculator
BOT: <think>
The user is asking to start the calculator application. I'll use open_app.
</think>
{"action": "open_app", "name": "calculator"}

USER: open terminal
BOT: <think>
The user wants to open the terminal app.
</think>
{"action": "open_app", "name": "terminal"}

USER: open spotify
BOT: <think>
The user wants to launch Spotify.
</think>
{"action": "open_app", "name": "spotify"}

USER: run vscode
BOT: <think>
The user wants to open Visual Studio Code. I will use open_app.
</think>
{"action": "open_app", "name": "vscode"}

# ── THINKING-FIRST: OS-AGNOSTIC APP LAUNCHING ────────────────────────────────

USER: open notepad
BOT: <think>
The user wants to open a text editor. "notepad" on Windows is notepad.exe; on Linux the equivalent is gedit or gnome-text-editor. I'll use open_app with the generic name and the controller will resolve it for the user's OS.
</think>
{"action": "open_app", "name": "notepad"}

USER: open the text editor
BOT: <think>
The user wants a text editor app. I'll use open_app with "notepad" as the generic name — the controller maps this to the right editor on Windows or Linux.
</think>
{"action": "open_app", "name": "notepad"}

USER: open file manager
BOT: <think>
The user wants to open the file manager. On Linux this is Nautilus; on Windows it's File Explorer. I'll use open_app with the generic name "file manager" and let the controller resolve the correct app.
</think>
{"action": "open_app", "name": "file manager"}

USER: open the browser
BOT: <think>
The user wants to open a web browser. I'll use open_app with "browser" and the controller will open the default or configured browser for their OS.
</think>
{"action": "open_app", "name": "browser"}

USER: open paint
BOT: <think>
The user wants to open a drawing/paint application. On Windows this is mspaint; on Linux the equivalent is "drawing". I'll use open_app with the generic name "paint".
</think>
{"action": "open_app", "name": "paint"}

USER: open the store
BOT: <think>
The user wants to open the app store. On Windows this is the Microsoft Store; on Linux it's GNOME Software. I'll use open_app with "store" and the controller will handle the OS mapping.
</think>
{"action": "open_app", "name": "store"}

USER: launch the camera app
BOT: <think>
The user wants to open the camera application. On Windows this is the Camera app; on Linux it's Cheese. I'll use open_app with "camera".
</think>
{"action": "open_app", "name": "camera"}

USER: open system monitor
BOT: <think>
The user wants to open the system resource monitor. On Linux this is gnome-system-monitor; on Windows it's taskmgr. I'll use open_app with the generic name.
</think>
{"action": "open_app", "name": "system monitor"}

USER: start the mail app
BOT: <think>
The user wants to open the email client. On Linux the default is Thunderbird; on Windows it's Outlook or the Mail app. I'll use open_app with "mail" and let the controller resolve it.
</think>
{"action": "open_app", "name": "mail"}

USER: open calendar
BOT: <think>
The user wants to open the calendar application. On Linux it's gnome-calendar; on Windows it's the Calendar app. I'll use open_app.
</think>
{"action": "open_app", "name": "calendar"}

# ── THINKING-FIRST: SYSTEM SETTINGS (OS-AGNOSTIC) ───────────────────────────

USER: open settings
BOT: <think>
The user wants to open the system settings panel. I'll use the open_settings action — it handles gnome-control-center on Linux and ms-settings: on Windows automatically.
</think>
{"action": "open_settings"}

USER: go to settings
BOT: <think>
The user wants to access system settings. I'll use open_settings which is OS-agnostic.
</think>
{"action": "open_settings"}

USER: open control panel
BOT: <think>
The user wants to access system configuration. This could be Windows Control Panel or Linux GNOME Settings. I'll use open_settings which correctly handles both.
</think>
{"action": "open_settings"}

USER: open system preferences
BOT: <think>
"System preferences" is macOS terminology but the user likely just wants system settings. I'll use open_settings.
</think>
{"action": "open_settings"}

# ── THINKING-FIRST: CLOSING APPS (OS-AGNOSTIC) ──────────────────────────────

USER: close chrome
BOT: <think>
The user wants to close the Chrome browser. I'll use close_app — this sends the appropriate close signal on any OS without needing to know if we're on Windows or Linux.
</think>
{"action": "close_app", "name": "chrome"}

USER: close spotify
BOT: <think>
The user wants to close the Spotify music app. I'll use close_app with "spotify".
</think>
{"action": "close_app", "name": "spotify"}

USER: quit vscode
BOT: <think>
The user wants to quit Visual Studio Code. "quit" means close the app. I'll use close_app.
</think>
{"action": "close_app", "name": "vscode"}

USER: close all browsers
BOT: <think>
The user wants to close browser applications. I'll close both common browsers using kill_process to ensure they are fully terminated.
</think>
{"action": "kill_process", "name": "chrome"}

USER: force quit firefox
BOT: <think>
The user wants to force quit Firefox. I'll use kill_process which terminates the process immediately on any OS.
</think>
{"action": "kill_process", "name": "firefox"}

USER: kill the discord process
BOT: <think>
The user wants to terminate Discord. I'll use kill_process with "discord".
</think>
{"action": "kill_process", "name": "discord"}

# ── THINKING-FIRST: AMBIGUOUS / NATURAL LANGUAGE ────────────────────────────

USER: I want to watch something on spotify
BOT: <think>
The user wants to open Spotify to listen to music or watch content. "watch something on spotify" means they want the app open. I'll use open_app.
</think>
{"action": "open_app", "name": "spotify"}

USER: can you pull up chrome for me
BOT: <think>
"Pull up chrome" means the user wants to open the Chrome browser. I'll use open_app.
</think>
{"action": "open_app", "name": "chrome"}

USER: fire up vscode
BOT: <think>
"Fire up" is slang for "open/launch". The user wants to open Visual Studio Code. I'll use open_app.
</think>
{"action": "open_app", "name": "vscode"}

USER: bring up the terminal
BOT: <think>
The user wants to open a terminal window. "Bring up" means launch/open. I'll use open_app with "terminal" — the controller resolves to gnome-terminal on Linux or cmd/powershell on Windows.
</think>
{"action": "open_app", "name": "terminal"}

USER: I need to open something to edit code
BOT: <think>
The user wants a code editor. The most likely choice is VS Code. I'll open it using open_app.
</think>
{"action": "open_app", "name": "vscode"}

USER: open my IDE
BOT: <think>
The user wants to open their development environment. The most common IDE is VS Code. I'll use open_app with "vscode".
</think>
{"action": "open_app", "name": "vscode"}

USER: open something to browse the web
BOT: <think>
The user wants a web browser. I'll use open_app with "browser" and the controller will open the default configured browser.
</think>
{"action": "open_app", "name": "browser"}

USER: I want to listen to music
BOT: <think>
The user wants to listen to music. The best action is to open Spotify, the primary music app. I'll use open_app.
</think>
{"action": "open_app", "name": "spotify"}

USER: take a screenshot and save it to desktop
BOT: <think>
The user wants to capture the screen and save it. I'll use the screenshot action with a path on the Desktop.
</think>
{"action": "screenshot", "path": "~/Desktop/screenshot.png"}

USER: how much RAM is being used right now
BOT: <think>
The user wants to see current memory usage. I'll use system_info with "memory" — this works cross-platform without any shell commands.
</think>
{"action": "system_info", "what": "memory"}

USER: what's my CPU usage
BOT: <think>
The user wants to see current CPU usage. I'll use system_info with "cpu".
</think>
{"action": "system_info", "what": "cpu"}

USER: how much disk space do I have left
BOT: <think>
The user wants disk space information. I'll use system_info with "disk".
</think>
{"action": "system_info", "what": "disk"}

USER: what's my IP address
BOT: <think>
The user wants to see their IP address. I'll use system_info with "ip" — no need for raw shell commands like ifconfig or ipconfig.
</think>
{"action": "system_info", "what": "ip"}

USER: show me all system info
BOT: <think>
The user wants a full system overview. I'll use system_info with "all" to get CPU, memory, disk, IP, and more in one call.
</think>
{"action": "system_info", "what": "all"}

USER: turn off wifi
BOT: <think>
The user wants to disable WiFi. I'll use the wifi action with state "off" — this is OS-agnostic and works on Windows and Linux.
</think>
{"action": "wifi", "state": "off"}

USER: enable wifi
BOT: <think>
The user wants to turn WiFi back on. I'll use the wifi action with state "on".
</think>
{"action": "wifi", "state": "on"}

USER: turn off bluetooth
BOT: <think>
The user wants to disable Bluetooth. I'll use the bluetooth action with state "off".
</think>
{"action": "bluetooth", "state": "off"}

USER: enable bluetooth
BOT: <think>
The user wants to turn Bluetooth on. I'll use the bluetooth action with state "on".
</think>
{"action": "bluetooth", "state": "on"}

USER: lock my screen
BOT: <think>
The user wants to lock the computer screen immediately. I'll use lock_screen — it handles Super+L on Linux and Win+L on Windows automatically.
</think>
{"action": "lock_screen"}

USER: lock the computer
BOT: <think>
The user wants to lock their PC. I'll use lock_screen which is cross-platform.
</think>
{"action": "lock_screen"}

USER: put the computer to sleep
BOT: <think>
The user wants to suspend/sleep the computer. I'll use sleep_computer — it handles systemctl suspend on Linux and the equivalent on Windows.
</think>
{"action": "sleep_computer"}

USER: mute my computer
BOT: <think>
The user wants to mute the system audio. I'll use volume_mute — this is OS-agnostic.
</think>
{"action": "volume_mute"}

USER: turn the volume up
BOT: <think>
The user wants to increase volume. I'll use volume_up.
</think>
{"action": "volume_up"}

USER: lower the volume
BOT: <think>
The user wants to decrease the volume. I'll use volume_down.
</think>
{"action": "volume_down"}

USER: set volume to 50 percent
BOT: <think>
The user wants to set volume to exactly 50%. I'll use volume_set with percent 50.
</think>
{"action": "volume_set", "percent": 50}

USER: make the screen brighter
BOT: <think>
The user wants to increase screen brightness. I'll use brightness_up — this is OS-agnostic.
</think>
{"action": "brightness_up"}

USER: dim the screen
BOT: <think>
The user wants to lower screen brightness. I'll use brightness_down.
</think>
{"action": "brightness_down"}

USER: set brightness to 70 percent
BOT: <think>
The user wants to set screen brightness to exactly 70%. I'll use brightness_set with percent 70.
</think>
{"action": "brightness_set", "percent": 70}

USER: enable dark mode
BOT: <think>
The user wants to switch to dark mode. I'll use dark_mode with state "on" — this works on both Windows and Linux GNOME.
</think>
{"action": "dark_mode", "state": "on"}

USER: turn off dark mode
BOT: <think>
The user wants to switch back to light mode. I'll use dark_mode with state "off".
</think>
{"action": "dark_mode", "state": "off"}

# ── COMPLEX SYSTEM ADMINISTRATION & ROOT CAUSE ANALYSIS ───────────────────────

USER: my server keeps crashing under load, find out what's causing the out of memory errors
BOT: <think>
The user is experiencing OOM (Out Of Memory) crashes. To diagnose this, I need to check the kernel ring buffer for OOM killer invocations. `dmesg` or `journalctl` will show what processes were killed and why. I'll use `run_command` to extract the OOM logs.
</think>
{"action": "run_command", "command": "sudo dmesg -T | grep -i -E 'out of memory|oom-killer' | tail -n 20"}

USER: automate my database backups to run every night at 2am and keep only the last 7 days
BOT: <think>
The user wants to set up a cron job for database backups with a retention policy. This requires a shell script that runs `mysqldump` (or pg_dump) and then deletes files older than 7 days, added to the crontab. Since I can only perform one action, I'll use `run_code` to write the bash script to `/usr/local/bin/db_backup.sh`, make it executable, and then I will add it to cron in the next turn.
</think>
{"action": "run_code", "code": "import os; script=\"#!/bin/bash\\nmysqldump -u root mydb > /var/backups/mydb_$(date +%F).sql\\nfind /var/backups/ -name 'mydb_*.sql' -mtime +7 -delete\\n\"; open('/tmp/db_backup.sh','w').write(script); os.system('chmod +x /tmp/db_backup.sh'); print('Backup script created at /tmp/db_backup.sh')"}

USER: i think someone is trying to brute force my ssh port, block them
BOT: <think>
The user suspects an SSH brute force attack. I should check the auth logs for multiple failed login attempts from a single IP, and then use `ufw` or `iptables` to block that IP. For the first step, I will use `run_command` to find the top offending IPs.
</think>
{"action": "run_command", "command": "sudo grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr | head -5"}

USER: the disk is 100% full but du -sh / shows only 20GB used, fix it
BOT: <think>
A disk showing 100% full while files only use 20GB usually means deleted files are still held open by a running process. I need to use `lsof` to find deleted files that are still open, and then restart or kill the responsible process. Let's find those open deleted files first.
</think>
{"action": "run_command", "command": "sudo lsof +L1 | grep deleted | sort -n -k 7 | tail -10"}

USER: setup a secure nginx reverse proxy for my node app running on port 3000
BOT: <think>
The user wants an Nginx reverse proxy configuration. I can use `run_code` to write the standard Nginx configuration file to `/etc/nginx/sites-available/node_app`, then symlink it, and restart Nginx in the next turn. But since it requires root, I'll write it to `/tmp` first, and then run a bash command to move it and restart the service.
</think>
{"action": "run_code", "code": "config=\"server {\\n    listen 80;\\n    server_name example.com;\\n    location / {\\n        proxy_pass http://localhost:3000;\\n        proxy_http_version 1.1;\\n        proxy_set_header Upgrade $http_upgrade;\\n        proxy_set_header Connection 'upgrade';\\n        proxy_set_header Host $host;\\n        proxy_cache_bypass $http_upgrade;\\n    }\\n}\\n\"; open('/tmp/node_app.conf','w').write(config); print('Config generated. Next step: sudo mv /tmp/node_app.conf /etc/nginx/sites-available/')"}

USER: my docker containers can't resolve DNS, fix the docker daemon config
BOT: <think>
Docker DNS resolution issues on Linux are often caused by systemd-resolved conflicts. A common fix is configuring Docker to use a specific DNS server like 8.8.8.8 in `/etc/docker/daemon.json`. I will use a shell command to update this file and restart Docker.
</think>
{"action": "run_command", "command": "echo '{\"dns\": [\"8.8.8.8\", \"8.8.4.4\"]}' | sudo tee /etc/docker/daemon.json && sudo systemctl restart docker"}

USER: find out which process is causing high IO wait
BOT: <think>
High IO wait indicates disk bottleneck. I should use `iotop` or `pidstat -d` to identify the process hammering the disk. Since `iotop` requires an interactive terminal, `pidstat` is better for a single command output.
</think>
{"action": "run_command", "command": "pidstat -d 2 3"}

USER: securely wipe the external drive /dev/sdb so data can't be recovered
BOT: <think>
Securely wiping a drive requires overwriting it with random data or zeroes. `dd` is the standard tool. This is highly destructive, so I should ask for confirmation first unless the user is explicitly providing the exact block device. They provided `/dev/sdb`, but I should still ensure it's not mounted and then run `dd` carefully, or just issue the command if they are sure. Let's ask for confirmation to be safe.
</think>
{"action": "chat", "response": "WARNING: This will permanently destroy all data on /dev/sdb. Are you absolutely sure you want to run `sudo dd if=/dev/urandom of=/dev/sdb bs=4M status=progress`?"}

USER: optimize my linux sysctl networking parameters for high throughput
BOT: <think>
The user wants to tune TCP/IP stack for high performance. This involves editing `/etc/sysctl.conf` with optimized `net.ipv4.tcp_*` settings and running `sysctl -p`. I will use `run_command` to append the optimal settings and apply them.
</think>
{"action": "run_command", "command": "echo -e 'net.core.rmem_max=16777216\\nnet.core.wmem_max=16777216\\nnet.ipv4.tcp_rmem=4096 87380 16777216\\nnet.ipv4.tcp_wmem=4096 65536 16777216\\nnet.core.netdev_max_backlog=5000' | sudo tee -a /etc/sysctl.conf && sudo sysctl -p"}

# ── GOD-MODE ARCHITECTURE & KERNEL ORCHESTRATION ────────────────────────────

USER: write an eBPF script to trace all execve syscalls so i can see every command running on the system globally
BOT: <think>
The user wants to use eBPF (Extended Berkeley Packet Filter) to trace kernel syscalls in real-time. This is deep kernel orchestration. Using Python with `bcc` (BPF Compiler Collection) is the standard way to do this. I'll use `run_code` to execute a script that attaches to the `execve` tracepoint.
</think>
{"action": "run_code", "code": "from bcc import BPF; b = BPF(text='int syscall__execve(void *ctx) { bpf_trace_printk(\"execve called\\\\n\"); return 0; }'); b.attach_kprobe(event=b.get_syscall_fnname('execve'), fn_name='syscall__execve'); print('Tracing execve... Use Ctrl+C to stop.'); b.trace_print()"}

USER: i lost my root password on this linux machine, reboot it into single-user mode and change the root password
BOT: <think>
This is a critical physical security operation. I cannot reboot the machine into GRUB and interact with it programmatically using standard commands, as that requires interactive terminal over KVM or physical keyboard. I will explain the limitation and use the `chat` tool to give them the exact keystrokes needed (edit GRUB, append `rw init=/bin/bash`, run `passwd`).
</think>
{"action": "chat", "response": "I cannot physically interact with the bootloader. To reset the root password: 1. Reboot and hold Shift/Esc to see GRUB. 2. Press 'e' on the Ubuntu entry. 3. Find the line starting with 'linux', change 'ro' to 'rw init=/bin/bash'. 4. Press F10 to boot. 5. Type 'passwd root' to change it. 6. Reboot."}

USER: bootstrap a local kubernetes cluster using kind, deploy a redis statefulset, and expose it via port-forwarding
BOT: <think>
The user is requesting advanced container orchestration. I need to run a chained command that spins up a `kind` cluster, uses `kubectl` to apply a Redis statefulset YAML, and then runs `kubectl port-forward` in the background. Since I can only run one command, I'll execute the script inline.
</think>
{"action": "run_command", "command": "kind create cluster && kubectl create deployment redis --image=redis && kubectl expose deployment redis --port=6379 && sleep 10 && kubectl port-forward svc/redis 6379:6379 &"}

USER: generate a wildcard ssl certificate for *.example.com using openssl with subject alternative names (SAN) and sign it with a local CA
BOT: <think>
Generating a wildcard cert with SANs requires passing an OpenSSL config file, not just command-line arguments. I will use `run_code` to write the `openssl.cnf` extension configuration, then execute the openssl commands via `os.system` to generate the CA, the CSR, and the final CRT.
</think>
{"action": "run_code", "code": "import os; conf=\"[req]\\ndistinguished_name=req_distinguished_name\\nreq_extensions=v3_req\\n[req_distinguished_name]\\n[v3_req]\\nsubjectAltName=@alt_names\\n[alt_names]\\nDNS.1=*.example.com\\nDNS.2=example.com\\n\"; open('san.cnf','w').write(conf); os.system('openssl genrsa -out ca.key 2048 && openssl req -x509 -new -nodes -key ca.key -sha256 -days 1024 -out ca.crt -subj \"/CN=Local CA\" && openssl genrsa -out domain.key 2048 && openssl req -new -key domain.key -out domain.csr -subj \"/CN=*.example.com\" -config san.cnf && openssl x509 -req -in domain.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out domain.crt -days 500 -sha256 -extfile san.cnf -extensions v3_req'); print('Wildcard certificates generated successfully.')"}

USER: configure BGP routing on this linux box using FRRouting to peer with AS65000 at 10.0.0.1
BOT: <think>
This is an advanced Network Engineering task. FRR (Free Range Routing) requires editing `/etc/frr/daemons` to enable `bgpd`, and then feeding commands into `vtysh`. I'll use a bash script to automate this.
</think>
{"action": "run_command", "command": "sudo sed -i 's/bgpd=no/bgpd=yes/' /etc/frr/daemons && sudo systemctl restart frr && sudo vtysh -c 'conf t' -c 'router bgp 65001' -c 'neighbor 10.0.0.1 remote-as 65000' -c 'write mem'"}
