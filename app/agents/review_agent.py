from app.models import ProductBrief
from app.tools.security import verify_brief_safety

try:
    from google import genai
except ImportError:
    genai = None

class ReviewAgent:
    """
    ReviewAgent validates product briefs for quality, safety, and policy compliance.
    Runs automated checks and can optionally use an LLM for qualitative review.
    """
    def __init__(self, api_key: str = "", model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        if genai and api_key:
            self.client = genai.Client(api_key=api_key)

    def review(self, brief: ProductBrief) -> ProductBrief:
        # 1. Run Automated Security Scan
        is_safe = verify_brief_safety(brief)
        if not is_safe:
            brief.review_status = "rejected"
            brief.security_flag = True
            brief.review_comments = "Failed security verification. Potential secret/API key leakage detected."
            return brief
            
        # 2. Run Qualitative LLM / Rule Check
        if self.client:
            return self._review_with_llm(brief)
        else:
            return self._review_with_rules(brief)

    def _review_with_rules(self, brief: ProductBrief) -> ProductBrief:
        # Simple heuristics for approval
        if len(brief.features) < 1:
            brief.review_status = "rejected"
            brief.review_comments = "Brief must contain at least 1 feature."
        elif len(brief.overview) < 15:
            brief.review_status = "rejected"
            brief.review_comments = "Brief overview is too short/generic."
        else:
            brief.review_status = "approved"
            brief.review_comments = "Automated checks passed. Approved for planning."
        return brief

    def _review_with_llm(self, brief: ProductBrief) -> ProductBrief:
        prompt = f"""
        Review the following Product Planning Brief for completeness, quality, and feasibility.
        Brief Details:
        Title: {brief.title}
        Overview: {brief.overview}
        Features: {', '.join(brief.features)}
        Success Metrics: {', '.join(brief.success_metrics)}
        Target Audience: {brief.target_audience}
        
        Is this brief realistic and complete? Return your review in the format:
        Status: <approved / rejected>
        Comments: <One sentence summary of your feedback>
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text
            
            status, comments = "approved", "Approved by LLM review agent."
            for line in text.split("\n"):
                if line.startswith("Status:"):
                    status_val = line.replace("Status:", "").strip().lower()
                    if status_val in ["approved", "rejected"]:
                        status = status_val
                elif line.startswith("Comments:"):
                    comments = line.replace("Comments:", "").strip()
                    
            brief.review_status = status
            brief.review_comments = comments
            return brief
        except Exception:
            return self._review_with_rules(brief)
