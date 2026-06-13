from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import os

from app.database.session import get_db
from app.services.layout_extractor import LayoutExtractor
from app.services.layout_analyzer import LayoutAnalyzer
from app.services.template_builder import TemplateBuilder
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

        # Use storage_url to identify the file
        file_identifier = resume.storage_url or resume.stored_filename
        
        # If not found locally, this will fail - we should ideally use storage service
        # But for Phase 6 setup, we focus on the service logic
        
        extractor = LayoutExtractor()
        analyzer = LayoutAnalyzer()
        builder = TemplateBuilder()
        
        # 2. Extract and Analyze
        # Note: In a production environment, file_path would be a temporary local file
        # extracted_layout = await extractor.extract_layout(file_path)
        
        # MOCKING extraction for now since we don't have a physical file in the sandbox
        extracted_layout = {
            "page": {"width": 595, "height": 841, "page_count": 1},
            "fonts": ["Arial"],
            "font_sizes": [10, 12, 14],
            "colors": ["#000000"],
            "margins": {"top": 40, "bottom": 40, "left": 40, "right": 40},
            "elements": []
        }
        
        analysis = await analyzer.analyze_sections(extracted_layout)
        
        # 3. Build Template
        template_html = await builder.build_template(extracted_layout, analysis)
        
        # 4. Store in Database
        # Check if exists
        template_result = await db.execute(select(ResumeTemplate).where(ResumeTemplate.resume_id == resume_id))
        db_template = template_result.scalars().first()
        
        template_variables = {
            "contact": "contact",
            "professional_summary": "professional_summary",
            "skills": "skills",
            "experience": "experience",
            "projects": "projects",
            "education": "education"
        }
        
        if db_template:
            db_template.template_html = template_html
            db_template.layout_metadata = extracted_layout
            db_template.section_order = analysis["section_order"]
            db_template.template_variables = template_variables
        else:
            db_template = ResumeTemplate(
                resume_id=resume_id,
                user_id=resume.user_id,
                template_html=template_html,
                layout_metadata=extracted_layout,
                section_order=analysis["section_order"],
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
