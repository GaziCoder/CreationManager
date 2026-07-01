from pydantic import BaseModel, Field
from typing import List, Optional

class FeedbackItem(BaseModel):
    id: str
    source: str  # e.g., 'comments', 'notes', 'transcript'
    content: str
    likes: int = 0
    metadata: Optional[dict] = Field(default_factory=dict)

class Insight(BaseModel):
    id: str
    title: str
    description: str
    source_ids: List[str]
    category: str  # e.g., 'topic_request', 'quality_issue', 'production_suggestion'
    confidence: float = 1.0
    evidence_items: List[FeedbackItem] = Field(default_factory=list)

class PrioritizedInsight(BaseModel):
    insight: Insight
    priority_score: float  # 0 to 10
    impact_score: float  # 0 to 10 (Demand/Audience Reach)
    effort_score: float  # 0 to 10 (Production Difficulty/Time)
    justification: str
    ranking_rationale: str

class ContentBrief(BaseModel):
    id: str
    title: str  # Content Working Title
    format_type: str  # e.g., 'Video Tutorial', 'Podcast Episode', 'Newsletter Post'
    overview: str  # Content outline / synopsis
    sections: List[str]  # Key sections / outline points (insight-specific features)
    target_audience: str
    success_metrics: List[str]  # Concrete metrics (no placeholders)
    linked_insight_ids: List[str]
    priority_score: float
    confidence_score: float
    ranking_rationale: str
    evidence_comments: List[str]  # Exact quote list for verification
    review_status: str = "pending"  # pending, approved, rejected
    safety_flag: bool = False
    review_comments: Optional[str] = None
