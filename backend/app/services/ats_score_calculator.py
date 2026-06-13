from typing import Dict, Any

class ATSScoreCalculator:
    """
    Calculates ATS and Coverage scores based on match results.
    """
    
    def __init__(self):
        self.weights = {
            "skills": 0.35,
            "keywords": 0.30,
            "projects": 0.20,
            "experience": 0.15
        }

    def calculate_scores(self, matches: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculates final scores.
        """
        # Coverage Score: (matched_skills / total_required_skills) * 100
        matched_skills = len(matches.get("matched_skills", []))
        missing_skills = len(matches.get("missing_skills", []))
        total_required = matched_skills + missing_skills
        
        coverage_score = (matched_skills / total_required * 100) if total_required > 0 else 0.0
        
        # ATS Score: Weighted average of match components
        # For simplicity, we normalize each component to 0-100
        
        # Skills match (0-100)
        skills_score = coverage_score
        
        # Keywords match (0-100)
        keywords_score = matches.get("keyword_match_percentage", 0.0)
        
        # Projects match (0-100) - based on number of relevant projects found (max 5)
        projects_found = len(matches.get("relevant_projects", []))
        projects_score = min(100, projects_found * 20)
        
        # Experience match (0-100) - based on top relevance score
        exp_list = matches.get("relevant_experience", [])
        top_exp_score = exp_list[0].get("relevance_score", 0) if exp_list else 0
        experience_score = min(100, top_exp_score * 10)
        
        ats_score = (
            skills_score * self.weights["skills"] +
            keywords_score * self.weights["keywords"] +
            projects_score * self.weights["projects"] +
            experience_score * self.weights["experience"]
        )
        
        return {
            "coverage_score": round(coverage_score, 2),
            "ats_score": round(ats_score, 2)
        }
