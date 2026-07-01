from app.models import Insight, PrioritizedInsight

def calculate_creator_priority(reach: float, confidence: float, effort: float) -> float:
    """
    Calculates priority score for content creation opportunities:
    Score = (Reach * Confidence) / (Effort or 1)
    """
    if effort <= 0:
        effort = 0.5
    return round((reach * confidence) / effort, 2)

def prioritize_insight_item(insight: Insight, impact: float, effort: float) -> PrioritizedInsight:
    # Reach is calculated based on evidence count + total likes
    evidence_count = len(insight.evidence_items)
    total_likes = sum(item.likes for item in insight.evidence_items)
    
    # reach = count of sources + likes
    reach = evidence_count + (total_likes * 0.5)
    
    priority_score = calculate_creator_priority(reach, insight.confidence, effort)
    
    justification = (
        f"Weighted Reach of {reach:.1f} (based on {evidence_count} comments/sources and {total_likes} total likes) "
        f"evaluated against estimated Production Effort of {effort:.1f}."
    )
    
    ranking_rationale = (
        f"This opportunity ranks at {priority_score} due to high direct viewer demand "
        f"({total_likes} likes indicating strong community validation) relative to moderate production complexity."
    )
    
    return PrioritizedInsight(
        insight=insight,
        priority_score=priority_score,
        impact_score=reach,
        effort_score=effort,
        justification=justification,
        ranking_rationale=ranking_rationale
    )
