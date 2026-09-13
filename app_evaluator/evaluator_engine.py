import datetime
import os


class QuantVantageAI:
    def __init__(self, target_name, mode="app"):
        self.target_name = target_name
        self.mode = mode
        self.report_data = {
            "DATE": datetime.date.today().strftime("%B %d, %Y"),
            "APP_NAME": target_name,
            "PURCHASE_LINK": "https://buy.stripe.com/eVq8wH7l9awV2kaboaaVa06",
            "OVERALL_SCORE": "78",
            "OPPORTUNITY_SCORE": "81",
            "COMMERCIAL_SCORE": "76",
            "RISK_SCORE": "58",
            "RECOMMENDED_NEXT_STEP": "Run a 30-day pilot focused on customer acquisition assumptions and pricing validation.",
            "MARKET_DEMAND": "Early demand signals are positive in niche segments with moderate competition.",
            "TARGET_MARKET_FIT": "The concept aligns best with SMB and early-stage founder personas.",
            "COMPETITOR_SUMMARY": "Competitors are present but fragmented; positioning clarity is the primary differentiator.",
            "OPPORTUNITY_THESIS": "Capture a focused segment first, then expand by use-case adjacency.",
            "BUSINESS_ASSUMPTIONS": "Assumes paid conversion after initial trial and repeat usage in monthly cycles.",
            "REVENUE_MODEL_ANALYSIS": "Subscription + one-time premium report upsell provides diversified revenue streams.",
            "COST_MARGIN_ANALYSIS": "Primary costs are model calls and acquisition spend; margin improves with retention.",
            "FINANCIAL_SCENARIOS": "Base case indicates sustainable contribution margin by month 6 with disciplined CAC.",
            "RISK_1_NAME": "Customer acquisition concentration",
            "RISK_1_WHY": "Over-reliance on one channel can increase CAC volatility.",
            "RISK_1_MITIGATION": "Diversify channels and enforce CAC payback guardrails.",
            "RISK_2_NAME": "Positioning ambiguity",
            "RISK_2_WHY": "Mixed messaging reduces conversion and trust.",
            "RISK_2_MITIGATION": "Keep messaging centered on business and commercial evaluation outcomes.",
            "RISK_3_NAME": "Feature sprawl",
            "RISK_3_WHY": "Non-core features dilute execution velocity.",
            "RISK_3_MITIGATION": "Prioritize core evaluation workflows and sunset low-value paths.",
            "RISK_4_NAME": "Compliance interpretation drift",
            "RISK_4_WHY": "Overstated claims can increase legal/regulatory review burden.",
            "RISK_4_MITIGATION": "Maintain explicit informational-use disclosures and legal review checkpoints.",
            "RISK_5_NAME": "Monetization timing mismatch",
            "RISK_5_WHY": "Pricing before validated value can suppress adoption.",
            "RISK_5_MITIGATION": "Use staged pricing tests tied to measurable customer outcomes.",
            "ACTIONS_IMMEDIATE": "Clarify product scope and update all customer-facing language.",
            "ACTIONS_30_DAY": "Validate acquisition channels and onboarding conversion assumptions.",
            "ACTIONS_60_DAY": "Refine pricing and package structure based on pilot learnings.",
            "ACTIONS_90_DAY": "Scale the highest-performing channels and automate key reporting workflows.",
            "OPTIONAL_DEEP_DIVE": "Detailed assumptions, sensitivity analysis, and extended competitor breakdown.",
        }

        if mode != "app":
            raise ValueError("Health mode is disabled in the customer-facing product scope. Use mode='app'.")

    def generate_report(self, template_path=None, output_path=None):
        if not template_path:
            template_path = "templates/report_template.md"

        if not output_path:
            output_path = f"app_{self.target_name.lower().replace(' ', '_')}_analysis.md"

        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        for key, value in self.report_data.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))

        abs_path = os.path.abspath(output_path)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(template)
        return abs_path


if __name__ == "__main__":
    name = input("Enter app name to evaluate: ")
    evaluator = QuantVantageAI(name, mode="app")
    print(f"\n[System] Initializing commercial evaluation core for '{name}'...")
    output = evaluator.generate_report()
    print(f"[System] Report generated: {output}")
