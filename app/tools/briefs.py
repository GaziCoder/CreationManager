from app.models import ContentBrief

def format_brief_to_markdown(brief: ContentBrief) -> str:
    """
    Formats a ContentBrief into a professional markdown template containing:
    - Working Title & Format
    - Overview & Script Outline
    - Evidence & Engagement signals
    - Prioritization Scores (Opportunity, Confidence, Rationale)
    - Specific concrete success metrics (no placeholders)
    """
    evidence_lines = ""
    for idx, quote in enumerate(brief.evidence_comments, 1):
        # Escaping markdown blockquotes in quote if any
        clean_quote = quote.replace("\n", " ")
        evidence_lines += f"> {idx}. \"{clean_quote}\"\n"

    sections_lines = ""
    for sec in brief.sections:
        sections_lines += f"- **{sec.split(':')[0]}**: {sec.split(':')[-1] if ':' in sec else ''}\n"

    metrics_lines = ""
    for metric in brief.success_metrics:
        metrics_lines += f"- {metric}\n"

    markdown = f"""# CONTENT DECISION BRIEF: {brief.title}

## Overview
{brief.overview}

---

## 📊 Prioritization & Decision Scoring
* **Opportunity / Priority Score**: `{brief.priority_score} / 10`
* **Confidence Score**: `{brief.confidence_score} / 1.0`
* **Target Audience**: {brief.target_audience}
* **Format Type**: {brief.format_type}

### Ranking Rationale
{brief.ranking_rationale}

---

## 🔍 Evidence-Backed Signals (Verification Source)
This content decision was synthesized directly from user feedback. The backing comments and engagement signals include:

{evidence_lines}

---

## 📝 Outline & Key Script Sections
{sections_lines}

---

## 📈 Concrete Success Metrics
The performance of this content piece will be evaluated against the following target metrics:
{metrics_lines}

---

## 🛡️ Review & Safety Metadata
- **Status**: `{brief.review_status.upper()}`
- **Safety Flag**: `{brief.safety_flag}`
- **Reviewer Comments**: {brief.review_comments if brief.review_comments else "None"}
- **Linked Insight IDs**: {', '.join(brief.linked_insight_ids)}
"""
    return markdown
