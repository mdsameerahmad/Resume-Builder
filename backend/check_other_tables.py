import asyncio
from app.database.database import AsyncSessionLocal
from app.models.uploaded_resume import UploadedResume
from app.models.resume_extraction import ResumeExtraction
from sqlalchemy import select

async def check_all_tables():
    async with AsyncSessionLocal() as session:
        # Check Uploaded Resumes
        uploaded = await session.execute(select(UploadedResume))
        print(f"Uploaded Resume IDs: {[str(r.id) for r in uploaded.scalars().all()]}")
        
        # Check Extractions
        extractions = await session.execute(select(ResumeExtraction))
        print(f"Extraction IDs: {[str(e.id) for e in extractions.scalars().all()]}")

if __name__ == "__main__":
    asyncio.run(check_all_tables())
