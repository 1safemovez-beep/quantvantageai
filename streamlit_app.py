# QuantVantage AI Pro - Analytical Engine
# Build Version: 2026-09-13-RISK-REDUCTION
import base64
import json
import os
import re
import requests
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
    h1 { white-space: nowrap; }
    @media (max-width: 640px) { h1 { font-size: 1.35rem !important; } }
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


def extract_scores(report_text: str) -> dict:
    """Pull the four headline scores out of a report so they can be charted."""
    scores = {}
    patterns = {
        "Overall": r"Overall score:\*?\*?\s*(\d+)",
        "Opportunity": r"Opportunity score:\*?\*?\s*(\d+)",
        "Commercial": r"Commercial score:\*?\*?\s*(\d+)",
        "Risk": r"Risk score:\*?\*?\s*(\d+)",
    }
    for label, pat in patterns.items():
        m = re.search(pat, report_text or "")
        if m:
            try:
                scores[label] = int(m.group(1))
            except ValueError:
                pass
    return scores if len(scores) == 4 else {}


def build_fallback_finale_report(creation_name: str, context_notes: str, ad_price_note: str, commercial_price_note: str) -> str:
    name = (creation_name or "").strip()
    notes = (context_notes or "").strip()
    thin_input = len(name) < 12 and not notes
    if thin_input:
        overall, opportunity, commercial, risk = 22, 25, 20, 70
        next_step = "Describe what the creation actually does, who it serves, and how it earns money, then re-run the evaluation."
        missing = "The input was too thin to evaluate properly — a name or URL alone is not an idea. "
        financial = ("- No financial picture is possible yet — there is not enough detail to estimate costs, "
                     "pricing, or revenue. Describe the idea and re-run the evaluation.")
        risks = ("1. \U0001F534 **Too little information**\n"
                 "   - Why it matters: nothing here can be priced, scoped, or validated\n"
                 "   - How to reduce it: describe the creation, its buyer, and how it earns money")
    else:
        overall, opportunity, commercial, risk = 62, 65, 60, 55
        next_step = "Run a 30-day validation sprint focused on audience fit and conversion assumptions."
        missing = ""
        try:
            price = float((commercial_price_note or "").strip().replace("$", "").replace(",", "") or 25)
        except ValueError:
            price = 25.0
        price_s = f"${price:,.0f}" if price == int(price) else f"${price:,.2f}"
        cons_rev = int(1000 * 0.01 * price)
        base_rev = int(5000 * 0.02 * price)
        opt_rev = int(20000 * 0.03 * price)
        financial = (
            f"- **Estimated startup cost range:** $2,000 - $8,000 (lean build, first marketing tests, basic tooling).\n"
            f"- **Revenue scenarios** (audience reached x conversion x {price_s} price point):\n"
            f"  - Conservative: 1,000 x 1% x {price_s} = **${cons_rev:,}/mo** (~${cons_rev * 12:,}/yr)\n"
            f"  - Base: 5,000 x 2% x {price_s} = **${base_rev:,}/mo** (~${base_rev * 12:,}/yr)\n"
            f"  - Optimistic: 20,000 x 3% x {price_s} = **${opt_rev:,}/mo** (~${opt_rev * 12:,}/yr)\n"
            f"- **Break-even sketch:** at the base case, roughly 300-400 paying customers cover a lean $5,000 launch.\n"
            f"- **Possible levers (not promises):** if acquisition cost fell 20% and buyers purchased twice a year instead of once, "
            f"base-case revenue could roughly double and margin could rise from ~40% toward ~60%. Possible — not guaranteed."
        )
        risks = ("1. \U0001F534 **Acquisition concentration**\n"
                 "   - Why it matters: CAC spikes from single-channel dependency\n"
                 "   - How to reduce it: diversify channels and cap paid spend tests\n"
                 "2. \U0001F7E1 **Positioning drift**\n"
                 "   - Why it matters: unclear messaging lowers conversion\n"
                 "   - How to reduce it: keep one value proposition per landing flow\n"
                 "3. \U0001F7E1 **Feature overload**\n"
                 "   - Why it matters: slows execution and confuses users\n"
                 "   - How to reduce it: keep roadmap tied to conversion metrics")
    return f"""# PAGE 1 — Executive Summary
- **Overall score:** {overall} / 100
- **Opportunity score:** {opportunity} / 100
- **Commercial score:** {commercial} / 100
- **Risk score:** {risk} / 100
- **Recommended next step:** {missing}{next_step}

## WHAT YOU'LL GET
- Market opportunity analysis
- Competitor analysis
- Customer/target-market analysis
- Commercial viability
- Revenue-model analysis
- Financial scenario analysis (costs, revenue scenarios, break-even, possible levers)
- Risk analysis (ranked \U0001F534 critical / \U0001F7E1 moderate)
- Strategic recommendations
- Action plan
- Possible value estimate (rough planning estimate, not a valuation)

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

## Financial picture
{financial}

# PAGE 4 — Top Risks
{risks}

# PAGE 5 — Strategic Recommendations
- **Immediate actions:** tighten messaging and define one primary KPI
- **30-day priorities:** run structured acquisition and onboarding tests
- **60-day priorities:** optimize pricing and activation sequence
- **90-day priorities:** scale channels with strongest retention outcomes

# PAGE 6 — Optional Deep-Dive Material
- Additional assumptions, scenario sensitivity, and extended competitor notes.

# PAGE 7 — Possible Value Estimate
- **Rough estimate:** $5,000 - $25,000 at small-scale launch
- **Because:** this assumes a narrow early audience, a modest price point, and low single-digit conversion on first outreach. A rough planning estimate only — not a professional valuation, not a guarantee, not investment advice.
"""


