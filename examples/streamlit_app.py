# QuantVantage AI Pro - Analytical Engine
# Build Version: 2026-09-09-FINAL
import streamlit as st
import anthropic
import os
import json

# Restoration of the "First Theme" Design (Clean & Professional)
st.set_page_config(page_title="QuantVantage AI Pro | Analytical Engine", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #F9F9F9; }
    .stButton>button {
        background-color: #3E7096; /* Original Blue */
        color: white;
        border-radius: 30px;
        padding: 10px 24px;
        font-weight: bold;
    }
    h1, h2, h3 { color: #3E7096; font-weight: 800; }
    .premium-card {
        background-color: #f0f4f7;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #3E7096;
        margin-bottom: 20px;
    }
    .owner-badge {
        background-color: #6F8854;
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & PRICING ---
st.sidebar.title("💎 QuantVantage AI Pro")
st.sidebar.info("High-precision AI reports and real-time market optics.")

PERSONAL_TIER_LINK = st.secrets.get("PERSONAL_TIER_LINK", os.getenv("PERSONAL_TIER_LINK", "https://buy.stripe.com/eVq8wH7l9awV2kaboaaVa06"))
COMMERCIAL_TIER_LINK = st.secrets.get("COMMERCIAL_TIER_LINK", os.getenv("COMMERCIAL_TIER_LINK", "https://quantvantage-beta.site.accio.ai"))
ADVERTISING_TIER_LINK = st.secrets.get("ADVERTISING_TIER_LINK", os.getenv("ADVERTISING_TIER_LINK", "https://buy.stripe.com/bJefZ9fRFfRfgb0ak6aVa0e"))

st.sidebar.markdown("### 🚀 Personal Tier")
st.sidebar.markdown(f"[Unlock Full 12-Page Report ($4.99)]({PERSONAL_TIER_LINK})")

st.sidebar.markdown("### 🏢 Commercial Tier")
st.sidebar.markdown(f"[Launch QVpro Commercial Analysis ($12.00)]({COMMERCIAL_TIER_LINK})")

st.sidebar.markdown("### 📣 Advertising Tier")
st.sidebar.markdown(f"[Run Advertising Placement Package ($199.00)]({ADVERTISING_TIER_LINK})")

st.sidebar.divider()

if st.sidebar.button("Creator Login"):
    st.login()

# --- MAIN APP ---
st.title("QuantVantage AI Pro")
st.subheader("Professional Grade Analytical Intelligence")

is_owner = False
admin_email = "1safemovez@gmail.com"
admin_password = st.secrets.get("ADMIN_PASSWORD", os.getenv("ADMIN_PASSWORD"))
try:
    if st.experimental_user.is_logged_in and st.experimental_user.email == admin_email:
        if admin_password:
            entered_admin_password = st.sidebar.text_input("Admin Password", type="password", key="admin_password")
            if entered_admin_password:
                if entered_admin_password == admin_password:
                    is_owner = True
                    st.markdown('<div class="owner-badge">👑 OWNER & CREATOR ACCESS</div>', unsafe_allow_html=True)
                else:
                    st.sidebar.error("Incorrect admin password.")
            else:
                st.sidebar.info("Enter admin password to unlock creator analytics.")
        else:
            st.sidebar.warning("ADMIN_PASSWORD is not configured. Add it to Streamlit Secrets.")
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
                # Get API Key from Secrets
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
                    
                    # --- DOWNLOAD BUTTON ---
                    st.download_button(
                        label="📄 Download Analysis Copy",
                        data=analysis_text,
                        file_name=f"{app_name.lower().replace(' ', '_')}_analysis.txt",
                        mime="text/plain"
                    )
                    
                    st.divider()
                    st.markdown(f"""
                        <div class="premium-card">
                            <h3>🔓 Want the Full 12-Page Deep Dive?</h3>
                            <p>Unlock detailed revenue projections, competitor analysis, and viral score optimization.</p>
                            <a href="{PERSONAL_TIER_LINK}" target="_blank"><button style="background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">Get Full Report - $4.99</button></a>
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

                    # --- DOWNLOAD BUTTON ---
                    st.download_button(
                        label="📄 Download Health Insights Copy",
                        data=insights_text,
                        file_name="respiratory_health_insights.txt",
                        mime="text/plain"
                    )
                    
                    st.divider()
                    st.markdown(f"""
                        <div class="premium-card">
                            <h3>📣 Advertising Tier</h3>
                            <p>Activate sponsored placement and campaign visibility with your ad package.</p>
                            <a href="{ADVERTISING_TIER_LINK}" target="_blank"><button style="background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">Start Advertising - $199.00</button></a>
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
st.caption("© 2026 QuantVantage AI. Professional Grade Analytics.")
