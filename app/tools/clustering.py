from typing import List
from app.models import FeedbackItem, Insight

def cluster_feedback(items: List[FeedbackItem]) -> List[List[FeedbackItem]]:
    """
    Groups feedback items based on basic keyword matching or semantic clustering stubs.
    """
    # Simple keyword clusters for demonstration
    clusters = {}
    categories = {
        "performance": ["slow", "speed", "performance", "fast", "lag", "crash"],
        "ui_ux": ["design", "ui", "ux", "button", "color", "look", "interface", "layout"],
        "feature_request": ["add", "want", "feature", "new", "support", "create"],
        "billing": ["price", "cost", "billing", "subscribe", "payment", "expensive"]
    }
    
    unclustered = []
    
    for item in items:
        content_lower = item.content.lower()
        matched = False
        for cat, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                if cat not in clusters:
                    clusters[cat] = []
                clusters[cat].append(item)
                matched = True
                break
        if not matched:
            unclustered.append(item)
            
    result = list(clusters.values())
    if unclustered:
        result.append(unclustered)
        
    return result
