import re
from typing import Optional

class SeniorityClassifier:
    """
    Determines experience level and role seniority based on experience requirements.
    """
    
    def __init__(self):
        self.rules = [
            {"max_years": 1, "level": "Entry Level"},
            {"max_years": 3, "level": "Junior"},
            {"max_years": 6, "level": "Mid Level"},
            {"max_years": 99, "level": "Senior"}
        ]

    def classify(self, experience_text: str) -> str:
        """
        Determines the seniority level from a string describing experience requirements.
        """
        if not experience_text:
            return "Mid Level"  # Default if not specified

        # Extract numbers from text (e.g., "3-5 years", "minimum 6 years")
        years = self._extract_years(experience_text)
        
        if years is None:
            # Fallback based on keywords
            text_lower = experience_text.lower()
            if any(k in text_lower for k in ["senior", "lead", "architect", "principal"]):
                return "Senior"
            if any(k in text_lower for k in ["junior", "entry", "associate"]):
                return "Junior" if "junior" in text_lower else "Entry Level"
            return "Mid Level"

        for rule in self.rules:
            if years <= rule["max_years"]:
                return rule["level"]
        
        return "Senior"

    def _extract_years(self, text: str) -> Optional[int]:
        """
        Extracts the numeric years of experience from text.
        """
        # Look for patterns like "5+ years", "3-5 years", "at least 4 years"
        # Improved regex to handle "+" and more variations
        matches = re.findall(r'(\d+)\s*(?:\+)?\s*(?:-|to)?\s*(?:\d+)?\s*year', text.lower())
        if matches:
            # Take the first number found as the primary indicator
            return int(matches[0])
        return None
