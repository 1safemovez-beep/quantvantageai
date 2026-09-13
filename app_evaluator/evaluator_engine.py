import datetime
import json
from pathlib import Path
from uuid import uuid4

class QuantVantageAI:
    def __init__(self, target_name, mode="app", registry_path=None, output_dir=None):
        self.target_name = target_name
        self.mode = mode
        self.base_dir = Path(__file__).resolve().parent
        self.registry_path = Path(registry_path) if registry_path else self.base_dir / "data" / "generated_records.json"
        self.output_dir = Path(output_dir) if output_dir else self.base_dir / "generated_reports"
        self.last_generated_record = None
        self.report_data = {
            "DATE": datetime.date.today().strftime("%B %d, %Y"),
            "PURCHASE_LINK": "https://buy.stripe.com/eVq8wH7l9awV2kaboaaVa06",
        }
        
        if mode == "app":
            self.report_data.update({
                "APP_NAME": target_name,
                "MARKET_STATUS": "Analyzing...",
                "CORE_FEATURES": "",
                "REVENUE_MODEL": "",
                "INCOME_FREQUENCY": "",
                "INCOME_PROJECTION": "",
                "COMPETITOR_TABLE": "| App | Similarity | Better Method? |\n| :--- | :--- | :--- |\n",
                "SIMILARITIES": "",
                "DIFFERENCES": "",
                "UNIQUENESS_SCORE": "0",
                "ACTIVITY_LEVEL": "",
                "CAGR": "",
                "NET_WORTH_EVALUATION": "",
                "BEST_CASE": "",
                "WORST_CASE": "",
                "RECOMMENDATION": "",
                "DOWNLOAD_LINK": "#",
                "DONATE_LINK": "https://www.buymeacoffee.com/yourhandle",
                "SUBSCRIPTION_LINK": "https://buy.stripe.com/cNi8wH5d120pe2S9g2aVa01",
                "AFFILIATE_NAME": "Top AI Tools Directory",
                "AFFILIATE_URL": "https://example.com/affiliate",
                "AFFILIATE_DESC": "Get 20% off the best AI tools for app development.",
                "PROFIT_MARGIN": "0",
                "EST_CAC": "0.00",
                "BREAK_EVEN_UNITS": "0",
                "PROFIT_OUTLOOK": "Analyzing...",
                "TECH_STACK_COST": "",
                "MONETIZATION_HACKS": "",
                "VIRAL_SCORE": "0",
                "UX_IMPROVEMENT": "",
                "TRUST_IMPROVEMENT": "",
                "PERFORMANCE_IMPROVEMENT": "",
                "BETTER_CHOICE_SUMMARY": ""
            })
        elif mode == "health":
            self.report_data.update({
                "SUBJECT_NAME": target_name,
                "RESPIRATORY_METRICS": "Analyzing physiological optics...",
                "PHYSIOLOGICAL_TRENDS": "Identifying core patterns...",
                "BASELINE_DATA": "Standardized respiratory metrics...",
                "HEALTH_INSIGHTS_BODY": "AI-powered physiological synthesis...",
                "IMMEDIATE_ACTION": "Optimization adjustments...",
                "LONG_TERM_ROADMAP": "Tactical health stability...",
                "VITALITY_SCORE": "0"
            })

    def _slugify(self, value):
        normalized = "".join(char.lower() if char.isalnum() else "_" for char in str(value))
        return normalized.strip("_") or "report"

    def _load_registry(self, registry_path=None):
        registry_file = Path(registry_path) if registry_path else self.registry_path
        if not registry_file.exists():
            return []

        with registry_file.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, dict):
            return payload.get("records", [])
        return payload

    def _save_registry(self, records, registry_path=None):
        registry_file = Path(registry_path) if registry_path else self.registry_path
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        with registry_file.open("w", encoding="utf-8") as handle:
            json.dump({"records": records}, handle, indent=2)
        return registry_file

    def _append_record(self, output_path, owner_reference=None, registry_path=None, request_id=None):
        registry_file = Path(registry_path) if registry_path else self.registry_path
        records = self._load_registry(registry_file)
        record = {
            "request_id": request_id or f"qv-{uuid4().hex[:8]}",
            "target_name": self.target_name,
            "mode": self.mode,
            "output_path": str(Path(output_path).resolve()),
            "owner_reference": owner_reference or "",
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
        records.append(record)
        self._save_registry(records, registry_file)
        self.last_generated_record = record
        return record

    def store_generated_output(self, content, extension="txt", owner_reference=None, output_dir=None, registry_path=None):
        output_directory = Path(output_dir) if output_dir else self.output_dir
        output_directory.mkdir(parents=True, exist_ok=True)
        request_id = f"qv-{uuid4().hex[:8]}"
        filename = f"{self.mode}_{self._slugify(self.target_name)}_{request_id}.{extension.lstrip('.')}"
        output_path = output_directory / filename
        output_path.write_text(content, encoding="utf-8")
        return self._append_record(output_path, owner_reference=owner_reference, registry_path=registry_path, request_id=request_id)

    def generate_report(self, template_path=None, output_path=None):
        if not template_path:
            template_path = "templates/report_template.md" if self.mode == "app" else "templates/health_template.md"
        
        if not output_path:
            prefix = "app" if self.mode == "app" else "health"
            output_path = f"{prefix}_{self.target_name.lower().replace(' ', '_')}_analysis.md"
            
        with open(template_path, 'r', encoding="utf-8") as f:
            template = f.read()
        
        for key, value in self.report_data.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
            
        abs_path = Path(output_path).resolve()
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        with open(abs_path, 'w', encoding="utf-8") as f:
            f.write(template)
        self._append_record(abs_path)
        return str(abs_path)

    def delete_customer(self, stripe_customer_id):
        """
        Delete locally stored generated report data associated with a reference.
        """
        customer_reference = str(stripe_customer_id).strip()
        if not customer_reference:
            return {
                "id": stripe_customer_id,
                "deleted": False,
                "deleted_records": 0,
                "deleted_files": 0,
                "files_deleted": [],
                "missing_files": [],
                "errors": ["A deletion reference is required."],
            }

        remaining_records = []
        matched_records = []
        for record in self._load_registry():
            output_path = record.get("output_path", "")
            record_reference = str(record.get("request_id", "")).strip()
            owner_reference = str(record.get("owner_reference", "")).strip()
            output_name = Path(output_path).name if output_path else ""

            if customer_reference in {record_reference, owner_reference, output_path, output_name}:
                matched_records.append(record)
            else:
                remaining_records.append(record)

        if not matched_records:
            return {
                "id": customer_reference,
                "deleted": False,
                "deleted_records": 0,
                "deleted_files": 0,
                "files_deleted": [],
                "missing_files": [],
                "errors": [f"No generated data found for reference '{customer_reference}'."],
            }

        files_deleted = []
        missing_files = []
        errors = []
        for record in matched_records:
            output_path = record.get("output_path")
            if not output_path:
                continue

            path = Path(output_path)
            if path.exists() and path.is_file():
                path.unlink()
                files_deleted.append(str(path))
            elif path.exists():
                errors.append(f"Unable to delete non-file path '{path}'.")
            else:
                missing_files.append(str(path))

        self._save_registry(remaining_records)
        return {
            "id": customer_reference,
            "deleted": not errors,
            "deleted_records": len(matched_records),
            "deleted_files": len(files_deleted),
            "files_deleted": files_deleted,
            "missing_files": missing_files,
            "errors": errors,
        }

if __name__ == "__main__":
    mode = input("Select mode (app/health): ").strip().lower()
    name = input(f"Enter the {'app name' if mode == 'app' else 'subject name'} to evaluate: ")
    evaluator = QuantVantageAI(name, mode=mode)
    print(f"\n[System] Initializing Core for '{name}' (Mode: {mode})...")
    print("[System] Searching for metrics and optics...")
    # In a full app, this would call search/sensor APIs. 
    print("[System] Analysis complete. Generating report...")
    output = evaluator.generate_report()
    print(f"[System] Report generated: {output}")
