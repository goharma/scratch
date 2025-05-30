import os
import sys
import requests
from urllib.parse import urlparse, unquote, quote, urljoin
import json
import re

def safe_dirname(url):
    parsed = urlparse(url)
    return parsed.netloc.replace(":", "_")

def safe_filepath(url, base_dir):
    parsed = urlparse(url)
    netloc = parsed.netloc
    path = unquote(parsed.path.lstrip("/"))
    if not path or path.endswith("/"):
        path = os.path.join(path, "index.json")
    filename = quote(path, safe="/")  # keep slashes for subdirs
    return os.path.join(base_dir, netloc, filename)

def scrape(url, visited, base_dir, auth=None):
    if url in visited:
        return
    visited.add(url)
    try:
        resp = requests.get(url, auth=auth, headers={"X-Requested-By": "MyClient"})
        resp.raise_for_status()
        data = resp.json()
        # Save JSON to file
        file_path = safe_filepath(url, base_dir)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        # Follow links
        links = data.get("links", [])
        for link in links:
            raw_href = link.get("href", "")
            unescaped_href = re.sub(r'\\/', '/', raw_href)
            next_url = urljoin(url, unescaped_href)
            if next_url not in visited:
                scrape(next_url, visited, base_dir, auth=auth)
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scrape_wls.py <url> [username] [password]")
        sys.exit(1)
    url = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else None
    password = sys.argv[3] if len(sys.argv) > 3 else None
    auth = (username, password) if username else None
    base_dir = "."  # Save in current directory
    scrape(url, set(), base_dir, auth=auth)
