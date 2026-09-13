# QuantVantage AI Pro - Analytical Engine
# Build Trigger: 2026-09-05
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

tabs = ["🚀 App Evaluator"]
if is_owner:
    tabs.append("📊 Owner Analytics")

tab_list = st.tabs(tabs)

with tab_list[0]:
    st.header("Universal App Evaluator")
    app_name = st.text_input("ENTER THE NAME OF YOUR VENTURE", placeholder="e.g. Premier tool bazaar Mall")
    
    if st.button("INITIALIZE COMMERCIAL ANALYSIS"):
        if app_name:
            try:
                # Use Haiku as it is more likely to be accessible on new accounts
                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
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
                    st.markdown("""
                        <div style="background: rgba(177, 151, 252, 0.05); border: 1px solid #3E7096; padding: 20px; border-radius: 15px; margin-bottom: 20px;">
                            <h3 style="color: #3E7096; margin-top: 0;">🏢 Fork to AI Mall</h3>
                            <p style="font-size: 0.9rem;">Ready to scale? Take your evaluation results to the <b>Business Floor</b> of the Premium Tool Bazaar to find the right AI tech stack.</p>
                            <a href="https://premium-tool-bazaar.emergent.host/storefronts/ai-instructor" target="_blank">
                                <button style="background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">ENTER BUSINESS MALL FLOOR</button>
                            </a>
                        </div>
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

if is_owner:
    with tab_list[1]:
        st.header("Core Business Analytics")
        st.write("Logged in as Creator")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", "$499.00", "+12%")
        col2.metric("Reports Generated", "102", "+5")
        col3.metric("Affiliate Clicks", "452", "+28%")

st.divider()
st.caption("© 2026 QuantVantage AI. Professional Grade Analytics.")
