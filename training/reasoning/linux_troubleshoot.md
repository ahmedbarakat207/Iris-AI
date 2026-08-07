SYSTEM: You are an AI PC assistant. The user will ask you to perform tasks. Respond with a single JSON object that describes the action to take.

Available actions:
- open_website(url)
- open_app(name)
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

# --- File Management ---
USER: list all files in the current directory including hidden ones
BOT: {"action": "run_command", "command": "ls -la"}

USER: copy the config file to a backup
BOT: {"action": "run_command", "command": "cp config.conf config.conf.bak"}

USER: move the photos folder to the external drive
BOT: {"action": "run_command", "command": "mv ~/Pictures /Volumes/External/Photos"}

USER: delete the temporary files in /tmp
BOT: {"action": "run_command", "command": "rm -rf /tmp/*"}

USER: find all files larger than 100MB in my home folder
BOT: {"action": "run_command", "command": "find ~ -type f -size +100M"}

USER: count how many lines are in the log file
BOT: {"action": "run_command", "command": "wc -l system.log"}

USER: search for the word 'error' in all log files
BOT: {"action": "run_command", "command": "grep -r \"error\" /var/log"}

USER: create a compressed archive of the project folder
BOT: {"action": "run_command", "command": "tar -czf project.tar.gz ./project"}

USER: extract the contents of archive.zip
BOT: {"action": "run_command", "command": "unzip archive.zip"}

USER: change the owner of the web server folder to www-data
BOT: {"action": "run_command", "command": "sudo chown -R www-data:www-data /var/www/html"}

# --- System & Monitoring ---
USER: show me a summary of system resources
BOT: {"action": "run_command", "command": "top -l 1 -n 10"}

USER: check the kernel version
BOT: {"action": "run_command", "command": "uname -a"}

USER: show me the distribution version
BOT: {"action": "run_command", "command": "cat /etc/os-release"}

USER: how long has the system been running?
BOT: {"action": "run_command", "command": "uptime"}

USER: show me the last 50 lines of the system log
BOT: {"action": "run_command", "command": "tail -n 50 /var/log/system.log"}

USER: check which processes are using the most memory
BOT: {"action": "run_command", "command": "ps aux --sort=-%mem | head -n 11"}

USER: kill the process with PID 1234
BOT: {"action": "run_command", "command": "kill -9 1234"}

USER: check the disk usage in human readable format
BOT: {"action": "run_command", "command": "df -h"}

USER: check the temperature of the CPU
BOT: {"action": "run_command", "command": "osx-cpu-temp"}

USER: show me the battery status
BOT: {"action": "run_command", "command": "pmset -g batt"}

# --- Networking ---
USER: show me all network interfaces and their IPs
BOT: {"action": "run_command", "command": "ifconfig -a"}

USER: check if I can reach google
BOT: {"action": "run_command", "command": "ping -c 4 google.com"}

USER: trace the route to 8.8.8.8
BOT: {"action": "run_command", "command": "traceroute 8.8.8.8"}

USER: list all listening ports
BOT: {"action": "run_command", "command": "lsof -i -P -n | grep LISTEN"}

USER: find my external IP address
BOT: {"action": "run_command", "command": "curl ifconfig.me"}

USER: lookup the DNS records for iris.ai
BOT: {"action": "run_command", "command": "nslookup iris.ai"}

USER: download the file from this url: http://example.com/file.zip
BOT: {"action": "run_command", "command": "curl -O http://example.com/file.zip"}

USER: check the speed of my connection
BOT: {"action": "run_command", "command": "networksetup -getadslstatus"}

# --- Troubleshooting & Fixes ---
USER: my dns is not working, flush the cache
BOT: {"action": "run_command", "command": "sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"}

USER: reset the wifi interface
BOT: {"action": "run_command", "command": "networksetup -setnetworkserviceenabled Wi-Fi off; sleep 2; networksetup -setnetworkserviceenabled Wi-Fi on"}

USER: the disk is full, find the biggest folders
BOT: {"action": "run_command", "command": "du -sh /* 2>/dev/null | sort -rh | head -n 10"}

USER: my app is crashing with 'too many open files'
BOT: {"action": "run_command", "command": "ulimit -n 4096"}

USER: fix the 'command not found' error for brew
BOT: {"action": "run_command", "command": "export PATH=\"/usr/local/bin:/opt/homebrew/bin:$PATH\""}

USER: permissions denied on my ssh key
BOT: {"action": "run_command", "command": "chmod 600 ~/.ssh/id_rsa"}

