import json
import re
from bs4 import BeautifulSoup
from utils.llm import get_llm


def optimize_content(ad_analysis, page_data):
    """
    1. Ask the LLM to rewrite each text node using ad insights.
    2. Inject the rewrites back into the original HTML (same structure).
    3. Return a tuple: (original_html, optimized_html)
    """
    raw_html = page_data["raw_html"]
    text_nodes = page_data["text_nodes"]

    llm = get_llm()

    if not text_nodes:
        # Nothing meaningful to rewrite — return original twice
        return raw_html, raw_html

    # ── Build a compact JSON map for the LLM ────────────────────────────────
    nodes_json = json.dumps(text_nodes, indent=2)

    prompt = f"""You are a conversion-rate-optimization expert.

TASK: Rewrite the landing-page text nodes below so they better match the ad.
- Keep every key EXACTLY as-is.
- Only improve the text values — do NOT change layout, HTML, or add new keys.
- Match the ad's tone, audience, and offer.
- Be concise and persuasive.

Ad Insights:
{ad_analysis}

Text Nodes to rewrite (JSON):
{nodes_json}

Return ONLY a valid JSON object with the same keys and improved values.
No explanation, no markdown fences, just raw JSON."""

    raw_response = llm.invoke(prompt)

    # ── Parse LLM response ───────────────────────────────────────────────────
    try:
        # Strip markdown fences if present
        cleaned = re.sub(r"```(?:json)?|```", "", str(raw_response)).strip()
        rewrites = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        # Fallback: return originals if parsing failed
        return raw_html, raw_html

    # ── Inject rewrites back into the original HTML ──────────────────────────
    soup = BeautifulSoup(raw_html, "html.parser")

    for key, new_text in rewrites.items():
        # Parse key like "h1[0]", "p[2]", "cta[0]"
        match = re.match(r"^([a-z0-9]+)\[(\d+)\]$", key)
        if not match:
            continue

        tag_name, idx = match.group(1), int(match.group(2))

        if tag_name == "cta":
            elements = soup.find_all(
                ["button", "a"],
                class_=lambda c: c and (
                    "btn" in " ".join(c).lower() or "cta" in " ".join(c).lower()
                ),
            )
        else:
            elements = soup.find_all(tag_name)

        if idx < len(elements):
            elements[idx].string = new_text

    optimized_html = str(soup)
    return raw_html, optimized_html