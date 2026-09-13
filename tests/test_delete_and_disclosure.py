import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STREAMLIT_FILES = [
    ROOT / "streamlit_app.py",
    ROOT / "examples" / "streamlit_app.py",
    ROOT / "quantvantage_v3" / "streamlit_app.py",
    ROOT / "quantvantage_v3" / "examples" / "streamlit_app.py",
]
MIRRORED_FILES = [
    ("app_evaluator/marketing/admin_dashboard.html", "quantvantage_v3/app_evaluator/marketing/admin_dashboard.html"),
    ("app_evaluator/marketing/landing_page.html", "quantvantage_v3/app_evaluator/marketing/landing_page.html"),
    ("app_evaluator/marketing/support.html", "quantvantage_v3/app_evaluator/marketing/support.html"),
    ("app_evaluator/legal/terms_of_service.md", "quantvantage_v3/app_evaluator/legal/terms_of_service.md"),
    ("app_evaluator/legal/privacy_policy.md", "quantvantage_v3/app_evaluator/legal/privacy_policy.md"),
    ("app_evaluator/evaluator_engine.py", "quantvantage_v3/app_evaluator/evaluator_engine.py"),
]
ENGINE_PATHS = [
    ROOT / "app_evaluator" / "evaluator_engine.py",
    ROOT / "quantvantage_v3" / "app_evaluator" / "evaluator_engine.py",
]


def load_engine(engine_path):
    spec = importlib.util.spec_from_file_location(engine_path.stem, engine_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DeleteAndDisclosureTests(unittest.TestCase):
    def test_disclosure_and_delete_controls_exist_in_streamlit_apps(self):
        for file_path in STREAMLIT_FILES:
            content = file_path.read_text(encoding="utf-8")
            self.assertIn("Important disclosure", content, str(file_path))
            self.assertIn("Delete My Data", content, str(file_path))
            self.assertIn("Deletion reference", content, str(file_path))

    def test_marketing_pages_include_privacy_and_delete_guidance(self):
        landing = (ROOT / "app_evaluator" / "marketing" / "landing_page.html").read_text(encoding="utf-8")
        admin = (ROOT / "app_evaluator" / "marketing" / "admin_dashboard.html").read_text(encoding="utf-8")
        support = (ROOT / "app_evaluator" / "marketing" / "support.html").read_text(encoding="utf-8")

        self.assertIn("Important Disclosure", landing)
        self.assertIn("Request Data Deletion", landing)
        self.assertIn("../legal/privacy_policy.md", landing)
        self.assertIn("deleteTransaction(this)", admin)
        self.assertIn("action-status", admin)
        self.assertIn("Data Deletion Request", support)
        self.assertIn("privacy_policy.md", support)

    def test_mirrored_files_are_synchronized(self):
        for left, right in MIRRORED_FILES:
            left_path = ROOT / left
            right_path = ROOT / right
            self.assertEqual(
                left_path.read_text(encoding="utf-8"),
                right_path.read_text(encoding="utf-8"),
                f"{left_path} and {right_path} diverged",
            )

    def test_delete_customer_removes_generated_data(self):
        for engine_path in ENGINE_PATHS:
            engine_module = load_engine(engine_path)
            with self.subTest(engine=str(engine_path)):
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_root = Path(temp_dir)
                    evaluator = engine_module.QuantVantageAI(
                        "Demo Venture",
                        registry_path=temp_root / "data" / "generated_records.json",
                        output_dir=temp_root / "generated_reports",
                    )
                    record = evaluator.store_generated_output("classified report body", owner_reference="buyer@example.com")
                    generated_path = Path(record["output_path"])

                    self.assertTrue(generated_path.exists())
                    result = evaluator.delete_customer(record["request_id"])

                    self.assertTrue(result["deleted"])
                    self.assertEqual(result["deleted_records"], 1)
                    self.assertEqual(result["deleted_files"], 1)
                    self.assertFalse(generated_path.exists())

                    registry_payload = json.loads((temp_root / "data" / "generated_records.json").read_text(encoding="utf-8"))
                    self.assertEqual(registry_payload["records"], [])

    def test_delete_customer_handles_missing_reference(self):
        engine_module = load_engine(ENGINE_PATHS[0])
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            evaluator = engine_module.QuantVantageAI(
                "Demo Venture",
                registry_path=temp_root / "data" / "generated_records.json",
                output_dir=temp_root / "generated_reports",
            )

            blank_result = evaluator.delete_customer("")
            self.assertFalse(blank_result["deleted"])
            self.assertIn("deletion reference is required", blank_result["errors"][0].lower())

            missing_result = evaluator.delete_customer("missing-reference")
            self.assertFalse(missing_result["deleted"])
            self.assertIn("No generated data found", missing_result["errors"][0])

    def test_delete_customer_rejects_unmanaged_paths(self):
        engine_module = load_engine(ENGINE_PATHS[0])
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            registry_path = temp_root / "data" / "generated_records.json"
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            registry_path.write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "request_id": "qv-badpath",
                                "target_name": "Unsafe",
                                "mode": "app",
                                "output_path": str((temp_root / ".." / "outside.txt").resolve()),
                                "owner_reference": "",
                                "created_at": "2026-09-13T00:00:00Z",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            evaluator = engine_module.QuantVantageAI(
                "Demo Venture",
                registry_path=registry_path,
                output_dir=temp_root / "generated_reports",
            )

            result = evaluator.delete_customer("qv-badpath")

            self.assertFalse(result["deleted"])
            self.assertIn("Refusing to delete unmanaged path", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
