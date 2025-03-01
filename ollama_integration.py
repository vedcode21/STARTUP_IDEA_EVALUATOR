import requests
import json
import re

OLLAMA_URL = 'http://localhost:11434'

def generate_search_queries(idea, country, target_market, budget, stage_of_development, key_technologies):
    """
    Generate specific search queries for evaluating a startup idea with additional context.
    
    Args:
        idea (str): The startup idea.
        country (str): The country of operation.
        target_market (str): The target market segment.
        budget (str): The budget in dollars.
        stage_of_development (str): Current stage (e.g., ideation, MVP).
        key_technologies (str): Technologies used.
    
    Returns:
        list: A list of tailored search queries.
    """
    prompt = (
        f"Generate specific search queries to gather data for evaluating the startup idea '{idea}' in {country}, "
        f"targeting '{target_market}' with a budget of ${budget}. The startup is at the '{stage_of_development}' stage "
        f"and uses technologies like '{key_technologies}'. Include queries for:\n"
        f"1. Market size and growth trends for '{idea}' in {country}.\n"
        f"2. Top competitors in the space of '{idea}' using similar technologies.\n"
        f"3. User adoption rates and engagement metrics for similar ideas at the '{stage_of_development}' stage.\n"
        f"4. Cost estimates for developing '{idea}' with {key_technologies}.\n"
        f"5. Successful business models for '{idea}'.\n"
        f"6. Partnerships and integrations common in the industry of '{idea}'.\n"
        f"Ensure the queries are detailed and tailored to the idea's unique aspects."
    )
    
    # Send request to Ollama API
    response = requests.post(f'{OLLAMA_URL}/api/generate', json={'model': 'llama3', 'prompt': prompt})
    
    if response.status_code != 200:
        print(f"Error generating queries: Received status code {response.status_code}")
        return []
    
    queries = []
    for line in response.text.splitlines():
        if line.strip():
            try:
                data = json.loads(line)
                if 'response' in data:
                    queries.append(data['response'])
            except json.JSONDecodeError as e:
                print(f"Failed to parse line: {line} - Error: {e}")
                continue
    
    # Concatenate response chunks without extra spaces
    full_text = ''.join(queries)
    # Split into individual lines
    lines = full_text.split('\n')
    
    # Define pattern for search queries: number, period, optional whitespace, quoted text
    query_pattern = r'^\d+\.\s*"(.*)"'
    extracted_queries = []
    
    # Filter and extract queries
    for line in lines:
        match = re.match(query_pattern, line.strip())
        if match:
            # Extract the text inside the quotes
            extracted_queries.append(match.group(1))
    
    return extracted_queries
# Updated generate_analysis function

def generate_analysis(scraped_data, idea, country, target_market, budget, stage_of_development, team_size, key_technologies, funding_goals, timeline_to_launch):
    # Combine scraped data into a single string
    combined_data = "\n".join([data.get('content', '') or '' if isinstance(data, dict) else '' for data in scraped_data])
    
    # Prompt to get all content (we'll format it later)
    prompt = (
        f"Generate a detailed analysis for the startup idea '{idea}' in {country}, targeting '{target_market}' "
        f"with a budget of ${budget}. Include insights on market research, competitors, feasibility, budget needs, "
        f"business model, requirements to start, SWOT analysis, risks, scalability, and customer acquisition costs. "
        f"Use the scraped data below:\n\n{combined_data}"
    )
    
    # Send request to Ollama API with streaming
    response = requests.post(f'{OLLAMA_URL}/api/generate', json={'model': 'llama3', 'prompt': prompt}, stream=True)
    if response.status_code != 200:
        return "Unable to generate report due to API error."
    
    # Collect the full response
    report_parts = []
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if 'response' in data:
                report_parts.append(data['response'])
            if data.get('done', False):
                break
    full_report = ''.join(report_parts)
    
    # Define your desired sections in order
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
        "Customer Acquisition Cost (CAC) Estimate"
    ]
    
    # Extract content for a section
    def extract_section_content(section_name):
        pattern = rf'(?i)(?:## |### |#### )?{re.escape(section_name)}(.*?)(?=(?:## |### |#### )\w|\Z)'
        match = re.search(pattern, full_report, re.DOTALL)
        if match:
            content = match.group(1).strip()
            bullets = re.findall(r'-\s*(.+)', content)
            if bullets:
                return "\n".join([f"- {b.strip()}" for b in bullets[:3]])  # Limit to 3 bullets
            return content[:500]  # Fallback to first 500 chars
        return "- Insufficient data available."

    # Generate a competitor table
    def generate_competitor_table():
        table_pattern = r'\|.*?\|\n\|.*?\|\n(?:\|.*?\|\n)+'
        if re.search(table_pattern, full_report):
            return re.search(table_pattern, full_report).group(0)
        return (
            "| Competitor | Strengths | Weaknesses | Market Position |\n"
            "|------------|-----------|------------|-----------------|\n"
            "| Company A  | Strong brand | High costs | Leader |\n"
            "| Company B  | Innovation   | Limited reach | Emerging |\n"
            "| Company C  | Low prices   | Small scale   | Niche |"
        )
    
    # Build the final report
    final_report = []
    for section in sections:
        final_report.append(f"## {section}")
        if section == "Competitor Analysis":
            final_report.append(generate_competitor_table())
        else:
            final_report.append(extract_section_content(section))
        final_report.append("")  # Blank line between sections
    
    return "\n".join(final_report)