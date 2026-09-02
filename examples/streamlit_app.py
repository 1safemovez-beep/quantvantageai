import streamlit as st
import os
import json
from dotenv import load_dotenv
import requests
import pandas as pd
import plotly.express as px

# Load environment
load_dotenv()
API_KEY = os.getenv("QUANTVANTAGE_API_KEY", "")
API_URL = os.getenv("QUANTVANTAGE_API_URL", "https://api.quantvantage.ai/v1/assistant")

st.set_page_config(page_title="QuantVantage App Evaluation", layout="centered")

# --- CSS / styling (metallic chrome, pop colors) ---
css = """
<style>
/* Metallic chrome-like background */
body, .main, .block-container {
  background: radial-gradient(circle at 10% 20%, rgba(255,255,255,0.12), transparent 8%),
              linear-gradient(135deg, #e9eef3 0%, #cfd6db 30%, #eef2f5 60%, #ffffff 100%);
  background-attachment: fixed;
  color: #000 !important;
  -webkit-font-smoothing:antialiased;
}

/* Card / panel look */
.card {
  background: rgba(255,255,255,0.72);
  border-radius: 10px;
  padding: 12px;
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

/* Smaller explanation boxes with scroll */
.explain-box {
  max-height: 150px;
  overflow:auto;
  padding:8px;
  font-size:13px;
  line-height:1.35;
  color:#000;
  background: linear-gradient(180deg, rgba(255,255,255,0.7), rgba(250,250,250,0.6));
  border-radius:6px;
  border: 1px solid rgba(0,0,0,0.04);
}

/* Pop accent colors for buttons and highlights */
.stButton>button, .btn-pop {
  background: linear-gradient(90deg,#ff5f6d,#ffc371) !important;
  color: #030303 !important;
  font-weight:600;
  border-radius:8px !important;
  box-shadow: 0 6px 14px rgba(255,95,109,0.18);
}

/* Balance badge */
.coin-badge {
  background: linear-gradient(90deg,#ffd26a,#ffd66a);
  color: #070707;
  padding:6px 10px;
  border-radius:999px;
  font-weight:700;
  display:inline-block;
}

/* Print-friendly overrides */
@media print {
  body, .main, .block-container {
    background: white !important;
    color: black !important;
  }
  .no-print { display:none !important; }
}
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# --- Simple CoinManager (JSON-backed) ---
class CoinManager:
    def __init__(self, path="coin_balances.json"):
        self.path = path
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump({}, f)
        with open(path, "r") as f:
            try:
                self.balances = json.load(f)
            except:
                self.balances = {}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.balances, f, indent=2)

    def get_balance(self, user_id):
        return self.balances.get(str(user_id), 0)

    def add(self, user_id, amount):
        uid = str(user_id)
        self.balances[uid] = self.get_balance(uid) + int(amount)
        self.save()

    def spend(self, user_id, amount):
        uid = str(user_id)
        bal = self.get_balance(uid)
        if bal >= amount:
            self.balances[uid] = bal - amount
            self.save()
            return True
        return False

cm = CoinManager()

# --- UI ---
st.title("QuantVantage — App Evaluation")

# Simple user id for demo (in production use auth)
user_id = st.text_input("Your user id (for demo):", value="tester")

col1, col2 = st.columns([2,1])
with col2:
    st.markdown(f'<div class="coin-badge">{cm.get_balance(user_id)} COIN</div>', unsafe_allow_html=True)
    if st.button("Earn 10 COIN", key="earn"):
        cm.add(user_id, 10)
        st.experimental_rerun()

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Evaluation Questionnaire")
    q1 = st.slider("Usability (1-10)", 1, 10, 7)
    q2 = st.slider("Performance (1-10)", 1, 10, 6)
    q3 = st.slider("Design (1-10)", 1, 10, 8)
    notes = st.text_area("Short notes / explanation", height=80)
    st.markdown('</div>', unsafe_allow_html=True)

# Small explanation box
st.markdown('<div class="explain-box">This demo collects human answers and asks the AI assistant for feedback. Use the Earn/Spend buttons to manage COIN. The AI call is a placeholder — replace with the real QuantumVantage API contract.</div>', unsafe_allow_html=True)

if st.button("Submit Evaluation and Ask AI", key="submit"):
    payload = {
        "user_id": user_id,
        "answers": {"usability": q1, "performance": q2, "design": q3},
        "notes": notes,
    }

    # If API key present, make a real call; otherwise use a mock
    if API_KEY:
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        try:
            resp = requests.post(API_URL, json=payload, headers=headers, timeout=10)
            ai_text = resp.json().get("answer") if resp.status_code==200 else f"API error {resp.status_code}: {resp.text}"
        except Exception as e:
            ai_text = f"API request failed: {e}"
    else:
        # Mock AI response
        avg = (q1+q2+q3)/3.0
        ai_text = f"Mock assistant: overall score {avg:.1f}/10.\nSuggestion: Improve performance by optimizing images and lazy-loading resources. Notes received: {notes[:200]}"

    st.subheader("AI Assistant Response")
    st.info(ai_text)

    # Reward coins for completing an evaluation
    cm.add(user_id, 5)
    st.success("You earned 5 COIN for submitting this evaluation!")

    # Save interaction to history.json
    history_path = "history.json"
    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r") as f:
                history = json.load(f)
        except:
            history = []
    history.append({"user_id":user_id, "payload":payload, "ai":ai_text})
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    st.experimental_rerun()

# Show simple charts summarizing history
if os.path.exists("history.json"):
    with open("history.json", "r") as f:
        try:
            history = json.load(f)
        except:
            history = []
else:
    history = []

if history:
    df_rows = []
    for h in history:
        a = h.get("payload", {}).get("answers", {})
        df_rows.append({"usability": a.get("usability",0), "performance": a.get("performance",0), "design": a.get("design",0)})
    df = pd.DataFrame(df_rows)
    df_mean = df.mean().reset_index()
    df_mean.columns = ["metric","score"]
    fig = px.bar(df_mean, x="metric", y="score", color="metric", title="Average scores from history")
    st.plotly_chart(fig, use_container_width=True)

# Spend COIN example
st.markdown("---")
st.header("Redeem / Spend COIN")
cost = st.number_input("Cost to redeem hint (COIN)", min_value=1, max_value=100, value=10)
if st.button("Redeem hint for cost", key="redeem"):
    if cm.spend(user_id, int(cost)):
        st.success(f"Redeemed {cost} COIN. Here's your hint: Focus on first-contentful-paint and image compression.")
    else:
        st.error("Not enough COIN. Earn more by submitting evaluations.")

st.markdown('<div class="no-print" style="margin-top:20px">Built for demo. Replace the mock AI call with your QuantumVantage API implementation.</div>', unsafe_allow_html=True)
