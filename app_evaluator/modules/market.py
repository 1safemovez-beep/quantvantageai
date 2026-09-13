from .base import BaseModule

class MarketModule(BaseModule):
    def analyze(self, target_name):
        prompt = f"Analyze the market potential for '{target_name}'. Focus on market size, trends, and demand."
        return self.ai_query(prompt)
