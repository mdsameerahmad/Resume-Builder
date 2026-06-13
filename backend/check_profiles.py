import asyncio
from app.database.database import AsyncSessionLocal
from app.models.master_resume_profile import MasterResumeProfile
from sqlalchemy import select

async def check_profiles():
    async with AsyncSessionLocal() as session:
        profiles = await session.execute(select(MasterResumeProfile))
        print(f"Existing Profile Resume IDs: {[str(p.resume_id) for p in profiles.scalars().all()]}")

if __name__ == "__main__":
    asyncio.run(check_profiles())