USER: check for zombie processes
BOT: {"action": "run_command", "command": "ps axo stat,ppid,pid,comm | grep -w Z"}

USER: repair the disk permissions
BOT: {"action": "run_command", "command": "diskutil repairPermissions /"}

USER: check the smart status of the drive
BOT: {"action": "run_command", "command": "diskutil info / | grep SMART"}

USER: clear the swap memory
BOT: {"action": "run_command", "command": "sudo purge"}

USER: my mac is slow after wake, reset pmset
BOT: {"action": "run_command", "command": "sudo pmset -a restoredefaults"}

USER: stop the indexing process
BOT: {"action": "run_command", "command": "sudo mdutil -i off /"}

USER: re-enable indexing
BOT: {"action": "run_command", "command": "sudo mdutil -i on /"}

USER: find who is using port 8080
BOT: {"action": "run_command", "command": "lsof -i :8080"}

USER: kill whatever is using port 3000
BOT: {"action": "run_command", "command": "fuser -k 3000/tcp"}

USER: check for broken packages
BOT: {"action": "run_command", "command": "brew doctor"}

USER: update all my command line tools
BOT: {"action": "run_command", "command": "brew update && brew upgrade"}

USER: my screen resolution is wrong, reset it
BOT: {"action": "run_command", "command": "displaymode -reset"}

USER: fix the audio driver
BOT: {"action": "run_command", "command": "sudo killall coreaudiod"}

USER: check the system uptime in days
BOT: {"action": "run_command", "command": "uptime | awk '{print $3}'"}

# --- Advanced Troubleshooting ---
USER: find the source of the high load average
BOT: {"action": "run_command", "command": "vmstat 1 5"}

USER: check the disk I/O wait
BOT: {"action": "run_command", "command": "iostat -dx 1 5"}

USER: find which files are currently open by the user
BOT: {"action": "run_command", "command": "lsof -u $USER"}

USER: check the memory allocation in detail
BOT: {"action": "run_command", "command": "vm_stat"}

USER: find why the computer won't sleep
BOT: {"action": "run_command", "command": "pmset -g assertions"}

USER: check for malicious active connections
BOT: {"action": "run_command", "command": "netstat -atup"}

USER: verify the integrity of the system files
BOT: {"action": "run_command", "command": "pkgutil --check-signature /System/Library/Kernels/kernel"}

USER: check the boot log for errors
BOT: {"action": "run_command", "command": "log show --predicate 'eventMessage contains \"error\"' --last 1h"}

USER: check the current temperature of the disk
BOT: {"action": "run_command", "command": "smartctl -a /dev/disk0 | grep Temperature"}

USER: list all kernel extensions loaded
BOT: {"action": "run_command", "command": "kextstat | grep -v com.apple"}

USER: check the firewall status
BOT: {"action": "run_command", "command": "/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate"}

USER: enable the firewall
BOT: {"action": "run_command", "command": "/usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on"}

USER: find where the biggest logs are
BOT: {"action": "run_command", "command": "find /var/log -type f -size +10M"}

USER: check if the system is 64-bit
BOT: {"action": "run_command", "command": "getconf LONG_BIT"}

USER: find the local time of the system
BOT: {"action": "run_command", "command": "date"}

USER: sync the system clock
BOT: {"action": "run_command", "command": "sudo sntp -sS time.apple.com"}

USER: check the power usage of the CPU
BOT: {"action": "run_command", "command": "sudo powermetrics -n 1 --powermetrics_count 1"}

USER: list all mounted drives and their formats
BOT: {"action": "run_command", "command": "mount | column -t"}

USER: check for hardware failures in the log
BOT: {"action": "run_command", "command": "log show --predicate 'process == \"kernel\"' --last 30m | grep -i \"failure\""}

USER: find out which shell I am using
BOT: {"action": "run_command", "command": "echo $SHELL"}

# --- Package Management (macOS & Linux) ---
USER: check available updates via apt
BOT: {"action": "run_command", "command": "apt list --upgradable"}

USER: install htop on linux
BOT: {"action": "run_command", "command": "sudo apt install -y htop"}

USER: install wget via yum
BOT: {"action": "run_command", "command": "sudo yum install -y wget"}

USER: upgrade all brew packages
BOT: {"action": "run_command", "command": "brew upgrade"}

USER: clean brew cache
BOT: {"action": "run_command", "command": "brew cleanup -s"}

