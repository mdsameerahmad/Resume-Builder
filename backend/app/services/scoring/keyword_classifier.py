from typing import List

class KeywordClassifier:
    """
    Classifies and filters ATS keywords to exclude metadata like job titles.
    """
    
    EXCLUDED_TERMS = {
        "junior", "senior", "lead", "fresher", "remote", "wfh", "full time", 
        "part time", "contract", "intern", "developer", "engineer", "analyst",
        "manager", "software engineer", "software developer", "backend developer",
        "frontend developer", "full stack developer", "data analyst", "data scientist"
    }

    def classify_keywords(self, keywords: List[str]) -> List[str]:
        """
        Filters out job titles and metadata from the ATS keywords list.
        """
        cleaned_keywords = []
        for kw in keywords:
            kw_lower = kw.lower().strip()
            # 1. Check if term or any of its words are in EXCLUDED_TERMS
            words = kw_lower.split()
            if any(word in self.EXCLUDED_TERMS for word in words):
                continue
            
            # 2. Check if the full term is in EXCLUDED_TERMS
            if kw_lower in self.EXCLUDED_TERMS:
                continue
            
            # Additional heuristic: if it's too long or contains common metadata phrases
            if len(kw_lower.split()) > 4:
                continue
                
            cleaned_keywords.append(kw)
            
        return cleaned_keywords
