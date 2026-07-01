import uuid
from typing import List
from app.models import FeedbackItem, Insight
from app.tools.clustering import cluster_feedback

try:
    from google import genai
except ImportError:
    genai = None

class InsightAgent:
    """
    InsightAgent analyzes clustered creator feedback items and synthesizes them into structured Insights.
    Ensures that backing evidence items are attached for verification.
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
            
        clusters = cluster_feedback(items)
        insights = []
        
        for idx, cluster in enumerate(clusters):
            if not cluster:
                continue
                
            if self.client:
                insights.append(self._synthesize_with_llm(cluster, idx))
            else:
                insights.append(self._synthesize_with_rules(cluster, idx))
                
        return insights

    def _synthesize_with_rules(self, cluster: List[FeedbackItem], idx: int) -> Insight:
        sources = [item.id for item in cluster]
        categories = [item.source for item in cluster]
        dominant_category = max(set(categories), key=categories.count)
        
        # Categorize
        if any(kw in cluster[0].content.lower() for kw in ["audio", "sound", "pacing", "quiet"]):
            category = "quality_issue"
            title = "Audio Quality and Pacing Improvements"
            desc = "Adjust microphones, vocal gain levels, and slow down code walkthrough speed."
        elif any(kw in cluster[0].content.lower() for kw in ["github", "repo", "code"]):
            category = "production_suggestion"
            title = "Provide GitHub Repositories for Tutorials"
            desc = "Publish clean source code repos in descriptions for all coding walkthroughs."
        else:
            category = "topic_request"
            title = f"Topic Request: {cluster[0].content[:40]}..."
            desc = f"Viewer interest in: {' | '.join([i.content[:60] for i in cluster[:2]])}"
            
        return Insight(
            id=f"insight_{uuid.uuid4().hex[:8]}",
            title=title,
            description=desc,
            source_ids=sources,
            category=category,
            confidence=0.9,
            evidence_items=cluster
        )

    def _synthesize_with_llm(self, cluster: List[FeedbackItem], idx: int) -> Insight:
        context = "\n".join([f"- [{item.id}] Source: {item.source} (Likes: {item.likes}) - Content: {item.content}" for item in cluster])
        prompt = f"""
        Analyze the following creator audience feedback cluster and synthesize it into a single coherent insight.
        Provide the response in the following format:
        Title: <Short descriptive title of the content theme / issue / request>
        Category: <topic_request / quality_issue / production_suggestion>
        Description: <Clear description of what viewers are requesting or complaining about, and why it matters>
        Confidence: <A float between 0.0 and 1.0 based on feedback volume and source agreement>

        Feedback items:
        {context}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text
            
            title, category, description, confidence = f"Insight {idx}", "topic_request", "", 0.9
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
                confidence=confidence,
                evidence_items=cluster
            )
        except Exception:
            return self._synthesize_with_rules(cluster, idx)
