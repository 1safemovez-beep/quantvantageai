from .base import BaseModule
class FinancialModule(BaseModule):
    def analyze(self, target_name):
        return self.ai_query(f"Provide a financial analysis for '{target_name}', including estimated CAC and profit margins.")
