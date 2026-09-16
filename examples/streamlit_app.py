# QuantVantage AI Pro - Analytical Engine
# Build Version: 2026-09-09-FINAL
import streamlit as st
import anthropic
import os
import json
import time
import urllib.request
import urllib.error
import urllib.parse


def verify_stripe_payment(session_id, expected_amount=499, expected_currency="usd", expected_email=None):
    if not session_id:
        return False
    if isinstance(session_id, list):
        session_id = session_id[0] if session_id else None
    if not session_id:
        return False

    stripe_secret_key = st.secrets.get("STRIPE_SECRET_KEY", os.getenv("STRIPE_SECRET_KEY"))
    if not stripe_secret_key:
        return False

    encoded_session_id = urllib.parse.quote(str(session_id), safe="")
    url = f"https://api.stripe.com/v1/checkout/sessions/{encoded_session_id}"
    auth_header = "Bearer " + stripe_secret_key
    request = urllib.request.Request(
        url,
        headers={"Authorization": auth_header}
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status != 200:
                return False
            payload = response.read().decode("utf-8")
        session_data = json.loads(payload)
        if session_data.get("payment_status") != "paid":
            return False
        if session_data.get("status") != "complete":
            return False
        if session_data.get("amount_total") != expected_amount:
            return False
        if str(session_data.get("currency", "")).lower() != expected_currency.lower():
            return False

        if expected_email:
            customer_details = session_data.get("customer_details") or {}
            checkout_email = (
                customer_details.get("email")
                or session_data.get("customer_email")
                or ""
            ).strip().lower()
            if checkout_email != expected_email.strip().lower():
                return False

        return True
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, TimeoutError, ValueError):
        return False


def load_stripe_redemptions():
    redemptions_path = os.path.join(os.path.dirname(__file__), ".stripe_redemptions.json")
    try:
        with open(redemptions_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return {}


def get_session_fingerprint(session_id):
    if not session_id:
        return None

    stripe_secret_key = st.secrets.get("STRIPE_SECRET_KEY", os.getenv("STRIPE_SECRET_KEY"))
    if not stripe_secret_key:
        return None

    return hashlib.sha256(f"{session_id}|{stripe_secret_key}".encode("utf-8")).hexdigest()


def redeem_session_for_report(session_fingerprint, report_key):
    if not session_fingerprint or not report_key:
        return False

    redemptions_path = os.path.join(os.path.dirname(__file__), ".stripe_redemptions.json")
    lock_path = redemptions_path + ".lock"
    lock_fd = None
    try:
        deadline = time.time() + 3
        while lock_fd is None:
            try:
                lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            except FileExistsError:
                if time.time() >= deadline:
                    return False
                time.sleep(0.05)

        with open(redemptions_path, "a+", encoding="utf-8") as f:
            f.seek(0)
            raw_data = f.read().strip()
            redemptions = {}
            if raw_data:
                try:
                    parsed = json.loads(raw_data)
                    if isinstance(parsed, dict):
                        redemptions = parsed
                except (json.JSONDecodeError, ValueError):
                    redemptions = {}

            existing_report_key = redemptions.get(session_fingerprint)
            if existing_report_key:
                return existing_report_key == report_key

            redemptions[session_fingerprint] = report_key
            f.seek(0)
            f.truncate()
            json.dump(redemptions, f)
            f.flush()
            os.fsync(f.fileno())
            return True
    except OSError:
        return False
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
            try:
                os.remove(lock_path)
            except OSError:
                pass

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

session_id = st.query_params.get("session_id")
if isinstance(session_id, list):
    session_id = session_id[0] if session_id else None
if session_id:
    st.session_state.pending_stripe_session_id = session_id
    try:
        st.query_params.clear()
    except (AttributeError, TypeError):
        pass
session_id = st.session_state.get("pending_stripe_session_id")
expected_email = None
try:
    if st.experimental_user.is_logged_in and st.experimental_user.email:
        expected_email = st.experimental_user.email
except AttributeError:
    pass

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
    if "current_report_key" not in st.session_state:
        st.session_state.current_report_key = None
    
    if st.button("INITIALIZE COMMERCIAL ANALYSIS"):
        if app_name:
            try:
                st.session_state.current_report_key = os.urandom(16).hex()
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
                    
                    report_key = st.session_state.current_report_key
                    session_fingerprint = get_session_fingerprint(session_id)
                    redeemed_report_key = load_stripe_redemptions().get(session_fingerprint)
                    payment_verified = bool(session_id) and redeemed_report_key == report_key

                    if not payment_verified and session_id and redeemed_report_key is None:
                        payment_verified = verify_stripe_payment(session_id, expected_email=expected_email)
                        if payment_verified:
                            payment_verified = redeem_session_for_report(session_fingerprint, report_key)

                    st.divider()
                    if payment_verified:
                        st.success("✅ Payment verified — Full Report unlocked.")
                        st.download_button(
                            label="📄 Download Full Report",
                            data=analysis_text,
                            file_name=f"{app_name.lower().replace(' ', '_')}_full_report.txt",
                            mime="text/plain"
                        )
                    else:
                        st.markdown("""
                            <div class="premium-card">
                                <h3>🔓 Want the Full 12-Page Deep Dive?</h3>
                                <p>Unlock detailed revenue projections, competitor analysis, and viral score optimization.</p>
                                <a href="https://buy.stripe.com/eVq8wH7l9awV2kaboaaVa06" target="_blank" style="display: inline-block; background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; text-decoration: none;">Get Full Report - $4.99</a>
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
st.caption("© 2026 QuantVantage AI. Professional Grade Analytics.")
