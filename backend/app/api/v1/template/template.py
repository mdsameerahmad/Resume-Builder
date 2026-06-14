from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import os
import tempfile
import httpx

from app.database.session import get_db
from app.services.layout_extractor import LayoutExtractor
from app.services.rendering.master_template_service import MasterTemplateService
from app.services.html_generator import HTMLGenerator
from app.models.uploaded_resume import UploadedResume
from app.models.resume_template import ResumeTemplate
from app.models.master_resume_profile import MasterResumeProfile
from app.schemas.template import TemplateCreateResponse, ResumeTemplateSchema
from loguru import logger

router = APIRouter()

@router.post("/generate/{resume_id}", response_model=TemplateCreateResponse)
async def generate_template(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyzes an uploaded resume PDF and generates a reusable HTML template.
    """
    try:
        # 1. Fetch Resume metadata
        result = await db.execute(select(UploadedResume).where(UploadedResume.id == resume_id))
        resume = result.scalars().first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Extraction already creates the high-fidelity template. Make this
        # endpoint idempotent instead of depending on a deleted temp file.
        template_result = await db.execute(select(ResumeTemplate).where(ResumeTemplate.resume_id == resume_id))
        existing_template = template_result.scalars().first()
        if existing_template:
            return TemplateCreateResponse(
                status="success",
                template_id=existing_template.id,
                resume_id=resume_id
            )

        if resume.file_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Layout-preserving templates currently require a PDF")
        if not resume.storage_url:
            raise HTTPException(status_code=409, detail="Resume file is not available in storage")

        extractor = LayoutExtractor()
        builder = MasterTemplateService()

        # Rebuild only when needed by downloading the durable original file.
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(resume.storage_url)
            response.raise_for_status()

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            extracted_layout = await extractor.extract_layout(temp_path)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

        # 3. Build a template from the actual fonts, dimensions and sections.
        template_data = builder.create_template(extracted_layout)
        template_html = template_data["template_html"]
        template_css = template_data["template_css"]
        
        # 4. Store in Database
        # Check if exists
        db_template = None
        
        template_variables = {
            "contact": "contact",
            "professional_summary": "professional_summary",
            "skills": "skills",
            "experience": "experience",
            "projects": "projects",
            "education": "education"
        }
        
        db_template = ResumeTemplate(
            resume_id=resume_id,
            user_id=resume.user_id,
            template_html=template_html,
            template_css=template_css,
            layout_metadata=extracted_layout,
            section_order=template_data["section_order"],
            template_variables=template_variables
        )
        db.add(db_template)
            
        await db.commit()
        await db.refresh(db_template)
        
        return TemplateCreateResponse(
            status="success",
            template_id=db_template.id,
            resume_id=resume_id
        )
    except Exception as e:
        logger.error(f"Template generation error: {e}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{resume_id}", response_model=ResumeTemplateSchema)
async def get_template(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ResumeTemplate).where(ResumeTemplate.resume_id == resume_id))
    template = result.scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.get("/{resume_id}/preview")
async def preview_template(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Renders the template with data from Master Resume Profile.
    """
    # 1. Get Template
    template_result = await db.execute(select(ResumeTemplate).where(ResumeTemplate.resume_id == resume_id))
    template = template_result.scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    # 2. Get Master Profile Data
    profile_result = await db.execute(select(MasterResumeProfile).where(MasterResumeProfile.resume_id == resume_id))
    profile = profile_result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Master Resume Profile not found")
        
    # 3. Generate HTML
    generator = HTMLGenerator()
    html_content = await generator.generate_html(template.template_html, profile.master_resume_json)
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)
