import uuid
from typing import List
from app.models import FeedbackItem, Insight
from app.tools.clustering import cluster_feedback
# Import gemini client if needed
try:
    from google import genai
except ImportError:
    genai = None

class InsightAgent:
    """
    InsightAgent analyzes clustered feedback items and synthesizes them into distinct, structured Insights.
    It can use an LLM or keyword rules depending on whether an API key is available.
    """
    def __init__(self, api_key: str = "", model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        if genai and api_key:
            self.client = genai.Client(api_key=api_key)

    def extract_insights(self, items: List[FeedbackItem]) -> List[Insight]:
        if not items:
            return []
            
        # Group feedback items into clusters first
        clusters = cluster_feedback(items)
        insights = []
        
        for idx, cluster in enumerate(clusters):
            if not cluster:
                continue
                
            # Synthesize insight from cluster
            # For simplicity, if we have LLM, we use it. Otherwise, we do rule-based synthesis.
            if self.client:
                insights.append(self._synthesize_with_llm(cluster, idx))
            else:
                insights.append(self._synthesize_with_rules(cluster, idx))
                
        return insights

    def _synthesize_with_rules(self, cluster: List[FeedbackItem], idx: int) -> Insight:
        sources = [item.id for item in cluster]
        categories = [item.source for item in cluster]
        dominant_category = max(set(categories), key=categories.count)
        
        # Sample heuristics
        titles = {
            "comments": f"User feedback trend on Comments ({idx})",
            "notes": "Internal brainstorm insights",
            "transcript": "Customer meeting takeaways"
        }
        
        title = titles.get(dominant_category, f"Synthesized Insight {idx}")
        # Take a summary or concat first few chars
        summary_desc = " | ".join([item.content[:60] + "..." for item in cluster[:3]])
        
        return Insight(
            id=f"insight_{uuid.uuid4().hex[:8]}",
            title=title,
            description=f"Synthesized from {len(cluster)} items: {summary_desc}",
            source_ids=sources,
            category=dominant_category,
            confidence=0.8
        )

    def _synthesize_with_llm(self, cluster: List[FeedbackItem], idx: int) -> Insight:
        # Construct prompt
        context = "\n".join([f"- [{item.id}] Source: {item.source} - Content: {item.content}" for item in cluster])
        prompt = f"""
        Analyze the following feedback cluster and synthesize it into a single coherent insight.
        Provide the response in the following format:
        Title: <A short descriptive title summarizing the trend>
        Category: <Performance / UI-UX / Feature Request / General>
        Description: <A paragraph describing what the users want or the main issue, and why it is important>
        Confidence: <A float between 0.0 and 1.0 indicating how clear the trend is>

        Feedback items:
        {context}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text
            
            # Simple parser
            title, category, description, confidence = f"Insight {idx}", "General", "", 0.8
            for line in text.split("\n"):
                if line.startswith("Title:"):
                    title = line.replace("Title:", "").strip()
                elif line.startswith("Category:"):
                    category = line.replace("Category:", "").strip()
                elif line.startswith("Description:"):
                    description = line.replace("Description:", "").strip()
                elif line.startswith("Confidence:"):
                    try:
                        confidence = float(line.replace("Confidence:", "").strip())
                    except ValueError:
                        pass
            
            if not description:
                description = text.strip()
                
            return Insight(
                id=f"insight_{uuid.uuid4().hex[:8]}",
                title=title,
                description=description,
                source_ids=[item.id for item in cluster],
                category=category,
                confidence=confidence
            )
        except Exception as e:
            # Fallback on failure
            return self._synthesize_with_rules(cluster, idx)
