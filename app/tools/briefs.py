from app.models import ProductBrief

def format_brief_to_markdown(brief: ProductBrief) -> str:
    """
    Formats a ProductBrief into a professional markdown template.
    """
    markdown = f"""# PRODUCT PLANNING BRIEF: {brief.title}

## Overview
{brief.overview}

## Key Features
"""
    for feature in brief.features:
        markdown += f"- {feature}\n"
        
    markdown += f"\n## Target Audience\n{brief.target_audience}\n\n## Success Metrics\n"
    for metric in brief.success_metrics:
        markdown += f"- {metric}\n"
        
    markdown += f"\n## Metadata\n- **Brief ID**: {brief.id}\n- **Status**: {brief.review_status}\n- **Security Flag**: {brief.security_flag}\n"
    if brief.review_comments:
        markdown += f"- **Reviewer Comments**: {brief.review_comments}\n"
        
    markdown += f"- **Linked Insight IDs**: {', '.join(brief.linked_insight_ids)}\n"
    return markdown
