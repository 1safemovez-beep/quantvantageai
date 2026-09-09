# 🚀 QuantVantage AI Prototype

This tool automates the process of market research, competitive analysis, and financial projection for any app.

## 💳 Stripe & Mobile Integration

### Stripe Payment Link:
1. Go to your **Stripe Dashboard** -> **Payment Links**.
2. Create a new link for "$4.99 - QuantVantage Report".
3. Copy the URL and paste it into the `PURCHASE_LINK` field in `evaluator_engine.py`.

### Mobile Usage:
- The app is a **Web-App** (PWA compatible). 
- To use as a mobile app, users simply "Add to Home Screen" on iOS/Android.
- The `landing_page.html` is fully responsive for small screens.

### Features:
- **Print**: Uses the device's native print-to-PDF functionality.
- **Share**: Uses the **Web Share API** (native mobile sharing tray).
- **Save to Drive**: Provides a direct link to the user's cloud storage.

## Files:
- `evaluator_engine.py`: The core logic for data synthesis.
- `templates/report_template.md`: The standardized reporting format.
- `[app_name]_evaluation.md`: The final generated deliverable.

---
*Created for analytical market intelligence.*
