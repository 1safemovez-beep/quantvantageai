import re

class ScoringEngine:
    def calculate(self, analysis_data):
        """
        Calculates scores for each module on a 0.1 - 100.0 scale by parsing the AI text.
        Looks for the pattern [SCORE: XX.X] in the analysis strings.
        """
        scores = {}
        modules = ["market", "product", "competitor", "financial", "commercial", "monetization", "growth", "risks"]
        
        for module in modules:
            text = analysis_data.get(module, "")
            # Look for [SCORE: 85.5] or similar
            match = re.search(r"\[SCORE:\s*(\d+\.?\d*)\]", text)
            if match:
                scores[module] = float(match.group(1))
            else:
                # Never generate random fallback scores. 
                # If a valid score cannot be extracted, return None.
                scores[module] = None
            
        # Overall QVPro Score
        weights = {
            "market": 0.20,
            "product": 0.15,
            "competitor": 0.10,
            "financial": 0.15,
            "commercial": 0.15,
            "monetization": 0.10,
            "growth": 0.10,
            "risks": 0.05
        }
        
        # Calculate overall only if all modules have scores
        if all(scores[m] is not None for m in modules):
            overall = sum(scores[m] * weights[m] for m in modules)
            scores["overall"] = round(overall, 1)
        else:
            scores["overall"] = None
            
        return scores

    def get_verdict(self, scores):
        score = scores.get("overall")
        if score is None:
            return "Insufficient Evidence for Verdict"
        
        if score >= 85:
            return "Strong Buy / High Priority Build"
        elif score >= 70:
            return "Moderate Build / Proceed with Caution"
        elif score >= 50:
            return "Pivotal Strategy Required"
        else:
            return "High Risk / Avoid or Major Re-engineering Needed"
