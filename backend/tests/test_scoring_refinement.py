import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scoring.semantic_matcher import SemanticMatcher
from app.services.scoring.keyword_classifier import KeywordClassifier
from app.services.scoring.coverage_calculator import CoverageCalculator
from app.services.scoring.project_relevance_engine import ProjectRelevanceEngine

def test_semantic_matcher():
    matcher = SemanticMatcher()
    assert matcher.is_match("JS", "JavaScript") == True
    assert matcher.is_match("NodeJS", "Node.js") == True
    assert matcher.is_match("ReactJS", "React") == True
    assert matcher.is_match("Github", "Git") == True
    assert matcher.is_match("Python", "Java") == False
    print("test_semantic_matcher passed")

def test_keyword_classifier():
    classifier = KeywordClassifier()
    keywords = ["React", "Senior Developer", "Node.js", "Remote", "JavaScript", "Full Time"]
    cleaned = classifier.classify_keywords(keywords)
    assert "React" in cleaned
    assert "Node.js" in cleaned
    assert "JavaScript" in cleaned
    assert "Senior Developer" not in cleaned
    assert "Remote" not in cleaned
    assert "Full Time" not in cleaned
    print("test_keyword_classifier passed")

def test_coverage_calculator():
    calc = CoverageCalculator()
    resume_skills = ["Java", "Spring Boot", "SQL"]
    jd_required = ["Java", "Microservices", "Docker"]
    jd_techs = ["Java", "Spring Boot", "AWS"]
    jd_resps = ["Develop APIs", "Manage Cloud"]
    
    result = calc.calculate_coverage(resume_skills, jd_required, jd_techs, jd_resps, "I build Java APIs and manage Cloud infrastructure.")
    # 1/3 skills (33%), 2/3 techs (66%), 2/2 resps (100%)
    # (33.33 * 0.5) + (66.67 * 0.25) + (100 * 0.25) = 16.66 + 16.66 + 25 = 58.32
    assert result["coverage_score"] < 100
    assert result["coverage_score"] > 50
    print(f"test_coverage_calculator result: {result['coverage_score']}")

def test_project_relevance():
    engine = ProjectRelevanceEngine()
    projects = [
        {
            "title": "E-commerce",
            "description": "Built a Java Spring Boot backend with REST APIs",
            "technologies": ["Java", "Spring Boot", "PostgreSQL"]
        }
    ]
    jd_techs = ["Java", "Spring Boot"]
    jd_keywords = ["REST API", "Microservices"]
    jd_resps = ["Build scalable APIs"]
    
    scored = engine.score_projects(projects, jd_techs, jd_keywords, jd_resps, "E-commerce")
    # Tech Match: 2/2 (40 pts)
    # Keyword Match: 1/2 (12.5 pts)
    # Domain Match: 1/1 (15 pts)
    # Resp Match: 1/1 (10 pts)
    # Complexity: ~5 pts
    # Total: ~82.5
    assert scored[0]["relevance_score"] > 75
    assert scored[0]["rank"] == 1
    print(f"test_project_relevance result: {scored[0]['relevance_score']}")

if __name__ == "__main__":
    test_semantic_matcher()
    test_keyword_classifier()
    test_coverage_calculator()
    test_project_relevance()
    print("All scoring refinement tests passed!")
