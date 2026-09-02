# QuantVantageAI (repo: quantvantageai)

This repository contains a demo scaffold for an "app evaluation" tool backed by an AI assistant. The repo previously contained PDFs; this scaffold adds a Streamlit example app, a README, and supporting files so you can run a local demo.

Features
- Streamlit example UI that collects human answers to an evaluation questionnaire.
- Placeholder AI assistant call to QuantumVantage (configurable via environment variables).
- Simple charts (Plotly) that summarize responses.
- Local history logging of interactions to history.json.

Quick start (Python / Streamlit)
1. Clone the repo:
   git clone https://github.com/1safemovez-beep/quantvantageai.git
   cd quantvantageai

2. Create a virtual environment and install dependencies:
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\\Scripts\\activate    # Windows
   pip install -r requirements.txt

3. Copy the example environment file and add your API key:
   cp .env.example .env
   # Edit .env and set QUANTVANTAGE_API_KEY. Optionally set QUANTVANTAGE_API_URL.

4. Run the Streamlit app:
   streamlit run examples/streamlit_app.py

Configuration
- QUANTVANTAGE_API_KEY: Your API key for the QuantumVantage service. If not provided, the app uses a local mock assistant for demos.
- QUANTVANTAGE_API_URL: The assistant endpoint. Default in .env.example is a placeholder. Replace with the real endpoint if you have it.

Notes
- The current repo root includes PDF files (certificate.pdf and fghagft9). Verify whether those should remain in a public repo.
- This scaffold uses a placeholder request format for the AI assistant. Update examples/streamlit_app.py with the real API contract for QuantumVantage when you have the docs.

Next steps
- Add your real QuantumVantage API endpoint and API key to .env, or implement a proper SDK call if QuantumVantage provides one.
- Extend the questionnaire, store results in a DB, or wire results into dashboards.

License
- Add a LICENSE file if you want to publish under a specific license.
