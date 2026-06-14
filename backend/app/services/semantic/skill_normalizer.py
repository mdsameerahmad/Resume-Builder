import re

class SkillNormalizer:
    """
    Normalizes skill strings for better matching.
    """
    @staticmethod
    def normalize(text: str) -> str:
        if not text:
            return ""
        # Lowercase
        text = text.lower().strip()
        # Remove common technical separators/punctuation but keep the letters/numbers
        text = re.sub(r'[^a-z0-9]', '', text)
        return text
