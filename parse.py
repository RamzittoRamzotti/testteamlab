from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
from utils import DEFAULT_MAX_PAGES, DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from utils import extract_emails, extract_phones
from utils import same_domain

def parse(start_url: str, max_pages: int = DEFAULT_MAX_PAGES) -> dict:
    parsed_start = urlparse(start_url)
    if not parsed_start.scheme or not parsed_start.netloc:
        return {"url": start_url, "emails": [], "phones": []}
    base_netloc = parsed_start.netloc
    base_url = f"{parsed_start.scheme}://{parsed_start.netloc}"

    emails = set()
    phones = set()
    visited = set()
    to_visit = [start_url]

    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_USER_AGENT})

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = session.get(url, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            if "text/html" not in resp.headers.get("Content-Type", ""):
                continue
            raw = resp.text
        except Exception:
            continue

        emails.update(extract_emails(raw))
        phones.update(extract_phones(raw))

        try:
            soup = BeautifulSoup(raw, "html.parser")
        except Exception:
            continue

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)
            if parsed.fragment:
                full_url = full_url.split("#")[0]
            if full_url in visited or full_url in to_visit:
                continue
            if same_domain(full_url, base_netloc) and parsed.scheme in ("http", "https"):
                to_visit.append(full_url)

    return {
        "url": base_url,
        "emails": emails,
        "phones": phones,
    }