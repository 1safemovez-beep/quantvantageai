import os
import datetime
from .modules.market import MarketModule
from .modules.product import ProductModule
from .modules.competitor import CompetitorModule
from .modules.financial import FinancialModule
from .modules.commercial import CommercialModule
from .modules.monetization import MonetizationModule
from .modules.growth import GrowthModule
from .modules.risks import RisksModule
from .modules.health import HealthModule
from .scoring import ScoringEngine
from .reporting import ReportGenerator
from .security import SecureVault

class QVProEngine:
    """
    Master QVPro Analysis Engine.
    Coordinates the complete QVPro evaluation pipeline.
    """
    def __init__(self, target_name, api_key=None):
        self.target_name = target_name
        self.api_key = api_key
        self.data = {
            "target_name": target_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "analysis": {}
        }
        
        # Initialize specialized modules
        self.market = MarketModule(api_key)
        self.product = ProductModule(api_key)
        self.competitor = CompetitorModule(api_key)
        self.financial = FinancialModule(api_key)
        self.commercial = CommercialModule(api_key)
        self.monetization = MonetizationModule(api_key)
        self.growth = GrowthModule(api_key)
        self.risks = RisksModule(api_key)
        self.health = HealthModule(api_key)
        
        self.scoring = ScoringEngine()
        self.reporting = ReportGenerator()
        self.vault = SecureVault()

    def run_full_evaluation(self):
        """Coordinates the complete QVPro evaluation pipeline."""
        self.data["analysis"]["market"] = self.market.analyze(self.target_name)
        self.data["analysis"]["product"] = self.product.analyze(self.target_name)
        self.data["analysis"]["competitor"] = self.competitor.analyze(self.target_name)
        self.data["analysis"]["financial"] = self.financial.analyze(self.target_name)
        self.data["analysis"]["commercial"] = self.commercial.analyze(self.target_name)
        self.data["analysis"]["monetization"] = self.monetization.analyze(self.target_name)
        self.data["analysis"]["growth"] = self.growth.analyze(self.target_name)
        self.data["analysis"]["risks"] = self.risks.analyze(self.target_name)
        
        self.data["scores"] = self.scoring.calculate(self.data["analysis"])
        self.data["verdict"] = self.scoring.get_verdict(self.data["scores"])
        
        return self.data

    def generate_report(self):
        """Generates the standardized QVPro result report."""
        report = self.reporting.generate(self.data)
        # Optional: Encrypt sensitive parts if needed
        return report

    def get_encrypted_report(self):
        """Returns an encrypted version of the full report."""
        report = self.generate_report()
        return self.vault.encrypt(report)

    def run_health_evaluation(self, health_metrics, lang="English"):
        """Separate health pathway analysis (Respiratory/Health data)."""
        return self.health.analyze(health_metrics, lang=lang)

    def delete_account(self, email):
        """
        [NOT IMPLEMENTED] Initiates account deletion for the specified email.
        This method is a placeholder for your production database/auth deletion flow.
        """
        print(f"[QVPro Engine] WARNING: delete_account called for {email} but not implemented.")
        return {
            "status": "not_implemented",
            "message": "Account deletion requires connection to a production database (e.g. PostgreSQL, Firebase) and auth provider (e.g. Stripe, Auth0).",
            "timestamp": datetime.datetime.now().isoformat()
        }

    def delete_evaluation_file(self, filename):
        """Deletes a specific evaluation report file from the filesystem."""
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False

# Legacy compatibility alias
class QuantVantageAI(QVProEngine):
    pass
