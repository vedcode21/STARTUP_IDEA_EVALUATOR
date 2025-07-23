import subprocess
import sys
import re
import matplotlib.pyplot as plt
import os

OLLAMA_BIN = "ollama"
MODEL = "tinyllama"

# ─── SMOKE TEST ───

def smoke_test(model: str):
    try:
        proc = subprocess.run(
            [OLLAMA_BIN, "run", model, "Hello!"],
            text=True, capture_output=True, check=True
        )
        out = proc.stdout.strip()
        if not out:
            print(f"⛔ [smoke test {model}] returned no output. Is it installed?")
            sys.exit(1)
        print(f"✅ [smoke test {model}] OK → {out!r}")
    except Exception as e:
        print(f"⛔ [smoke test {model}] FAILED: {e}")
        sys.exit(1)

smoke_test(MODEL)

# ─── INVOKE OLLAMA ───

def _invoke_ollama(prompt: str) -> str:
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
        return proc.stdout or ""
    except subprocess.CalledProcessError as e:
        print(f"❌ [{MODEL}] error:\n{e.stderr.strip()}")
        return ""

# ─── GENERATE SEARCH QUERIES ───

def generate_search_queries(
    idea: str,
    country: str,
    target_market: str,
    budget: str,
    stage_of_development: str,
    key_technologies: str,
) -> list[str]:
    prompt = (
        f"Generate 6 specific Google search queries to evaluate the startup idea '{idea}' "
        f"in {country}, targeting '{target_market}', with a budget of ${budget}, at the "
        f"'{stage_of_development}' stage, using {key_technologies}. List one query per line."
    )
    print("📝 [prompt] →\n", prompt, "\n" + "-"*50)
    full_text = _invoke_ollama(prompt)
    print("📬 [stdout] →\n", full_text, "\n" + "-"*50)

    quoted = re.findall(r'"([^"]+)"', full_text)
    queries = []
    for q in quoted:
        q = q.strip()
        if q and q not in queries:
            queries.append(q)
        if len(queries) >= 6:
            break

    if not queries:
        for line in full_text.splitlines():
            q = line.strip()
            if q and q not in queries:
                queries.append(q)
            if len(queries) >= 6:
                break

    print(f"📋 Parsed queries ({len(queries)}): {queries}")
    return queries

# ─── GENERATE DETAILED ANALYSIS ───

def plot_swot():
    labels = ['Strengths', 'Weaknesses', 'Opportunities', 'Threats']
    sizes = [25, 25, 30, 20]
    colors = ['green', 'red', 'blue', 'orange']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.title("SWOT Summary")
    if not os.path.exists("charts"):
        os.makedirs("charts")
    path = os.path.join("charts", "swot_chart.png")
    plt.savefig(path)
    plt.close()
    return path

def generate_analysis(
    scraped_data: list[dict],
    idea: str,
    country: str,
    target_market: str,
    budget: str,
    stage_of_development: str,
    team_size: int,
    key_technologies: str,
    funding_goals: str,
    timeline_to_launch: str,
) -> str:
    combined = "\n".join(item.get("content", "")[:1000] for item in scraped_data[:2])
    scraped_prompt = (
        f"You're an expert startup analyst. Based on the following scraped content and startup details, craft a pitch-perfect, structured report in markdown.\n"
        f"Startup: '{idea}' in {country}\nTarget Market: '{target_market}'\nBudget: ${budget}, Team Size: {team_size}\n"
        f"Technologies: {key_technologies}\nStage: {stage_of_development}\nFunding Goal: ${funding_goals}\nLaunch Timeline: {timeline_to_launch} months\n"
        "Structure using **only these markdown headings (##)**, and include meaningful insights even if scraped data is limited. Never skip or omit a section:\n"
        "## Market Research\n## Competitor Analysis\n## Feasibility\n## Budget Requirements\n## Business Outline\n"
        "## Requirements to Get Started\n## SWOT Analysis\n## Risk Assessment\n## Scalability Potential\n## Customer Acquisition Cost (CAC) Estimate\n"
        f"\nScraped Data:\n{combined}"
    )
    print("📝 [SCRAPED‑DATA PROMPT] →\n", scraped_prompt, "\n" + "-"*60)
    report = _invoke_ollama(scraped_prompt)
    print("📬 [SCRAPED‑DATA OUTPUT] →\n", report, "\n" + "-"*60)

    if not re.search(r'##+\s*Market Research|^Market Research:', report, re.MULTILINE):
        fallback_prompt = scraped_prompt.replace(f"\nScraped Data:\n{combined}", "")
        print("⚠️ [FALLBACK to model‑only prompt]")
        print("📝 [KNOWLEDGE‑ONLY PROMPT] →\n", fallback_prompt, "\n" + "-"*60)
        report = _invoke_ollama(fallback_prompt)
        print("📬 [KNOWLEDGE‑ONLY OUTPUT] →\n", report, "\n" + "-"*60)

    def get_section(name: str) -> str:
        pat_md = rf'##+\s*{re.escape(name)}(.*?)(?=\n##+|\Z)'
        m = re.search(pat_md, report, re.DOTALL | re.IGNORECASE)
        if m and m.group(1).strip():
            content = m.group(1).strip()
        else:
            pat_plain = rf'^{re.escape(name)}:\s*(.*?)(?=\n^[A-Z][A-Za-z ]+:\s|\Z)'
            m2 = re.search(pat_plain, report, re.MULTILINE | re.DOTALL)
            if m2 and m2.group(1).strip():
                content = m2.group(1).strip()
            else:
                return f"- *{name} not directly found; no structured insight extracted.*"
        if name.lower().startswith("competitor analysis"):
            tbl = re.search(r'(\|.*\|\n)(\|[-:\s]+\|\n)(?:\|.*\|\n)+', content)
            return tbl.group(0) if tbl else content
        bullets = re.findall(r'-\s*(.+)', content)
        return "\n".join(f"- {b}" for b in bullets) if bullets else content

    sections = [
        "Market Research",
        "Competitor Analysis",
        "Feasibility",
        "Budget Requirements",
        "Business Outline",
        "Requirements to Get Started",
        "SWOT Analysis",
        "Risk Assessment",
        "Scalability Potential",
        "Customer Acquisition Cost (CAC) Estimate",
    ]

    output = []
    for sec in sections:
        output.append(f"## {sec}")
        output.append(get_section(sec))
        output.append("")

    swot_path = plot_swot()
    output.append(f"![SWOT Chart]({swot_path})")

    final = "\n".join(output)
    print("🎯 [FORMATTED REPORT] →\n", final, "\n" + "="*60)
    return final