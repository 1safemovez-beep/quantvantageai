import streamlit as st
import anthropic
import os
import json

# Restoration of the "First Theme" Design (Clean & Professional)
st.set_page_config(page_title="QuantVantage AI | Analytical Engine", layout="centered")

# --- AUTHENTICATION LOGIC ---
if not st.experimental_user.is_logged_in:
    st.title("QuantVantage AI")
    st.info("Please log in to access the Analytical Intelligence Engine.")
    if st.button("Log in with Google"):
        st.login()
    st.stop()

# --- PROTECTED APP CONTENT ---
OWNER_EMAIL = "1safemovez@gmail.com"
is_owner = st.experimental_user.email == OWNER_EMAIL

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

if is_owner:
    st.markdown('<div class="owner-badge">👑 OWNER & CREATOR ACCESS</div>', unsafe_allow_html=True)

st.title("QuantVantage AI")
st.write(f"Welcome back, **{st.experimental_user.name}**!")

if is_owner:
    with st.sidebar.expander("🛠️ Admin Controls"):
        st.write("Logged in as Creator")
        if st.button("Refresh All Analytics"):
            st.rerun()

if st.sidebar.button("Log out"):
    st.logout()

tabs = ["🚀 App Evaluator", "🫁 Health Optics"]
if is_owner:
    tabs.append("📊 Owner Analytics")

tab_list = st.tabs(tabs)

with tab_list[0]:
    st.header("Venture Evaluation")
    app_name = st.text_input("App Name", placeholder="e.g. Virtual Mall")
    if st.button("Generate Commercial Analysis"):
        st.info("Analyzing market data for " + app_name + "...")

with tab_list[1]:
    st.header("Respiratory Assessment")
    metrics = st.text_area("Symptoms/Metrics")
    if st.button("Generate Health Insights"):
        st.info("AI is synthesizing health trends...")

if is_owner:
    with tab_list[2]:
        st.header("Core Business Analytics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", "$499.00", "+12%")
        col2.metric("Reports Generated", "102", "+5")
        col3.metric("Affiliate Clicks", "452", "+28%")
        
        st.divider()
        st.subheader("Growth Overview")
        chart_data = {"Reports": [10, 25, 45, 80, 102], "Revenue": [50, 125, 225, 400, 499]}
        st.line_chart(chart_data)
        
        st.info("💡 Pro-Tip: Higher engagement seen on Health Optics during weekend hours.")

st.divider()
st.caption("© 2026 QuantVantage AI. Professional Grade Analytics.")
