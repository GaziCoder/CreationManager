import re

def clean_text(text: str) -> str:
    """
    Cleans raw text by normalizing whitespace and stripping leading/trailing spaces.
    """
    if not text:
        return ""
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_pii(text: str) -> str:
    """
    Basic placeholder PII removal (e.g., email, phone numbers).
    """
    # Simple email pattern
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    text = re.sub(email_pattern, "[EMAIL_REDACTED]", text)
    
    # Simple phone number pattern
    phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    # Only replace if it looks reasonably like a phone number (e.g. length of digits > 7)
    # This is a basic stub/placeholder
    return text