def normalize_final_report(report_text: str, creation_name: str, context_notes: str, ad_price_note: str, commercial_price_note: str) -> str:
    cleaned = dedupe_report_lines(report_text or "")
    # Lenient structure check: accept "page 1" in any letter case.
    lowered = cleaned.lower()
    required = ["page 1", "page 2", "page 3", "page 4", "page 5", "page 7"]
    if cleaned and all(section in lowered for section in required):
        return cleaned
    # Never silently throw away a real AI response: if the model returned
    # substantial content, keep it even if its headings drifted from the template.
    if len(cleaned.strip()) >= 800:
        return cleaned
    return build_fallback_finale_report(creation_name, context_notes, ad_price_note, commercial_price_note)


expire_campaigns_if_needed()

st.sidebar.title("💎 QuantVantage AI Pro")
st.sidebar.info("AI-powered creation, market, and commercial evaluation.")

st.sidebar.markdown("### 🚀 Get a Full Analysis")
st.sidebar.markdown("[Unlock Full 12-Page Report (Grand Opening Price)](https://buy.stripe.com/dRm4grdJxcF3bUKgIuaVa0d)")


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
if "qv_unlocked" not in st.session_state:
    st.session_state["qv_unlocked"] = False

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

STRIPE_FULL_REPORT_URL = "https://buy.stripe.com/dRm4grdJxcF3bUKgIuaVa0d"


def verify_stripe_payment(email):
    """Return True if Stripe shows a completed (paid) checkout session for this email.

    Payment Links create checkout sessions, so we list recent sessions and match
    on the customer email. Used to unlock the full report after purchase.
    """
    try:
        secret = st.secrets.get("STRIPE_SECRETS_KEY", "")
    except Exception:
        secret = ""
    email = (email or "").strip().lower()
    if not secret or not email:
        return False
    try:
        resp = requests.get(
            "https://api.stripe.com/v1/checkout/sessions",
            auth=(secret, ""),
            params={"limit": 100},
            timeout=20,
        )
        if resp.status_code != 200:
            return False
        for sess in resp.json().get("data", []):
            details = sess.get("customer_details") or {}
            if (details.get("email") or "").strip().lower() == email and sess.get("payment_status") == "paid":
                return True
    except Exception:
        return False
    return False


tab_list = st.tabs(base_tabs)

