import json
from typing import Dict, Any, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.services.gemini_service import GeminiService
from app.services.json_validator import JsonValidator
from app.prompts.job_intelligence_prompt import JOB_INTELLIGENCE_PROMPT
from app.services.job_title_inference import JobTitleInferenceService
from app.services.industry_classifier import IndustryClassifier
from app.services.seniority_classifier import SeniorityClassifier
from app.models.job_description import JobDescription
from app.schemas.job_description import JDAnalysisSchema, JDAnalysisResponse

class JDAnalyzer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gemini_service = GeminiService()
        self.validator = JsonValidator()
        self.title_inferrer = JobTitleInferenceService()
        self.industry_classifier = IndustryClassifier()
        self.seniority_classifier = SeniorityClassifier()

    async def analyze_jd(self, raw_jd: str, user_id: UUID) -> JDAnalysisResponse:
        """
        Analyzes a raw Job Description using Gemini AI with enhanced intelligence.
        """
        logger.info("Starting Enhanced JD Analysis...")
        
        # 1. Prepare Prompt
        prompt = JOB_INTELLIGENCE_PROMPT.replace("{raw_jd}", raw_jd)
        
        # 2. Call Gemini
        ai_response = await self.gemini_service.generate_content(prompt)
        
        # 3. Clean and Validate JSON
        parsed_json = self.validator.clean_json_response(ai_response)
        
        # 4. Post-processing with Specialized Services (if needed)
        # If Gemini fails to infer title/industry, use services as fallback
        if not parsed_json.get("job_title"):
            inference = self.title_inferrer.infer_title(
                parsed_json.get("required_skills", []),
                parsed_json.get("technologies", []),
                parsed_json.get("responsibilities", [])
            )
            parsed_json["job_title"] = inference["inferred_title"]
            parsed_json["confidence_score"] = inference["confidence_score"]

        if not parsed_json.get("industry"):
            industry_info = self.industry_classifier.classify_industry(
                parsed_json.get("job_title", ""),
                parsed_json.get("required_skills", [])
            )
            parsed_json["industry"] = industry_info["industry"]

        if not parsed_json.get("seniority_level"):
            parsed_json["seniority_level"] = self.seniority_classifier.classify(
                parsed_json.get("experience_required", "")
            )

        # 5. Store in database
        try:
            db_jd = JobDescription(
                user_id=user_id,
                raw_jd=raw_jd,
                parsed_jd=parsed_json,
                job_title=parsed_json.get("job_title", ""),
                industry=parsed_json.get("industry", ""),
                job_category=parsed_json.get("job_category", ""),
                department=parsed_json.get("department", ""),
                seniority_level=parsed_json.get("seniority_level", ""),
                confidence_score=parsed_json.get("confidence_score", 0.0)
            )
            self.db.add(db_jd)
            await self.db.commit()
            await self.db.refresh(db_jd)
            
            logger.info(f"Successfully analyzed and stored JD: {db_jd.id}")
            
            return JDAnalysisResponse(
                status="success",
                job_id=db_jd.id,
                analysis=JDAnalysisSchema(**parsed_json)
            )
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error during JD storage: {e}")
            raise e
