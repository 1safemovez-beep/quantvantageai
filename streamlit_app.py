import streamlit as st
import anthropic
import os
import json

# Restoration of the "First Theme" Design (Clean & Professional)
st.set_page_config(page_title="QuantVantage AI | Analytical Engine", layout="centered")

# --- PUBLIC ACCESS MODE (NO LOGIN REQUIRED FOR TESTING) ---
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
    h1 { color: #3E7096; font-weight: 800; }
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

st.title("QuantVantage AI")
st.subheader("Analytical Intelligence Engine")

# Owner check still works if you log in manually, but doesn't block the site
if st.sidebar.button("Sign in as Creator"):
    st.login()

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
    st.header("Venture Evaluation")
    app_name = st.text_input("App Name", placeholder="e.g. Virtual Mall")
    if st.button("Generate Commercial Analysis"):
        if app_name:
            try:
                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                with st.spinner("Analyzing " + app_name + "..."):
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20240620",
                        max_tokens=1000,
                        messages=[{"role": "user", "content": f"Provide a professional commercial analysis for a venture named '{app_name}'. Include market potential, risks, and a 'QuantVantage' rating."}]
                    )
                    st.success("Analysis Complete")
                    st.write(response.content[0].text)
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
                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                with st.spinner("Synthesizing health trends..."):
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20240620",
                        max_tokens=1000,
                        messages=[{"role": "user", "content": f"As a health data analyzer, provide professional insights based on these respiratory metrics: '{metrics}'. (Disclaimer: For informational purposes only)."}]
                    )
                    st.success("Insights Generated")
                    st.write(response.content[0].text)
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

st.divider()
st.caption("© 2026 QuantVantage AI. Professional Grade Analytics.")
