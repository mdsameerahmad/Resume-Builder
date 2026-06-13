import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.services.job_title_inference import JobTitleInferenceService
from app.services.industry_classifier import IndustryClassifier
from app.services.seniority_classifier import SeniorityClassifier

def test_job_title_inference():
    service = JobTitleInferenceService()
    
    # Test ServiceNow
    res1 = service.infer_title(["ServiceNow", "JavaScript"], ["GlideRecord"], ["Build business rules"])
    assert res1["inferred_title"] == "ServiceNow Developer"
    assert res1["confidence_score"] > 0.5
    
    # Test Backend
    res2 = service.infer_title(["Java", "Spring Boot"], ["Microservices"], ["Develop APIs"])
    assert res2["inferred_title"] == "Backend Developer"
    
    # Test Frontend
    res3 = service.infer_title(["React", "HTML", "CSS"], ["JavaScript"], ["Build UI components"])
    assert res3["inferred_title"] == "Frontend Developer"

def test_industry_classification():
    service = IndustryClassifier()
    
    # Test IT
    res1 = service.classify_industry("ServiceNow Developer", ["ServiceNow", "ITSM"])
    assert res1["industry"] == "Information Technology"
    
    # Test Analytics
    res2 = service.classify_industry("Data Analyst", ["Python", "Pandas", "SQL"])
    assert res2["industry"] == "Analytics"

def test_seniority_classification():
    service = SeniorityClassifier()
    
    assert service.classify("0-1 years of experience") == "Entry Level"
    assert service.classify("2 years experience") == "Junior"
    assert service.classify("5 years of experience") == "Mid Level"
    assert service.classify("8+ years of experience") == "Senior"
    assert service.classify("Senior Software Engineer") == "Senior"

if __name__ == "__main__":
    # Simple manual run if pytest is not available
    print("Running manual tests...")
    test_job_title_inference()
    test_industry_classification()
    test_seniority_classification()
    print("All tests passed!")
