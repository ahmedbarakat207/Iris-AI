import os
import sys
import json
import re
import shlex
from llama_cpp import Llama

def rule_based_translate(cmd: str) -> str:
    cmd = cmd.strip()
    
                                                     
    if cmd.startswith("sudo "):
        cmd = cmd[5:].strip()
        
    if cmd.startswith("cd "):
        path = cmd[3:].strip().strip('"').strip("'")
        return f"Set-Location -Path '{path}'"
    if cmd == "cd":
        return "Set-Location -Path ~"
        
    if cmd == "pwd" or cmd == "/bin/pwd":
        return "Get-Location"
        
    if cmd == "ls":
        return "Get-ChildItem"
    if cmd.startswith("ls "):
        args = cmd[3:].strip()
        args_clean = re.sub(r'-[laR]+', '', args).strip()
        if args_clean:
            return f"Get-ChildItem -Path '{args_clean}'"
        return "Get-ChildItem"
        
    if cmd.startswith("cat "):
        files = cmd[4:].strip()
        return f"Get-Content -Path '{files}'"
        
    if cmd.startswith("mkdir "):
        dir_path = cmd[6:].strip().replace("-p ", "").strip().strip('"').strip("'")
        return f"New-Item -ItemType Directory -Path '{dir_path}'"
        
    if cmd.startswith("touch "):
        file_path = cmd[6:].strip().strip('"').strip("'")
        return f"New-Item -ItemType File -Path '{file_path}'"
        
    if cmd.startswith("cp "):
        parts = cmd[3:].strip()
        recurse = "-Recurse" if "-r" in parts or "-R" in parts else ""
        parts_clean = re.sub(r'-[rR]', '', parts).strip()
        try:
            paths = shlex.split(parts_clean)
            if len(paths) >= 2:
                return f"Copy-Item -Path '{paths[0]}' -Destination '{paths[1]}' {recurse}".strip()
        except Exception:
            pass
            
    if cmd.startswith("mv "):
        parts = cmd[3:].strip()
        try:
            paths = shlex.split(parts)
            if len(paths) >= 2:
                return f"Move-Item -Path '{paths[0]}' -Destination '{paths[1]}'"
        except Exception:
            pass
            
    if cmd.startswith("rm "):
        parts = cmd[3:].strip()
        recurse = "-Recurse" if "-r" in parts or "-R" in parts or "-rf" in parts else ""
        parts_clean = re.sub(r'-r[f]?|-R[f]?|-f', '', parts).strip()
        return f"Remove-Item -Path '{parts_clean}' {recurse}".strip()
        
    if cmd.startswith("grep "):
        parts = cmd[5:].strip()
        recurse = "-Recurse" in parts or "-r" in parts
        parts_clean = re.sub(r'-r|-Recurse', '', parts).strip()
        try:
            subparts = shlex.split(parts_clean)
            if len(subparts) >= 2:
                pattern = subparts[0]
                path = subparts[1]
                if recurse:
                    return f"Get-ChildItem -Path '{path}' -Recurse | Select-String -Pattern '{pattern}'"
                return f"Select-String -Pattern '{pattern}' -Path '{path}'"
            elif len(subparts) == 1:
                return f"Select-String -Pattern '{subparts[0]}'"
        except Exception:
            pass

    if cmd.startswith("zip "):
        parts = cmd[4:].strip()
        parts_clean = re.sub(r'-r', '', parts).strip()
        try:
            subparts = shlex.split(parts_clean)
            if len(subparts) >= 2:
                archive = subparts[0]
                sources = ", ".join(f"'{s}'" for s in subparts[1:])
                return f"Compress-Archive -Path {sources} -DestinationPath '{archive}'"
        except Exception:
            pass

    if cmd.startswith("tar "):
        parts = cmd[4:].strip()
        if "-c" in parts or (parts.split() and "c" in parts.split()[0]):
            parts_clean = re.sub(r'-[czvfgx]+', '', parts).strip()
            try:
                subparts = shlex.split(parts_clean)
                if len(subparts) >= 2:
                    archive = subparts[0]
                    sources = ", ".join(f"'{s}'" for s in subparts[1:])
                    return f"Compress-Archive -Path {sources} -DestinationPath '{archive}'"
            except Exception:
                pass
        elif "-x" in parts or (parts.split() and "x" in parts.split()[0]):
            parts_clean = re.sub(r'-[xzvf]+', '', parts).strip()
            try:
                subparts = shlex.split(parts_clean)
                if len(subparts) >= 1:
                    return f"Expand-Archive -Path '{subparts[0]}'"
            except Exception:
                pass

    if cmd.startswith("bzip2 ") or cmd.startswith("gzip "):
        parts = cmd.split()
        if len(parts) >= 2:
            filename = parts[1]
            return f"Compress-Archive -Path '{filename}' -DestinationPath '{filename}.zip'"

    if cmd.startswith("ping "):
        parts = cmd.split()
        host = parts[-1]
        count = None
        if "-c" in parts:
            try:
                idx = parts.index("-c")
                if idx + 1 < len(parts):
                    count = parts[idx+1]
            except ValueError:
                pass
        if count:
            return f"Test-Connection -ComputerName '{host}' -Count {count}"
        return f"Test-Connection -ComputerName '{host}'"

    if cmd.startswith("ifconfig") or cmd.startswith("ip a") or cmd.startswith("ip addr"):
        return "ipconfig"

    if cmd == "who" or cmd.startswith("who ") or cmd == "w" or cmd.startswith("w "):
        return "query user"

    if cmd.startswith("free"):
        return "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory"

    if cmd.startswith("df"):
        return "Get-Volume"

    if cmd.startswith("du"):
        return "Get-ChildItem -Recurse | Measure-Object -Property Length -Sum"

    if cmd.startswith("uname"):
        return "[System.Environment]::OSVersion"

    if cmd.startswith("curl ") or cmd.startswith("wget "):
        try:
            parts = shlex.split(cmd)
            url = parts[-1]
            if "-o" in parts:
                idx = parts.index("-o")
                if idx + 1 < len(parts):
                    return f"Invoke-WebRequest -Uri '{url}' -OutFile '{parts[idx+1]}'"
            return f"Invoke-WebRequest -Uri '{url}'"
        except Exception:
            pass

    if cmd.startswith("nslookup ") or cmd.startswith("host ") or cmd.startswith("dig "):
        parts = cmd.split()
        domain = parts[-1]
        return f"Resolve-DnsName -Name '{domain}'"

    if cmd.startswith("passwd "):
        parts = cmd.split()
        user = parts[-1]
        return f"net user {user} *"

    if cmd.startswith("blkid"):
        return "Get-Volume"

    if cmd.startswith("sleep "):
        parts = cmd.split()
        seconds = parts[-1]
        return f"Start-Sleep -Seconds {seconds}"

    if cmd.startswith("traceroute "):
        host = cmd.split()[-1]
        return f"tracert {host}"

    if cmd.startswith("mtr "):
        host = cmd.split()[-1]
        return f"pathping {host}"

    if cmd.startswith("useradd "):
        username = cmd.split()[-1]
        return f"New-LocalUser -Name '{username}'"
    if cmd.startswith("userdel "):
        username = cmd.split()[-1]
        return f"Remove-LocalUser -Name '{username}'"
    if cmd.startswith("usermod "):
        parts = cmd.split()
        username = parts[-1]
        return f"Set-LocalUser -Name '{username}'"

    if cmd.startswith("groupadd "):
        groupname = cmd.split()[-1]
        return f"New-LocalGroup -Name '{groupname}'"
    if cmd.startswith("groupdel "):
        groupname = cmd.split()[-1]
        return f"Remove-LocalGroup -Name '{groupname}'"
    if cmd.startswith("groupmod "):
        groupname = cmd.split()[-1]
        return f"Set-LocalGroup -Name '{groupname}'"

    if cmd.startswith("chmod "):
        parts = cmd.split()
        target = parts[-1]
        return f"icacls '{target}' /grant 'Everyone:(OI)(CI)F'"
    if cmd.startswith("chown ") or cmd.startswith("chgrp "):
        parts = cmd.split()
        target = parts[-1]
        return f"takeown /f '{target}' /a"

    if cmd.startswith("rsync "):
        try:
            parts = shlex.split(cmd)
            parts_clean = [p for p in parts if not p.startswith("-") and p != "rsync"]
            if len(parts_clean) >= 2:
                return f"robocopy '{parts_clean[0]}' '{parts_clean[1]}' /E"
        except Exception:
            pass

    if cmd.startswith("find "):
        parts = cmd.split()
        path = "."
        if len(parts) > 1 and not parts[1].startswith("-"):
            path = parts[1]
        name_match = re.search(r'-name\s+["\']?([^"\']+)["\']?', cmd)
        if name_match:
            return f"Get-ChildItem -Path '{path}' -Filter '{name_match.group(1)}' -Recurse"
        return f"Get-ChildItem -Path '{path}' -Recurse"

    if cmd.startswith("nmcli "):
        return "Get-NetAdapter"

    if cmd.startswith("su "):
        parts = cmd.split()
        user = parts[-1]
        return f"Start-Process PowerShell -Credential '{user}'"

    if cmd.startswith("gpasswd "):
        parts = cmd.split()
        user = parts[-2]
        group = parts[-1]
        if "-a" in parts:
            return f"Add-LocalGroupMember -Group '{group}' -Member '{user}'"
        if "-d" in parts:
            return f"Remove-LocalGroupMember -Group '{group}' -Member '{user}'"

    if cmd.startswith("fdisk") or cmd.startswith("parted"):
        return "Get-Disk"

    if cmd.startswith("vim "):
        target = cmd[4:].strip()
        return f"notepad '{target}'"

    if cmd == "clear":
        return "Clear-Host"

    if cmd.startswith("locate "):
        target = cmd[7:].strip()
        return f"Get-ChildItem -Path C:\\ -Filter '{target}' -Recurse -ErrorAction SilentlyContinue"

    if cmd.startswith("netstat") or cmd.startswith("ss"):
        return "Get-NetTCPConnection"

    if cmd.startswith("ssh "):
        return cmd

    if cmd.startswith("watch "):
        subcmd = cmd[6:].strip()
        subcmd = re.sub(r'-n\s+\d+', '', subcmd).strip()
        win_sub = rule_based_translate(subcmd) or subcmd
        return f"while ($true) {{ {win_sub}; Start-Sleep -Seconds 2; Clear-Host }}"

    if cmd.startswith("umount "):
        target = cmd[7:].strip()
        return f"Dismount-DiskImage -ImagePath '{target}'"

    if cmd.startswith("nohup "):
        subcmd = cmd[6:].strip().rstrip("&").strip()
        win_sub = rule_based_translate(subcmd) or subcmd
        return f"Start-Process -FilePath '{win_sub}' -NoNewWindow"

    if cmd.startswith("alias "):
        parts = cmd[6:].strip().split("=")
        if len(parts) == 2:
            name = parts[0].strip()
            value = parts[1].strip().strip("'").strip('"')
            win_val = rule_based_translate(value) or value
            return f"Set-Alias -Name '{name}' -Value '{win_val}'"

    if cmd.startswith("env"):
        return "Get-ChildItem Env:"

    if cmd.startswith("service "):
        parts = cmd.split()
        if len(parts) >= 3:
            name = parts[1]
            action = parts[2]
            if action == "start":
                return f"Start-Service -Name '{name}'"
            if action == "stop":
                return f"Stop-Service -Name '{name}'"
            if action == "restart":
                return f"Restart-Service -Name '{name}'"
            if action == "status":
                return f"Get-Service -Name '{name}'"

    if cmd.startswith("screen"):
        return "Start-Job"

    if cmd.startswith("awk "):
        return "ForEach-Object"

    if cmd.startswith("sed "):
        parts = shlex.split(cmd)
        expr = parts[1] if len(parts) > 1 else ""
        target = parts[-1] if len(parts) > 2 else ""
        if expr.startswith("s/"):
            expr_parts = expr.split("/")
            if len(expr_parts) >= 3:
                find_p = expr_parts[1]
                replace_p = expr_parts[2]
                if target:
                    return f"(Get-Content '{target}') -replace '{find_p}', '{replace_p}' | Set-Content '{target}'"
        return "ForEach-Object { $_ -replace 'pattern', 'replacement' }"

    if cmd.startswith("dd "):
        return "Copy-Item"

    if cmd.startswith("mount "):
        parts = cmd.split()
        if len(parts) >= 3:
            src = parts[-2]
            dst = parts[-1]
            return f"New-PSDrive -Name '{dst.rstrip(':')}' -PSProvider FileSystem -Root '{src}' -Persist"
        return "Get-Volume"

    if cmd.startswith("history"):
        return "Get-History"

    if cmd.startswith("systemctl "):
        parts = cmd.split()
        action = parts[1]
        service = parts[2] if len(parts) > 2 else ""
        if action == "start":
            return f"Start-Service '{service}'"
        if action == "stop":
            return f"Stop-Service '{service}'"
        if action == "restart":
            return f"Restart-Service '{service}'"
        if action == "status":
            return f"Get-Service '{service}'"
        if action == "enable":
            return f"Set-Service '{service}' -StartupType Automatic"
        if action == "disable":
            return f"Set-Service '{service}' -StartupType Disabled"

    if cmd.startswith("crontab"):
        return "Get-ScheduledTask"

    if cmd.startswith("echo"):
        return cmd.replace("echo ", "Write-Output ")

    if cmd.startswith("ps"):
        return "Get-Process"

    if cmd.startswith("nice ") or cmd.startswith("renice "):
        return "Set-ProcessPriority"

    if cmd.startswith("rmdir "):
        target = cmd[6:].strip()
        return f"Remove-Item -Path '{target}' -Recurse"

    if cmd.startswith("journalctl") or cmd.startswith("dmesg"):
        return "Get-WinEvent -LogName System"

    if cmd.startswith("top") or cmd.startswith("htop") or cmd.startswith("atop"):
        return "Get-Process | Sort-Object CPU -Descending | Select-Object -First 20"

    if cmd.startswith("killall ") or cmd.startswith("pkill "):
        target = cmd.split()[-1]
        return f"Stop-Process -Name '{target}'"

    if cmd.startswith("lsof"):
        return "Get-Process"

    if cmd.startswith("kill "):
        parts = cmd.split()
        pid = parts[-1]
        if pid.isdigit():
            return f"Stop-Process -Id {pid}"
        return f"Stop-Process -Name '{pid}'"

    if cmd.startswith("tmux") or cmd.startswith("Ctrl-b"):
        return "Start-Job"

    if cmd.startswith("less "):
        target = cmd[5:].strip()
        return f"Get-Content '{target}' | Out-Host -Paging"

    if cmd.startswith("tail "):
        parts = cmd.split()
        target = parts[-1]
        lines = 10
        if "-n" in parts:
            try:
                idx = parts.index("-n")
                lines = parts[idx+1]
            except Exception:
                pass
        return f"Get-Content '{target}' -Tail {lines}"

    if cmd.startswith("mkfs."):
        parts = cmd.split()
        fs_type = parts[0].split(".")[-1].upper()
        drive = parts[-1]
        if fs_type in ("EXT4", "EXT3", "EXT2", "XFS"):
            fs_type = "NTFS"
        return f"Format-Volume -DriveLetter '{drive.replace('/dev/sd', '')}' -FileSystem {fs_type}"

    if cmd.startswith("scp "):
        return cmd

    if cmd.startswith("date"):
        return "Get-Date"

    return None

