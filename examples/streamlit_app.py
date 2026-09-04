import streamlit as st
import anthropic
import os
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Luxury Branding
st.set_page_config(page_title="QuantVantage AI | App Evaluator", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #0A0A0B;
        color: #E0E0E0;
    }
    .stButton>button {
        background-color: #D4AF37;
        color: black;
        border-radius: 2px;
        font-weight: bold;
        text-transform: uppercase;
        width: 100%;
    }
    h1 {
        color: #D4AF37;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("QUANTVANTAGE AI")
st.subheader("Analytical Intelligence Engine")

# Mode Selection Tabs
tab1, tab2 = st.tabs(["🚀 App Evaluator", "🫁 Respiratory Health"])

with tab1:
    st.header("Universal App Evaluator")
    app_name = st.text_input("ENTER THE NAME OF YOUR VENTURE", placeholder="e.g. Virtual Mall App")
    
    if st.button("INITIALIZE COMMERCIAL ANALYSIS"):
        if not os.getenv("ANTHROPIC_API_KEY"):
            st.error("API Key Missing: Please set ANTHROPIC_API_KEY in Secrets.")
        elif not app_name:
            st.warning("Please enter a venture name.")
        else:
            with st.spinner("Analyzing Commercial Architecture..."):
                client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                prompt = f"""Analyze the following app idea: {app_name}. 
                Provide a commercial evaluation in JSON format with these exact keys:
                - cost_weekly, cost_monthly, cost_yearly, cost_3year, profit_margin_pct, profit_amount, stand_out, run_better, look_better, higher_profit"""
                
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                try:
                    data = json.loads(response.content[0].text[response.content[0].text.find('{'):response.content[0].text.rfind('}')+1])
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Weekly Cost:** ${data['cost_weekly']}")
                        st.write(f"**Monthly Cost:** ${data['cost_monthly']}")
                        st.write(f"**Yearly Cost:** ${data['cost_yearly']}")
                    with c2:
                        st.metric("Net Margin", f"{data['profit_margin_pct']}%")
                        st.write(f"**Est. Profit:** ${data['profit_amount']}")
                    st.info(f"**Stand Out:** {data['stand_out']}")
                    st.success(f"**Run Better:** {data['run_better']}")
                    
                    st.divider()
                    st.header("📂 Export & Share")
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        if st.button("🖨️ Prepare for Print"):
                            st.info("Browser print dialog opening... Use 'Save as PDF' to keep your report.")
                            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
                    with col_s2:
                        share_text = f"QuantVantage AI Evaluation for {app_name}: Costs starting at ${data['cost_weekly']}/week with a {data['profit_margin_pct']}% margin!"
                        st.text_input("Copy Shareable Result", value=share_text)
                    
                    st.divider()
                    st.markdown("### 🏢 Featured Ecosystem")
                    st.markdown("[Explore the Premium Tool Bazaar Mall](https://quantvantage.ai/mall)")
                except: st.error("Parsing failed.")

with tab2:
    st.header("Respiratory Health Assessment")
    health_metrics = st.text_area("DESCRIBE RESPIRATORY SYMPTOMS OR METRICS", placeholder="e.g. Cough duration, breath depth...")
    
    if st.button("INITIALIZE HEALTH EVALUATION"):
        if not os.getenv("ANTHROPIC_API_KEY"):
            st.error("API Key Missing.")
        elif not health_metrics:
            st.warning("Please provide metrics.")
        else:
            with st.spinner("Analyzing Health Data..."):
                client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                prompt = f"Analyze these respiratory metrics and provide a health assessment: {health_metrics}"
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                st.write(response.content[0].text)
