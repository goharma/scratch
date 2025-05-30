import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote, unquote
import logging

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

def scrape(url, visited, base_dir, depth=1, max_depth=2):
    if url in visited or depth > max_depth:
        return
    visited.add(url)
    logger.info(f"Scraping: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        logger.info(f"Page title: {soup.title.string if soup.title else 'No title found'}")
        links = soup.find_all("a", href=True)
        logger.info("First 5 links on the page:")
        for link in links[:5]:
            logger.info(link["href"])
        # Save page
        filepath = safe_filepath(url)
        full_path = os.path.join(base_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        # Follow links on the same domain
        base = urlparse(url).netloc
        for link in links:
            next_url = urljoin(url, link["href"])
            if urlparse(next_url).netloc == base and next_url not in visited:
                scrape(next_url, visited, base_dir, depth + 1, max_depth)
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
    scrape(url, visited, base_dir)
