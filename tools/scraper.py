import urllib3
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def scrape_page(url):
    """
    Fetch the page and return:
      - raw_html: the full HTML string (to reconstruct later)
      - text_nodes: a dict of CSS-selector → text for the LLM to rewrite
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    res = requests.get(url, verify=False, headers=headers, timeout=15)
    res.raise_for_status()

    raw_html = res.text
    soup = BeautifulSoup(raw_html, "html.parser")

    # ── Extract meaningful text nodes for LLM context ───────────────────────
    text_nodes = {}

    # All headings
    for tag in ["h1", "h2", "h3"]:
        elements = soup.find_all(tag)
        for i, el in enumerate(elements):
            text = el.get_text(strip=True)
            if text:
                key = f"{tag}[{i}]"
                text_nodes[key] = text

    # First few paragraphs (skip very short ones)
    for i, el in enumerate(soup.find_all("p")):
        text = el.get_text(strip=True)
        if len(text) > 30:
            text_nodes[f"p[{i}]"] = text
        if i >= 4:          # cap at 5 paragraphs to stay within LLM context
            break

    # Button / CTA text
    for i, el in enumerate(soup.find_all(["button", "a"], class_=lambda c: c and (
        "btn" in " ".join(c).lower() or "cta" in " ".join(c).lower()
    ))):
        text = el.get_text(strip=True)
        if text:
            text_nodes[f"cta[{i}]"] = text
        if i >= 3:
            break

    return {
        "raw_html": raw_html,
        "text_nodes": text_nodes,
        "url": url,
    }