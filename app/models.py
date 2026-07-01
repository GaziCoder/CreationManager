from pydantic import BaseModel, Field
from typing import List, Optional

class FeedbackItem(BaseModel):
    id: str
    source: str  # e.g., 'comments', 'notes', 'transcript'
    content: str
    metadata: Optional[dict] = Field(default_factory=dict)

class Insight(BaseModel):
    id: str
    title: str
    description: str
    source_ids: List[str]
    category: str
    confidence: float = 1.0

class PrioritizedInsight(BaseModel):
    insight: Insight
    priority_score: float  # 0 to 10
    impact_score: float  # 0 to 10
    effort_score: float  # 0 to 10
    justification: str

class ProductBrief(BaseModel):
    id: str
    title: str
    overview: str
    features: List[str]
    target_audience: str
    success_metrics: List[str]
    linked_insight_ids: List[str]
    review_status: str = "pending"  # pending, approved, rejected
    security_flag: bool = False
    review_comments: Optional[str] = None
