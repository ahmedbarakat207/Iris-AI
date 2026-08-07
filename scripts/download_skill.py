
import os
import sys
import argparse
import urllib.request
import urllib.error
import json
import re

def get_github_url_from_officialskills(url: str) -> str:
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        match = re.search(r'(https://github\.com/[^"]+/(?:tree|blob)/[^"]+)', html)
        if match:
            
            clean_url = match.group(1).split('<')[0].split('"')[0]
            return clean_url
        return url
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return url

def parse_github_url(url: str):
    
    
    pattern = r'https://github\.com/([^/]+)/([^/]+)/(?:tree|blob)/([^/]+)/(.*)'
    match = re.search(pattern, url)
    if not match:
        raise ValueError(f"Could not parse GitHub URL: {url}. It must be a full tree or blob URL.")
    
    return {
        "owner": match.group(1),
        "repo": match.group(2),
        "branch": match.group(3),
        "path": match.group(4)
    }

def fetch_github_contents(owner, repo, branch, path):
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    req = urllib.request.Request(api_url, headers={
        'User-Agent': 'Iris-AI-Downloader',
        'Accept': 'application/vnd.github.v3+json'
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise Exception(f"GitHub API Error: {e.code} for URL: {api_url}")

def download_file(download_url, dest_path):
    
    req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        content = response.read()
        with open(dest_path, "wb") as f:
            f.write(content)
    print(f"[SUCCESS] Downloaded: {os.path.basename(dest_path)}")

def main():
    parser = argparse.ArgumentParser(description="Download AI Agent Skills from officialskills.sh or GitHub")
    parser.add_argument("url", help="URL of the skill (officialskills.sh or github.com)")
    parser.add_argument("--role", required=True, help="Target model role (e.g., code, reasoning, triage)")
    
    args = parser.parse_args()
    
    print(f"Analyzing URL: {args.url}")
    target_url = args.url
    
    if "officialskills.sh" in target_url:
        print("Detected officialskills.sh link, extracting true GitHub source...")
        target_url = get_github_url_from_officialskills(target_url)
        print(f"Found GitHub Source: {target_url}")
        
    try:
        gh_data = parse_github_url(target_url)
    except ValueError as e:
        print(e)
        sys.exit(1)
        
    
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(here)
    target_dir = os.path.join(project_root, "skills", args.role)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"Target Directory: {target_dir}")
    print("Fetching from GitHub API...")
    
    try:
        contents = fetch_github_contents(gh_data["owner"], gh_data["repo"], gh_data["branch"], gh_data["path"])
        
        
        if isinstance(contents, dict) and contents.get("type") == "file":
            contents = [contents]
            
        download_count = 0
        for item in contents:
            if item.get("type") == "file":
                filename = item.get("name", "")
                if filename.endswith(".md") or filename.endswith(".txt"):
                    dest_path = os.path.join(target_dir, filename)
                    download_url = item.get("download_url")
                    if download_url:
                        download_file(download_url, dest_path)
                        download_count += 1
                        
        if download_count == 0:
            print("⚠️ No .md or .txt files found to download.")
        else:
            print(f"🎉 Successfully imported {download_count} skill files for role '{args.role}'.")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
