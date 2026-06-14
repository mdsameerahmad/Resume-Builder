import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.semantic.semantic_matcher import SemanticMatcher
from app.services.semantic.skill_normalizer import SkillNormalizer
from app.services.semantic.synonym_registry import SynonymRegistry
from app.services.semantic.technology_mapper import TechnologyMapper

def test_advanced_semantic_matcher():
    matcher = SemanticMatcher()
    
    resume_skills = ["RESTful API Design", "FastAPI", "Docker", "AWS", "PostgreSQL", "Postman"]
    resume_text = "Experienced Backend Developer working with RESTful APIs, FastAPI, and Docker. Managed AWS EC2 instances."
    
    # Test 1: REST API -> RESTful API Design (Synonym Match)
    match1 = matcher.find_match("REST API", resume_skills, resume_text)
    assert match1 is not None
    assert match1["strategy"] == "synonym_match"
    print("Test 1 Passed: REST API matched")

    # Test 2: DevOps -> Docker (Synonym Match via Registry)
    match2 = matcher.find_match("DevOps", resume_skills, resume_text)
    assert match2 is not None
    assert match2["strategy"] == "synonym_match"
    print("Test 2 Passed: DevOps matched via Docker")

    # Test 3: API Development -> FastAPI (Synonym Match via Registry)
    match3 = matcher.find_match("API Development", resume_skills, resume_text)
    assert match3 is not None
    assert match3["strategy"] == "synonym_match"
    print("Test 3 Passed: API Development matched via FastAPI")

    # Test 4: Cloud Platform -> AWS (Synonym Match)
    match4 = matcher.find_match("Cloud Platform", resume_skills, resume_text)
    assert match4 is not None
    assert match4["strategy"] == "synonym_match"
    print("Test 4 Passed: Cloud Platform matched via AWS")

    # Test 5: Normalization Match
    match5 = matcher.find_match("node.js", ["NodeJS"], "I use NodeJS")
    assert match5 is not None
    assert match5["strategy"] == "normalized_match"
    print("Test 5 Passed: Normalization Match")

if __name__ == "__main__":
    test_advanced_semantic_matcher()
    print("All Phase 8.2 Semantic Matching tests passed!")
