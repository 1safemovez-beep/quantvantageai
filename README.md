# QuantVantageAI (repo: quantvantageai)

QuantVantageAI/QVPro provides **AI-powered creation, market, and commercial evaluation**.

## Product scope
- Creation and market evaluation reports
- Commercial scenario analysis and strategic recommendations
- Compact sponsored placement support (clearly labeled)

QVPro is **not** positioned as:
- an investment adviser
- a brokerage
- a trading platform
- a portfolio manager
- a personalized investment recommendation service

## Quick start (Python / Streamlit)
1. Clone the repo:
   ```bash
   git clone https://github.com/1safemovez-beep/quantvantageai.git
   cd quantvantageai
   ```
2. Create and activate a virtual environment, then install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```
3. Copy env template and configure:
   ```bash
   cp .env.example .env
   ```
4. Run the app:
   ```bash
   streamlit run examples/streamlit_app.py
   ```

## Configuration
- `ANTHROPIC_API_KEY`: Runtime API key for commercial evaluation generation.
- `QV_DATA_ENCRYPTION_KEY`: Required Fernet key for encrypted-at-rest storage of advertiser, sponsor-request, and generated-report data.
- `QUANTVANTAGE_API_URL`: Optional placeholder endpoint config.

## Security notes
- Sensitive local storage is encrypted at rest when `QV_DATA_ENCRYPTION_KEY` is configured.
- Do not commit secrets, API keys, or encryption keys to the repository.
- Transport security depends on HTTPS deployment configuration (e.g., Streamlit Cloud / hosting TLS).

## Legal/disclosure note
Outputs are informational and support commercial planning. They are not investment advice or personalized investment recommendations.
