import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote, unquote
import logging
import getpass
import re

# Setup a single logger for all levels
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("scraper")

def safe_dirname(url):
    # Make a safe directory name from the URL
    parsed = urlparse(url)
    netloc = parsed.netloc.replace(":", "_")
    return netloc

def safe_filepath(url):
    # Create a subdirectory structure that matches the URL path
    parsed = urlparse(url)
    netloc = parsed.netloc.replace(":", "_")
    path = unquote(parsed.path.lstrip("/"))
    if not path or path.endswith("/"):
        path = os.path.join(path, "index.html")
    filename = quote(path, safe="/")  # keep slashes for subdirs
    return os.path.join(netloc, filename)

def scrape(url, visited, base_dir, depth=1, max_depth=2, auth=None):
    if url in visited or depth > max_depth:
        return
    visited.add(url)
    logger.info(f"Scraping: {url}")
    try:
        headers = {"X-Requested-By": "MyClient"}
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()
        # Try to parse as JSON
        try:
            data = response.json()
            links = data.get("links", [])
            logger.info("First 5 links on the page:")
            for link in links[:5]:
                logger.info(link.get("href", ""))
            # Save page
            filepath = safe_filepath(url)
            full_path = os.path.join(base_dir, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            # Follow links on the same domain
            base = urlparse(url).netloc
            for link in links:
                raw_href = link.get("href", "")
                unescaped_href = re.sub(r'\\/', '/', raw_href)
                next_url = urljoin(url, unescaped_href)
                if urlparse(next_url).netloc == base and next_url not in visited:
                    scrape(next_url, visited, base_dir, depth + 1, max_depth, auth=auth)
        except Exception as json_exc:
            logger.error(f"Failed to parse JSON from {url}: {json_exc}")
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter a URL to scrape: ")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    visited = set()
    base_dir = "."  # Save in current directory

    # Accept username and password from command line if provided
    username = None
    password = None
    if len(sys.argv) > 2:
        username = sys.argv[2]
    if len(sys.argv) > 3:
        password = sys.argv[3]

    if username is None:
        username = input("Enter username for Basic Auth (leave blank for none): ").strip()
    if username:
        if password is None:
            import getpass
            password = getpass.getpass("Enter password for Basic Auth: ")
        auth = (username, password)
    else:
        auth = None

    scrape(url, visited, base_dir, auth=auth)
