# QuantVantageAI (repo: quantvantageai)

This repository contains a demo scaffold for an "app evaluation" tool backed by an AI assistant. The repo previously contained PDF files (certificate.pdf and fghagft9); this scaffold adds a Streamlit example app, styling, and a simple in-app coin system.

Features
- Streamlit example UI that collects human answers to an evaluation questionnaire.
- Simple CoinManager (JSON-backed) that tracks user coins and supports earn/spend actions.
- Placeholder AI assistant call to QuantumVantage (configurable via environment variables).
- Simple Plotly charts that summarize responses.
- Styling (metallic/chrome background, pop colors) and print-friendly overrides.

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

Coin system
- The app includes a simple JSON-backed coin store (coin_balances.json). This is NOT a blockchain token — it's a local rewards system to let your agent reward users.
- To upgrade to a blockchain ERC-20 token, see the TODOs in the README.

Next steps
- Add your real QuantumVantage API endpoint and API key to .env, or implement a proper SDK call if QuantumVantage provides one.
- Extend the questionnaire, store results in a DB, or wire results into dashboards.

License
- Add a LICENSE file if you want to publish under a specific license.
