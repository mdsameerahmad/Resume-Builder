from typing import List, Dict, Any
from loguru import logger

class JDKeywordExtractor:
    def __init__(self):
        self.categories = [
            "technical_skills", 
            "tools", 
            "frameworks", 
            "cloud_platforms", 
            "soft_skills", 
            "methodologies", 
            "certifications"
        ]

    def extract_and_categorize(self, parsed_jd: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Refines and categorizes keywords from the parsed JD.
        (In a real scenario, this might involve NLP or pre-defined taxonomies)
        """
        logger.info("Extracting and categorizing keywords from JD...")
        
        # For now, we use the categorization already provided by Gemini in JDAnalyzer
        # This service acts as a layer for future enhancement (e.g., scoring importance)
        
        return {
            "technical_skills": parsed_jd.get("required_skills", []),
            "tools_and_tech": parsed_jd.get("technologies", []),
            "soft_skills": parsed_jd.get("soft_skills", []),
            "ats_keywords": parsed_jd.get("ats_keywords", []),
            "certifications": parsed_jd.get("certifications", [])
        }
