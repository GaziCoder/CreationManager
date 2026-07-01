from app.models import Insight, PrioritizedInsight

def calculate_priority(impact: float, effort: float, confidence: float = 1.0) -> float:
    """
    Calculates priority score using a modified RICE / Cost-Value matrix.
    Score = (Impact * Confidence) / (Effort or 1)
    """
    if effort <= 0:
        effort = 0.5  # Prevent division by zero and handle low effort
    return round((impact * confidence) / effort, 2)

def prioritize_insight_item(insight: Insight, impact: float, effort: float) -> PrioritizedInsight:
    priority_score = calculate_priority(impact, effort, insight.confidence)
    justification = f"Impact ({impact}) divided by Effort ({effort}) with confidence {insight.confidence}."
    return PrioritizedInsight(
        insight=insight,
        priority_score=priority_score,
        impact_score=impact,
        effort_score=effort,
        justification=justification
    )
