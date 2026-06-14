from typing import List, Dict, Any
from app.services.scoring.semantic_matcher import SemanticMatcher

class ProjectRelevanceEngine:
    """
    Generates normalized 0-100 project relevance scores.
    """
    
    def __init__(self):
        self.semantic_matcher = SemanticMatcher()
        self.factors = {
            "technology_match": 40,
            "keyword_match": 25,
            "domain_match": 15,
            "responsibility_match": 10,
            "complexity": 10
        }

    def score_projects(self, 
                       resume_projects: List[Dict[str, Any]], 
                       jd_technologies: List[str],
                       jd_keywords: List[str],
                       jd_responsibilities: List[str],
                       jd_industry: str) -> List[Dict[str, Any]]:
        """
        Scores and ranks projects.
        """
        scored_projects = []
        
        for proj in resume_projects:
            score = 0
            proj_title = proj.get("title", "")
            proj_desc = proj.get("description", "").lower()
            proj_techs = [t.lower() for t in proj.get("technologies", [])]
            
            # 1. Tech Match (40%)
            tech_matches = 0
            for tech in jd_technologies:
                if any(self.semantic_matcher.is_match(tech, t) for t in proj_techs) or tech.lower() in proj_desc:
                    tech_matches += 1
            tech_ratio = (tech_matches / len(jd_technologies)) if jd_technologies else 1.0
            score += tech_ratio * self.factors["technology_match"]
            
            # 2. Keyword Match (25%)
            kw_matches = 0
            for kw in jd_keywords:
                if kw.lower() in proj_desc:
                    kw_matches += 1
            kw_ratio = (kw_matches / len(jd_keywords)) if jd_keywords else 1.0
            score += kw_ratio * self.factors["keyword_match"]
            
            # 3. Domain Match (15%)
            if jd_industry and (jd_industry.lower() in proj_desc or jd_industry.lower() in proj_title.lower()):
                score += self.factors["domain_match"]
                
            # 4. Responsibility Match (10%)
            resp_matches = 0
            for resp in jd_responsibilities:
                if resp.lower() in proj_desc:
                    resp_matches += 1
                else:
                    # Partial match for responsibilities
                    resp_words = [w for w in resp.lower().split() if len(w) > 3]
                    if resp_words and any(w in proj_desc for w in resp_words):
                        resp_matches += 0.5
            resp_ratio = (resp_matches / len(jd_responsibilities)) if jd_responsibilities else 1.0
            score += resp_ratio * self.factors["responsibility_match"]
            
            # 5. Complexity (10%) - Heuristic based on description length and tech count
            complexity_bonus = min(10, (len(proj_desc.split()) / 50) * 5 + (len(proj_techs) * 1))
            score += complexity_bonus
            
            scored_projects.append({
                "title": proj_title,
                "relevance_score": round(min(100, score), 2),
                "technologies": proj_techs
            })
            
        # Sort by relevance
        scored_projects.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Add rank
        for i, proj in enumerate(scored_projects):
            proj["rank"] = i + 1
            
        return scored_projects
