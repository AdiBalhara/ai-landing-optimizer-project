# 🚀 AI Landing Page Optimizer



An agentic AI tool that reads your ad copy, understands its tone and intent, scrapes a real landing page, and uses a local LLM (Llama 3 via Ollama) to rewrite the page's content so it perfectly matches the ad — without changing the design or layout.

---

## 📋 Table of Contents

1. [What It Does](#-what-it-does)
2. [Architecture](#-architecture)
3. [How It Works — Step by Step](#-how-it-works--step-by-step)
4. [Project File Structure](#-project-file-structure)
5. [File Descriptions](#-file-descriptions)
6. [Key Components & Agent Design](#-key-components--agent-design)
7. [Robustness: How We Handle Common Failure Modes](#-robustness-how-we-handle-common-failure-modes)
8. [Getting Started](#-getting-started)

---

## 🎯 What It Does

When a user runs an ad campaign, there is often a **message mismatch** between the ad copy and the landing page. This tool fixes that problem automatically:

- 📢 You paste your **ad copy** (headline, body, CTA)
- 🌐 You paste the **landing page URL**
- 🤖 The AI analyzes the ad's tone, audience, and offer
- ✍️ It rewrites the page's text nodes to align with the ad — **same layout, different words**
- 👀 You see a **side-by-side comparison** of the original vs. optimized page

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   USER (Browser)                    │
│            Streamlit UI  ─  app.py                  │
└──────────────┬──────────────────┬───────────────────┘
               │                  │
        Ad Copy Input       Landing Page URL
               │                  │
               ▼                  ▼
   ┌───────────────────┐  ┌───────────────────────┐
   │  tools/           │  │  tools/               │
   │  ad_analyzer.py   │  │  scraper.py           │
   │                   │  │                       │
   │  Extracts:        │  │  Fetches:             │
   │  - audience       │  │  - raw_html           │
   │  - tone           │  │  - text_nodes dict    │
   │  - offer          │  │    (h1, h2, h3,       │
   │  - message        │  │     p, cta buttons)   │
   └────────┬──────────┘  └──────────┬────────────┘
            │                        │
            └──────────┬─────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │  tools/optimizer.py   │
           │                       │
           │  1. Builds LLM prompt │
           │  2. Sends to Llama 3  │
           │  3. Parses JSON resp  │
           │  4. Injects rewrites  │
           │     into HTML         │
           └──────────┬────────────┘
                      │
              ┌───────┴────────┐
              │                │
              ▼                ▼
      original_html     optimized_html
              │                │
              └───────┬────────┘
                      │
                      ▼
           ┌───────────────────────┐
           │    Streamlit UI       │
           │  Side-by-side render  │
           │  + Text diff expander │
           └───────────────────────┘
```

### LLM Layer

```
utils/llm.py
    │
    └──► OllamaLLM (model=llama3)
              │
              └──► Runs LOCALLY on your machine
                   No API keys. No cost. No data leaves your system.
```

---

## 🔄 How It Works — Step by Step

| Step | What Happens | Module |
|------|-------------|--------|
| 1 | User inputs ad copy + URL in the Streamlit UI | `app.py` |
| 2 | The page at the URL is fetched with a realistic browser `User-Agent` | `tools/scraper.py` |
| 3 | BeautifulSoup parses the HTML and extracts key text nodes (headings, paragraphs, CTAs) into a structured dict | `tools/scraper.py` |
| 4 | The ad text is sent to the LLM, which extracts structured insights: audience, tone, offer, message | `tools/ad_analyzer.py` |
| 5 | Both the ad insights and the text node dict are sent to the LLM in a single prompt asking for JSON rewrites | `tools/optimizer.py` |
| 6 | The LLM response is parsed, markdown fences are stripped, and the JSON is validated | `tools/optimizer.py` |
| 7 | Each rewritten text node is injected back into the original HTML using BeautifulSoup's DOM traversal | `tools/optimizer.py` |
| 8 | Both original and optimized HTML are rendered side-by-side in the browser via Streamlit components | `app.py` |

---

## 📁 Project File Structure

```
ai-landing-optimizer/
│
├── app.py                    # Streamlit frontend — the UI entry point
│
├── tools/
│   ├── ad_analyzer.py        # Extracts insights from ad copy using LLM
│   ├── scraper.py            # Fetches and parses the target landing page
│   └── optimizer.py          # Core agent: builds prompts, calls LLM, injects rewrites
│
├── utils/
│   └── llm.py                # LLM factory — returns a configured Ollama/Llama3 instance
│
├── requirements.txt          # Python dependencies
├── testing-ollama.py         # Quick sanity-check script for Ollama connectivity
└── .agent/                   # OpenSpec workflow and skill definitions (dev tooling)
    ├── skills/
    └── workflows/
```

---

## 📄 File Descriptions

### `app.py` — The Frontend & Orchestrator
**Why it exists:** This is the single entry point of the application. It wires together all the tools and presents the interface.

**What it does:**
- Configures the Streamlit page (title, layout, icon)
- Renders the two input fields: Ad Copy (textarea) and Landing Page URL
- On button click, runs the full pipeline: scrape → analyze → optimize
- Renders the original and optimized HTML side-by-side in iframes
- Shows an expandable "what changed" section with the extracted text nodes
- Handles errors gracefully at each stage with user-friendly messages

---

### `tools/ad_analyzer.py` — Ad Copy Intelligence
**Why it exists:** The optimizer needs to *understand* the ad before it can rewrite anything. Raw ad text alone isn't enough — we need structured insights the LLM can act on.

**What it does:**
- Takes raw ad copy text as input
- Sends it to the LLM with a structured prompt asking for a JSON breakdown
- Extracts four key signals:
  - `audience` — Who the ad is targeting
  - `tone` — The emotional/stylistic register (urgent, friendly, professional, etc.)
  - `offer` — What is being offered (free trial, discount, feature, etc.)
  - `message` — The core value proposition

---

### `tools/scraper.py` — Landing Page Data Fetcher
**Why it exists:** To give the LLM real, current page content to work with — not placeholders or mocks.

**What it does:**
- Sends an HTTP GET request with a real browser `User-Agent` to bypass bot detection
- Parses the full HTML with BeautifulSoup
- Extracts a structured `text_nodes` dictionary keyed by CSS-style selectors:
  - All `h1`, `h2`, `h3` headings
  - First 5 meaningful paragraphs (skips text < 30 chars to cut noise)
  - CTA buttons and anchor tags with `btn`/`cta` CSS classes
- Returns both the `raw_html` (for injection later) and the `text_nodes` dict (for the LLM)
- Disables SSL verification warnings to handle pages with certificate issues

---

### `tools/optimizer.py` — The Core Agent
**Why it exists:** This is the brain of the system. It bridges the gap between ad intent and page content.

**What it does:**
1. Receives the ad analysis and the scraped page data
2. Serializes the `text_nodes` dict to a compact JSON string
3. Builds a precise, constrained prompt instructing the LLM to:
   - Keep every JSON key exactly the same
   - Only change text values (not structure)
   - Match the ad's tone, audience, and offer
   - Return raw JSON only (no markdown, no explanation)
4. Calls the LLM and receives a JSON response
5. Strips any markdown fences (` ```json `) from the response
6. Parses the JSON and injects each rewritten value back into the original HTML via BeautifulSoup DOM traversal
7. Returns a tuple: `(original_html, optimized_html)`

---

### `utils/llm.py` — LLM Factory
**Why it exists:** Centralizes the LLM configuration so all tools use the same model without repeating setup code. Swapping models only requires changing one file.

**What it does:**
- Returns an `OllamaLLM` instance configured to use the `llama3` model
- Runs entirely locally via Ollama — zero API costs, zero data exposure

---

### `requirements.txt` — Python Dependencies
**Why it exists:** Reproducible installs across environments.

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `langchain` | LLM abstraction layer |
| `langchain-community` | Ollama integration for LangChain |
| `beautifulsoup4` | HTML parsing and DOM manipulation |
| `requests` | HTTP page fetching |

---

### `testing-ollama.py` — Connectivity Sanity Check
**Why it exists:** Before running the full app, developers can quickly verify Ollama is running and responding. Useful for debugging environment setup.

---

### `.agent/` — Developer Workflow Tooling
**Why it exists:** Contains OpenSpec workflow definitions (skills and workflows) used by the AI coding assistant to propose, apply, and archive changes in a structured way. Not part of the runtime application.

---

## 🧠 Key Components & Agent Design

The optimizer is a **single-pass agentic pipeline** — not a multi-agent loop. Here's how the "agent" thinking is structured:

### 1. Perception — `scraper.py`
The agent *perceives* the world by fetching the real landing page. It doesn't work from a static mock — it reads the actual DOM, extracts meaningful signals (headings, CTAs, key paragraphs), and discards noise (short text, boilerplate).

### 2. Reasoning — `ad_analyzer.py`
The agent *reasons* about the ad. Rather than feeding raw ad text into the optimizer, it first builds **structured intent** out of it. This is a classic "decomposition" step — breaking an unstructured input into actionable properties (audience, tone, offer, message).

### 3. Acting — `optimizer.py`
The agent *acts* by:
- Constructing a constrained, role-based prompt (it plays the role of a "CRO expert")
- Constraining the output format strictly to JSON with matching keys
- Using the LLM as a tool for text transformation, not free-form generation
- Surgically injecting results back into the DOM without touching structure

### 4. Presentation — `app.py`
The agent *communicates* results by rendering both before and after views, letting the human judge and decide — keeping the human in the loop.

---

## 🛡️ Robustness: How We Handle Common Failure Modes

### ❓ Random / Unexpected Changes
**Problem:** The LLM might decide to add new keys, restructure the JSON, or rename things.

**Solution:** The prompt explicitly instructs the LLM to *"Keep every key EXACTLY as-is"* and *"Return ONLY a valid JSON object with the same keys."* The injection code then only processes keys that match the expected pattern `tag[index]` (e.g. `h1[0]`, `p[2]`). Unrecognized keys are silently ignored — the page is never broken by unexpected output.

```python
match = re.match(r"^([a-z0-9]+)\[(\d+)\]$", key)
if not match:
    continue  # Unknown key → skip safely
```

---

### 💥 Broken UI (Scraping / Rendering Failures)
**Problem:** Some pages block scrapers, redirect to login, have broken SSL, or return non-200 status codes.

**How we handle it:**
- `requests.get(..., verify=False)` skips SSL errors that would otherwise crash the fetch
- `res.raise_for_status()` immediately surfaces HTTP errors (403, 404, 500)
- All three pipeline stages (scrape, analyze, optimize) are wrapped in `try/except` in `app.py` with user-friendly error messages — the app never shows a raw Python traceback to the user
- If no meaningful text nodes are found on the page, the optimizer short-circuits and returns the original HTML twice (original = optimized), rather than crashing

```python
if not text_nodes:
    return raw_html, raw_html  # Safe no-op
```

---

### 🤪 Hallucinations
**Problem:** The LLM might invent new CTAs, fabricate statistics, or write irrelevant copy.

**How we handle it:**
- The optimizer prompt is **highly constrained**: rewrite only, same keys, no new keys, no HTML, no layout changes
- The system works at the **text node level** — it rewrites existing copy rather than generating new sections from scratch, which bounds how far the output can drift
- The prompt includes the actual ad insights as grounding context so the LLM is anchored to your real offer, not something it imagined
- The expander section ("View text changes made by AI") shows the original text nodes so the user can spot-check what was changed

---

### 🔀 Inconsistent Outputs
**Problem:** Llama 3 sometimes wraps JSON in markdown fences (` ```json`), adds comments, or returns partial JSON.

**How we handle it:**
- A `re.sub` strip removes markdown fences before parsing:
  ```python
  cleaned = re.sub(r"```(?:json)?|```", "", str(raw_response)).strip()
  ```
- `json.loads()` is wrapped in a `try/except (json.JSONDecodeError, ValueError)` block
- If parsing fails entirely, the function gracefully falls back to returning the original HTML twice — the user sees the original page rather than a crash

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally
- Llama 3 model pulled: `ollama pull llama3`

### Installation

```bash
git clone https://github.com/your-username/ai-landing-optimizer.git
cd ai-landing-optimizer

# Create a virtual environment
python -m venv env
.\env\Scripts\activate        # Windows
# source env/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`, paste your ad copy and a landing page URL, and click **Optimize Landing Page**.

---

## 🧪 Example Input

**Ad Copy:**
```
Headline: Stop Losing Customers to Slow, Generic Landing Pages

Body: Most landing pages are built once and forgotten — but your ads change every week.
AdaptIQ automatically rewrites your landing page to match your ad's exact message, tone,
and offer. No developers. No delays. Just higher conversions from day one.

CTA: Start Your Free 14-Day Trial — No Credit Card Required
```

**Landing Page URL:** `https://unbounce.com`

---

## 📝 License


