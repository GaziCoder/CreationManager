from typing import List
from app.models import Insight, PrioritizedInsight
from app.tools.scoring import prioritize_insight_item

try:
    from google import genai
except ImportError:
    genai = None

class PrioritizationAgent:
    """
    PrioritizationAgent evaluates the production effort of insights and ranks them.
    It can use an LLM to evaluate effort or fall back to pre-defined rules.
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
        # Static effort scoring based on category
        cat = insight.category.lower()
        if "quality" in cat:
            effort = 3.0
        elif "production" in cat:
            effort = 4.0
        else:
            effort = 7.0
            
        return prioritize_insight_item(insight, impact=0.0, effort=effort)

    def _prioritize_with_llm(self, insight: Insight) -> PrioritizedInsight:
        prompt = f"""
        Evaluate the following content creator insight for Production Effort.
        Effort should be scored from 1 to 10 (1 = trivial editing tweak, 10 = massive multi-part video series requiring days of coding and recording).
        
        Provide the response in the following format:
        Effort: <float>
        Justification: <One sentence explanation of the effort score based on creator workload>
        
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
            
            effort = 5.0
            for line in text.split("\n"):
                if line.startswith("Effort:"):
                    try:
                        effort = float(line.replace("Effort:", "").strip())
                    except ValueError:
                        pass
                    
            return prioritize_insight_item(insight, impact=0.0, effort=effort)
        except Exception as e:
            raise RuntimeError(f"PrioritizationAgent API request failed: {str(e)}")