with tab_list[0]:
    st.header("Creation & Market Evaluation")
    app_name = st.text_input("ENTER Business NAME,URL or YOUR CREATION/IDEA", placeholder="e.g. Premium tool bazaar idea")
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
                            max_tokens=2400,
                            messages=[
                                {
                                    "role": "user",
                                    "content": (
                                        "Generate a concise 6-8 page markdown creation evaluation for idea: "
                                        f"'{app_name}'. Use exactly this structure and headings: \n"
                                        "PAGE 1: Executive Summary\n"
                                        "- Overall score\n- Opportunity score\n- Commercial score\n- Risk score\n- Recommended next step\n"
                                        "- WHAT YOU'LL GET section including: Market opportunity analysis, Competitor analysis, Customer/target-market analysis, Commercial viability, Revenue-model analysis, Risk analysis, Strategic recommendations, Action plan, Financial scenario analysis, Possible value estimate (rough planning estimate, not a valuation).\n"
                                        "PAGE 2: Market & Opportunity\n"
                                        "PAGE 3: Commercial Analysis\n"
"Include a Financial picture subsection: estimated startup cost range; three revenue scenarios (conservative/base/optimistic) showing the math as audience x conversion x price; a break-even sketch; and 2 possible levers (e.g. if acquisition cost fell 20%, show how margin moves) framed as possibilities, never guarantees.\n"
                                        "PAGE 4: Top Risks (3-5 only, ranked with \U0001F534 Critical / \U0001F7E1 Moderate indicators, each with Risk / Why it matters / How to reduce it)\n"
                                        "PAGE 5: Strategic Recommendations (Immediate actions, 30-day, 60-day, 90-day priorities)\n"
                                        "PAGE 6: Optional Deep-Dive Material (optional section, concise).\n"
                                        "PAGE 7: Possible Value Estimate\n"
                                        "- Give one estimated dollar range for what this creation could be worth at a small-scale launch (for example \"$X - $Y\"), then 2-3 sentences beginning with \"because\" that spell out the assumptions behind it (audience size, price point, conversion rate). "
                                        "Tie the range to the scores above: stronger commercial and opportunity scores support a higher range. "
                                        "Label it plainly as a rough planning estimate — never a professional valuation, never a guarantee, never investment advice.\n"
                                        "Use language for market analysis, creation analysis, commercial evaluation, financial scenario analysis, creation assumptions, and commercial recommendations. "
                                        "Do not provide personalized investment advice. Do not include buy/sell signals, brokerage guidance, or guaranteed predictions. Remove repetitive filler.\nSCORING RUBRIC — use the full 0-100 range and make scores discriminate between strong and weak inputs. 90-100: exceptional, clear demand, strong defensibility. 70-89: solid concept with real opportunity and manageable risks. 40-69: plausible but unproven, major assumptions untested. 10-39: weak, vague, or fundamentally flawed concept. 0-9: no evaluable content. Judge the idea AS DESCRIBED, not its best possible version. If the input is only a URL, a company name, or a few words with no description of what the creation does, who it serves, or how it earns money, scores must reflect that: overall score below 30, and state plainly what information is missing. Never default to the middle. Two different ideas must get meaningfully different scores. If every idea scores the same, the scoring has failed.\n"
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

            score_snapshot = extract_scores(report_text)
            if score_snapshot:
                st.subheader("\U0001F4CA Score snapshot")
                st.bar_chart(score_snapshot)

            if st.session_state.get("qv_unlocked"):
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
            else:
                teaser = report_text[:700].rsplit("\n", 1)[0]
                st.markdown(teaser)
                st.markdown("*🔒 The full 6–8 page report is locked. Unlock below to keep reading.*")
                st.divider()
                st.subheader("🔓 Unlock the full report")
                st.markdown(
                    f"<a href=\"{STRIPE_FULL_REPORT_URL}\" target=\"_blank\"><button style=\"background-color: #3E7096; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;\">Get Full Report - Grand Opening Price ($12)</button></a>",
                    unsafe_allow_html=True,
                )
                with st.expander("I already paid — unlock with my payment email"):
                    pay_email = st.text_input("Email used at checkout", key="qv_pay_email")
                    if st.button("Verify payment", key="qv_verify_btn"):
                        if verify_stripe_payment(pay_email):
                            st.session_state["qv_unlocked"] = True
                            st.success("Payment verified — full report unlocked.")
                            st.rerun()
                        else:
                            st.error("No completed payment found for that email. Check the spelling, or finish checkout first.")
                tester_code = ""
                try:
                    tester_code = st.secrets.get("TESTER_CODE", "")
                except Exception:
                    tester_code = ""
                if tester_code:
                    with st.expander("I have a tester code"):
                        code_in = st.text_input("Tester code", key="qv_tester_code", type="password")
                        if st.button("Apply tester code", key="qv_tester_btn"):
                            if code_in.strip() == tester_code:
                                st.session_state["qv_unlocked"] = True
                                st.success("Tester code accepted — full report unlocked.")
                                st.rerun()
                            else:
                                st.error("That code didn't match.")
        else:
            st.warning("Please enter an idea name.")

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
