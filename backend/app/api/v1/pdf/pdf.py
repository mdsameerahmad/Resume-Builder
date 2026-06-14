from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import os
from loguru import logger

from app.database.session import get_db
from app.models.optimized_resume import OptimizedResume
from app.models.generated_resume import GeneratedResume
from app.models.resume_template import ResumeTemplate
from app.schemas.generated_resume import PDFGenerateRequest, PDFGenerateResponse, PDFDetailResponse
from app.services.compression.page_optimizer import PageOptimizer
from app.services.rendering.template_engine import TemplateEngine
from app.services.rendering.pdf_generator import PDFGenerator
from app.services.rendering.master_template_service import MasterTemplateService

router = APIRouter()

# Directory for storing generated files
OUTPUT_DIR = "static/resumes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.post("/generate", response_model=PDFGenerateResponse)
async def generate_pdf(
    request: PDFGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Transforms Optimized Resume JSON into a one-page A4 PDF using the Master Template.
    """
    try:
        # 1. Fetch Optimized Resume
        result = await db.execute(select(OptimizedResume).where(OptimizedResume.id == request.optimized_resume_id))
        optimized = result.scalars().first()
        if not optimized:
            raise HTTPException(status_code=404, detail="Optimized resume not found")

        # 2. Fetch Master Template
        t_result = await db.execute(select(ResumeTemplate).where(ResumeTemplate.resume_id == optimized.resume_id))
        template = t_result.scalars().first()
        
        # 3. Page Compression Engine
        optimizer = PageOptimizer()
        compressed_json = optimizer.optimize_layout(optimized.optimized_resume_json)

        # 4. HTML Rendering
        renderer = TemplateEngine()
        if template:
            logger.info(f"Using Master Template for resume {optimized.resume_id}")
            # Rebuild from stored source layout so renderer improvements apply
            # to existing resumes without requiring another upload/extraction.
            template_data = MasterTemplateService().create_template(template.layout_metadata)
            html_content = renderer.render_custom_template(
                template_data["template_html"],
                template_data["template_css"],
                compressed_json
            )
        else:
            logger.warning(f"No Master Template found for resume {optimized.resume_id}. Falling back to default.")
            html_content = renderer.render_resume(compressed_json)
        
        # Save HTML for debugging/preview
        html_filename = f"{optimized.id}.html"
        html_path = os.path.join(OUTPUT_DIR, html_filename)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 4. PDF Generation (Phase 12)
        pdf_generator = PDFGenerator()
        pdf_filename = f"{optimized.id}.pdf"
        pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
        
        success = await pdf_generator.generate_pdf(html_content, pdf_path)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")

        # 5. Store in DB
        db_generated = GeneratedResume(
            user_id=optimized.user_id,
            resume_id=optimized.resume_id,
            job_id=optimized.job_id,
            optimized_resume_id=optimized.id,
            pdf_url=f"/static/resumes/{pdf_filename}",
            html_url=f"/static/resumes/{html_filename}",
            page_count=1,
            is_one_page=True
        )
        db.add(db_generated)
        await db.commit()
        await db.refresh(db_generated)

        return PDFGenerateResponse(
            generated_resume_id=db_generated.id,
            page_count=1,
            is_one_page=True,
            pdf_url=db_generated.pdf_url,
            html_url=db_generated.html_url,
            created_at=db_generated.created_at
        )

    except Exception as e:
        logger.error(f"PDF Generation error: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{generated_id}/preview")
async def preview_pdf(generated_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Returns the HTML preview of a generated resume.
    """
    try:
        result = await db.execute(select(GeneratedResume).where(GeneratedResume.id == generated_id))
        generated = result.scalars().first()
        if not generated or not generated.html_url:
            raise HTTPException(status_code=404, detail="HTML preview not found")
        
        file_path = generated.html_url.replace("/static/resumes/", os.path.join(OUTPUT_DIR, ""))
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Preview file not found on disk")
        
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        logger.error(f"Preview error: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{generated_id}", response_model=PDFDetailResponse)
async def get_pdf_details(generated_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GeneratedResume).where(GeneratedResume.id == generated_id))
    generated = result.scalars().first()
    if not generated:
        raise HTTPException(status_code=404, detail="Generated resume not found")
    return generated

@router.get("/{generated_id}/download")
async def download_pdf(generated_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GeneratedResume).where(GeneratedResume.id == generated_id))
    generated = result.scalars().first()
    if not generated or not generated.pdf_url:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    file_path = generated.pdf_url.replace("/static/resumes/", os.path.join(OUTPUT_DIR, ""))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File on disk not found")
        
    return FileResponse(path=file_path, filename=f"ATS_Resume_{generated_id}.pdf", media_type='application/pdf')