USER: search for a package called 'ffmpeg' in homebrew
BOT: {"action": "run_command", "command": "brew search ffmpeg"}

USER: remove the package node via apt
BOT: {"action": "run_command", "command": "sudo apt remove -y node"}

USER: list installed ports in macports
BOT: {"action": "run_command", "command": "port installed"}

USER: update macports tree
BOT: {"action": "run_command", "command": "sudo port selfupdate"}

# --- User Management ---
USER: show the current user's groups
BOT: {"action": "run_command", "command": "groups"}

USER: add a new user named 'john'
BOT: {"action": "run_command", "command": "sudo adduser john"}

USER: delete the user 'testuser' and its home directory
BOT: {"action": "run_command", "command": "sudo userdel -r testuser"}

USER: change the password for user 'admin'
BOT: {"action": "run_command", "command": "sudo passwd admin"}

USER: list all users on the system
BOT: {"action": "run_command", "command": "cat /etc/passwd | cut -d: -f1"}

USER: see who is logged in
BOT: {"action": "run_command", "command": "who"}

USER: add a user to the sudo group
BOT: {"action": "run_command", "command": "sudo usermod -aG sudo username"}

# --- Process Management ---
USER: show all processes of user 'www-data'
BOT: {"action": "run_command", "command": "ps -u www-data"}

USER: display a process tree
BOT: {"action": "run_command", "command": "pstree"}

USER: kill all processes named 'nginx'
BOT: {"action": "run_command", "command": "pkill -f nginx"}

USER: run a process in the background
BOT: {"action": "run_command", "command": "nohup ./long_script.sh &"}

USER: bring the last background job to foreground
BOT: {"action": "run_command", "command": "fg"}

USER: show all running daemons
BOT: {"action": "run_command", "command": "launchctl list"}

USER: restart the cups printing service
BOT: {"action": "run_command", "command": "sudo launchctl kickstart -kp system/org.cups.cupsd"}

USER: list systemd units that failed
BOT: {"action": "run_command", "command": "systemctl --failed"}

USER: enable a systemd service to start at boot
BOT: {"action": "run_command", "command": "sudo systemctl enable sshd"}

# --- Disk & Filesystem ---
USER: show the type of filesystem on /dev/sda1
BOT: {"action": "run_command", "command": "lsblk -f /dev/sda1"}

USER: create a new ext4 partition on /dev/sdb1
BOT: {"action": "run_command", "command": "sudo mkfs.ext4 /dev/sdb1"}

USER: mount a USB drive
BOT: {"action": "run_command", "command": "sudo mount /dev/sdc1 /mnt/usb"}

USER: unmount the drive at /mnt/backup
BOT: {"action": "run_command", "command": "sudo umount /mnt/backup"}

USER: check for bad blocks on /dev/sda
BOT: {"action": "run_command", "command": "sudo badblocks -v /dev/sda"}

USER: find the largest 10 files in the entire system
BOT: {"action": "run_command", "command": "find / -type f -exec du -Sh {} + 2>/dev/null | sort -rh | head -n 10"}

USER: display disk usage of the current directory
BOT: {"action": "run_command", "command": "du -sh ."}

USER: create a RAM disk of size 1GB
BOT: {"action": "run_command", "command": "diskutil erasevolume HFS+ 'RAMDisk' `hdiutil attach -nomount ram://2097152`"}

USER: expand the disk image file
BOT: {"action": "run_command", "command": "hdiutil resize -size 20g image.dmg"}

# --- Security & Permissions ---
USER: list all SUID binaries
BOT: {"action": "run_command", "command": "find / -perm -4000 -type f 2>/dev/null"}

USER: check for open ports via nmap
BOT: {"action": "run_command", "command": "nmap -sT -O localhost"}

USER: scan for viruses using ClamAV
BOT: {"action": "run_command", "command": "clamscan -r /home"}

USER: check SSH login attempts
BOT: {"action": "run_command", "command": "grep \"Failed password\" /var/log/auth.log"}

USER: generate a new SSH key pair
BOT: {"action": "run_command", "command": "ssh-keygen -t ed25519 -C \"your_email@example.com\""}

USER: copy my public key to a remote server
BOT: {"action": "run_command", "command": "ssh-copy-id user@remotehost"}

USER: set immutable flag on a critical file
BOT: {"action": "run_command", "command": "sudo chflags schg /path/to/file"}

USER: check file hashes against known good ones
BOT: {"action": "run_command", "command": "shasum -a 256 /etc/passwd"}

