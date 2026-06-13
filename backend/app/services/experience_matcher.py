from typing import List, Dict, Any

class ExperienceMatcher:
    """
    Finds and ranks experience relevant to JD.
    """
    
    def match_experience(self, experiences: List[Dict[str, Any]], jd_responsibilities: List[str], jd_title: str) -> List[Dict[str, Any]]:
        """
        Scores and ranks experience by relevance to the target role.
        """
        relevant_exp = []
        jd_title_lower = jd_title.lower()
        
        for exp in experiences:
            score = 0
            role = exp.get("role", "").lower()
            company = exp.get("company", "")
            description = exp.get("description", "").lower()
            
            # Title match is high value
            if jd_title_lower in role or role in jd_title_lower:
                score += 5
            
            # Responsibility matches - checking for keyword overlaps
            for resp in jd_responsibilities:
                resp_words = {w.lower() for w in resp.split() if len(w) > 3}
                desc_words = {w.lower() for w in description.split()}
                
                # Check for exact phrase first
                if resp.lower() in description:
                    score += 2
                # Then check for keyword overlap
                elif resp_words & desc_words:
                    score += 1
            
            if score > 0:
                relevant_exp.append({
                    "company": company,
                    "role": exp.get("role"),
                    "relevance_score": score
                })
                
        relevant_exp.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant_exp
