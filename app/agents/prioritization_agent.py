from typing import List
from app.models import Insight, PrioritizedInsight
from app.tools.scoring import prioritize_insight_item

try:
    from google import genai
except ImportError:
    genai = None

class PrioritizationAgent:
    """
    PrioritizationAgent evaluates the impact and effort of insights and ranks them.
    It can use an LLM to evaluate impact/effort or fall back to pre-defined rules.
    """
    def __init__(self, api_key: str = "", model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        if genai and api_key:
            self.client = genai.Client(api_key=api_key)

    def prioritize(self, insights: List[Insight]) -> List[PrioritizedInsight]:
        prioritized = []
        for insight in insights:
            if self.client:
                prioritized.append(self._prioritize_with_llm(insight))
            else:
                prioritized.append(self._prioritize_with_rules(insight))
                
        # Sort by priority score descending
        prioritized.sort(key=lambda x: x.priority_score, reverse=True)
        return prioritized

    def _prioritize_with_rules(self, insight: Insight) -> PrioritizedInsight:
        # Static scoring based on category
        cat = insight.category.lower()
        if "performance" in cat or "slow" in cat:
            impact, effort = 9.0, 4.0
        elif "feature" in cat or "add" in cat:
            impact, effort = 8.0, 7.0
        elif "ui" in cat or "ux" in cat:
            impact, effort = 6.0, 3.0
        else:
            impact, effort = 5.0, 5.0
            
        return prioritize_insight_item(insight, impact, effort)

    def _prioritize_with_llm(self, insight: Insight) -> PrioritizedInsight:
        prompt = f"""
        Evaluate the following product insight for Impact and Effort.
        Impact should be scored from 1 to 10 (1 = minimal impact, 10 = massive user value / blocker).
        Effort should be scored from 1 to 10 (1 = trivial change, 10 = major architecture redesign).
        
        Provide the response in the following format:
        Impact: <float>
        Effort: <float>
        Justification: <One sentence explanation of the scores>
        
        Insight:
        Title: {insight.title}
        Category: {insight.category}
        Description: {insight.description}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text
            
            impact, effort, justification = 5.0, 5.0, "Default prioritization scoring"
            for line in text.split("\n"):
                if line.startswith("Impact:"):
                    try:
                        impact = float(line.replace("Impact:", "").strip())
                    except ValueError:
                        pass
                elif line.startswith("Effort:"):
                    try:
                        effort = float(line.replace("Effort:", "").strip())
                    except ValueError:
                        pass
                elif line.startswith("Justification:"):
                    justification = line.replace("Justification:", "").strip()
                    
            return prioritize_insight_item(insight, impact, effort)
        except Exception:
            return self._prioritize_with_rules(insight)
