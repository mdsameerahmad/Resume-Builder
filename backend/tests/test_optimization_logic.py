import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.link_preservation_service import LinkPreservationService, ContactPreservationService
from app.services.content_prioritizer import ContentPrioritizer, KeywordInjector

def test_preservation_services():
    link_service = LinkPreservationService()
    contact_service = ContactPreservationService()
    
    orig_links = {"linkedin": "https://linkedin.com/in/test", "github": "https://github.com/test"}
    opt_links = {"linkedin": "MODIFIED", "website": "https://test.com"}
    
    preserved_links = link_service.preserve_links(orig_links, opt_links)
    assert preserved_links["linkedin"] == "https://linkedin.com/in/test"
    assert preserved_links["github"] == "https://github.com/test"
    assert preserved_links["website"] == "https://test.com"
    
    orig_contact = {"full_name": "John Doe", "email": "test@test.com", "phone": "12345"}
    opt_contact = {"full_name": "HALLUCINATED", "email": "BAD@BAD.COM"}
    
    preserved_contact = contact_service.preserve_contact(orig_contact, opt_contact)
    assert preserved_contact["full_name"] == "John Doe"
    assert preserved_contact["email"] == "test@test.com"
    print("test_preservation_services passed")

def test_content_prioritizer():
    prioritizer = ContentPrioritizer()
    
    orig_skills = ["React", "Java", "Python"]
    matched = ["Java"]
    prioritized = prioritizer.prioritize_skills(orig_skills, matched)
    assert prioritized[0] == "Java"
    assert len(prioritized) == 3
    
    projects = [{"title": "P1"}, {"title": "P2"}]
    rankings = [{"title": "P2", "relevance_score": 90}, {"title": "P1", "relevance_score": 10}]
    prioritized_projs = prioritizer.prioritize_projects(projects, rankings)
    assert prioritized_projs[0]["title"] == "P2"
    print("test_content_prioritizer passed")

def test_keyword_injector():
    injector = KeywordInjector()
    missing = ["JavaScript", "AWS"]
    resume_content = "I am a JS developer working on Amazon Web Services"
    injectable = injector.get_injectable_keywords(missing, resume_content)
    # JS matches JavaScript semantically, Amazon Web Services matches AWS
    assert "JavaScript" in injectable
    assert "AWS" in injectable
    print("test_keyword_injector passed")

if __name__ == "__main__":
    test_preservation_services()
    test_content_prioritizer()
    test_keyword_injector()
    print("All Phase 9/10 logic tests passed!")
