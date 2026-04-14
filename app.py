import streamlit as st
import streamlit.components.v1 as components
from tools.ad_analyzer import analyze_ad
from tools.scraper import scrape_page
from tools.optimizer import optimize_content

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Landing Page Optimizer",
    page_icon="🚀",
    layout="wide",
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🚀 AI Landing Page Optimizer")
st.markdown(
    "Paste your ad copy and a landing page URL — "
    "the AI will **enhance the existing page** to match your ad's tone and offer."
)

st.divider()

# ── Inputs ───────────────────────────────────────────────────────────────────
col_in1, col_in2 = st.columns([1, 1])

with col_in1:
    ad_text = st.text_area(
        "📢 Ad Copy",
        placeholder="Paste your ad headline, body, and CTA here…",
        height=160,
    )

with col_in2:
    url = st.text_input(
        "🌐 Landing Page URL",
        placeholder="https://example.com/landing",
    )
    render_height = st.slider(
        "Preview height (px)", min_value=400, max_value=1200, value=700, step=50
    )

st.divider()

# ── Optimize button ───────────────────────────────────────────────────────────
if st.button("⚡ Optimize Landing Page", type="primary", use_container_width=True):

    if not ad_text.strip() or not url.strip():
        st.error("⚠️ Please provide both the ad copy and a landing page URL.")

    else:
        with st.spinner("🔍 Fetching page…"):
            try:
                page_data = scrape_page(url)
            except Exception as e:
                st.error(f"❌ Could not fetch the page: {e}")
                st.stop()

        with st.spinner("🧠 Analyzing ad and optimizing content…"):
            try:
                ad_analysis = analyze_ad(ad_text)
                original_html, optimized_html = optimize_content(ad_analysis, page_data)
            except Exception as e:
                st.error(f"❌ Optimization failed: {e}")
                st.stop()

        # ── Side-by-side rendered HTML ────────────────────────────────────────
        st.success("✅ Done! Here's your enhanced landing page:")
        st.markdown("")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔴 Original Page")
            components.html(original_html, height=render_height, scrolling=True)

        with col2:
            st.subheader("🟢 Optimized Page")
            components.html(optimized_html, height=render_height, scrolling=True)

        # ── What changed ──────────────────────────────────────────────────────
        with st.expander("📋 View text changes made by AI"):
            orig_nodes = page_data.get("text_nodes", {})
            if orig_nodes:
                import json, re
                raw_resp = ad_analysis  # reuse ad_analysis as context reference only
                st.markdown("**Text nodes extracted from original page:**")
                st.json(orig_nodes)
            else:
                st.info("No meaningful text nodes were found on that page.")