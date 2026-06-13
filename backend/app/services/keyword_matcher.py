from typing import List, Dict, Any

class KeywordMatcher:
    """
    Compares ATS keywords from JD with Resume content.
    """
    
    def match_keywords(self, resume_text: str, jd_keywords: List[str]) -> Dict[str, Any]:
        """
        Finds matched and missing keywords in the resume text.
        """
        if not jd_keywords:
            return {"matched_keywords": [], "missing_keywords": [], "match_percentage": 0.0}
            
        resume_text_lower = resume_text.lower()
        matched = []
        missing = []
        
        for kw in jd_keywords:
            if kw.lower().strip() in resume_text_lower:
                matched.append(kw)
            else:
                missing.append(kw)
        
        match_percentage = (len(matched) / len(jd_keywords)) * 100 if jd_keywords else 0.0
        
        return {
            "matched_keywords": matched,
            "missing_keywords": missing,
            "match_percentage": round(match_percentage, 2)
        }
