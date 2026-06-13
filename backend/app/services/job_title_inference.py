from typing import List, Dict, Any

class JobTitleInferenceService:
    """
    Infers the most likely job title from technologies, responsibilities, and required skills.
    """
    
    def __init__(self):
        self.mapping = [
            {
                "keywords": ["servicenow", "gliderecord", "business rules", "client scripts"],
                "title": "ServiceNow Developer"
            },
            {
                "keywords": ["java", "spring boot", "microservices", "hibernate", "maven"],
                "title": "Backend Developer"
            },
            {
                "keywords": ["react", "javascript", "css", "html", "vue", "angular", "frontend"],
                "title": "Frontend Developer"
            },
            {
                "keywords": ["python", "pandas", "sql", "power bi", "tableau", "analytics", "data analyst"],
                "title": "Data Analyst"
            },
            {
                "keywords": ["aws", "azure", "gcp", "terraform", "kubernetes", "docker", "cloud"],
                "title": "Cloud Engineer"
            },
            {
                "keywords": ["devops", "jenkins", "cicd", "pipelines"],
                "title": "DevOps Engineer"
            }
        ]

    def infer_title(self, skills: List[str], technologies: List[str], responsibilities: List[str]) -> Dict[str, Any]:
        """
        Infers the job title and returns it along with a confidence score.
        """
        all_text = " ".join(skills + technologies + responsibilities).lower()
        
        best_match = None
        max_score = 0
        
        for entry in self.mapping:
            score = sum(1 for kw in entry["keywords"] if kw.lower() in all_text)
            if score > max_score:
                max_score = score
                best_match = entry["title"]
        
        # Calculate a simple confidence score
        confidence = min(0.95, 0.5 + (max_score * 0.1)) if best_match else 0.0
        
        return {
            "inferred_title": best_match or "Software Engineer",
            "confidence_score": confidence
        }

    def validate_title(self, title: str) -> bool:
        """
        Validates if the inferred title is reasonable.
        """
        return len(title) > 3 and title.lower() != "unknown"
