from fastapi import APIRouter

from .health import router as health_router
from .database import router as database_router
from .resume.upload import router as resume_router
from .resume.extract import router as extract_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(database_router, prefix="/database", tags=["Database"])
api_router.include_router(resume_router, prefix="/resume", tags=["Resume"])
api_router.include_router(extract_router, prefix="/resume", tags=["Extraction"])