# --- macOS Specific Utilities ---
USER: show all hidden files in Finder
BOT: {"action": "run_command", "command": "defaults write com.apple.finder AppleShowAllFiles YES; killall Finder"}

USER: hide desktop icons
BOT: {"action": "run_command", "command": "defaults write com.apple.finder CreateDesktop false; killall Finder"}

USER: enable the Develop menu in Safari
BOT: {"action": "run_command", "command": "defaults write com.apple.Safari IncludeDevelopMenu -bool true"}

USER: take a screenshot of a specific window
BOT: {"action": "run_command", "command": "screencapture -iW ~/Desktop/screenshot.png"}

USER: record the screen for 10 seconds
BOT: {"action": "run_command", "command": "screencapture -v -T 10 ~/Desktop/recording.mov"}

USER: disable the boot chime
BOT: {"action": "run_command", "command": "sudo nvram SystemAudioVolume=%80"}

USER: show the current keyboard layout
BOT: {"action": "run_command", "command": "defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources"}

USER: set the Dock to auto-hide
BOT: {"action": "run_command", "command": "defaults write com.apple.dock autohide -bool true; killall Dock"}

USER: increase the mouse tracking speed
BOT: {"action": "run_command", "command": "defaults write -g com.apple.mouse.scaling 5"}

USER: display the status of all Spotlight imports
BOT: {"action": "run_command", "command": "mdutil -s /"}

# --- Linux Specific Utilities ---
USER: show available kernel modules
BOT: {"action": "run_command", "command": "lsmod"}

USER: load the kernel module 'vboxdrv'
BOT: {"action": "run_command", "command": "sudo modprobe vboxdrv"}

USER: blacklist a kernel module
BOT: {"action": "run_command", "command": "echo \"blacklist pcspkr\" | sudo tee /etc/modprobe.d/blacklist-pcspkr.conf"}

USER: change the I/O scheduler for sda
BOT: {"action": "run_command", "command": "echo deadline | sudo tee /sys/block/sda/queue/scheduler"}

USER: set the swappiness to 10
BOT: {"action": "run_command", "command": "sudo sysctl vm.swappiness=10"}

USER: show current sysctl kernel parameters
BOT: {"action": "run_command", "command": "sysctl -a"}

USER: check the init system
BOT: {"action": "run_command", "command": "cat /proc/1/comm"}

USER: view the systemd journal for the last boot
BOT: {"action": "run_command", "command": "journalctl -b -1"}

USER: check if SELinux is enforcing
BOT: {"action": "run_command", "command": "getenforce"}

USER: set SELinux to permissive mode
BOT: {"action": "run_command", "command": "sudo setenforce 0"}

# --- Shell & Scripting ---
USER: run a python one-liner to sum a list
BOT: {"action": "run_command", "command": "python3 -c \"import sys; print(sum(int(x) for x in sys.argv[1:]))\" 1 2 3 4 5"}

USER: create a bash script that prints 'hello world'
BOT: {"action": "run_command", "command": "echo -e '#!/bin/bash\\necho \"hello world\"' > hello.sh; chmod +x hello.sh"}

USER: schedule a cron job to run daily at 2am
BOT: {"action": "run_command", "command": "echo \"0 2 * * * /path/to/script.sh\" | crontab -"}

USER: list current cron jobs
BOT: {"action": "run_command", "command": "crontab -l"}

USER: create an alias 'll' for 'ls -l'
BOT: {"action": "run_command", "command": "alias ll='ls -l'"}

USER: write a sed command to replace 'foo' with 'bar' in file.txt
BOT: {"action": "run_command", "command": "sed -i '' 's/foo/bar/g' file.txt"}

USER: use awk to print the second column of a CSV
BOT: {"action": "run_command", "command": "awk -F, '{print $2}' data.csv"}

USER: diff two directories
BOT: {"action": "run_command", "command": "diff -rq dir1 dir2"}

# --- System Rescue & Recovery ---
USER: boot into single user mode command
BOT: {"action": "run_command", "command": "sudo nvram boot-args=\"-s\"; sudo shutdown -r now"}

USER: reset the NVRAM on next boot
BOT: {"action": "run_command", "command": "sudo nvram -c"}

USER: rebuild the kernel extension cache
BOT: {"action": "run_command", "command": "sudo kextcache -i /"}

USER: check and repair the APFS container
BOT: {"action": "run_command", "command": "fsck_apfs -y /dev/disk1"}

