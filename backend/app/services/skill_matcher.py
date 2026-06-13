from typing import List, Dict, Set

class SkillMatcher:
    """
    Compares JD required skills with resume skills.
    """
    
    def match_skills(self, resume_skills: List[str], jd_required: List[str], jd_preferred: List[str]) -> Dict[str, List[str]]:
        """
        Identifies matched and missing skills.
        """
        # Normalize for comparison
        resume_set = {s.lower().strip() for s in resume_skills}
        required_set = {s.lower().strip() for s in jd_required}
        preferred_set = {s.lower().strip() for s in jd_preferred}
        
        matched_required = [s for s in jd_required if s.lower().strip() in resume_set]
        matched_preferred = [s for s in jd_preferred if s.lower().strip() in resume_set]
        
        missing_required = [s for s in jd_required if s.lower().strip() not in resume_set]
        missing_preferred = [s for s in jd_preferred if s.lower().strip() not in resume_set]
        
        return {
            "matched_skills": list(dict.fromkeys(matched_required + matched_preferred)),
            "missing_skills": missing_required,
            "missing_preferred_skills": missing_preferred
        }
