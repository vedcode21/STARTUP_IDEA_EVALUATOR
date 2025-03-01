import streamlit as st
from ollama_integration import generate_search_queries, generate_analysis
from web_scraper import scrape_web_sync

st.title("Startup Idea Analyzer")
st.write("Enter details about your startup idea to get a comprehensive analysis.")

with st.form("startup_form"):
    idea = st.text_input("Startup Idea", placeholder="e.g., Banana peel packaging")
    country = st.text_input("Country", placeholder="e.g., United States")
    target_market = st.text_input("Target Audience", placeholder="e.g., Eco-conscious businesses")
    budget = st.text_input("Budget (in USD)", placeholder="e.g., $50,000")
    stage_of_development = st.selectbox("Stage of Development", ["Idea", "Prototype", "Early Traction", "Scaling"])
    team_size = st.number_input("Team Size", min_value=1, step=1)
    # Removed: team_expertise = st.text_area("Team Expertise (comma-separated)", placeholder="e.g., Machine Learning, Marketing")
    key_technologies = st.text_input("Key Technologies", placeholder="e.g., AI, Blockchain")
    # Removed: go_to_market_strategy = st.text_input("Go-to-Market Strategy", placeholder="e.g., Digital Marketing, Partnerships")
    funding_goals = st.text_input("Funding Goals", placeholder="e.g., $100,000 from VC")
    timeline_to_launch = st.text_input("Timeline to Launch", placeholder="e.g., 6 months")
    submit_button = st.form_submit_button("Analyze My Idea")

if submit_button:
    if not all([idea, country, target_market, budget, stage_of_development, team_size, key_technologies, funding_goals, timeline_to_launch]):
        st.error("Please fill out all fields.")
    else:
        with st.spinner("Analyzing your startup idea..."):
            # Adjusted call: Removed go_to_market_strategy
            search_queries = generate_search_queries(idea, country, target_market, budget, stage_of_development, key_technologies)
            if not search_queries:
                st.error("Failed to generate search queries. Check Ollama server connection.")
            else:
                st.write("Generated queries:", search_queries)  # Debugging output
                
                # Scrape web data
                scraped_data = scrape_web_sync(search_queries)
                if not scraped_data:
                    st.error("No data scraped. Try refining your inputs or check scraping tools.")
                else:
                    st.write("Scraped data URLs:", [data['url'] for data in scraped_data])  # Debugging output
                    
                    # Adjusted call: Removed team_expertise and go_to_market_strategy
                    report = generate_analysis(scraped_data, idea, country, target_market, budget, stage_of_development, team_size, key_technologies, funding_goals, timeline_to_launch)
                    if report == "Unable to generate report.":
                        st.error("Failed to generate analysis. Check Ollama server.")
                    else:
                        st.markdown(report)