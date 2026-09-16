from .base import BaseModule
class ProductModule(BaseModule):
    def analyze(self, target_name):
        return self.ai_query(f"Analyze the product features and value proposition of '{target_name}'.")
