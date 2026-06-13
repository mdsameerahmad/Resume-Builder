import asyncio
from app.database.database import AsyncSessionLocal
from app.models.master_resume import MasterResume
from app.models.job_description import JobDescription
from sqlalchemy import select

async def check_ids():
    async with AsyncSessionLocal() as session:
        # Check Master Resumes
        resumes = await session.execute(select(MasterResume))
        resume_ids = [str(r.id) for r in resumes.scalars().all()]
        print(f"Existing Resume IDs: {resume_ids}")
        
        # Check Job Descriptions
        jds = await session.execute(select(JobDescription))
        jd_ids = [str(j.id) for j in jds.scalars().all()]
        print(f"Existing JD IDs: {jd_ids}")

if __name__ == "__main__":
    asyncio.run(check_ids())
