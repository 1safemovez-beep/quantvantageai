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

st.title("ROADMAP TO SUCCESS")
st.subheader("Analytical Intelligence Engine")

app_name = st.text_input("ENTER THE NAME OF YOUR VENTURE", placeholder="e.g. Virtual Mall App")

if st.button("INITIALIZE ANALYSIS"):
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("API Key Missing: Please set ANTHROPIC_API_KEY in Secrets.")
    elif not app_name:
        st.warning("Please enter a venture name.")
    else:
        with st.spinner("Analyzing Commercial Architecture..."):
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            prompt = f"""Analyze the following app idea: {app_name}. 
            Provide a commercial evaluation in JSON format with these exact keys:
            - cost_weekly: (estimated cost to run)
            - cost_monthly:
            - cost_yearly:
            - cost_3year:
            - profit_margin_pct: (percentage)
            - profit_amount: (estimated monthly profit)
            - stand_out: (what makes it unique)
            - run_better: (performance recommendation)
            - look_better: (UI/UX recommendation)
            - higher_profit: (profit maximization hack)
            """
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            try:
                # Clean and parse JSON
                content = response.content[0].text
                data = json.loads(content[content.find('{'):content.rfind('}')+1])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.header("📊 Financial Projections")
                    st.write(f"**Weekly Cost:** ${data['cost_weekly']}")
                    st.write(f"**Monthly Cost:** ${data['cost_monthly']}")
                    st.write(f"**Yearly Cost:** ${data['cost_yearly']}")
                    st.write(f"**3-Year Projection:** ${data['cost_3year']}")
                    
                with col2:
                    st.header("💰 Profitability")
                    st.metric("Net Profit Margin", f"{data['profit_margin_pct']}%")
                    st.write(f"**Estimated Monthly Profit:** ${data['profit_amount']}")
                
                st.divider()
                st.header("✨ Competitive Edge")
                st.info(f"**What Stands Out:** {data['stand_out']}")
                
                st.header("🚀 Optimization Roadmap")
                st.success(f"**Run Better:** {data['run_better']}")
                st.warning(f"**Look Better:** {data['look_better']}")
                st.error(f"**Higher Profit:** {data['higher_profit']}")
                
                st.divider()
                st.markdown("### 🏢 Featured Ecosystem")
                st.markdown("[Explore the Premium Tool Bazaar Mall](https://quantvantage.ai/mall)")

            except Exception as e:
                st.error("Analysis completed, but failed to parse results. Please try again.")
                st.write(response.content[0].text)
