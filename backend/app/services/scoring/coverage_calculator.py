from typing import List, Dict, Any
from app.services.scoring.semantic_matcher import SemanticMatcher

class CoverageCalculator:
    """
    Calculates a realistic coverage score based on weighted JD components.
    """
    
    def __init__(self):
        self.semantic_matcher = SemanticMatcher()
        self.weights = {
            "required_skills": 0.50,
            "technologies": 0.25,
            "responsibilities": 0.25
        }

    def calculate_coverage(self, 
                           resume_skills: List[str], 
                           jd_required_skills: List[str],
                           jd_technologies: List[str],
                           jd_responsibilities: List[str],
                           resume_text: str) -> Dict[str, Any]:
        """
        Calculates the weighted coverage score.
        """
        # 1. Skills Score
        skills_matches = 0
        for req in jd_required_skills:
            if any(self.semantic_matcher.is_match(req, s) for s in resume_skills):
                skills_matches += 1
        
        skills_score = (skills_matches / len(jd_required_skills) * 100) if jd_required_skills else 100

        # 2. Technologies Score
        tech_matches = 0
        resume_text_lower = resume_text.lower()
        for tech in jd_technologies:
            if tech.lower() in resume_text_lower:
                tech_matches += 1
            elif any(self.semantic_matcher.is_match(tech, s) for s in resume_skills):
                tech_matches += 1
                
        tech_score = (tech_matches / len(jd_technologies) * 100) if jd_technologies else 100

        # 3. Responsibilities Score
        resp_matches = 0
        for resp in jd_responsibilities:
            resp_lower = resp.lower()
            # Check for exact phrase first
            if resp_lower in resume_text_lower:
                resp_matches += 1
                continue
            # Simple keyword overlap check for responsibilities
            keywords = [w for w in resp_lower.split() if len(w) > 3]
            if not keywords: continue
            match_count = sum(1 for kw in keywords if kw in resume_text_lower)
            if match_count >= max(1, len(keywords) // 2):
                resp_matches += 1
                
        resp_score = (resp_matches / len(jd_responsibilities) * 100) if jd_responsibilities else 100

        # Weighted Final Score
        final_coverage = (
            (skills_score * self.weights["required_skills"]) +
            (tech_score * self.weights["technologies"]) +
            (resp_score * self.weights["responsibilities"])
        )

        return {
            "coverage_score": round(final_coverage, 2),
            "breakdown": {
                "skills_coverage": round(skills_score, 2),
                "tech_coverage": round(tech_score, 2),
                "resp_coverage": round(resp_score, 2)
            }
        }
