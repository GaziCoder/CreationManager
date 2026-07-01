from typing import List
from app.models import FeedbackItem

def cluster_feedback(items: List[FeedbackItem]) -> List[List[FeedbackItem]]:
    """
    Groups feedback items into creator-specific clusters: topic_request, quality_issue, production_suggestion.
    """
    clusters = {}
    categories = {
        "topic_request": ["tutorial", "video on", "episode on", "deploy", "mcp", "fastmcp", "sdk", "build"],
        "quality_issue": ["audio", "sound", "hum", "quiet", "pacing", "fast", "slow", "hear"],
        "production_suggestion": ["github", "repo", "code", "copy-paste", "link", "chapter"]
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
