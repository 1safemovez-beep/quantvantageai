# QuantVantage AI Pro - Analytical Engine
# Build Version: 2026-09-13-ADVERTISING
import base64
import html
import json
import os
import tempfile
import uuid
from datetime import date, datetime
from pathlib import Path

import anthropic
import streamlit as st

st.set_page_config(page_title="QuantVantage AI Pro | Analytical Engine", layout="wide")

st.markdown(
    """
    <style>
    .main { background-color: #F9F9F9; }
    .stButton>button {
        background-color: #3E7096;
        color: white;
        border-radius: 30px;
        padding: 10px 24px;
        font-weight: bold;
    }
    h1, h2, h3 { color: #3E7096; font-weight: 800; }
    .premium-card {
        background-color: #f0f4f7;
        padding: 14px;
        border-radius: 15px;
        border-left: 5px solid #3E7096;
        margin-bottom: 14px;
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
    .ad-mini-title { font-size: 0.95rem; font-weight: 700; margin-bottom: 4px; }
    .ad-mini-desc { font-size: 0.85rem; margin-bottom: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
AD_DATA_PATH = BASE_DIR / "advertising_data.json"
RATE_CARD_PATH = BASE_DIR / "advertising_rate_card.json"
SUBSCRIPTIONS_PATH = BASE_DIR / "ad_subscriptions.json"

OWNER_EMAIL = "1safemovez@gmail.com"
AD_STATUSES = ["Draft", "Pending Approval", "Approved", "Active", "Paused", "Expired"]
PLACEMENTS = ["Sidebar Compact", "App Evaluator Compact", "Health Optics Compact", "Premium Compact"]

DEFAULT_RATE_CARD = {
    "QVPro Sponsor": "199",
    "3-Month Sponsor": "499",
    "Premium Placement": "299",
    "Exclusive Category Sponsor": "499",
    "Exclusive Site Sponsor": "750-1000",
}


def _load_json(path: Path, default_value):
    if not path.exists():
        return default_value
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default_value


def _save_json(path: Path, value):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp_file:
        tmp_file.write(json.dumps(value, indent=2))
        temp_path = Path(tmp_file.name)
    temp_path.replace(path)


def load_ads():
    return _load_json(AD_DATA_PATH, {"ads": []})


def save_ads(data):
    _save_json(AD_DATA_PATH, data)


def load_rate_card():
    return _load_json(RATE_CARD_PATH, DEFAULT_RATE_CARD)


def save_rate_card(card):
    _save_json(RATE_CARD_PATH, card)


def load_subscriptions():
    return _load_json(SUBSCRIPTIONS_PATH, {"subscriptions": []})


def save_subscriptions(data):
    _save_json(SUBSCRIPTIONS_PATH, data)


def encode_uploaded_image(uploaded_file):
    if not uploaded_file:
        return ""
    raw = uploaded_file.getvalue()
    b64 = base64.b64encode(raw).decode("utf-8")
    return f"data:{uploaded_file.type};base64,{b64}"


def parse_date_string(value: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None


def compute_metrics(ad):
    impressions = int(ad.get("impressions", 0))
    clicks = int(ad.get("clicks", 0))
    ctr = (clicks / impressions * 100.0) if impressions > 0 else 0.0
    revenue = float(ad.get("campaign_price", 0.0) or 0.0)
    return impressions, clicks, ctr, revenue


def active_ads(all_ads, placement=None):
    today = date.today()
    result = []
    for ad in all_ads:
        start = parse_date_string(ad.get("start_date", ""))
        end = parse_date_string(ad.get("end_date", ""))
        ad_placement = ad.get("placement", "Sidebar Compact")
        if placement and ad_placement != placement:
            continue
        if ad.get("status") == "Active" and start and end and start <= today <= end:
            result.append(ad)
    return result


def upsert_ad(ad_payload):
    ad_store = load_ads()
    ads = ad_store.get("ads", [])
    found = False
    for i, ad in enumerate(ads):
        if ad.get("id") == ad_payload.get("id"):
            ads[i] = ad_payload
            found = True
            break
    if not found:
        ads.append(ad_payload)
    ad_store["ads"] = ads
    save_ads(ad_store)


def delete_ad(ad_id):
    ad_store = load_ads()
    ad_store["ads"] = [a for a in ad_store.get("ads", []) if a.get("id") != ad_id]
    save_ads(ad_store)


def increment_metric(ad_id, metric):
    ad_store = load_ads()
    updated = False
    for ad in ad_store.get("ads", []):
        if ad.get("id") == ad_id:
            ad[metric] = int(ad.get(metric, 0)) + 1
            updated = True
            break
    if updated:
        save_ads(ad_store)


def expire_campaigns_if_needed():
    today = date.today()
    ad_store = load_ads()
    changed = False
    for ad in ad_store.get("ads", []):
        end = parse_date_string(ad.get("end_date", ""))
        if end and end < today and ad.get("status") in {"Active", "Approved"}:
            ad["status"] = "Expired"
            changed = True
    if changed:
        save_ads(ad_store)


expire_campaigns_if_needed()

st.sidebar.title("💎 QuantVantage AI Pro")
st.sidebar.info("High-precision AI reports and real-time market optics.")

st.sidebar.markdown("### 🚀 Get a Full Analysis")
st.sidebar.markdown("[Unlock Full 12-Page Report ($4.99)](https://buy.stripe.com/eVq8wH7l9awV2kaboaaVa06)")

st.sidebar.markdown("### 📈 Monthly Membership")
st.sidebar.markdown("[🌟 Pro Subscription ($2/mo)](https://buy.stripe.com/cNi8wH5d120pe2S9g2aVa01)")

st.sidebar.divider()

if st.sidebar.button("Creator Login"):
    st.login()

st.title("QuantVantage AI Pro")
st.subheader("Professional Grade Analytical Intelligence")

is_owner = False
try:
    if st.experimental_user.is_logged_in and st.experimental_user.email == OWNER_EMAIL:
        is_owner = True
        st.markdown('<div class="owner-badge">👑 OWNER & CREATOR ACCESS</div>', unsafe_allow_html=True)
except Exception:
    pass

ad_store = load_ads()
all_ads = ad_store.get("ads", [])
current_active_ads = active_ads(all_ads, placement="Sidebar Compact")

if "ad_impressions_seen" not in st.session_state:
    st.session_state["ad_impressions_seen"] = set()

if current_active_ads:
    compact_ad = sorted(current_active_ads, key=lambda a: float(a.get("campaign_price", 0) or 0), reverse=True)[0]
    if compact_ad["id"] not in st.session_state["ad_impressions_seen"]:
        increment_metric(compact_ad["id"], "impressions")
        st.session_state["ad_impressions_seen"].add(compact_ad["id"])

    with st.container(border=True):
        st.markdown("### 📣 Sponsored")
        cols = st.columns([1, 3])
        with cols[0]:
            if compact_ad.get("logo"):
                st.image(compact_ad["logo"], width=64)
            elif compact_ad.get("creative"):
                st.image(compact_ad["creative"], width=64)
        with cols[1]:
            st.markdown(f"<div class='ad-mini-title'>{compact_ad.get('headline', 'Sponsored')}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='ad-mini-desc'>{compact_ad.get('short_description', '')}</div>",
                unsafe_allow_html=True,
            )
            if st.button("Visit Sponsor", key=f"visit_{compact_ad['id']}"):
                increment_metric(compact_ad["id"], "clicks")
                destination_url = compact_ad.get("destination_url", "https://example.com")
                safe_destination_url = html.escape(destination_url, quote=True)
                st.markdown(
                    f'<meta http-equiv="refresh" content="0; url={safe_destination_url}">',
                    unsafe_allow_html=True,
                )

base_tabs = ["🚀 App Evaluator", "🫁 Health Optics", "📧 Sponsor With Email"]
if is_owner:
    base_tabs.extend(["🛠️ Advertising", "📊 Owner Analytics"])

tab_list = st.tabs(base_tabs)

with tab_list[0]:
    st.header("Universal App Evaluator")
    app_name = st.text_input("ENTER THE NAME OF YOUR VENTURE", placeholder="e.g. Premier tool bazaar Mall")

    if st.button("INITIALIZE COMMERCIAL ANALYSIS"):
        if app_name:
            try:
                api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
                if not api_key:
                    st.error("API Key Missing: Please set ANTHROPIC_API_KEY in Streamlit Secrets.")
                    st.stop()

                client = anthropic.Anthropic(api_key=api_key)
                with st.spinner("Analyzing " + app_name + "..."):
                    response = client.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=1000,
                        messages=[
                            {
                                "role": "user",
                                "content": f"Provide a professional commercial analysis for a venture named '{app_name}'. Include market potential, risks, and a 'QuantVantage' rating.",
                            }
                        ],
                    )
                    st.success("Analysis Complete")
                    analysis_text = response.content[0].text
                    st.write(analysis_text)

                    st.download_button(
                        label="📄 Download Analysis Copy",
                        data=analysis_text,
                        file_name=f"{app_name.lower().replace(' ', '_')}_analysis.txt",
                        mime="text/plain",
                    )

                    st.divider()
                    st.markdown(
                        """
                        <div class="premium-card">
                            <h3>🔓 Want the Full 12-Page Deep Dive?</h3>
                            <p>Unlock detailed revenue projections, competitor analysis, and viral score optimization.</p>
                            <a href="https://buy.stripe.com/eVq8wH7l9awV2kaboaaVa06" target="_blank"><button style="background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">Get Full Report - $4.99</button></a>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
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
                        messages=[
                            {
                                "role": "user",
                                "content": f"As a health data analyzer, provide professional insights based on these respiratory metrics: '{metrics}'. (Disclaimer: For informational purposes only).",
                            }
                        ],
                    )
                    st.success("Insights Generated")
                    insights_text = response.content[0].text
                    st.write(insights_text)

                    st.download_button(
                        label="📄 Download Health Insights Copy",
                        data=insights_text,
                        file_name="respiratory_health_insights.txt",
                        mime="text/plain",
                    )

                    st.divider()
                    st.markdown(
                        """
                        <div class="premium-card">
                            <h3>🏥 Upgrade to Pro Health Optics</h3>
                            <p>Get personalized physiological roadmaps and immediate action steps.</p>
                            <a href="https://buy.stripe.com/cNi8wH5d120pe2S9g2aVa01" target="_blank"><button style="background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">Upgrade Now - $2/mo</button></a>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
            except Exception as e:
                st.error(f"AI Error: {str(e)}")
        else:
            st.warning("Please provide metrics.")

with tab_list[2]:
    st.header("Sponsor With Email")
    st.caption("Compact advertiser onboarding request form.")
    with st.form("ad_subscription_form", clear_on_submit=True):
        company = st.text_input("Company Name")
        contact_email = st.text_input("Contact Email")
        interest = st.selectbox("Interest", list(load_rate_card().keys()))
        notes = st.text_area("Campaign Notes", placeholder="Placement goals, dates, budget range...")
        submitted = st.form_submit_button("Submit Sponsor Request")
        if submitted:
            if company and contact_email:
                subs = load_subscriptions()
                subs["subscriptions"].append(
                    {
                        "id": str(uuid.uuid4()),
                        "company": company,
                        "contact_email": contact_email,
                        "interest": interest,
                        "notes": notes,
                        "created_at": datetime.utcnow().isoformat(),
                    }
                )
                save_subscriptions(subs)
                st.success("Request submitted.")
            else:
                st.error("Company and contact email are required.")

if is_owner:
    with tab_list[3]:
        st.header("Advertising Management")

        st.subheader("Rate Card (Creator editable)")
        rate_card = load_rate_card()
        with st.form("rate_card_form"):
            updated_rate_card = {}
            for name, value in rate_card.items():
                updated_rate_card[name] = st.text_input(name, value=str(value))
            if st.form_submit_button("Save Rate Card"):
                save_rate_card(updated_rate_card)
                st.success("Rate card updated.")

        st.info("ADVERTISING PAYMENT FLOW NOT YET CONFIGURED")
        st.caption("Existing Stripe links are for current app products; advertiser checkout is not implemented yet.")

        st.subheader("Add Advertiser")
        with st.form("add_advertiser_form", clear_on_submit=True):
            company_name = st.text_input("Advertiser/Company Name")
            contact_email = st.text_input("Contact Email")
            logo_upload = st.file_uploader("Logo Upload", type=["png", "jpg", "jpeg"], key="logo_upload")
            logo_url = st.text_input("Logo URL (optional)")
            creative_upload = st.file_uploader("Ad Creative Upload", type=["png", "jpg", "jpeg"], key="creative_upload")
            creative_url = st.text_input("Ad Creative URL (optional)")
            headline = st.text_input("Headline")
            short_description = st.text_area("Short Description", max_chars=240)
            destination_url = st.text_input("Destination URL")
            campaign_price = st.number_input("Campaign Price", min_value=0.0, step=1.0)
            start_date = st.date_input("Start Date", value=date.today())
            end_date = st.date_input("End Date", value=date.today())
            placement = st.selectbox("Placement", PLACEMENTS)
            status = st.selectbox("Status", AD_STATUSES)
            add_submit = st.form_submit_button("Add Advertiser")

            if add_submit:
                if company_name and contact_email and headline and destination_url:
                    upsert_ad(
                        {
                            "id": str(uuid.uuid4()),
                            "company_name": company_name,
                            "contact_email": contact_email,
                            "logo": encode_uploaded_image(logo_upload) or logo_url,
                            "creative": encode_uploaded_image(creative_upload) or creative_url,
                            "headline": headline,
                            "short_description": short_description,
                            "destination_url": destination_url,
                            "campaign_price": float(campaign_price),
                            "start_date": start_date.isoformat(),
                            "end_date": end_date.isoformat(),
                            "placement": placement,
                            "status": status,
                            "impressions": 0,
                            "clicks": 0,
                            "created_at": datetime.utcnow().isoformat(),
                        }
                    )
                    st.success("Advertiser added.")
                else:
                    st.error("Company, contact email, headline, and destination URL are required.")

        refreshed_ads = load_ads().get("ads", [])
        if refreshed_ads:
            st.subheader("Creator Controls")
            options = {f"{ad.get('company_name')} — {ad.get('headline')} ({ad.get('status')})": ad for ad in refreshed_ads}
            selected_label = st.selectbox("Select Campaign", list(options.keys()))
            selected_ad = options[selected_label]

            with st.form("edit_ad_form"):
                company_name_e = st.text_input("Advertiser/Company Name", value=selected_ad.get("company_name", ""))
                contact_email_e = st.text_input("Contact Email", value=selected_ad.get("contact_email", ""))
                logo_e = st.text_input("Logo URL / Data URI", value=selected_ad.get("logo", ""))
                creative_e = st.text_input("Creative URL / Data URI", value=selected_ad.get("creative", ""))
                headline_e = st.text_input("Headline", value=selected_ad.get("headline", ""))
                short_desc_e = st.text_area("Short Description", value=selected_ad.get("short_description", ""), max_chars=240)
                destination_e = st.text_input("Destination URL", value=selected_ad.get("destination_url", ""))
                price_e = st.number_input("Campaign Price", min_value=0.0, step=1.0, value=float(selected_ad.get("campaign_price", 0.0)))
                start_e = st.date_input("Start Date", value=parse_date_string(selected_ad.get("start_date", "")) or date.today(), key="start_edit")
                end_e = st.date_input("End Date", value=parse_date_string(selected_ad.get("end_date", "")) or date.today(), key="end_edit")
                placement_e = st.selectbox("Placement", PLACEMENTS, index=PLACEMENTS.index(selected_ad.get("placement", PLACEMENTS[0])) if selected_ad.get("placement") in PLACEMENTS else 0)
                status_e = st.selectbox("Status", AD_STATUSES, index=AD_STATUSES.index(selected_ad.get("status", "Draft")) if selected_ad.get("status") in AD_STATUSES else 0)
                if st.form_submit_button("Save Campaign Changes"):
                    selected_ad.update(
                        {
                            "company_name": company_name_e,
                            "contact_email": contact_email_e,
                            "logo": logo_e,
                            "creative": creative_e,
                            "headline": headline_e,
                            "short_description": short_desc_e,
                            "destination_url": destination_e,
                            "campaign_price": float(price_e),
                            "start_date": start_e.isoformat(),
                            "end_date": end_e.isoformat(),
                            "placement": placement_e,
                            "status": status_e,
                        }
                    )
                    upsert_ad(selected_ad)
                    st.success("Campaign updated.")

            col_a, col_b, col_c, col_d, col_e = st.columns(5)
            if col_a.button("Approve", use_container_width=True):
                selected_ad["status"] = "Approved"
                upsert_ad(selected_ad)
                st.success("Campaign approved.")
            if col_b.button("Activate", use_container_width=True):
                selected_ad["status"] = "Active"
                upsert_ad(selected_ad)
                st.success("Campaign active.")
            if col_c.button("Pause", use_container_width=True):
                selected_ad["status"] = "Paused"
                upsert_ad(selected_ad)
                st.success("Campaign paused.")
            if col_d.button("Resume", use_container_width=True):
                selected_ad["status"] = "Active"
                upsert_ad(selected_ad)
                st.success("Campaign resumed.")
            if col_e.button("Delete", type="primary", use_container_width=True):
                delete_ad(selected_ad.get("id"))
                st.success("Campaign deleted.")

            st.subheader("Analytics")
            rows = []
            total_revenue = 0.0
            for ad in load_ads().get("ads", []):
                impressions, clicks, ctr, revenue = compute_metrics(ad)
                total_revenue += revenue
                rows.append(
                    {
                        "Company": ad.get("company_name"),
                        "Headline": ad.get("headline"),
                        "Status": ad.get("status"),
                        "Impressions": impressions,
                        "Clicks": clicks,
                        "CTR (%)": round(ctr, 2),
                        "Campaign Start": ad.get("start_date"),
                        "Campaign End": ad.get("end_date"),
                        "Revenue": revenue,
                    }
                )
            st.dataframe(rows, use_container_width=True)
            st.metric("Total Campaign Revenue", f"${total_revenue:,.2f}")

            sub_count = len(load_subscriptions().get("subscriptions", []))
            st.metric("Sponsor Email Requests", sub_count)

    with tab_list[4]:
        st.header("Core Business Analytics")
        st.write("Logged in as Creator")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", "$499.00", "+12%")
        col2.metric("Reports Generated", "102", "+5")
        col3.metric("Affiliate Clicks", "452", "+28%")

st.divider()
st.caption("© 2026 QuantVantage AI. Professional Grade Analytics.")
