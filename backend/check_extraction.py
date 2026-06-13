import asyncio
from app.database.database import AsyncSessionLocal
from app.models.resume_extraction import ResumeExtraction
from sqlalchemy import select
from uuid import UUID

async def check_extraction():
    target_id = UUID('46457d9d-1c8f-48c9-a7ee-a1a68604dcd2')
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ResumeExtraction).where(ResumeExtraction.resume_id == target_id))
        extraction = result.scalars().first()
        if extraction:
            print(f"Found extraction for {target_id}")
            print(f"Sections: {list(extraction.sections.keys()) if extraction.sections else 'None'}")
        else:
            print(f"No extraction found for {target_id}")

if __name__ == "__main__":
    asyncio.run(check_extraction())
