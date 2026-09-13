import datetime
import json
from pathlib import Path
from uuid import uuid4

class QuantVantageAI:
    def __init__(self, target_name, mode="app"):
        self.target_name = target_name
        self.mode = mode
        self.base_dir = Path(__file__).resolve().parent
        self.registry_path = self.base_dir / "data" / "generated_records.json"
        self.output_dir = self.base_dir / "generated_reports"
        self.last_generated_record = None
        self.report_data = {
            "DATE": datetime.date.today().strftime("%B %d, %Y"),
            "PURCHASE_LINK": "https://buy.stripe.com/bJe4grgVJ5cB1g64ZMaVa0b",
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

    def _load_registry(self):
        registry_file = self.registry_path
        if not registry_file.exists():
            return []

        with registry_file.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, dict):
            return payload.get("records", [])
        return payload

    def _save_registry(self, records):
        registry_file = self.registry_path
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        with registry_file.open("w", encoding="utf-8") as handle:
            json.dump({"records": records}, handle, indent=2)
        return registry_file

    def _resolve_output_directory(self):
        output_directory = self.output_dir
        output_directory.mkdir(parents=True, exist_ok=True)
        return output_directory.resolve()

    def _resolve_output_path(self, filename):
        output_directory = self._resolve_output_directory()
        safe_name = Path(filename).name
        resolved_path = (output_directory / safe_name).resolve()
        if resolved_path.parent != output_directory:
            raise ValueError("Output path must stay within the generated reports directory.")
        return resolved_path

    def _is_managed_output_path(self, candidate_path):
        try:
            Path(candidate_path).resolve().relative_to(self._resolve_output_directory())
            return True
        except ValueError:
            return False

    def _append_record(self, output_path, owner_reference=None, request_id=None):
        records = self._load_registry()
        resolved_output_path = Path(output_path).resolve()
        if not self._is_managed_output_path(resolved_output_path):
            raise ValueError("Output path must stay within the generated reports directory.")
        record = {
            "request_id": request_id or f"qv-{uuid4().hex[:8]}",
            "target_name": self.target_name,
            "mode": self.mode,
            "output_path": str(resolved_output_path),
            "owner_reference": owner_reference or "",
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
        records.append(record)
        self._save_registry(records)
        self.last_generated_record = record
        return record

    def store_generated_output(self, content, extension="txt", owner_reference=None):
        request_id = f"qv-{uuid4().hex[:8]}"
        filename = f"{self.mode}_{request_id}.{extension.lstrip('.')}"
        output_path = self._resolve_output_path(filename)
        output_path.write_text(content, encoding="utf-8")
        return self._append_record(output_path, owner_reference=owner_reference, request_id=request_id)

    def generate_report(self, template_name=None):
        default_template = "report_template.md" if self.mode == "app" else "health_template.md"
        template_name = Path(template_name).name if template_name else default_template
        template_path = (self.base_dir / "templates" / template_name).resolve()
             
        with open(template_path, 'r', encoding="utf-8") as f:
            template = f.read()
        
        for key, value in self.report_data.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
            
        output_name = f"{self.mode}_{uuid4().hex[:8]}_analysis.md"
        abs_path = self._resolve_output_path(output_name)
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

            path = Path(output_path).resolve()
            if not self._is_managed_output_path(path):
                errors.append(f"Refusing to delete unmanaged path '{path}'.")
                continue
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
