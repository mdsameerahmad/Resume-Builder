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
from app.services.ats_score_calculator import ATSScoreCalculator
from app.services.recommendation_engine import RecommendationEngine

class GapAnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.skill_matcher = SkillMatcher()
        self.keyword_matcher = KeywordMatcher()
        self.project_matcher = ProjectMatcher()
        self.experience_matcher = ExperienceMatcher()
        self.score_calculator = ATSScoreCalculator()
        self.recommendation_engine = RecommendationEngine()

    async def analyze_gap(self, resume_id: UUID, job_id: UUID, user_id: UUID) -> Optional[GapAnalysis]:
        """
        Orchestrates the gap analysis process.
        resume_id is the ID of the UploadedResume (which corresponds to resume_id in MasterResumeProfile)
        """
        # 1. Fetch Resume Profile and JD
        # We query by resume_id in MasterResumeProfile which refers to the UploadedResume ID
        resume_result = await self.db.execute(select(MasterResumeProfile).where(MasterResumeProfile.resume_id == resume_id))
        resume_profile_obj = resume_result.scalars().first()
        
        jd_result = await self.db.execute(select(JobDescription).where(JobDescription.id == job_id))
        jd = jd_result.scalars().first()
        
        if not resume_profile_obj or not jd:
            logger.error(f"Master Resume Profile for resume_id {resume_id} or JD {job_id} not found")
            return None
            
        resume_profile = resume_profile_obj.master_resume_json
        parsed_jd = jd.parsed_jd or {}
        
        # 2. Extract components for matching
        resume_skills = resume_profile.get("skills", [])
        resume_projects = resume_profile.get("projects", [])
        resume_experience = resume_profile.get("experience", [])
        resume_text = str(resume_profile) # Simplified text representation
        
        jd_required_skills = parsed_jd.get("required_skills", [])
        jd_preferred_skills = parsed_jd.get("preferred_skills", [])
        jd_keywords = parsed_jd.get("ats_keywords", [])
        jd_technologies = parsed_jd.get("technologies", [])
        jd_responsibilities = parsed_jd.get("responsibilities", [])
        jd_title = jd.job_title or ""
        
        # 3. Perform matching
        skill_matches = self.skill_matcher.match_skills(resume_skills, jd_required_skills, jd_preferred_skills)
        keyword_matches = self.keyword_matcher.match_keywords(resume_text, jd_keywords)
        project_matches = self.project_matcher.match_projects(resume_projects, jd_technologies, jd_responsibilities)
        experience_matches = self.experience_matcher.match_experience(resume_experience, jd_responsibilities, jd_title)
        
        # 4. Calculate scores
        all_matches = {
            **skill_matches,
            **keyword_matches,
            "relevant_projects": project_matches,
            "relevant_experience": experience_matches
        }
        scores = self.score_calculator.calculate_scores(all_matches)
        
        # 5. Generate recommendations
        insights = self.recommendation_engine.generate_recommendations({**all_matches, **scores})
        
        # 6. Store report
        report = GapAnalysis(
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
            matched_skills=skill_matches["matched_skills"],
            missing_skills=skill_matches["missing_skills"],
            matched_keywords=keyword_matches["matched_keywords"],
            missing_keywords=keyword_matches["missing_keywords"],
            relevant_projects=project_matches,
            relevant_experience=experience_matches,
            strengths=insights["strengths"],
            weaknesses=insights["weaknesses"],
            coverage_score=scores["coverage_score"],
            ats_score=scores["ats_score"],
            recommendations=insights["optimization_recommendations"]
        )
        
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        return report
