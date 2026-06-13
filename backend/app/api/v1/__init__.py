from fastapi import APIRouter

from .health import router as health_router
from .database import router as database_router
from .resume.upload import router as resume_router
from .resume.extract import router as extract_router
from .resume.parse import router as parse_router
from .template.template import router as template_router
from .jd.jd import router as jd_router
from .gap.gap import router as gap_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(database_router, prefix="/database", tags=["Database"])
api_router.include_router(resume_router, prefix="/resume", tags=["Resume"])
api_router.include_router(extract_router, prefix="/resume", tags=["Extraction"])
api_router.include_router(parse_router, prefix="/resume", tags=["Parsing"])
api_router.include_router(template_router, prefix="/template", tags=["Template"])
api_router.include_router(jd_router, prefix="/jd", tags=["Job Description"])
api_router.include_router(gap_router, prefix="/gap", tags=["Gap Analysis"])
