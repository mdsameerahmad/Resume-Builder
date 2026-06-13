from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger
from app.middleware.exceptions import global_exception_handler
from app.api.v1 import api_router
from app.database.database import startup_db_check

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Set CORS middleware
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add global exception handler
    application.add_exception_handler(Exception, global_exception_handler)

    # Include routers
    application.include_router(api_router, prefix=settings.API_V1_STR)
    
    return application

app = create_application()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up ATS Resume Agent...")
    await startup_db_check()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down ATS Resume Agent...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
