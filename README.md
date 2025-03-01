# Startup Idea Analyzer
A fully open-source Streamlit application that leverages an Ollama LLM and RAG (Retrieval-Augmented Generation) agent to evaluate startup ideas. This tool generates targeted search queries, scrapes real-time web data, and produces structured analysis reports on market trends, competitors, and feasibility using regex and markdown formatting. Ideal for entrepreneurs and investors seeking technical insights into startup viability.

---

## Features
- **LLM Integration**: Uses Ollama's Llama3 model for natural language processing and query generation.
- **RAG Agent**: Combines retrieval (web scraping) and generation for comprehensive startup analysis.
- **Structured Output**: Reports formatted in markdown with sections like Market Research, Competitor Analysis, and SWOT.
- **Technical Precision**: Implements regex for data extraction and robust API-driven workflows.
- **Open-Source**: 100% free and community-driven, built with accessible tools.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Ollama server running locally (install from [Ollama](https://ollama.ai/))
- Git for cloning the repository

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/startup-idea-analyzer.git
   cd startup-idea-analyzer
2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt


4. **Start the Ollama Server**:
   ```bash
   ollama serve & ollama pull llama3

5. **Run the Application**:
   ```bash
   streamlit run app.py

## Usage

1. Open your browser to `http://localhost:8501`.
2. Fill in the form with:
   - **Startup Idea**: e.g., "Biodegradable pellets from waste"
   - **Country**: e.g., "United States"
   - **Target Market**: e.g., "Eco-conscious businesses"
   - **Budget**: e.g., "$50,000"
   - **Stage of Development**: e.g., "Idea"
   - **Team Size**: e.g., "3"
   - **Key Technologies**: e.g., "Eco-friendly manufacturing"
   - **Funding Goals**: e.g., "$100,000"
   - **Timeline to Launch**: e.g., "6 months"
3. Click "Analyze My Idea" to generate a detailed report.


## Project Structure

startup-idea-analyzer/
├── app.py                # Main Streamlit application
├── ollama_integration.py # LLM and RAG agent logic
├── requirements.txt      # Dependencies
└── README.md             # Project documentation


## Dependencies
- `streamlit`: Web app framework
- `requests`: HTTP requests for Ollama API
- `json`: JSON parsing
- `re`: Regular expressions for formatting

  Install via:
  ```bash
  pip install streamlit requests

## Contributing
Contributions are welcome! Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

## Acknowledgments
- Built with [Streamlit](https://streamlit.io/) and [Ollama](https://ollama.ai/).
- Inspired by the need for quick, technical startup evaluations.

