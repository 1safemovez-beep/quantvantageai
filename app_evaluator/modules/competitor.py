from .base import BaseModule

class CompetitorModule(BaseModule):
    def analyze(self, target_name):
        prompt = f"""
        Build a 'Real Competitor Engine' comparison for '{target_name}'.
        
        1. Identify 3 primary competitors (A, B, C).
        2. Create a Comparison Matrix table with the following columns:
           Capability | YOU ({target_name}) | Competitor A | Competitor B | Competitor C
        3. Include rows for: Feature 1, Feature 2, Pricing, AI/Tech, and Differentiation.
        4. Use symbols like '✓', '-', and '$' for the matrix values.
        5. Below the table, add a section: '🏆 WHERE CAN THIS PRODUCT ACTUALLY WIN?'
        
        STRICT RULES:
        - DO NOT invent competitors, pricing, or capabilities.
        - If a competitor or pricing detail is unknown, mark it as 'Unknown/Estimated'.
        - Clearly distinguish verified market facts from strategic uncertainty.
        - Focus on identifying the specific strategic gap that '{target_name}' fills better than A, B, and C.
        """
        return self.ai_query(prompt)
