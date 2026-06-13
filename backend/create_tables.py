import asyncio
from app.database.database import async_engine
from app.database.base import Base
# Import all models to ensure they are registered with Base
from app.models import user, master_resume, resume_links, job_description, generated_resume, ats_report, gap_analysis, uploaded_resume, resume_extraction, master_resume_profile, resume_template

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())