def main():
    source_path = "training/control/linuxcommands.json"
    dest_dir = "training/control"
    dest_path = os.path.join(dest_dir, "windowscommands.json")
    
    os.makedirs(dest_dir, exist_ok=True)
    
    if not os.path.exists(source_path):
        print(f"Source file {source_path} not found.")
        sys.exit(1)
        
    with open(source_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} commands from {source_path}.")
    
    llm = None
    model_path = "models/iris_004.gguf"
    
    results = []
    llm_calls = 0
    rule_calls = 0
    
    for i, item in enumerate(data):
        inp = item.get("input", "")
        out = item.get("output", "")
        
                                          
        res = rule_based_translate(out)
        
        if res:
            results.append({
                "input": inp,
                "output": res
            })
            rule_calls += 1
        else:
                                      
            if llm is None:
                print(f"Loading local model {model_path} for remaining translations...")
                llm = Llama(model_path=model_path, n_ctx=2048, verbose=False)
                print("Model loaded successfully!")
                
            prompt = f"""<system>You are a systems administrator expert in both Linux bash and Windows PowerShell.
Translate the given Linux command to a native Windows PowerShell command that performs the equivalent action.
Do not just append .exe to the Linux command name. Use native PowerShell cmdlets (like Get-Content, Select-String, Compress-Archive, Copy-Item, etc.) where possible.
Format your output as a JSON object with keys "input" and "output".</system>
<user>
Linux command: {out}
Description: {inp}
</user>
<assistant>
{{
  "input": "{inp}",
  "output": """
            
            try:
                res_obj = llm(prompt, max_tokens=150, stop=["}"])
                text = res_obj["choices"][0]["text"].strip()
                                                               
                match = re.search(r'"([^"]+)"', text)
                if match:
                    val = match.group(1)
                else:
                    val = text.strip('"')
                
                results.append({
                    "input": inp,
                    "output": val
                })
                llm_calls += 1
            except Exception as e:
                                                                               
                results.append({
                    "input": inp,
                    "output": out
                })
                
        if (i + 1) % 1000 == 0:
            print(f"Processed {i + 1}/{len(data)} items... (Rules: {rule_calls}, LLM: {llm_calls})")
            
    print(f"Translation complete! Rule-based matches: {rule_calls}, LLM matches: {llm_calls}.")
    
    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved translated dataset to {dest_path}.")

if __name__ == "__main__":
    main()
