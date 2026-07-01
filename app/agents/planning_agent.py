import uuid
from typing import List
from app.models import PrioritizedInsight, ProductBrief

try:
    from google import genai
except ImportError:
    genai = None

class PlanningAgent:
    """
    PlanningAgent generates detailed ProductBriefs from prioritized insights.
    Uses LLM generation if api key is provided, or rule-based templates.
    """
    def __init__(self, api_key: str = "", model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        if genai and api_key:
            self.client = genai.Client(api_key=api_key)

    def create_briefs(self, prioritized_insights: List[PrioritizedInsight]) -> List[ProductBrief]:
        briefs = []
        for p_insight in prioritized_insights:
            if self.client:
                briefs.append(self._create_brief_with_llm(p_insight))
            else:
                briefs.append(self._create_brief_with_rules(p_insight))
        return briefs

    def _create_brief_with_rules(self, p_insight: PrioritizedInsight) -> ProductBrief:
        insight = p_insight.insight
        return ProductBrief(
            id=f"brief_{uuid.uuid4().hex[:8]}",
            title=f"Project Brief: {insight.title}",
            overview=f"This project addresses: {insight.description}.",
            features=[
                f"Feature 1 resolving {insight.category} issue",
                "Feedback analytics dashboard update",
                "Automated testing suite verification"
            ],
            target_audience="General Users & Engineers",
            success_metrics=[
                "Reduce related customer complaints by 50%",
                "Feature adoption rate > 30% in first month"
            ],
            linked_insight_ids=[insight.id]
        )

    def _create_brief_with_llm(self, p_insight: PrioritizedInsight) -> ProductBrief:
        insight = p_insight.insight
        prompt = f"""
        Generate a detailed Product Planning Brief based on the following prioritized insight:
        Title: {insight.title}
        Category: {insight.category}
        Description: {insight.description}
        Priority Score: {p_insight.priority_score}
        Justification: {p_insight.justification}
        
        Provide the response in the following YAML format:
        Title: <Title of the project>
        Overview: <Detailed overview paragraph of the project goals>
        Features:
          - <Feature 1>
          - <Feature 2>
        TargetAudience: <Target user segment>
        SuccessMetrics:
          - <Metric 1>
          - <Metric 2>
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text
            
            # Simple yaml-like parser
            title, overview, target_audience = f"Brief: {insight.title}", insight.description, "All users"
            features, success_metrics = [], []
            
            current_field = None
            for line in text.split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("Title:"):
                    title = stripped.replace("Title:", "").strip()
                elif stripped.startswith("Overview:"):
                    overview = stripped.replace("Overview:", "").strip()
                    current_field = "overview"
                elif stripped.startswith("TargetAudience:"):
                    target_audience = stripped.replace("TargetAudience:", "").strip()
                elif stripped.startswith("Features:"):
                    current_field = "features"
                elif stripped.startswith("SuccessMetrics:"):
                    current_field = "metrics"
                elif stripped.startswith("-") and current_field in ["features", "metrics"]:
                    val = stripped.replace("-", "", 1).strip()
                    if current_field == "features":
                        features.append(val)
                    else:
                        success_metrics.append(val)
                elif current_field == "overview" and not stripped.startswith("TargetAudience:") and not stripped.startswith("Features:"):
                    # append multiline overview
                    overview += " " + stripped
                    
            if not features:
                features = ["Default feature implementation"]
            if not success_metrics:
                success_metrics = ["Usage tracking metrics"]
                
            return ProductBrief(
                id=f"brief_{uuid.uuid4().hex[:8]}",
                title=title,
                overview=overview,
                features=features,
                target_audience=target_audience,
                success_metrics=success_metrics,
                linked_insight_ids=[insight.id]
            )
        except Exception:
            return self._create_brief_with_rules(p_insight)
