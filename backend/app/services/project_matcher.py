from typing import List, Dict, Any

class ProjectMatcher:
    """
    Finds and ranks projects relevant to JD technologies and responsibilities.
    """
    
    def match_projects(self, projects: List[Dict[str, Any]], jd_technologies: List[str], jd_responsibilities: List[str]) -> List[Dict[str, Any]]:
        """
        Scores and ranks projects by relevance.
        """
        relevant_projects = []
        jd_context = " ".join(jd_technologies + jd_responsibilities).lower()
        
        for project in projects:
            score = 0
            title = project.get("title", "")
            description = project.get("description", "").lower()
            technologies = [t.lower() for t in project.get("technologies", [])]
            
            # Check tech stack matches
            for tech in jd_technologies:
                if tech.lower() in technologies:
                    score += 2
                elif tech.lower() in description:
                    score += 1
            
            # Check context matches
            for resp in jd_responsibilities:
                if resp.lower() in description:
                    score += 1
            
            if score > 0:
                relevant_projects.append({
                    "title": title,
                    "relevance_score": score,
                    "technologies": technologies
                })
        
        # Sort by score descending
        relevant_projects.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return relevant_projects[:5]  # Return top 5
