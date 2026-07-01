import re
from app.models import ContentBrief
from app.tools.security import verify_brief_safety

try:
    from google import genai
except ImportError:
    genai = None

class ReviewAgent:
    """
    ReviewAgent validates content briefs for quality, safety, and brand compliance.
    Rejects any briefs containing unresolved placeholders (e.g., X%, Y, Z, <metric>).
    """
    def __init__(self, api_key: str = "", model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        if genai and api_key:
            self.client = genai.Client(api_key=api_key)

    def review(self, brief: ContentBrief) -> ContentBrief:
        # 1. Automated Security Check (secrets scan)
        # Note: We adapt the verify_brief_safety slightly to fit ContentBrief attributes
        # Since it has overview and sections, we check those
        is_safe = True
        from app.tools.security import scan_for_secrets
        if scan_for_secrets(brief.overview):
            is_safe = False
        for sec in brief.sections:
            if scan_for_secrets(sec):
                is_safe = False
                
        if not is_safe:
            brief.review_status = "rejected"
            brief.safety_flag = True
            brief.review_comments = "Failed security verification. Potential secret/API key leakage detected."
            return brief
            
        # 2. Automated Quality/Placeholder Check
        placeholder_pattern = r"(?i)\b[XYZ]\b|\bX%|\bY%|\bZ%|<.*>|\[.*\]|placeholder"
        has_placeholders = False
        for metric in brief.success_metrics:
            if re.search(placeholder_pattern, metric):
                has_placeholders = True
                break
        if re.search(placeholder_pattern, brief.overview):
            has_placeholders = True
            
        if has_placeholders:
            brief.review_status = "rejected"
            brief.review_comments = "Failed quality check: Unresolved placeholders (e.g., X%, Y, Z, <...>) detected in brief metrics or overview."
            return brief

        # 3. Qualitative LLM / Rule Check
        if self.client:
            return self._review_with_llm(brief)
        else:
            return self._review_with_rules(brief)

    def _review_with_rules(self, brief: ContentBrief) -> ContentBrief:
        if len(brief.sections) < 1:
            brief.review_status = "rejected"
            brief.review_comments = "Brief must contain at least 1 outline section."
        elif len(brief.overview) < 15:
            brief.review_status = "rejected"
            brief.review_comments = "Brief overview is too short/generic."
        else:
            brief.review_status = "approved"
            brief.review_comments = "Automated quality checks passed. Outline and metrics are complete and concrete."
        return brief

    def _review_with_llm(self, brief: ContentBrief) -> ContentBrief:
        prompt = f"""
        Review the following Content Planning Brief for completeness, quality, and feasibility.
        
        Title: {brief.title}
        Format: {brief.format_type}
        Overview: {brief.overview}
        Outline Sections: {', '.join(brief.sections)}
        Success Metrics: {', '.join(brief.success_metrics)}
        Target Audience: {brief.target_audience}
        
        Check if the outline sections are detailed and the success metrics are concrete (no placeholders like X%, Y, etc.).
        
        Return your review in the format:
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
