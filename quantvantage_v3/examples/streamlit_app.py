import streamlit as st
import anthropic
import os
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR if (BASE_DIR / "app_evaluator").exists() else BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app_evaluator.evaluator_engine import QuantVantageAI


def render_disclosure():
    st.info("Important disclosure: QuantVantage AI provides informational content only and does not provide financial, legal, or medical advice.")
    st.caption("App names, venture details, and health metrics entered here are sent to the AI processing provider to generate results. Stripe purchase links open Stripe-hosted checkout pages.")


def render_ai_status():
    st.markdown('<div class="qv-hero"><div class="qv-status">AI signal active</div><p><strong>QuantVantage Premium Interface</strong><br><span>Silver remains the anchor while electric blue and violet accents elevate the live analytical workflow.</span></p></div>', unsafe_allow_html=True)


def store_generated_output(target_name, mode, content):
    evaluator = QuantVantageAI(target_name or "quantvantage-request", mode=mode)
    return evaluator.store_generated_output(content, extension="txt")


def render_delete_controls():
    st.subheader("Privacy & Data Controls")
    st.caption("Delete My Data removes locally generated report files and their registry entries for this demo when you provide the deletion reference shown after generation.")
    deletion_reference = st.text_input("Deletion reference", key="delete_reference")
    if st.button("Delete My Data", key="delete_button"):
        result = QuantVantageAI("deletion-request").delete_customer(deletion_reference)
        if result["deleted"]:
            st.success(f"Deleted {result['deleted_records']} record(s) and {result['deleted_files']} generated file(s).")
            if result["missing_files"]:
                st.info("Some generated files were already absent, but matching records were removed.")
        else:
            st.error((result.get("errors") or ["Unable to delete generated data."])[0])
    st.caption("For manual privacy help, email support@quantvantage-ai.com with your deletion reference.")

