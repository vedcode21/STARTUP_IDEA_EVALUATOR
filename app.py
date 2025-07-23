import streamlit as st
import subprocess
import re
import sys
from web_scraper import scrape_web_sync
from ollama_integration import generate_search_queries, generate_analysis

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OLLAMA_BIN = "ollama"
MODEL = "tinyllama"

# ─── CORE: Run a prompt through TinyLlama, logging to terminal ────────────────
def _invoke_ollama(prompt: str) -> str:
    """
    Send prompt to tinyllama via CLI.  
    Prints prompt, stdout and stderr to your terminal for debugging.  
    Returns the model's stdout (empty on error).
    """
    print(f"\n>>> SENDING TO MODEL >>>\n{prompt}\n{'-'*60}")
    try:
        proc = subprocess.run(
            [OLLAMA_BIN, "run", MODEL],
            input=prompt,
            text=True,
            encoding="utf-8",
            errors="ignore",
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"!!! MODEL ERROR (stderr) !!!\n{e.stderr.strip()}\n{'='*60}")
        return ""
    out = proc.stdout or ""
    err = proc.stderr or ""
    print(f"<<< MODEL STDOUT <<<\n{out.strip()}\n{'-'*60}")
    if err.strip():
        print(f"<<< MODEL STDERR <<<\n{err.strip()}\n{'='*60}")
    return out

# ─── SANITY‐CHECK ENDPOINT ────────────────────────────────────────────────────
def test_model() -> str:
    """
    Returns the raw reply for a simple 'ping?' prompt.
    """
    return _invoke_ollama("ping?").strip() or "No response from model."

# ─── STREAMLIT UI ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Startup Idea Analyzer", layout="wide")
st.title("🚀 Startup Idea Analyzer")

# Test model connectivity
if st.button("🔄 Test Model Connection"):
    resp = test_model()
    if resp.startswith("No response"):
        st.error(resp)
    else:
        st.success(f"Model responded: {resp}")

# Main form
with st.form("startup_form"):
    idea            = st.text_input("💡 Startup Idea")
    country         = st.text_input("🌍 Country")
    target_market   = st.text_input("🎯 Target Market")
    budget          = st.text_input("💰 Budget (USD)")
    stage_of_dev    = st.selectbox("🚧 Stage of Development", ["Idea", "Prototype", "Early Traction", "Scaling"])
    team_size       = st.number_input("👥 Team Size", min_value=1, step=1)
    technologies    = st.text_input("🔧 Key Technologies")
    funding_goals   = st.text_input("🎯 Funding Goals (USD)")
    launch_timeline = st.text_input("⏳ Timeline to Launch (months)")
    submit          = st.form_submit_button("📊 Analyze")

if submit:
    # Validation
    if not all([idea, country, target_market, budget, stage_of_dev, team_size, technologies, funding_goals, launch_timeline]):
        st.error("🚫 Please fill out all fields.")
        st.stop()

    # 1) Generate queries
    with st.spinner("🔍 Generating search queries…"):
        queries = generate_search_queries(idea, country, target_market, budget, stage_of_dev, technologies)
    if not queries:
        st.error("❌ Failed to generate search queries.")
        st.stop()
    st.success("✅ Search queries generated!")
    st.write("📄 Queries:", queries)

    # 2) Scrape web
    with st.spinner("🕸️ Scraping web content…"):
        scraped = scrape_web_sync(queries)
    if not scraped:
        st.error("❌ No data scraped.")
        st.stop()
    st.success(f"✅ Scraped {len(scraped)} pages")
    st.write("🔗 URLs:", [d["url"] for d in scraped])

    # 3) Generate analysis
    with st.spinner("🧠 Generating AI-powered analysis…"):
        report = generate_analysis(
            scraped, idea, country, target_market,
            budget, stage_of_dev, team_size,
            technologies, funding_goals, launch_timeline
        )
    st.success("✅ Analysis Complete!")
    st.markdown(report)