USER: scan and repair a Linux ext4 filesystem
BOT: {"action": "run_command", "command": "sudo e2fsck -f /dev/sda1"}

USER: recover a deleted file using extundelete
BOT: {"action": "run_command", "command": "sudo extundelete /dev/sda1 --restore-file /path/to/file"}

USER: chroot into a broken Linux installation
BOT: {"action": "run_command", "command": "sudo mount /dev/sda1 /mnt; sudo mount --bind /dev /mnt/dev; sudo mount --bind /proc /mnt/proc; sudo mount --bind /sys /mnt/sys; sudo chroot /mnt"}

# --- Hardware & Peripherals ---
USER: list USB devices
BOT: {"action": "run_command", "command": "system_profiler SPUSBDataType"}

USER: list PCI devices
BOT: {"action": "run_command", "command": "lspci"}

USER: show detailed RAM information
BOT: {"action": "run_command", "command": "system_profiler SPMemoryDataType"}

USER: check battery cycle count
BOT: {"action": "run_command", "command": "system_profiler SPPowerDataType | grep \"Cycle Count\""}

USER: test microphone input
BOT: {"action": "run_command", "command": "ffmpeg -f avfoundation -i \":0\" -t 5 test.wav"}

USER: list all audio devices
BOT: {"action": "run_command", "command": "system_profiler SPAudioDataType"}

USER: calibrate the display color
BOT: {"action": "run_command", "command": "open /System/Library/ColorSync/Calibrators/Display Calibrator.app"}

# --- Automation & Scheduling ---
USER: create a launchd plist for a script
BOT: {"action": "run_command", "command": "cat > ~/Library/LaunchAgents/local.myscript.plist <<EOF\n<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n<plist version=\"1.0\">\n<dict>\n    <key>Label</key>\n    <string>local.myscript</string>\n    <key>ProgramArguments</key>\n    <array>\n        <string>/path/to/script.sh</string>\n    </array>\n    <key>RunAtLoad</key>\n    <true/>\n</dict>\n</plist>\nEOF"}

USER: load that launchd plist
BOT: {"action": "run_command", "command": "launchctl load ~/Library/LaunchAgents/local.myscript.plist"}

USER: use at to schedule a one-time job
BOT: {"action": "run_command", "command": "echo \"/path/to/script.sh\" | at now + 1 hour"}

USER: list pending at jobs
BOT: {"action": "run_command", "command": "atq"}

USER: remove an at job with id 5
BOT: {"action": "run_command", "command": "atrm 5"}

# --- Additional Genius-Level Commands ---
USER: open the system-wide plist for a specific preference domain
BOT: {"action": "open_file", "path": "/Library/Preferences/com.apple.SoftwareUpdate.plist"}

USER: search for configuration files containing 'Listen 80' in /etc
BOT: {"action": "search_files", "query": "*.conf", "folder": "/etc"}

USER: convert a man page to pdf
BOT: {"action": "run_command", "command": "man -t bash | open -f -a Preview"}

USER: download a whole website with wget
BOT: {"action": "run_command", "command": "wget --recursive --page-requisites --html-extension --convert-links --no-parent http://example.com"}

USER: compress a video with ffmpeg to smaller size
BOT: {"action": "run_command", "command": "ffmpeg -i input.mp4 -vcodec libx265 -crf 28 output.mp4"}

USER: generate a QR code from a URL and open it
BOT: {"action": "run_command", "command": "curl qrenco.de/$(echo -n 'https://iris.ai' | curl -s --data-binary @- qrenco.de) -o qr.png && open qr.png"}

USER: list all symbolic links in home folder
BOT: {"action": "run_command", "command": "find ~ -type l"}

USER: show the difference between two command outputs
BOT: {"action": "run_command", "command": "diff <(ls dir1) <(ls dir2)"}

USER: enable TRIM on a third-party SSD
BOT: {"action": "run_command", "command": "sudo trimforce enable"}

USER: watch a log file in real time with highlighting
BOT: {"action": "run_command", "command": "tail -f /var/log/system.log | grep --color -E 'error|$'"}

USER: get a notification when a long command finishes
BOT: {"action": "run_command", "command": "make; osascript -e 'display notification \"Build finished!\" with title \"Terminal\"'"}

USER: reboot into recovery mode
BOT: {"action": "run_command", "command": "sudo nvram \"recovery-boot-mode=unused\"; sudo shutdown -r now"}

USER: create an encrypted zip archive
BOT: {"action": "run_command", "command": "zip -e secure.zip file1.txt file2.txt"}