# Restoration of the "First Theme" Design (Clean & Professional)
st.set_page_config(page_title="QuantVantage AI Pro | Analytical Engine", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    :root {
        --qv-silver: #E8E8E8;
        --qv-silver-dark: #A9A9A9;
        --qv-blue: #3E7096;
        --qv-green: #6F8854;
        --qv-electric: #4AA8FF;
        --qv-violet: #867BFF;
        --qv-panel: rgba(18, 25, 40, 0.88);
    }
    .stApp {
        background:
            radial-gradient(circle at top, rgba(74, 168, 255, 0.16), transparent 28%),
            radial-gradient(circle at 85% 18%, rgba(134, 123, 255, 0.14), transparent 22%),
            linear-gradient(180deg, #070A12 0%, #0D1320 55%, #05070C 100%);
        color: var(--qv-silver);
    }
    .main { background: transparent; color: var(--qv-silver); }
    [data-testid="stAppViewContainer"] { color: var(--qv-silver); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(18, 25, 40, 0.96), rgba(8, 11, 18, 0.98));
        border-right: 1px solid rgba(232, 232, 232, 0.08);
    }
    .stButton>button {
        background: linear-gradient(135deg, #3E7096 0%, #4AA8FF 100%);
        color: white;
        border: 1px solid rgba(232, 232, 232, 0.12);
        border-radius: 999px;
        padding: 10px 24px;
        font-weight: bold;
        box-shadow: 0 16px 28px rgba(74, 168, 255, 0.18);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 20px 34px rgba(74, 168, 255, 0.24);
    }
    h1, h2, h3 { color: var(--qv-silver); font-weight: 800; letter-spacing: 0.02em; }
    .premium-card {
        background: linear-gradient(160deg, rgba(23, 32, 51, 0.94), rgba(10, 13, 21, 0.92));
        padding: 20px;
        border-radius: 22px;
        border-left: 5px solid var(--qv-silver);
        margin-bottom: 20px;
        border: 1px solid rgba(232, 232, 232, 0.08);
        box-shadow: 0 20px 40px rgba(0,0,0,0.25);
    }
    .owner-badge {
        background: linear-gradient(135deg, #6F8854 0%, #4AA8FF 100%);
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    .qv-hero {
        padding: 18px 22px;
        margin: 8px 0 22px;
        border-radius: 22px;
        border: 1px solid rgba(232, 232, 232, 0.1);
        background: linear-gradient(135deg, rgba(232, 232, 232, 0.08), var(--qv-panel));
        box-shadow: 0 20px 36px rgba(0,0,0,0.22);
    }
    .qv-hero strong { color: var(--qv-silver); letter-spacing: 0.08em; text-transform: uppercase; }
    .qv-hero span { color: rgba(232, 232, 232, 0.72); }
    .qv-status {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 8px 14px;
        border-radius: 999px;
        border: 1px solid rgba(232, 232, 232, 0.14);
        background: rgba(232, 232, 232, 0.05);
        color: var(--qv-silver-dark);
        font-size: 0.78rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }
    .qv-status::before {
        content: "";
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: #73E8FF;
        box-shadow: 0 0 14px rgba(115, 232, 255, 0.85);
    }
    [data-testid="stMetric"] {
        background: linear-gradient(160deg, rgba(23, 32, 51, 0.94), rgba(10, 13, 21, 0.92));
        border: 1px solid rgba(232, 232, 232, 0.08);
        padding: 14px;
        border-radius: 18px;
        box-shadow: 0 18px 36px rgba(0,0,0,0.22);
    }
    [data-baseweb="tab-list"] { gap: 8px; }
    [data-baseweb="tab"] {
        background: rgba(232, 232, 232, 0.04);
        border-radius: 999px;
        color: var(--qv-silver-dark);
        border: 1px solid rgba(232, 232, 232, 0.08);
        padding: 8px 16px;
    }
    [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(62, 112, 150, 0.72), rgba(134, 123, 255, 0.4)) !important;
        color: white !important;
    }
    .stTextInput input, .stTextArea textarea {
        background: rgba(232, 232, 232, 0.05);
        color: var(--qv-silver);
        border: 1px solid rgba(232, 232, 232, 0.12);
        border-radius: 16px;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder { color: rgba(232, 232, 232, 0.38); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & PRICING ---
st.sidebar.title("💎 QuantVantage AI Pro")
st.sidebar.info("High-precision AI reports and real-time market optics.")

st.sidebar.markdown("### 🚀 Get a Full Analysis")
st.sidebar.markdown("[Unlock Full 12-Page Report ($4.99)](https://buy.stripe.com/eVq8wH7l9awV2kaboaaVa06)")

st.sidebar.markdown("### 📈 Monthly Membership")
st.sidebar.markdown("[🌟 Pro Subscription ($2/mo)](https://buy.stripe.com/cNi8wH5d120pe2S9g2aVa01)")

st.sidebar.divider()

if st.sidebar.button("Creator Login"):
    st.login()

# --- MAIN APP ---
st.title("QuantVantage AI Pro")
st.subheader("Professional Grade Analytical Intelligence")
render_ai_status()
render_disclosure()

is_owner = False
try:
    if st.experimental_user.is_logged_in and st.experimental_user.email == "1safemovez@gmail.com":
        is_owner = True
        st.markdown('<div class="owner-badge">👑 OWNER & CREATOR ACCESS</div>', unsafe_allow_html=True)
except:
    pass

tabs = ["🚀 App Evaluator", "🫁 Health Optics"]
if is_owner:
    tabs.append("📊 Owner Analytics")

tab_list = st.tabs(tabs)

with tab_list[0]:
    st.header("Universal App Evaluator")
    app_name = st.text_input("ENTER THE NAME OF YOUR VENTURE", placeholder="e.g. Virtual Mall App")
    
    if st.button("INITIALIZE COMMERCIAL ANALYSIS"):
        if app_name:
            try:
                # Use Haiku for universal access
                api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
                if not api_key:
                    st.error("API Key Missing: Please set ANTHROPIC_API_KEY in Streamlit Secrets.")
                    st.stop()
                
                client = anthropic.Anthropic(api_key=api_key)
                with st.spinner("Analyzing " + app_name + "..."):
                    response = client.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=1000,
                        messages=[{"role": "user", "content": f"Provide a professional commercial analysis for a venture named '{app_name}'. Include market potential, risks, and a 'QuantVantage' rating."}]
                    )
                    st.success("Analysis Complete")
                    analysis_text = response.content[0].text
                    st.write(analysis_text)
                    record = store_generated_output(app_name, "app", analysis_text)
                    st.caption(f"Deletion reference: {record['request_id']}")
                    
                    # --- DOWNLOAD BUTTON ---
                    st.download_button(
                        label="📄 Download Analysis Copy",
                        data=analysis_text,
                        file_name=f"{app_name.lower().replace(' ', '_')}_analysis.txt",
                        mime="text/plain"
                    )
                    
                    st.divider()
                    st.markdown("""
                        <div class="premium-card">
                            <h3>🔓 Want the Full 12-Page Deep Dive?</h3>
                            <p>Unlock detailed revenue projections, competitor analysis, and viral score optimization.</p>
                            <a href="https://buy.stripe.com/eVq8wH7l9awV2kaboaaVa06" target="_blank"><button style="background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">Get Full Report - $4.99</button></a>
                        </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"AI Error: {str(e)}")
        else:
            st.warning("Please enter a name.")

with tab_list[1]:
    st.header("Respiratory Assessment")
    metrics = st.text_area("Symptoms/Metrics", placeholder="e.g. Coughing, shortness of breath...")
    if st.button("Generate Health Insights"):
        if metrics:
            try:
                api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
                client = anthropic.Anthropic(api_key=api_key)
                with st.spinner("Synthesizing health trends..."):
                    response = client.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=1000,
                        messages=[{"role": "user", "content": f"As a health data analyzer, provide professional insights based on these respiratory metrics: '{metrics}'. (Disclaimer: For informational purposes only)."}]
                    )
                    st.success("Insights Generated")
                    insights_text = response.content[0].text
                    st.write(insights_text)
                    record = store_generated_output(metrics[:40], "health", insights_text)
                    st.caption(f"Deletion reference: {record['request_id']}")

                    # --- DOWNLOAD BUTTON ---
                    st.download_button(
                        label="📄 Download Health Insights Copy",
                        data=insights_text,
                        file_name="respiratory_health_insights.txt",
                        mime="text/plain"
                    )
                    
                    st.divider()
                    st.markdown("""
                        <div class="premium-card">
                            <h3>🏥 Upgrade to Pro Health Optics</h3>
                            <p>Get personalized physiological roadmaps and immediate action steps.</p>
                            <a href="https://buy.stripe.com/cNi8wH5d120pe2S9g2aVa01" target="_blank"><button style="background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">Upgrade Now - $2/mo</button></a>
                        </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"AI Error: {str(e)}")
        else:
            st.warning("Please provide metrics.")

if is_owner:
    with tab_list[2]:
        st.header("Core Business Analytics")
        st.write("Logged in as Creator")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", "$499.00", "+12%")
        col2.metric("Reports Generated", "102", "+5")
        col3.metric("Affiliate Clicks", "452", "+28%")

st.divider()
render_delete_controls()
st.divider()
st.caption("© 2026 QuantVantage AI. Professional Grade Analytics.")
