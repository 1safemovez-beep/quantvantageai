# QuantVantage AI Pro - Master Analysis Engine
# Build Version: 2026-09-12-CONSOLIDATED
import streamlit as st
import os
import json
import urllib.parse
import urllib.request
import urllib.error
from app_evaluator.evaluator_engine import QVProEngine

try:
    import anthropic
except ImportError:
    anthropic = None


# ============================================================
# STRIPE PAYMENT VERIFICATION
# ============================================================
def verify_stripe_payment(session_id):
    """
    Verify a Stripe Checkout Session server-side.
    Requires STRIPE_SECRET_KEY from Streamlit secrets or environment.
    Livemode expectation is configurable via STRIPE_EXPECT_LIVEMODE and
    defaults from the Stripe secret key prefix when unset.
    Returns False for missing configuration or any request/parse failure.
    Returns True only when Stripe reports a paid session that matches the
    expected livemode.
    """

    if not session_id:
        return False

    try:
        stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        expected_livemode = os.getenv("STRIPE_EXPECT_LIVEMODE")

        try:
            stripe_secret_key = st.secrets.get("STRIPE_SECRET_KEY", stripe_secret_key)
            expected_livemode = st.secrets.get("STRIPE_EXPECT_LIVEMODE", expected_livemode)
        except Exception:
            pass

        if not stripe_secret_key:
            return False

        if expected_livemode is None:
            if stripe_secret_key.startswith("sk_live_"):
                expected_livemode = True
            elif stripe_secret_key.startswith("sk_test_"):
                expected_livemode = False
        else:
            expected_livemode = str(expected_livemode).strip().lower() in {"1", "true", "yes", "on"}

        encoded_session_id = urllib.parse.quote(session_id, safe="")
        url = f"https://api.stripe.com/v1/checkout/sessions/{encoded_session_id}"

        request = urllib.request.Request(
            url,
            headers={
                "Authorization": "Bearer " + stripe_secret_key
            },
            method="GET"
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            session = json.loads(response.read().decode("utf-8"))

        # Stripe must confirm this is the expected paid checkout context.
        return (
            session.get("payment_status") == "paid"
            and (expected_livemode is None or session.get("livemode") is expected_livemode)
        )

    except urllib.error.HTTPError:
        return False

    except urllib.error.URLError:
        return False

    except Exception:
        return False

# Restoration of the "Luxury Spatial Tech" Design (High-Performance Dark Mode)
st.set_page_config(page_title="QuantVantage AI Pro | Master Engine", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Main Background with Space Gradient */
    .main { 
        background: radial-gradient(circle at 50% 50%, #0D0D0F 0%, #000000 100%); 
        color: #E8E8E8;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #080808;
        border-right: 1px solid #1A1A1A;
    }
    
    /* Typography */
    h1, h2, h3 { 
        color: #E8E8E8 !important; 
        font-weight: 900 !important; 
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Button - Chrome & Emerald Glow */
    .stButton>button {
        background: linear-gradient(180deg, #FFFFFF 0%, #A9A9A9 100%);
        color: #000000 !important;
        border-radius: 0px !important;
        padding: 15px 40px !important;
        font-weight: 800 !important;
        border: none !important;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #008F68 !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 20px #008F68;
        transform: scale(1.02);
    }
    
    /* Premium Cards - Glassmorphism */
    .premium-card {
        background: rgba(232, 232, 232, 0.05);
        backdrop-filter: blur(20px);
        padding: 30px;
        border-radius: 0px;
        border: 1px solid #A9A9A9;
        border-left: 5px solid #008F68;
        margin-bottom: 25px;
    }
    
    /* Owner Badge - Emerald Glow */
    .owner-badge {
        background-color: #008F68;
        color: white;
        padding: 6px 15px;
        border-radius: 0px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
        box-shadow: 0 0 10px #008F68;
    }

    /* Input Field Styling */
    .stTextInput>div>div>input {
        background-color: #0A0A0A !important;
        color: #E8E8E8 !important;
        border: 1px solid #333 !important;
        border-radius: 0px !important;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0px;
        color: #666;
        font-weight: 700;
        border: 1px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #008F68 !important;
        border-bottom: 2px solid #008F68 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & PRICING ---
# Load Translations
with open("locales/translations.json", "r") as f:
    translations = json.load(f)

selected_lang = st.sidebar.selectbox("🌐 Select Language", list(translations.keys()))
t = translations[selected_lang]

st.sidebar.title(t["sidebar_title"])
st.sidebar.info(t["sidebar_info"])

st.sidebar.markdown(f"### {t['sidebar_analysis_header']}")
st.sidebar.markdown(f"[{t['sidebar_analysis_link']}](https://buy.stripe.com/eVq8wH7l9awV2kaboaaVa06)")

st.sidebar.markdown(f"### {t['sidebar_membership_header']}")
st.sidebar.markdown(f"[{t['sidebar_membership_link']}](https://buy.stripe.com/cNi8wH5d120pe2S9g2aVa01)")

st.sidebar.divider()

# --- SECURITY CHECK ---
encryption_key = None
try:
    encryption_key = st.secrets.get("QV_DATA_ENCRYPTION_KEY")
except:
    pass

if not encryption_key:
    encryption_key = os.getenv("QV_DATA_ENCRYPTION_KEY")

if not encryption_key:
    st.sidebar.warning("🔐 Security Warning: QV_DATA_ENCRYPTION_KEY is missing. Data will not be encrypted.")
    if st.sidebar.button("Generate New Key"):
        from app_evaluator.security import SecureVault
        new_key = SecureVault.generate_key()
        st.sidebar.code(new_key, language="text")
        st.sidebar.info("Copy this to your Streamlit Secrets or .env file.")

if st.sidebar.button(t["creator_login"]):
    st.login()

# --- MAIN APP ---
st.title(t["app_title"])
st.subheader(t["app_subtitle"])

is_owner = False
try:
    if st.experimental_user.is_logged_in and st.experimental_user.email == "1safemovez@gmail.com":
        is_owner = True
        st.markdown(f'<div class="owner-badge">{t["owner_badge"]}</div>', unsafe_allow_html=True)
except:
    pass

tabs = [t["tab_evaluator"], t["tab_health"]]
if is_owner:
    tabs.append(t["tab_analytics"])

tab_list = st.tabs(tabs)

with tab_list[0]:
    st.header(t["evaluator_header"])
    app_name = st.text_input(t["input_app_name"], placeholder=t["placeholder_app_name"])
    
    # Session state for current analysis
    if "current_analysis" not in st.session_state:
        st.session_state.current_analysis = None

    col_init, col_del = st.columns([1, 1])

    with col_init:
        if st.button(t["btn_initialize"]):
            if app_name:
                try:
                    # Get API Key from Secrets
                    api_key = None
                    try:
                        api_key = st.secrets.get("ANTHROPIC_API_KEY")
                    except:
                        pass
                    
                    if not api_key:
                        api_key = os.getenv("ANTHROPIC_API_KEY")
                    
                    engine = QVProEngine(app_name, api_key=api_key)
                    with st.spinner(f"{t['spinner_analyzing']} {app_name}..."):
                        analysis_data = engine.run_full_evaluation()
                        report_text = engine.generate_report()
                        
                        st.session_state.current_analysis = {
                            "name": app_name,
                            "report": report_text,
                            "data": analysis_data
                        }
                        st.success(t["success_complete"])
                except Exception as e:
                    st.error(f"QVPro Core Error: {str(e)}")
            else:
                st.warning(t["warning_name"])

    with col_del:
        if st.session_state.current_analysis:
            if st.button(t["btn_delete"], type="secondary"):
                st.session_state.current_analysis = None
                st.rerun()

    if st.session_state.current_analysis:
        analysis_data = st.session_state.current_analysis["data"]
        report_text = st.session_state.current_analysis["report"]
        scores = analysis_data["scores"]

        st.divider()
        st.subheader("📊 QVPro Score Breakdown")
        
        # Define metrics for mapping
        metrics_list = ["market", "product", "competitor", "financial", "commercial", "monetization", "growth", "risks"]
        
        # Dynamic Bar Chart for visual impact
        chart_data = {m: scores[m] for m in metrics_list}
        st.bar_chart(chart_data, color="#008F68")

        # High-Fidelity Terminal Scorecard
        cols = st.columns(len(scores) - 1)
        for idx, metric in enumerate(metrics_list):
            val = scores[metric]
            display_val = str(val) if val is not None else "N/A"
            # Logic: Emerald for high scores, Chrome for others
            color = "#008F68" if (val is not None and val >= 85) else "#A9A9A9"
            cols[idx].markdown(f"""
                <div style="background: rgba(232, 232, 232, 0.03); padding: 15px 5px; border: 1px solid {color}; text-align: center;">
                    <p style="color: #A9A9A9; font-size: 0.6rem; margin: 0; white-space: nowrap; overflow: hidden; letter-spacing: 0.1em;">{metric.upper()}</p>
                    <h3 style="color: {color}; margin: 5px 0; font-size: 1.4rem;">{display_val}</h3>
                </div>
            """, unsafe_allow_html=True)

        overall_score = scores['overall']
        display_overall = str(overall_score) if overall_score is not None else "N/A"
        st.markdown(f"""
            <div style="background: rgba(232, 232, 232, 0.05); backdrop-filter: blur(20px); padding: 40px; border: 2px solid #008F68; text-align: center; margin: 30px 0; box-shadow: 0 0 30px rgba(0, 143, 104, 0.2);">
                <h1 style="color: #FFFFFF !important; margin: 0; font-size: 4.5rem; letter-spacing: -0.05em;">{display_overall}</h1>
                <p style="color: #008F68; font-size: 1.4rem; margin: 10px 0; letter-spacing: 0.3em; font-weight: 300;">MASTER QVPRO OPTICS</p>
                <div style="background: #008F68; color: #000; padding: 8px 30px; font-size: 0.9rem; display: inline-block; font-weight: 900; letter-spacing: 0.1em;">
                    {analysis_data['verdict'].upper()}
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown(report_text)
        
        # --- DOWNLOAD BUTTON ---
        st.download_button(
            label=t["btn_download_copy"],
            data=report_text,
            file_name=f"{st.session_state.current_analysis['name'].lower().replace(' ', '_')}_analysis.md",
            mime="text/markdown"
        )
        
        st.divider()
        st.markdown(f"""
            <div class="premium-card">
                <h3>{t['premium_card_header']}</h3>
                <p>{t['premium_card_text']}</p>
                <a href="https://buy.stripe.com/eVq8wH7l9awV2kaboaaVa06" target="_blank"><button style="background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">{t['btn_get_full_report']}</button></a>
            </div>
        """, unsafe_allow_html=True)

with tab_list[1]:
    st.header(t["health_header"])
    metrics = st.text_area(t["input_metrics"], placeholder=t["placeholder_metrics"])
    if st.button(t["btn_generate_health"]):
        if metrics:
            try:
                api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
                engine = QVProEngine("Health Assessment", api_key=api_key)
                with st.spinner(t["spinner_health"]):
                    insights_text = engine.run_health_evaluation(metrics, selected_lang)
                    st.success(t["success_health"])
                    st.write(insights_text)

                    # --- DOWNLOAD BUTTON ---
                    st.download_button(
                        label=t["btn_download_health"],
                        data=insights_text,
                        file_name="respiratory_health_insights.txt",
                        mime="text/plain"
                    )
                    
                    st.divider()
                    st.markdown(f"""
                        <div class="premium-card">
                            <h3>{t['premium_health_header']}</h3>
                            <p>{t['premium_health_text']}</p>
                            <a href="https://buy.stripe.com/cNi8wH5d120pe2S9g2aVa01" target="_blank"><button style="background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">{t['btn_upgrade_now']}</button></a>
                        </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"AI Error: {str(e)}")
        else:
            st.warning(t["warning_metrics"])

if is_owner:
    with tab_list[2]:
        st.header(t["owner_header"])
        st.write(t["owner_login_status"])
        col1, col2, col3 = st.columns(3)
        col1.metric(t["metric_revenue"], "$499.00", "+12%")
        col2.metric(t["metric_reports"], "102", "+5")
        col3.metric(t["metric_clicks"], "452", "+28%")

st.divider()
st.caption(t["footer"])
