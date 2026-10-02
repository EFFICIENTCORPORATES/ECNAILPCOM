import os
import re
import time
from collections import deque
from urllib.parse import urljoin, urlparse, urlunparse, unquote

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


START_URL = "https://www.dpdpa.com/blog.html"
OUTPUT_DIR = r"D:\EffCorp_Products\ECNAILPCOM\HTML Files"

ALLOWED_DOMAINS = {"www.dpdpa.com", "dpdpa.com"}
REQUEST_TIMEOUT = 20
DELAY_BETWEEN_REQUESTS = 0.5


def create_session():
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD", "OPTIONS"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    })

    return session


def normalize_url(base_url, href):
    href = href.strip()
    absolute_url = urljoin(base_url, href)
    parsed = urlparse(absolute_url)

    cleaned = parsed._replace(fragment="", query="")
    return urlunparse(cleaned)


def is_target_blog_page(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    if domain not in ALLOWED_DOMAINS:
        return False

    if path == "/blog.html":
        return True

    if path.startswith("/blogs/") and path.endswith(".html"):
        return True

    return False


def sanitize_path_segment(segment):
    segment = unquote(segment).strip()
    segment = re.sub(r'[<>:"/\\|?*]', "_", segment)
    return segment if segment else "unnamed"


def url_to_file_path(url):
    parsed = urlparse(url)
    path = parsed.path

    if not path or path.endswith("/"):
        path = path.rstrip("/") + "/index.html"

    if not path.lower().endswith(".html"):
        path += ".html"

    path = path.lstrip("/")

    parts = [sanitize_path_segment(part) for part in path.split("/") if part]
    if not parts:
        parts = ["index.html"]

    return os.path.join(OUTPUT_DIR, *parts)


def fetch_html(session, url):
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        if not response.encoding or response.encoding.lower() == "iso-8859-1":
            response.encoding = response.apparent_encoding or "utf-8"

        return response.text
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch: {url}")
        print(f"        Reason: {e}")
        return None


def save_html_to_file(url, html_text):
    file_path = url_to_file_path(url)
    folder = os.path.dirname(file_path)
    os.makedirs(folder, exist_ok=True)

    with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(html_text)

    return file_path


def extract_blog_links(html_text, current_url):
    soup = BeautifulSoup(html_text, "html.parser")
    links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        if href.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue

        full_url = normalize_url(current_url, href)

        if is_target_blog_page(full_url):
            links.add(full_url)

    return links


def crawl_and_download():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    session = create_session()

    visited = set()
    queued = set()
    queue = deque()

    queue.append(START_URL)
    queued.add(START_URL)

    downloaded_count = 0

    while queue:
        current_url = queue.popleft()
        queued.discard(current_url)

        if current_url in visited:
            continue

        visited.add(current_url)
        print(f"[PROCESSING] {current_url}")

        html_text = fetch_html(session, current_url)
        if html_text is None:
            continue

        try:
            saved_file = save_html_to_file(current_url, html_text)
            downloaded_count += 1
            print(f"[SAVED] {saved_file}")
        except Exception as e:
            print(f"[ERROR] Could not save file for: {current_url}")
            print(f"        Reason: {e}")
            continue

        found_links = extract_blog_links(html_text, current_url)

        for link in sorted(found_links):
            if link not in visited and link not in queued:
                queue.append(link)
                queued.add(link)

        time.sleep(DELAY_BETWEEN_REQUESTS)

    print("\nDone.")
    print(f"Total pages downloaded: {downloaded_count}")
    print(f"Saved in folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    crawl_and_download()
