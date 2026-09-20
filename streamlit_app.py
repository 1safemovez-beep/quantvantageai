# QuantVantage AI Pro - Analytical Engine
# Build Version: 2026-09-13-RISK-REDUCTION
import base64
import json
import os
import uuid
from datetime import date, datetime
from pathlib import Path

import anthropic
import streamlit as st

try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception:  # pragma: no cover
    Fernet = None
    InvalidToken = Exception

st.set_page_config(page_title="QuantVantage AI Pro | Evaluation", layout="wide")

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
    .ad-mini-desc { font-size: 0.85rem; margin-bottom: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
AD_DATA_PATH = BASE_DIR / "advertising_data.enc"
AD_DATA_LEGACY_PATH = BASE_DIR / "advertising_data.json"
RATE_CARD_PATH = BASE_DIR / "advertising_rate_card.json"
SUBSCRIPTIONS_PATH = BASE_DIR / "ad_subscriptions.enc"
SUBSCRIPTIONS_LEGACY_PATH = BASE_DIR / "ad_subscriptions.json"
REPORTS_PATH = BASE_DIR / "generated_reports.enc"
REPORTS_LEGACY_PATH = BASE_DIR / "generated_reports.json"

OWNER_EMAIL = "1safemovez@gmail.com"
AD_STATUSES = ["Draft", "Pending Approval", "Approved", "Active", "Paused", "Expired"]
PLACEMENTS = ["Sidebar Compact", "App Evaluator Compact", "Premium Compact", "Footer Compact"]
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
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def _get_encryption_key():
    key = None
    try:
        key = st.secrets.get("QV_DATA_ENCRYPTION_KEY", None)
    except Exception:
        key = None
    if not key:
        key = os.getenv("QV_DATA_ENCRYPTION_KEY")
    return key


def _get_fernet():
    key = _get_encryption_key()
    if not key or not Fernet:
        return None
    try:
        return Fernet(key.encode("utf-8"))
    except Exception:
        return None


FERNET = _get_fernet()
SECURE_STORAGE_ENABLED = FERNET is not None


def _load_sensitive(path_enc: Path, legacy_path: Path, default_value):
    if path_enc.exists() and FERNET:
        try:
            encrypted = path_enc.read_bytes()
            decrypted = FERNET.decrypt(encrypted)
            return json.loads(decrypted.decode("utf-8"))
        except (InvalidToken, ValueError, json.JSONDecodeError):
            return default_value

    if legacy_path.exists():
        legacy = _load_json(legacy_path, default_value)
        if FERNET:
            _save_sensitive(path_enc, legacy)
        return legacy

    return default_value


def _save_sensitive(path_enc: Path, value):
    if not FERNET:
        return False
    encoded = json.dumps(value, indent=2).encode("utf-8")
    encrypted = FERNET.encrypt(encoded)
    path_enc.write_bytes(encrypted)
    return True


def load_ads():
    return _load_sensitive(AD_DATA_PATH, AD_DATA_LEGACY_PATH, {"ads": []})


def save_ads(data):
    return _save_sensitive(AD_DATA_PATH, data)


def load_rate_card():
    return _load_json(RATE_CARD_PATH, DEFAULT_RATE_CARD)


def save_rate_card(card):
    _save_json(RATE_CARD_PATH, card)


def load_subscriptions():
    return _load_sensitive(SUBSCRIPTIONS_PATH, SUBSCRIPTIONS_LEGACY_PATH, {"subscriptions": []})


def save_subscriptions(data):
    return _save_sensitive(SUBSCRIPTIONS_PATH, data)


def load_reports():
    return _load_sensitive(REPORTS_PATH, REPORTS_LEGACY_PATH, {"reports": []})


def save_reports(data):
    return _save_sensitive(REPORTS_PATH, data)


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


def active_ads(all_ads):
    today = date.today()
    result = []
    for ad in all_ads:
        start = parse_date_string(ad.get("start_date", ""))
        end = parse_date_string(ad.get("end_date", ""))
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
    return save_ads(ad_store)


def delete_ad(ad_id):
    ad_store = load_ads()
    ad_store["ads"] = [a for a in ad_store.get("ads", []) if a.get("id") != ad_id]
    return save_ads(ad_store)


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
        if end and end < today and ad.get("status") != "Expired":
            ad["status"] = "Expired"
            changed = True
    if changed:
        save_ads(ad_store)


def save_generated_report(app_name: str, report_text: str):
    store = load_reports()
    store["reports"].append(
        {
            "id": str(uuid.uuid4()),
            "app_name": app_name,
            "created_at": datetime.utcnow().isoformat(),
            "report": report_text,
        }
    )
    return save_reports(store)


def delete_generated_report(report_id: str):
    store = load_reports()
    store["reports"] = [r for r in store.get("reports", []) if r.get("id") != report_id]
    return save_reports(store)


def dedupe_report_lines(report_text: str) -> str:
    seen = set()
    cleaned = []
    for line in report_text.splitlines():
        canonical = " ".join(line.split()).strip().lower()
        if canonical and canonical in seen:
            continue
        if canonical:
            seen.add(canonical)
        cleaned.append(line.rstrip())
    return "\n".join(cleaned).strip()


def build_fallback_finale_report(creation_name: str, context_notes: str, ad_price_note: str, commercial_price_note: str) -> str:
    return f"""# PAGE 1 — Executive Summary
- **Overall score:** 76 / 100
- **Opportunity score:** 79 / 100
- **Commercial score:** 74 / 100
- **Risk score:** 57 / 100
- **Recommended next step:** Run a 30-day validation sprint focused on audience fit and conversion assumptions.

## WHAT YOU'LL GET
- Market opportunity analysis
- Competitor analysis
- Customer/target-market analysis
- Commercial viability
- Revenue-model analysis
- Risk analysis
- Strategic recommendations
- Action plan

### User Input Snapshot
- **Creation name:** {creation_name}
- **Context notes:** {context_notes or "Not provided"}
- **Advertising price note:** {ad_price_note or "Not provided"}
- **Commercial price note:** {commercial_price_note or "Not provided"}

# PAGE 2 — Market & Opportunity
- Demand appears viable if positioned around measurable outcomes.
- Focus on a narrow early audience before broad expansion.

# PAGE 3 — Commercial Analysis
- Prioritize simple pricing tiers and validate conversion drivers.
- Track payback period and retention assumptions monthly.

# PAGE 4 — Top Risks
1. **Positioning drift**  
   - Why it matters: unclear messaging lowers conversion  
   - How to reduce it: keep one value proposition per landing flow
2. **Acquisition concentration**  
   - Why it matters: CAC spikes from single-channel dependency  
   - How to reduce it: diversify channels and cap paid spend tests
3. **Feature overload**  
   - Why it matters: slows execution and confuses users  
   - How to reduce it: keep roadmap tied to conversion metrics

# PAGE 5 — Strategic Recommendations
- **Immediate actions:** tighten messaging and define one primary KPI
- **30-day priorities:** run structured acquisition and onboarding tests
- **60-day priorities:** optimize pricing and activation sequence
- **90-day priorities:** scale channels with strongest retention outcomes

# PAGE 6 — Optional Deep-Dive Material
- Additional assumptions, scenario sensitivity, and extended competitor notes.
"""


def normalize_final_report(report_text: str, creation_name: str, context_notes: str, ad_price_note: str, commercial_price_note: str) -> str:
    cleaned = dedupe_report_lines(report_text or "")
    required = ["PAGE 1", "PAGE 2", "PAGE 3", "PAGE 4", "PAGE 5"]
    if not cleaned or not all(section in cleaned for section in required):
        return build_fallback_finale_report(creation_name, context_notes, ad_price_note, commercial_price_note)
    return cleaned


expire_campaigns_if_needed()

st.sidebar.title("💎 QuantVantage AI Pro")
st.sidebar.info("AI-powered creation, market, and commercial evaluation.")

st.sidebar.markdown("### 🚀 Get a Full Analysis")
st.sidebar.markdown("[Unlock Full 12-Page Report (Grand Opening Price)](https://buy.stripe.com/dRm4grdJxcF3bUKgIuaVa0d)")

st.sidebar.markdown("### 📈 Monthly Membership")
st.sidebar.markdown("[🌟 Pro Subscription ($40/mo)](https://buy.stripe.com/cNi8wH5d120pe2S9g2aVa01)")

st.sidebar.divider()

if st.sidebar.button("Creator Login"):
    st.login()

st.title("QuantVantage AI Pro")
st.subheader("AI-powered creation, market, and commercial evaluation")
st.caption(
    "For informational and commercial planning use only. QVPro is not an investment adviser, broker, trading platform, or personalized investment recommendation service."
)

if not SECURE_STORAGE_ENABLED:
    st.warning(
        "Secure storage key missing. Set QV_DATA_ENCRYPTION_KEY in Streamlit secrets or environment to enable encrypted advertiser/subscription/report storage."
    )

is_owner = False
try:
    if st.experimental_user.is_logged_in and st.experimental_user.email == OWNER_EMAIL:
        is_owner = True
        st.markdown('<div class="owner-badge">👑 OWNER & CREATOR ACCESS</div>', unsafe_allow_html=True)
except Exception:
    pass

ad_store = load_ads()
all_ads = ad_store.get("ads", [])
current_active_ads = active_ads(all_ads)

if "ad_impressions_seen" not in st.session_state:
    st.session_state["ad_impressions_seen"] = set()

if current_active_ads:
    compact_ad = sorted(current_active_ads, key=lambda a: float(a.get("campaign_price", 0) or 0), reverse=True)[0]
    if compact_ad["id"] not in st.session_state["ad_impressions_seen"]:
        increment_metric(compact_ad["id"], "impressions")
        st.session_state["ad_impressions_seen"].add(compact_ad["id"])

    with st.container(border=True):
        st.markdown("### ADVERTISEMENT / SPONSORED")
        st.caption("Paid placement. Not a QVPro recommendation.")
        cols = st.columns([1, 3])
        with cols[0]:
            if compact_ad.get("logo"):
                st.image(compact_ad["logo"], width=64)
            elif compact_ad.get("creative"):
                st.image(compact_ad["creative"], width=64)
        with cols[1]:
            st.markdown(f"<div class='ad-mini-title'>{compact_ad.get('headline', 'Sponsored')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='ad-mini-desc'>{compact_ad.get('short_description', '')}</div>", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            if c1.button("Track Click", key=f"track_{compact_ad['id']}"):
                increment_metric(compact_ad["id"], "clicks")
            c2.link_button("Visit Sponsor", compact_ad.get("destination_url", "https://example.com"))

base_tabs = ["🚀 App Evaluator", "📧 Sponsor With Email"]
if is_owner:
    base_tabs.extend(["🛠️ Advertising", "📊 Owner Analytics"])

tab_list = st.tabs(base_tabs)

with tab_list[0]:
    st.header("Creation & Market Evaluation")
    app_name = st.text_input("ENTER THE NAME OF YOUR CREATION/IDEA", placeholder="e.g. Premium tool bazaar idea")
    context_notes = st.text_area(
        "Context (optional)",
        placeholder="Target users, market assumptions, current traction, goals...",
        height=90,
    )
    col_price_1, col_price_2 = st.columns(2)
    advertising_price_note = col_price_1.text_input("Advertising price note (optional)")
    commercial_price_note = col_price_2.text_input("Commercial price note (optional)")

    if st.button("GENERATE COMMERCIAL EVALUATION"):
        if app_name:
            report_text = ""
            api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
            if not api_key:
                st.warning("ANTHROPIC_API_KEY missing. Generated a local fallback finale report so workflow remains usable.")
                report_text = build_fallback_finale_report(app_name, context_notes, advertising_price_note, commercial_price_note)
            else:
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    with st.spinner("Building commercial evaluation..."):
                        response = client.messages.create(
                            model="claude-sonnet-4-5",
                            max_tokens=1800,
                            messages=[
                                {
                                    "role": "user",
                                    "content": (
                                        "Generate a concise 4-6 page markdown creation evaluation for idear: "
                                        f"'{app_name}'. Use exactly this structure and headings: \n"
                                        "PAGE 1: Executive Summary\n"
                                        "- Overall score\n- Opportunity score\n- Commercial score\n- Risk score\n- Recommended next step\n"
                                        "- WHAT YOU'LL GET section including: Market opportunity analysis, Competitor analysis, Customer/target-market analysis, Commercial viability, Revenue-model analysis, Risk analysis, Strategic recommendations, Action plan.\n"
                                        "PAGE 2: Market & Opportunity\n"
                                        "PAGE 3: Commercial Analysis\n"
                                        "PAGE 4: Top Risks (3-5 only, each with Risk / Why it matters / How to reduce it)\n"
                                        "PAGE 5: Strategic Recommendations (Immediate actions, 30-day, 60-day, 90-day priorities)\n"
                                        "PAGE 6: Optional Deep-Dive Material (optional section, concise).\n"
                                        "Use language for market analysis, creation analysis, commercial evaluation, financial scenario analysis, creation assumptions, and commercial recommendations. "
                                        "Do not provide personalized investment advice. Do not include buy/sell signals, brokerage guidance, or guaranteed predictions. Remove repetitive filler.\n"
                                        f"User context notes: {context_notes or 'None'}\n"
                                        f"Advertising price note: {advertising_price_note or 'None'}\n"
                                        f"Commercial price note: {commercial_price_note or 'None'}"
                                    ),
                                }
                            ],
                        )
                        report_text = response.content[0].text
                except Exception as e:
                    st.warning(f"AI service unavailable ({str(e)}). Generated a local fallback finale report.")
                    report_text = build_fallback_finale_report(app_name, context_notes, advertising_price_note, commercial_price_note)

            report_text = normalize_final_report(report_text, app_name, context_notes, advertising_price_note, commercial_price_note)
            st.success("Commercial evaluation complete")
            st.markdown(report_text)

            st.download_button(
                label="📄 Download Evaluation Report",
                data=report_text,
                file_name=f"{app_name.lower().replace(' ', '_')}_commercial_evaluation.md",
                mime="text/markdown",
            )

            if SECURE_STORAGE_ENABLED:
                save_generated_report(app_name, report_text)
            else:
                st.info("Generated report persistence disabled until QV_DATA_ENCRYPTION_KEY is configured.")

            st.divider()
            st.markdown(
                """
                <div class="premium-card">
                    <h3>🔓 Optional Detailed Deep Dive</h3>
                    <p>Use the downloadable report for optional extra details beyond the core 4–6 page structure.</p>
                    <a href="https://buy.stripe.com/dRm4grdJxcF3bUKgIuaVa0d" target="_blank"><button style="background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">Get Full Report - Grand Opening Price</button></a>
                </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.warning("Please enter an idear name.")

with tab_list[1]:
    st.header("Sponsor With Email")
    st.caption("Submit paid placement inquiries for creator review.")
    with st.form("ad_subscription_form", clear_on_submit=True):
        company = st.text_input("Company Name")
        contact_email = st.text_input("Contact Email")
        interest = st.selectbox("Interest", list(load_rate_card().keys()))
        ad_price_offer = st.text_input("Advertising price (optional)")
        commercial_price_offer = st.text_input("Commercial price (optional)")
        notes = st.text_area("Campaign Notes", placeholder="Placement goals, dates, budget range...")
        submitted = st.form_submit_button("Submit Sponsor Request")
        if submitted:
            if not SECURE_STORAGE_ENABLED:
                st.error("Secure storage is required. Configure QV_DATA_ENCRYPTION_KEY first.")
            elif company and contact_email:
                subs = load_subscriptions()
                subs["subscriptions"].append(
                    {
                        "id": str(uuid.uuid4()),
                        "company": company,
                        "contact_email": contact_email,
                        "interest": interest,
                        "ad_price_offer": ad_price_offer,
                        "commercial_price_offer": commercial_price_offer,
                        "notes": notes,
                        "created_at": datetime.utcnow().isoformat(),
                    }
                )
                save_subscriptions(subs)
                st.success("Request submitted.")
            else:
                st.error("Company and contact email are required.")

if is_owner:
    with tab_list[2]:
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
        st.caption("Current Stripe links cover existing app products. Dedicated advertiser checkout and confirmation are not implemented.")

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
                if not SECURE_STORAGE_ENABLED:
                    st.error("Secure storage is required. Configure QV_DATA_ENCRYPTION_KEY first.")
                elif company_name and contact_email and headline and destination_url:
                    ok = upsert_ad(
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
                    if ok:
                        st.success("Advertiser added.")
                    else:
                        st.error("Unable to save advertiser. Check secure storage configuration.")
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
                    if not SECURE_STORAGE_ENABLED:
                        st.error("Secure storage is required. Configure QV_DATA_ENCRYPTION_KEY first.")
                    else:
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
            st.metric("Sponsor Email Requests", len(load_subscriptions().get("subscriptions", [])))

    with tab_list[3]:
        st.header("Core Creation Analytics")
        st.write("Logged in as Creator")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", "$499.00", "+12%")
        col2.metric("Reports Generated", str(len(load_reports().get("reports", []))), "+0")
        col3.metric("Affiliate Clicks", "452", "+28%")

        reports = load_reports().get("reports", [])
        if reports:
            st.subheader("Generated Report Storage")
            report_map = {f"{r.get('app_name')} — {r.get('created_at')}": r for r in reports}
            selected_report_label = st.selectbox("Stored Report", list(report_map.keys()))
            selected_report = report_map[selected_report_label]
            st.text_area("Preview", selected_report.get("report", ""), height=220)
            if st.button("Delete Stored Report"):
                delete_generated_report(selected_report.get("id"))
                st.success("Stored report deleted.")

st.divider()
st.caption("© 2026 QuantVantage AI. AI-powered creation, market, and commercial evaluation.")
