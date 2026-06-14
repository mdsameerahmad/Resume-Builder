from typing import List, Dict, Any, Optional
from app.services.semantic.skill_normalizer import SkillNormalizer
from app.services.semantic.synonym_registry import SynonymRegistry
from app.services.semantic.technology_mapper import TechnologyMapper

class SemanticMatcher:
    """
    Intelligent matching engine for JD requirements and resume content.
    """
    
    MATCH_SCORES = {
        "exact_match": 100,
        "normalized_match": 95,
        "synonym_match": 90,
        "technology_family_match": 80,
        "semantic_similarity_match": 70
    }

    def __init__(self):
        self.normalizer = SkillNormalizer()
        self.synonym_registry = SynonymRegistry()
        self.tech_mapper = TechnologyMapper()

    def find_match(self, jd_term: str, resume_skills: List[str], resume_text: str) -> Optional[Dict[str, Any]]:
        """
        Tries to match a JD term against resume content using prioritized strategies.
        """
        # 1. Exact Match
        for skill in resume_skills:
            if jd_term.lower() == skill.lower():
                return {"strategy": "exact_match", "resume_term": skill, "score": self.MATCH_SCORES["exact_match"]}

        # 2. Normalized Match
        norm_jd = self.normalizer.normalize(jd_term)
        for skill in resume_skills:
            if norm_jd == self.normalizer.normalize(skill):
                return {"strategy": "normalized_match", "resume_term": skill, "score": self.MATCH_SCORES["normalized_match"]}
        # Check normalized match in full text too
        if norm_jd in self.normalizer.normalize(resume_text):
            return {"strategy": "normalized_match", "resume_term": jd_term, "score": self.MATCH_SCORES["normalized_match"]}

        # 3. Synonym Match
        synonyms = self.synonym_registry.get_synonyms(jd_term)
        for syn in synonyms:
            norm_syn = self.normalizer.normalize(syn)
            # Check if synonym is in resume skills
            for skill in resume_skills:
                if norm_syn == self.normalizer.normalize(skill):
                    return {"strategy": "synonym_match", "resume_term": skill, "score": self.MATCH_SCORES["synonym_match"]}
            # Check if synonym is in full resume text (normalized)
            if norm_syn in self.normalizer.normalize(resume_text):
                return {"strategy": "synonym_match", "resume_term": syn, "score": self.MATCH_SCORES["synonym_match"]}

        # 4. Technology Family Match
        family_techs = self.tech_mapper.get_family(jd_term)
        for tech in family_techs:
            for skill in resume_skills:
                if self.normalizer.normalize(tech) == self.normalizer.normalize(skill):
                    return {"strategy": "technology_family_match", "resume_term": skill, "score": self.MATCH_SCORES["technology_family_match"]}

        # 5. Semantic Similarity (Keyword overlap fallback)
        jd_words = set(norm_jd.split())
        if len(jd_words) > 1:
            for skill in resume_skills:
                skill_words = set(self.normalizer.normalize(skill).split())
                if jd_words & skill_words:
                    return {"strategy": "semantic_similarity_match", "resume_term": skill, "score": self.MATCH_SCORES["semantic_similarity_match"]}

        return None
