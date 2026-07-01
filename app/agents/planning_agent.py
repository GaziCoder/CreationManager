import uuid
from typing import List
from app.models import PrioritizedInsight, ContentBrief

try:
    from google import genai
except ImportError:
    genai = None

class PlanningAgent:
    """
    PlanningAgent generates detailed ContentBriefs from prioritized creator insights.
    Populates specific concrete outline sections, success metrics, and maps raw comments as evidence.
    """
    def __init__(self, api_key: str = "", model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        if genai and api_key:
            self.client = genai.Client(api_key=api_key)

    def create_briefs(self, prioritized_insights: List[PrioritizedInsight]) -> List[ContentBrief]:
        briefs = []
        for p_insight in prioritized_insights:
            if self.client:
                briefs.append(self._create_brief_with_llm(p_insight))
            else:
                briefs.append(self._create_brief_with_rules(p_insight))
        return briefs

    def _create_brief_with_rules(self, p_insight: PrioritizedInsight) -> ContentBrief:
        insight = p_insight.insight
        
        # Prepare evidence quotes
        evidence_comments = [item.content for item in insight.evidence_items]
        
        # Creator-specific static data
        cat = insight.category.lower()
        if "quality" in cat:
            title = "Channel Audio Audit & Pacing Overhaul"
            format_type = "Production Improvement Checklist"
            overview = "Action plan to clean up studio audio background hum, balance sound levels, and optimize code walkthrough pacing."
            sections = [
                "Vocal EQ & Noise Gate setup: Calibrate post-processing chain to suppress studio fan noise below -55dB.",
                "Pacing checkpoints: Inject brief chapter breaks before major coding blocks and slow speed to 80% default during live typing."
            ]
            success_metrics = [
                "Reduce viewer complaints about audio hum to zero in next 3 uploads.",
                "Maintain audience retention above 50% during the coding walkthrough sections."
            ]
        elif "production" in cat:
            title = "Establishing Tutorial Code Repository Workflow"
            format_type = "Internal Operations Brief"
            overview = "Creating a structured template and publishing workflow for GitHub companion repositories linked in tutorial descriptions."
            sections = [
                "Repo Template design: Standardize directories with app/, data/, outputs/, and setup guides.",
                "Publishing checklists: Add repo creation as a pre-upload step in the editing checklist."
            ]
            success_metrics = [
                "Include a working GitHub link in 100% of upcoming development tutorials.",
                "Achieve a 15% click-through rate on description repository links."
            ]
        else:
            title = f"Deep Dive: {insight.title}"
            format_type = "Video Tutorial & Outline"
            overview = f"Full tutorial addressing developer demand for: {insight.description}."
            sections = [
                "Introduction: Introduce the problem and explain architecture diagrams.",
                "Step-by-Step Code Walkthrough: Code the core structure live with slow pacing.",
                "Deployment: Deploy code to production environment (Cloud Run / Vercel)."
            ]
            success_metrics = [
                "Reach 10,000 views within 14 days of publication.",
                "Gain 150+ GitHub repository stars within week 1."
            ]

        return ContentBrief(
            id=f"brief_{uuid.uuid4().hex[:8]}",
            title=title,
            format_type=format_type,
            overview=overview,
            sections=sections,
            target_audience="Developers and Tech Subscribers",
            success_metrics=success_metrics,
            linked_insight_ids=[insight.id],
            priority_score=p_insight.priority_score,
            confidence_score=insight.confidence,
            ranking_rationale=p_insight.ranking_rationale,
            evidence_comments=evidence_comments
        )

    def _create_brief_with_llm(self, p_insight: PrioritizedInsight) -> ContentBrief:
        insight = p_insight.insight
        evidence_comments = [item.content for item in insight.evidence_items]
        
        prompt = f"""
        Generate a detailed tech Content Decision Brief based on the following prioritized audience insight:
        Title: {insight.title}
        Category: {insight.category}
        Description: {insight.description}
        Priority Score: {p_insight.priority_score}
        Justification: {p_insight.justification}
        
        Your output MUST be specific to content creators (e.g. video script, podcast episode, technical post outlines) and contain absolutely NO placeholders (like X%, Y, or Z). Make all success metrics fully concrete and realistic.
        
        Provide the response in the following YAML-like format:
        Title: <Content Title>
        FormatType: <e.g., Video Tutorial / Tech Podcast / Blog Post>
        Overview: <Detailed synopsis of the content piece>
        Sections:
          - <Section Name>: <Brief description of what is covered in this part of the script / content>
          - <Section Name>: <Brief description of what is covered in this part of the script / content>
        TargetAudience: <Target viewer/listener persona>
        SuccessMetrics:
          - <Concrete Metric 1, e.g., Reach 15,000 views in 14 days>
          - <Concrete Metric 2, e.g., Maintain >50% retention during setup section>
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text
            
            title, format_type, overview, target_audience = f"Outline: {insight.title}", "Video Tutorial", insight.description, "Tech audience"
            sections, success_metrics = [], []
            
            current_field = None
            for line in text.split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("Title:"):
                    title = stripped.replace("Title:", "").strip()
                elif stripped.startswith("FormatType:"):
                    format_type = stripped.replace("FormatType:", "").strip()
                elif stripped.startswith("Overview:"):
                    overview = stripped.replace("Overview:", "").strip()
                    current_field = "overview"
                elif stripped.startswith("TargetAudience:"):
                    target_audience = stripped.replace("TargetAudience:", "").strip()
                elif stripped.startswith("Sections:"):
                    current_field = "sections"
                elif stripped.startswith("SuccessMetrics:"):
                    current_field = "metrics"
                elif stripped.startswith("-") and current_field in ["sections", "metrics"]:
                    val = stripped.replace("-", "", 1).strip()
                    if current_field == "sections":
                        sections.append(val)
                    else:
                        success_metrics.append(val)
                elif current_field == "overview" and not any(stripped.startswith(k) for k in ["TargetAudience:", "Sections:", "SuccessMetrics:"]):
                    overview += " " + stripped
                    
            if not sections:
                sections = ["Intro: Problem intro", "Walkthrough: Step by step build", "Outro: Conclusion and call to action"]
            if not success_metrics:
                success_metrics = ["Audience retention > 45% at mid-point", "Gain 100+ likes in 48 hours"]
                
            return ContentBrief(
                id=f"brief_{uuid.uuid4().hex[:8]}",
                title=title,
                format_type=format_type,
                overview=overview,
                sections=sections,
                target_audience=target_audience,
                success_metrics=success_metrics,
                linked_insight_ids=[insight.id],
                priority_score=p_insight.priority_score,
                confidence_score=insight.confidence,
                ranking_rationale=p_insight.ranking_rationale,
                evidence_comments=evidence_comments
            )
        except Exception:
            return self._create_brief_with_rules(p_insight)
