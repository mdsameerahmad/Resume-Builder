from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional, Dict, Any
from loguru import logger

from app.models.master_resume_profile import MasterResumeProfile
from app.models.job_description import JobDescription
from app.models.gap_analysis import GapAnalysis

from app.services.skill_matcher import SkillMatcher
from app.services.keyword_matcher import KeywordMatcher
from app.services.project_matcher import ProjectMatcher
from app.services.experience_matcher import ExperienceMatcher
from app.services.recommendation_engine import RecommendationEngine

from app.services.scoring.coverage_calculator import CoverageCalculator
from app.services.scoring.ats_score_engine import ATSScoreEngine
from app.services.scoring.project_relevance_engine import ProjectRelevanceEngine
from app.services.scoring.keyword_classifier import KeywordClassifier
from app.services.scoring.semantic_matcher import SemanticMatcher as SimpleSemanticMatcher # To avoid name clash

from app.services.semantic.semantic_matcher import SemanticMatcher as AdvancedSemanticMatcher

class GapAnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.skill_matcher = SkillMatcher()
        self.keyword_matcher = KeywordMatcher()
        self.project_matcher = ProjectMatcher()
        self.experience_matcher = ExperienceMatcher()
        
        # New Scoring Engines
        self.coverage_calc = CoverageCalculator()
        self.ats_engine = ATSScoreEngine()
        self.project_engine = ProjectRelevanceEngine()
        self.keyword_classifier = KeywordClassifier()
        self.simple_semantic_matcher = SimpleSemanticMatcher()
        
        # Advanced Semantic Engine
        self.advanced_semantic_matcher = AdvancedSemanticMatcher()
        
        self.recommendation_engine = RecommendationEngine()

    async def analyze_gap(self, resume_id: UUID, job_id: UUID, user_id: UUID) -> Optional[GapAnalysis]:
        """
        Orchestrates the gap analysis process with refined scoring and advanced semantic matching.
        """
        # 1. Fetch Resume Profile and JD
        resume_result = await self.db.execute(select(MasterResumeProfile).where(MasterResumeProfile.resume_id == resume_id))
        resume_profile_obj = resume_result.scalars().first()
        
        jd_result = await self.db.execute(select(JobDescription).where(JobDescription.id == job_id))
        jd = jd_result.scalars().first()
        
        if not resume_profile_obj or not jd:
            logger.error(f"Master Resume Profile for resume_id {resume_id} or JD {job_id} not found")
            return None
            
        resume_profile = resume_profile_obj.master_resume_json
        parsed_jd = jd.parsed_jd or {}
        
        # 2. Extract components
        resume_skills = resume_profile.get("skills", [])
        resume_projects = resume_profile.get("projects", [])
        resume_experience = resume_profile.get("experience", [])
        resume_education = resume_profile.get("education", [])
        resume_certs = resume_profile.get("certifications", [])
        resume_text = str(resume_profile)
        
        jd_required_skills = parsed_jd.get("required_skills", [])
        jd_preferred_skills = parsed_jd.get("preferred_skills", [])
        jd_keywords = parsed_jd.get("ats_keywords", [])
        jd_technologies = parsed_jd.get("technologies", [])
        jd_responsibilities = parsed_jd.get("responsibilities", [])
        jd_title = jd.job_title or ""
        jd_industry = jd.industry or ""
        
        # 3. Refine Keywords (Exclude Job Titles)
        refined_jd_keywords = self.keyword_classifier.classify_keywords(jd_keywords)
        
        # 4. Perform Matching with Advanced Semantic Engine
        semantic_match_details = []
        matched_skills = []
        missing_skills = []
        
        all_jd_requirements = jd_required_skills + jd_preferred_skills
        for req in all_jd_requirements:
            match = self.advanced_semantic_matcher.find_match(req, resume_skills, resume_text)
            if match:
                matched_skills.append(req)
                semantic_match_details.append({
                    "jd_term": req,
                    "resume_term": match["resume_term"],
                    "confidence": match["score"]
                })
            else:
                missing_skills.append(req)

        # 5. Keyword Matching (also semantic)
        matched_keywords = []
        missing_keywords = []
        for kw in refined_jd_keywords:
            match = self.advanced_semantic_matcher.find_match(kw, resume_skills, resume_text)
            if match:
                matched_keywords.append(kw)
            else:
                missing_keywords.append(kw)
        
        keyword_match_percentage = (len(matched_keywords) / len(refined_jd_keywords) * 100) if refined_jd_keywords else 0.0

        # Refined Project Scoring
        project_rankings = self.project_engine.score_projects(
            resume_projects, jd_technologies, refined_jd_keywords, jd_responsibilities, jd_industry
        )
        
        experience_matches = self.experience_matcher.match_experience(resume_experience, jd_responsibilities, jd_title)
        
        # 6. Calculate Refined Coverage Score
        # We pass matched_skills and missing_skills directly to avoid redundant work
        total_reqs = len(all_jd_requirements)
        skills_coverage = (len(matched_skills) / total_reqs * 100) if total_reqs > 0 else 100
        
        coverage_result = self.coverage_calc.calculate_coverage(
            resume_skills, jd_required_skills, jd_technologies, jd_responsibilities, resume_text
        )
        # Use semantic skills_coverage instead of simple exact match
        coverage_score = (
            (skills_coverage * 0.50) + 
            (coverage_result["breakdown"]["tech_coverage"] * 0.25) + 
            (coverage_result["breakdown"]["resp_coverage"] * 0.25)
        )
        
        # 7. Calculate Refined ATS Score
        top_project_score = project_rankings[0]["relevance_score"] if project_rankings else 0.0
        top_exp_score = min(100, experience_matches[0]["relevance_score"] * 10) if experience_matches else 0.0
        
        education_score = 100.0 if resume_education else 0.0
        cert_score = 100.0 if resume_certs else 0.0
        
        ats_components = {
            "required_skills": skills_coverage,
            "ats_keywords": keyword_match_percentage,
            "projects": top_project_score,
            "experience": top_exp_score,
            "education": education_score,
            "certifications": cert_score
        }
        
        ats_result = self.ats_engine.calculate_ats_score(ats_components)
        ats_score = ats_result["ats_score"]
        breakdown = ats_result["breakdown"]
        
        # 8. Generate recommendations
        all_data_for_rec = {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "relevant_projects": project_rankings,
            "relevant_experience": experience_matches,
            "coverage_score": coverage_score,
            "ats_score": ats_score
        }
        insights = self.recommendation_engine.generate_recommendations(all_data_for_rec)
        
        # 9. Store report
        avg_confidence = sum(m["confidence"] for m in semantic_match_details) / len(semantic_match_details) if semantic_match_details else 0.0
        
        report = GapAnalysis(
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            project_rankings=project_rankings,
            relevant_experience=experience_matches,
            semantic_matches=semantic_match_details,
            matching_confidence=avg_confidence,
            strengths=insights["strengths"],
            weaknesses=insights["weaknesses"],
            coverage_score=round(coverage_score, 2),
            ats_score=ats_score,
            skill_score=breakdown["required_skills"],
            keyword_score=breakdown["ats_keywords"],
            project_score=breakdown["projects"],
            experience_score=breakdown["experience"],
            education_score=breakdown["education"],
            certification_score=breakdown["certifications"],
            recommendations=insights["optimization_recommendations"]
        )
        
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        return report
