import asyncio
from app.database.database import AsyncSessionLocal
from app.services.gap_analysis_service import GapAnalysisService
from uuid import UUID

async def test_analysis():
    resume_id = UUID('46457d9d-1c8f-48c9-a7ee-a1a68604dcd2')
    job_id = UUID('88eda2f4-6c08-4168-9780-1b5c17e6f41e')
    user_id = UUID('00000000-0000-0000-0000-000000000000')
    
    async with AsyncSessionLocal() as session:
        service = GapAnalysisService(session)
        report = await service.analyze_gap(resume_id, job_id, user_id)
        if report:
            print(f"Analysis successful! Report ID: {report.id}")
            print(f"ATS Score: {report.ats_score}")
        else:
            print("Analysis failed.")

if __name__ == "__main__":
    asyncio.run(test_analysis())
