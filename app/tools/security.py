import re
from app.models import ProductBrief

def scan_for_secrets(text: str) -> bool:
    """
    Checks for potential API keys, database URLs, or secret keys in text.
    """
    # Simple patterns for secrets
    patterns = [
        r"(?i)api[-_]key\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,}['\"]",
        r"(?i)password\s*[:=]\s*['\"][a-zA-Z0-9_\-]{8,}['\"]",
        r"(?i)secret[-_]key\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,}['\"]"
    ]
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False

def verify_brief_safety(brief: ProductBrief) -> bool:
    """
    Scans the product brief overview and features to verify no secrets are leaked.
    Returns True if safe, False if unsafe.
    """
    if scan_for_secrets(brief.overview):
        return False
    for feature in brief.features:
        if scan_for_secrets(feature):
            return False
    return True
