from typing import Dict, Any
from loguru import logger

class JDClassifier:
    def __init__(self):
        pass

    def classify_jd(self, parsed_jd: Dict[str, Any]) -> Dict[str, str]:
        """
        Detects job domain, category, and seniority from the parsed JD.
        """
        logger.info("Classifying JD for domain and seniority...")
        
        # Heuristic for seniority based on experience string
        exp_str = parsed_jd.get("experience_required", "").lower()
        seniority = "Entry-Level"
        
        if any(w in exp_str for w in ["senior", "sr.", "lead", "manager"]):
            seniority = "Senior"
        elif any(w in exp_str for w in ["mid", "intermediate"]):
            seniority = "Mid-Level"
        elif any(w in exp_str for w in ["junior", "jr.", "intern"]):
            seniority = "Entry-Level"
        elif "5+" in exp_str or "7+" in exp_str or "10+" in exp_str:
            seniority = "Senior/Lead"
        elif "2+" in exp_str or "3+" in exp_str:
            seniority = "Mid-Level"

        return {
            "industry": parsed_jd.get("industry", "Unknown"),
            "seniority": seniority,
            "domain": "Technology"  # Default for this project
        }
