from typing import Optional, List, Dict, Any
import json
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.resume_extraction import ResumeExtraction
from app.models.master_resume_profile import MasterResumeProfile
from app.services.gemini_service import GeminiService
from app.services.json_validator import JsonValidator
from app.prompts.master_resume_prompt import MASTER_RESUME_PROMPT
from app.schemas.master_resume import MasterResumeResponse, MasterResumeJSON

class MasterResumeParser:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gemini_service = GeminiService()
        self.validator = JsonValidator()

    async def parse_to_master(self, resume_id: UUID) -> MasterResumeResponse:
        """
        Coordinates the parsing of extracted data into a Master Resume JSON.
        """
        logger.info(f"Starting Master Resume parsing for resume_id: {resume_id}")
        
        # 1. Fetch extraction result
        result = await self.db.execute(select(ResumeExtraction).where(ResumeExtraction.resume_id == resume_id))
        extraction = result.scalars().first()
        if not extraction:
            raise Exception("Extraction results not found. Please run extraction first.")

        # 2. Prepare Gemini prompt
        # Use .replace() instead of .format() to avoid KeyError from braces in raw text or prompt schema
        prompt = MASTER_RESUME_PROMPT.replace("{raw_text}", extraction.raw_text) \
                                   .replace("{extracted_links}", json.dumps(extraction.extracted_links, indent=2)) \
                                   .replace("{contact_info}", json.dumps(extraction.contact_info, indent=2))

        # 3. Call Gemini
        ai_response = await self.gemini_service.generate_content(prompt)
        
        # 4. Clean and Validate JSON
        master_json_dict = self.validator.clean_json_response(ai_response)
        if not self.validator.validate_master_resume(master_json_dict):
            raise Exception("AI returned JSON that does not match the required Master Resume schema")

        # 5. Store in database
        # Check if profile already exists
        profile_result = await self.db.execute(select(MasterResumeProfile).where(MasterResumeProfile.resume_id == resume_id))
        db_profile = profile_result.scalars().first()
        
        if db_profile:
            db_profile.master_resume_json = master_json_dict
            db_profile.parsing_status = "completed"
        else:
            # We need the user_id from the original resume
            from app.models.uploaded_resume import UploadedResume
            resume_result = await self.db.execute(select(UploadedResume).where(UploadedResume.id == resume_id))
            resume = resume_result.scalars().first()
            
            db_profile = MasterResumeProfile(
                resume_id=resume_id,
                user_id=resume.user_id,
                master_resume_json=master_json_dict,
                parsing_status="completed"
            )
            self.db.add(db_profile)
        
        await self.db.commit()
        await self.db.refresh(db_profile)
        
        logger.info(f"Successfully created Master Resume Profile for resume_id: {resume_id}")
        
        return MasterResumeResponse(
            status="success",
            master_resume_id=db_profile.id,
            skills_count=len(master_json_dict.get("skills", [])),
            projects_count=len(master_json_dict.get("projects", []))
        )

    async def get_master_profile(self, resume_id: UUID) -> Optional[MasterResumeProfile]:
        result = await self.db.execute(select(MasterResumeProfile).where(MasterResumeProfile.resume_id == resume_id))
        return result.scalars().first()
