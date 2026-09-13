import anthropic
import os

class BaseModule:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def ai_query(self, prompt):
        if not self.client:
            return "AI Analysis unavailable (No API Key). Use local mock logic."
        
        # Request structured JSON format to minimize regex guessing
        structured_instruction = """
        IMPORTANT: Your final output must end with a structured summary in this exact format:
        ---
        {
          "score": XX.X,
          "summary": "Brief summary of findings",
          "strengths": ["...", "..."],
          "weaknesses": ["...", "..."],
          "recommendations": ["...", "..."]
        }
        [SCORE: XX.X]
        ---
        Where XX.X is a number from 0.1 to 100.0.
        """
        full_prompt = prompt + structured_instruction
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=800,
                messages=[{"role": "user", "content": full_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"AI Error: {str(e)}"
