import json
from typing import Optional, Dict, Any
from uuid import UUID
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.master_resume_profile import MasterResumeProfile
from app.models.job_description import JobDescription
from app.models.gap_analysis import GapAnalysis
from app.models.optimized_resume import OptimizedResume

from app.services.gemini_service import GeminiService
from app.services.json_validator import JsonValidator
from app.services.link_preservation_service import LinkPreservationService, ContactPreservationService
from app.services.content_prioritizer import ContentPrioritizer, KeywordInjector
from app.prompts.resume_optimization_prompt import RESUME_OPTIMIZATION_PROMPT

class ResumeOptimizer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gemini_service = GeminiService()
        self.validator = JsonValidator()
        self.link_service = LinkPreservationService()
        self.contact_service = ContactPreservationService()
        self.prioritizer = ContentPrioritizer()
        self.keyword_injector = KeywordInjector()

    async def optimize_resume(self, resume_id: UUID, job_id: UUID, user_id: UUID) -> Optional[OptimizedResume]:
        """
        Main optimization pipeline.
        """
        logger.info(f"Starting resume optimization for resume_id: {resume_id}, job_id: {job_id}")

        # 1. Fetch all required inputs
        resume_profile_obj = (await self.db.execute(select(MasterResumeProfile).where(MasterResumeProfile.resume_id == resume_id))).scalars().first()
        jd_obj = (await self.db.execute(select(JobDescription).where(JobDescription.id == job_id))).scalars().first()
        gap_obj = (await self.db.execute(select(GapAnalysis).where(GapAnalysis.resume_id == resume_id, GapAnalysis.job_id == job_id))).scalars().first()

        if not resume_profile_obj or not jd_obj or not gap_obj:
            logger.error("Required data for optimization missing (Resume Profile, JD, or Gap Analysis)")
            return None

        resume_profile = resume_profile_obj.master_resume_json
        parsed_jd = jd_obj.parsed_jd
        
        # 2. Content Prioritization (Deterministic)
        prioritized_skills = self.prioritizer.prioritize_skills(
            resume_profile.get("skills", []),
            gap_obj.matched_skills or []
        )
        
        prioritized_projects = self.prioritizer.prioritize_projects(
            resume_profile.get("projects", []),
            gap_obj.project_rankings or []
        )
        
        prioritized_experience = self.prioritizer.prioritize_experience(
            resume_profile.get("experience", []),
            gap_obj.relevant_experience or []
        )

        # 3. Keyword Injection Preparation
        injectable_keywords = self.keyword_injector.get_injectable_keywords(
            gap_obj.missing_keywords or [],
            str(resume_profile)
        )

        # 4. LLM Optimization (Summary & Bullet Rewriting)
        prompt = RESUME_OPTIMIZATION_PROMPT.format(
            resume_profile=json.dumps({
                "summary": resume_profile.get("professional_summary", ""),
                "projects": prioritized_projects,
                "experience": prioritized_experience
            }),
            parsed_jd=json.dumps(parsed_jd),
            gap_analysis=json.dumps({
                "strengths": gap_obj.strengths,
                "weaknesses": gap_obj.weaknesses
            }),
            injectable_keywords=json.dumps(injectable_keywords)
        )

        ai_response = await self.gemini_service.generate_content(prompt)
        optimized_data = self.validator.clean_json_response(ai_response)

        # 5. Link and Contact Preservation (Safety Layer)
        final_links = self.link_service.preserve_links(
            resume_profile.get("links", {}),
            optimized_data.get("links", {})
        )
        final_contact = self.contact_service.preserve_contact(
            resume_profile.get("contact", {}),
            optimized_data.get("contact", {})
        )

        # 6. Compose Final JSON
        final_resume_json = {
            "contact": final_contact,
            "links": final_links,
            "summary": optimized_data.get("summary", ""),
            "skills": prioritized_skills,
            "projects": optimized_data.get("projects", prioritized_projects),
            "experience": optimized_data.get("experience", prioritized_experience),
            "education": resume_profile.get("education", []),
            "certifications": resume_profile.get("certifications", []),
            "achievements": resume_profile.get("achievements", []),
            "languages": resume_profile.get("languages", []),
            "optimization_metadata": {
                "ats_keywords_used": optimized_data.get("optimization_metadata", {}).get("ats_keywords_used", []),
                "projects_prioritized": [p.get("title") for p in prioritized_projects],
                "optimization_score": optimized_data.get("optimization_metadata", {}).get("optimization_score", 0.0)
            }
        }

        # 7. Persist to DB
        db_optimized = OptimizedResume(
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
            optimized_resume_json=final_resume_json,
            optimization_metadata=final_resume_json["optimization_metadata"]
        )

        self.db.add(db_optimized)
        await self.db.commit()
        await self.db.refresh(db_optimized)

        logger.info(f"Successfully generated and stored optimized resume: {db_optimized.id}")
        return db_optimized
