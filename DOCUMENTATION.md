# QVPro Master Analysis Engine: Unified Documentation Package

## 1. Architecture Overview
The QVPro engine follows a decoupled, modular architecture designed for high portability and scalability.

### Core Architecture Flow
**QVPro Core → Analysis Orchestrator → Specialized Analysis Modules → Scoring/Evidence Layer → QVPro Verdict → UI/Reports**

- **Orchestrator (`evaluator_engine.py`)**: The central brain. It receives a target name, triggers specialized modules in parallel (or sequence), and passes raw data to the scoring engine.
- **Specialized Modules (`modules/`)**: Independent Python classes for Market, Product, Competitor, Financial, Commercial, Monetization, Growth, Risks, and Health.
- **Scoring Layer (`scoring.py`)**: Quantifies qualitative AI findings into a 0.1 - 100.0 scale.
- **Reporting Engine (`reporting.py`)**: Transforms data into the "Luxury Spatial Tech" Markdown format.

## 2. File & Folder Structure
```text
/
├── streamlit_app.py          # Frontend (Streamlit)
├── requirements.txt           # Python Dependencies
├── locales/                   # Internationalization (JSON)
│   └── translations.json
├── app_evaluator/             # Engine Root
│   ├── evaluator_engine.py    # Main Orchestrator
│   ├── scoring.py             # Logic Layer
│   ├── reporting.py           # Presentation Layer
│   ├── README.md              # Expansion Guide
│   ├── modules/               # Analysis Modules
│   │   ├── base.py            # AI Base Class
│   │   ├── commercial.py
│   │   ├── competitor.py      # Real Competitor Engine
│   │   ├── financial.py
│   │   ├── growth.py
│   │   ├── health.py
│   │   ├── market.py
│   │   ├── monetization.py
│   │   ├── product.py
│   │   └── risks.py
│   └── templates/             # (Optional) Future report templates
```

## 3. Data & Configuration
- **Storage**: The current version is stateless for the Analysis Engine. Generated reports are intended to be saved to the filesystem or downloaded via the UI.
- **Dynamic Scoring**: The `ScoringEngine` now uses high-precision Regex parsing to extract scores directly from AI output.
  - **Pattern**: `[SCORE: XX.X]`
  - **Logic**: If the AI fails to provide a score, the engine defaults to a qualitative simulation to ensure UI stability.
- **Configuration**: Managed via `locales/translations.json` for UI text.
- **Credentials**: The application requires an `ANTHROPIC_API_KEY`. 
  - **In Streamlit**: Reference via `st.secrets["ANTHROPIC_API_KEY"]`.
  - **In Environment**: Reference via `os.getenv("ANTHROPIC_API_KEY")`.

## 4. Deployment & Portability
### Local Development & Studio Fix
- **Android Studio Project**: [quantvantage_android_studio_project.zip](quantvantage_android_studio_project.zip) (Import the `twa-build` folder inside).
- **Backend Logic**: [qvpro_hardened_master_export.zip](qvpro_hardened_master_export.zip).
- **Signing Key**: `quantvantage.keystore` (Root directory).
1. Install Python 3.9+.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set your API Key: `export ANTHROPIC_API_KEY='your_key_here'`.
4. Run: `streamlit run streamlit_app.py`.

### Moving Outside Accio
The code is 100% standard Python and Streamlit. To move it:
1. Copy the entire directory to a new server/service (Vercel, Heroku, AWS, or local).
2. Ensure the `ANTHROPIC_API_KEY` is set in the new environment's secret manager.
3. No Accio-specific services are required for the engine to function.

## 5. Account & Data Deletion
- **UI Trigger**: The "Delete Analysis" button in `streamlit_app.py` clears the active session data immediately.
- **Engine Logic**: `evaluator_engine.py` contains the `delete_account` method. This is currently marked as **Not Implemented** for safety. It serves as a placeholder for you to connect your production database (e.g., PostgreSQL/Firebase) and authentication provider (e.g., Auth0/Stripe). **Do not use the placeholder for production data deletion without implementing the corresponding database calls.**

## 6. Build Instructions (Mobile)
- For **Google Play/Android**: This project can be wrapped using **Trusted Web Activities (TWA)** or a **Streamlit-to-App** wrapper (like `stlite` or `NativeStream`).
- Ensure the `manifest.json` and icons in the root are updated to match your brand.

---
© 2026 QuantVantage AI Pro | Ownership Package
