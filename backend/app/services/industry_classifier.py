from typing import List, Dict, Any

class IndustryClassifier:
    """
    Determines industry/domain from role requirements.
    """
    
    def __init__(self):
        self.industry_mapping = {
            "Software Development": ["frontend", "backend", "full stack", "software developer", "software engineer"],
            "Analytics": ["data analyst", "data scientist", "business analyst", "bi developer"],
            "Information Technology": ["servicenow", "it support", "system administrator", "network engineer", "cloud engineer"],
            "Cloud Computing": ["cloud engineer", "devops", "aws", "azure", "gcp"],
            "Cybersecurity": ["security analyst", "pentester", "cybersecurity engineer"],
            "Finance": ["fintech", "banking", "investment", "trading"],
            "Healthcare": ["healthtech", "medical", "hospital", "pharma"]
        }

    def classify_industry(self, job_title: str, skills: List[str]) -> Dict[str, Any]:
        """
        Classifies the industry based on job title and skills.
        """
        title_lower = job_title.lower()
        all_text = " ".join([title_lower] + [s.lower() for s in skills])
        
        best_industry = "Information Technology"  # Default
        max_matches = 0
        
        for industry, keywords in self.industry_mapping.items():
            matches = sum(1 for kw in keywords if kw in all_text)
            if matches > max_matches:
                max_matches = matches
                best_industry = industry
        
        confidence = min(0.95, 0.6 + (max_matches * 0.1))
        
        return {
            "industry": best_industry,
            "confidence_score": confidence
        }
