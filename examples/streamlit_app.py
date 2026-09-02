"""Streamlit demo app for QuantVantageAI evaluation tool.

This simple app demonstrates:
- A human questionnaire form
- Sending the combined prompt + answers to an AI assistant (placeholder for QuantumVantage)
- Displaying the AI response
- Rendering simple charts that summarize answers
- Saving a local history (history.json)

Update `send_to_quantvantage` with the real API request format when you have the docs.
"""

import os
import json
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("QUANTVANTAGE_API_KEY")
API_URL = os.getenv("QUANTVANTAGE_API_URL", "https://api.quantumvantage.ai/v1/assistant")
HISTORY_FILE = "history.json"

st.set_page_config(page_title="QuantVantage Evaluation Demo", layout="centered")
st.title("QuantVantageAI — App Evaluation Demo")
st.write("Fill the questionnaire, ask the AI assistant, and view charts summarizing responses.")

# Simple questionnaire definition
QUESTIONNAIRE = [
    {"id": "usability", "label": "Usability (1-5)", "type": "slider", "min": 1, "max": 5, "value": 3},
    {"id": "performance", "label": "Performance (1-5)", "type": "slider", "min": 1, "max": 5, "value": 3},
    {"id": "features", "label": "Feature completeness (1-5)", "type": "slider", "min": 1, "max": 5, "value": 3},
    {"id": "comments", "label": "Freeform comments", "type": "text", "value": ""},
]

with st.form("evaluation_form"):
    st.header("Evaluator answers")
    answers = {}
    for q in QUESTIONNAIRE:
        if q["type"] == "slider":
            answers[q["id"]] = st.slider(q["label"], min_value=q["min"], max_value=q["max"], value=q["value"]) 
        elif q["type"] == "text":
            answers[q["id"]] = st.text_area(q["label"], value=q["value"]) 

    st.write("---")
    st.header("AI Assistant")
    user_prompt = st.text_area("Question for AI assistant", value="Summarize the evaluation and suggest improvements.")

    submitted = st.form_submit_button("Submit")


def send_to_quantvantage(api_key: str, api_url: str, prompt: str, answers: dict) -> dict:
    """Placeholder request function.
    Replace this with the real QuantumVantage API contract.
    If no API key is provided, returns a mocked assistant response for demo.
    """
    payload = {
        "prompt": prompt,
        "answers": answers,
    }

    if not api_key:
        # Mocked response
        summary = (
            f"Summary:\nUsability={answers.get('usability')}, "
            f"Performance={answers.get('performance')}, "
            f"Features={answers.get('features')}\n\n"
            f"Comments: {answers.get('comments') or '(none)'}\n"
            "Suggestions: Improve onboarding, reduce load times, prioritize missing features."
        )
        return {"assistant": summary, "meta": {"mock": True}}

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"assistant": f"Error calling QuantVantage API: {e}", "meta": {"error": True}}


def save_history(entry: dict):
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
        data.append(entry)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.warning(f"Could not save history: {e}")


if submitted:
    with st.spinner("Calling AI assistant..."):
        result = send_to_quantvantage(API_KEY, API_URL, user_prompt, answers)

    assistant_text = result.get("assistant") if isinstance(result, dict) else str(result)

    st.subheader("AI assistant response")
    st.write(assistant_text)

    # Build a dataframe for the numeric answers
    numeric_keys = [k for k, v in answers.items() if isinstance(v, (int, float))]
    df = pd.DataFrame([{"metric": k, "value": answers[k]} for k in numeric_keys])

    st.subheader("Evaluation summary")
    if not df.empty:
        fig = px.bar(df, x="metric", y="value", range_y=[0,5], title="Numeric scores")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Freeform comments")
    st.write(answers.get("comments") or "(none)")

    # Save to local history
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "answers": answers,
        "prompt": user_prompt,
        "assistant": assistant_text,
        "meta": result.get("meta") if isinstance(result, dict) else {},
    }
    save_history(entry)

# Sidebar: show history
st.sidebar.header("Saved evaluations")
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        history = []
else:
    history = []

if history:
    for i, item in enumerate(reversed(history[-20:])):
        ts = item.get("timestamp")
        st.sidebar.markdown(f"**{i+1}.** {ts}")
        scores = item.get("answers", {})
        st.sidebar.write(f"U:{scores.get('usability')} P:{scores.get('performance')} F:{scores.get('features')}")
else:
    st.sidebar.write("No saved evaluations yet.")
