from typing import List, Dict, Any
from app.services.scoring.semantic_matcher import SemanticMatcher

class ContentPrioritizer:
    """
    Ranks skills, projects, and experience based on JD relevance scores from Gap Analysis.
    """
    
    def __init__(self):
        self.semantic_matcher = SemanticMatcher()

    def prioritize_skills(self, original_skills: List[str], matched_skills: List[str]) -> List[str]:
        """
        Moves matching skills to the top while keeping all original skills.
        """
        matched_set = {s.lower().strip() for s in matched_skills}
        
        top_skills = []
        other_skills = []
        
        for skill in original_skills:
            if skill.lower().strip() in matched_set:
                top_skills.append(skill)
            else:
                # Check semantic match too
                if any(self.semantic_matcher.is_match(skill, m) for m in matched_skills):
                    top_skills.append(skill)
                else:
                    other_skills.append(skill)
        
        return top_skills + other_skills

    def prioritize_projects(self, projects: List[Dict[str, Any]], rankings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sorts projects by relevance score provided in rankings.
        """
        # Map project title to relevance score
        score_map = {r["title"]: r["relevance_score"] for r in rankings}
        
        # Sort original projects based on the scores
        sorted_projects = sorted(
            projects, 
            key=lambda x: score_map.get(x.get("title", ""), 0), 
            reverse=True
        )
        
        return sorted_projects

    def prioritize_experience(self, experience: List[Dict[str, Any]], rankings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sorts experience by relevance.
        """
        # Rankings for experience usually use 'company' as key
        score_map = {r["company"]: r["relevance_score"] for r in rankings}
        
        sorted_exp = sorted(
            experience,
            key=lambda x: score_map.get(x.get("company", ""), 0),
            reverse=True
        )
        
        return sorted_exp

class KeywordInjector:
    """
    Identifies which missing ATS keywords can be naturally injected based on existing truth.
    """
    
    FORBIDDEN_KEYWORDS = {"wfh", "remote", "work from home", "company name", "company names"}

    def __init__(self):
        self.semantic_matcher = SemanticMatcher()

    def get_injectable_keywords(self, missing_keywords: List[str], resume_content: str) -> List[str]:
        """
        Only allows keywords that are already supported by resume content but weren't exact matches.
        Filters out forbidden keywords like 'WFH', 'Remote', etc.
        """
        injectable = []
        resume_lower = resume_content.lower()
        
        for kw in missing_keywords:
            kw_normalized = kw.lower().strip()
            
            # Skip forbidden keywords
            if kw_normalized in self.FORBIDDEN_KEYWORDS:
                continue
            
            # If the exact keyword or a synonym exists in resume
            if any(syn.lower() in resume_lower for syn in self.semantic_matcher.SYNONYMS.get(kw_normalized, [kw_normalized])):
                injectable.append(kw)
                
        return injectable
