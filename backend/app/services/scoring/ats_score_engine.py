from typing import Dict, Any

class ATSScoreEngine:
    """
    Final ATS scoring engine using weighted components.
    """
    
    def __init__(self):
        self.weights = {
            "required_skills": 0.35,
            "ats_keywords": 0.25,
            "projects": 0.20,
            "experience": 0.10,
            "education": 0.05,
            "certifications": 0.05
        }

    def calculate_ats_score(self, components: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculates final ATS score from 0-100.
        """
        final_score = 0.0
        for key, weight in self.weights.items():
            final_score += components.get(key, 0.0) * weight
            
        return {
            "ats_score": round(min(100, final_score), 2),
            "breakdown": {k: round(components.get(k, 0.0), 2) for k in self.weights.keys()}
        }
