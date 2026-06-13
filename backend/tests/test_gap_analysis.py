import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.services.skill_matcher import SkillMatcher
from app.services.keyword_matcher import KeywordMatcher
from app.services.project_matcher import ProjectMatcher
from app.services.experience_matcher import ExperienceMatcher
from app.services.ats_score_calculator import ATSScoreCalculator
from app.services.recommendation_engine import RecommendationEngine

def test_skill_matcher():
    matcher = SkillMatcher()
    resume_skills = ["Java", "Spring Boot", "SQL", "Docker"]
    jd_required = ["Java", "Microservices", "Kubernetes"]
    jd_preferred = ["Docker", "AWS"]
    
    result = matcher.match_skills(resume_skills, jd_required, jd_preferred)
    assert "Java" in result["matched_skills"]
    assert "Docker" in result["matched_skills"]
    assert "Microservices" in result["missing_skills"]
    assert "Kubernetes" in result["missing_skills"]
    assert "AWS" in result["missing_preferred_skills"]

def test_keyword_matcher():
    matcher = KeywordMatcher()
    resume_text = "Experienced Backend Developer with 5 years in Java and Microservices."
    jd_keywords = ["Java", "Microservices", "REST API"]
    
    result = matcher.match_keywords(resume_text, jd_keywords)
    assert "Java" in result["matched_keywords"]
    assert "Microservices" in result["matched_keywords"]
    assert "REST API" in result["missing_keywords"]
    assert result["match_percentage"] == 66.67

def test_project_matcher():
    matcher = ProjectMatcher()
    projects = [
        {
            "title": "E-commerce Platform",
            "description": "Built using Java and Spring Boot with Microservices architecture.",
            "technologies": ["Java", "Spring Boot", "MySQL"]
        },
        {
            "title": "Weather App",
            "description": "Simple React app to show weather data.",
            "technologies": ["React", "JavaScript"]
        }
    ]
    jd_technologies = ["Java", "Spring Boot"]
    jd_responsibilities = ["Design microservices"]
    
    result = matcher.match_projects(projects, jd_technologies, jd_responsibilities)
    assert len(result) == 1
    assert result[0]["title"] == "E-commerce Platform"
    assert result[0]["relevance_score"] >= 4

def test_experience_matcher():
    matcher = ExperienceMatcher()
    experiences = [
        {
            "company": "Tech Corp",
            "role": "Senior Java Developer",
            "description": "Lead the development of backend APIs."
        },
        {
            "company": "Design Studio",
            "role": "Frontend Designer",
            "description": "Created UI/UX designs."
        }
    ]
    jd_title = "Java Developer"
    jd_responsibilities = ["Develop backend APIs"]
    
    result = matcher.match_experience(experiences, jd_responsibilities, jd_title)
    assert len(result) >= 1
    assert result[0]["company"] == "Tech Corp"
    assert result[0]["relevance_score"] >= 6

def test_ats_score_calculator():
    calc = ATSScoreCalculator()
    matches = {
        "matched_skills": ["Java", "SQL"],
        "missing_skills": ["AWS", "Docker"], # 50% coverage
        "keyword_match_percentage": 75.0,
        "relevant_projects": [{"title": "P1"}, {"title": "P2"}], # 2 projects * 20 = 40
        "relevant_experience": [{"relevance_score": 8}] # 8 * 10 = 80
    }
    
    scores = calc.calculate_scores(matches)
    assert scores["coverage_score"] == 50.0
    # ATS = 50*0.35 + 75*0.30 + 40*0.20 + 80*0.15 = 17.5 + 22.5 + 8 + 12 = 60
    assert scores["ats_score"] == 60.0

if __name__ == "__main__":
    print("Running Gap Analysis Engine tests...")
    test_skill_matcher()
    test_keyword_matcher()
    test_project_matcher()
    test_experience_matcher()
    test_ats_score_calculator()
    print("All tests passed!")
