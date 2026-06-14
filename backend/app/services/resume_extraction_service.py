import httpx
import re
import os
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.uploaded_resume import UploadedResume
from app.models.resume_extraction import ResumeExtraction
from app.services.pdf_extractor import PDFExtractor
from app.services.docx_extractor import DOCXExtractor
from app.services.link_extractor import LinkExtractor
from app.services.contact_extractor import ContactExtractor
from app.services.layout_extractor import LayoutExtractor
from app.services.rendering.master_template_service import MasterTemplateService
from app.schemas.extraction import ExtractionResponse, ContactInfo, ExtractedLinks
from app.models.resume_template import ResumeTemplate

class ResumeExtractionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()
        self.link_extractor = LinkExtractor()
        self.contact_extractor = ContactExtractor()
        self.layout_extractor = LayoutExtractor()
        self.template_service = MasterTemplateService()
        
        # Section keywords for basic detection
        self.section_keywords = {
            "Summary": ["summary", "profile", "objective", "about me"],
            "Experience": ["experience", "work history", "employment", "professional background"],
            "Education": ["education", "academic", "qualifications"],
            "Skills": ["skills", "technical skills", "expertise", "competencies"],
            "Projects": ["projects", "personal projects", "academic projects"],
            "Certifications": ["certifications", "licenses", "awards", "honors"],
            "Languages": ["languages"],
            "Interests": ["interests", "hobbies"]
        }

    async def extract_resume(self, resume_id: UUID) -> ExtractionResponse:
        """
        Main workflow for resume extraction.
        """
        logger.info(f"Starting extraction for resume_id: {resume_id}")
        
        # 1. Fetch resume metadata
        result = await self.db.execute(select(UploadedResume).where(UploadedResume.id == resume_id))
        resume = result.scalars().first()
        if not resume:
            raise Exception("Resume not found")
        
        if resume.upload_status == "failed":
            raise Exception(f"Cannot extract: Upload for resume {resume_id} previously failed. Please upload the file again.")

        if not resume.storage_url:
            raise Exception("Resume file not yet uploaded to storage (status: pending)")

        # 2. Download file content
        async with httpx.AsyncClient() as client:
            response = await client.get(resume.storage_url)
            if response.status_code != 200:
                raise Exception(f"Failed to download resume from storage: {response.status_code}")
            file_content = response.content

        # 3. Detect format and run appropriate extractor
        extracted_data = {}
        layout_metadata = {}
        if resume.file_type == "application/pdf":
            extracted_data = await self.pdf_extractor.extract(file_content)
            # Create a temporary file for layout extraction since LayoutExtractor needs a path
            temp_path = f"temp_{resume_id}.pdf"
            with open(temp_path, "wb") as f:
                f.write(file_content)
            try:
                layout_metadata = await self.layout_extractor.extract_layout(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        elif resume.file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            extracted_data = await self.docx_extractor.extract(file_content)
        else:
            raise Exception(f"Unsupported file type for extraction: {resume.file_type}")

        raw_text = extracted_data["raw_text"]
        
        # 4. Extract Contact Info
        contact_info_dict = self.contact_extractor.extract_contact_info(raw_text)
        contact_info = ContactInfo(**contact_info_dict)
        
        # 5. Extract Links
        format_links = extracted_data.get("links", [])
        regex_links_dict = self.link_extractor.extract_links(raw_text + "\n" + "\n".join(format_links))
        links = ExtractedLinks(**regex_links_dict)
        
        # 6. Detect Sections (Basic heuristic)
        sections = self._detect_sections(raw_text)

        # 7. Create/Update Master Template if layout was extracted
        if layout_metadata:
            template_data = self.template_service.create_template(layout_metadata)
            
            templ_result = await self.db.execute(select(ResumeTemplate).where(ResumeTemplate.resume_id == resume_id))
            db_template = templ_result.scalars().first()
            
            if db_template:
                db_template.template_html = template_data["template_html"]
                db_template.template_css = template_data["template_css"]
                db_template.layout_metadata = template_data["layout_metadata"]
                db_template.section_order = template_data["section_order"]
                db_template.hyperlinks = links.dict()
            else:
                db_template = ResumeTemplate(
                    resume_id=resume_id,
                    user_id=resume.user_id,
                    template_html=template_data["template_html"],
                    template_css=template_data["template_css"],
                    layout_metadata=template_data["layout_metadata"],
                    section_order=template_data["section_order"],
                    template_variables={},
                    hyperlinks=links.dict()
                )
                self.db.add(db_template)
        
        # 8. Store results in database
        # Check if extraction already exists
        ext_result = await self.db.execute(select(ResumeExtraction).where(ResumeExtraction.resume_id == resume_id))
        db_extraction = ext_result.scalars().first()
        
        if db_extraction:
            db_extraction.raw_text = raw_text
            db_extraction.extracted_links = links.dict()
            db_extraction.contact_info = contact_info.dict()
            db_extraction.metadata_info = extracted_data["metadata"]
            db_extraction.sections = sections
        else:
            db_extraction = ResumeExtraction(
                resume_id=resume_id,
                raw_text=raw_text,
                extracted_links=links.dict(),
                contact_info=contact_info.dict(),
                metadata_info=extracted_data["metadata"],
                sections=sections
            )
            self.db.add(db_extraction)
        
        await self.db.commit()
        await self.db.refresh(db_extraction)
        
        logger.info(f"Successfully completed extraction for resume_id: {resume_id}")
        
        return ExtractionResponse(
            resume_id=resume_id,
            raw_text=raw_text,
            contact_info=contact_info,
            links=links,
            metadata=extracted_data["metadata"],
            sections=sections
        )

    def _detect_sections(self, text: str) -> List[str]:
        """
        Detects resume sections using keyword matching.
        """
        found_sections = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip().lower()
            if not line:
                continue
            
            # Look for lines that might be headers (short, maybe capitalized in original)
            if len(line.split()) < 4:
                for section, keywords in self.section_keywords.items():
                    if any(re.search(r'\b' + re.escape(kw) + r'\b', line) for kw in keywords):
                        if section not in found_sections:
                            found_sections.append(section)
        
        return found_sections

    async def get_extraction(self, resume_id: UUID) -> Optional[ResumeExtraction]:
        result = await self.db.execute(select(ResumeExtraction).where(ResumeExtraction.resume_id == resume_id))
        return result.scalars().first()
