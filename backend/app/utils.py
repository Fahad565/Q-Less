import re

def normalize_phone_number(phone_number: str) -> str:
    """
    Normalizes Kenyan phone numbers into E.164 format (+254...).
    Handles formats like:
      - 0712345678 -> +254712345678
      - 0112345678 -> +254112345678
      - 254712345678 -> +254712345678
      - +254712345678 -> +254712345678
    If the number doesn't match standard Kenyan local formats,
    it cleans whitespace/dashes and prepends + if missing.
    """
    if not phone_number:
        return ""

    cleaned = re.sub(r"[\s\-\(\)]", "", str(phone_number).strip())

    # Check Kenyan local formats starting with 07 or 01 (9 digits after 0)
    if re.match(r"^0([17]\d{8})$", cleaned):
        return f"+254{cleaned[1:]}"

    # Check Kenyan format without + e.g. 2547... or 2541...
    if re.match(r"^254([17]\d{8})$", cleaned):
        return f"+{cleaned}"

    # Standard E.164 format
    if cleaned.startswith("+"):
        return cleaned

    # Fallback
    return f"+{cleaned}" if cleaned else ""
