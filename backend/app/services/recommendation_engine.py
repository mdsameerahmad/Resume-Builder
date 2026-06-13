from typing import List, Dict, Any

class RecommendationEngine:
    """
    Generates optimization recommendations based on gap analysis.
    """
    
    def generate_recommendations(self, analysis_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Identifies strengths, weaknesses, and recommendations.
        """
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Skill-based insights
        missing_skills = analysis_data.get("missing_skills", [])
        matched_skills = analysis_data.get("matched_skills", [])
        
        if len(matched_skills) > 5:
            strengths.append(f"Strong match for core skills: {', '.join(matched_skills[:3])}")
            
        if missing_skills:
            weaknesses.append(f"Missing key skills: {', '.join(missing_skills[:3])}")
            recommendations.append(f"Consider highlighting experience with {missing_skills[0]} if you have it.")
        
        # Keyword-based insights
        missing_keywords = analysis_data.get("missing_keywords", [])
        if missing_keywords:
            recommendations.append(f"Incorporate missing ATS keywords like '{missing_keywords[0]}' and '{missing_keywords[1]}' naturally into your experience descriptions.")
            
        # Project-based insights
        relevant_projects = analysis_data.get("relevant_projects", [])
        if not relevant_projects:
            weaknesses.append("No projects found that match the job's technology stack.")
            recommendations.append("Add a technical project that demonstrates your proficiency with the required technologies.")
        else:
            strengths.append(f"Found {len(relevant_projects)} relevant projects.")
            recommendations.append(f"Prioritize the '{relevant_projects[0]['title']}' project in your resume as it has the highest relevance.")

        # Experience-based insights
        relevant_exp = analysis_data.get("relevant_experience", [])
        if relevant_exp:
            recommendations.append(f"Emphasize your role at {relevant_exp[0]['company']} as it aligns well with the target job title.")

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "optimization_recommendations": recommendations
        }
