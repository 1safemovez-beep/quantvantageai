from .base import BaseModule

class HealthModule(BaseModule):
    def analyze(self, metrics, lang="English"):
        prompt = f"As a health data analyzer, provide professional insights based on these respiratory metrics: '{metrics}'. (Disclaimer: For informational purposes only). IMPORTANT: Deliver the entire response in {lang}."
        return self.ai_query(prompt)
