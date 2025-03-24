import logging
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.routes import router
from app.config import get_settings

from .api import router as request_config_router
from .db.session import close_db, init_db

# Get settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Email Classification API",
    description="API for classifying emails and extracting data for banking service requests",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
app.include_router(request_config_router)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Email Classification API",
        version="1.0.0",
        description="API for classifying emails and extracting data for banking service requests",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting up Email Classification API")
    await init_db()
    # Log configuration
    logger.info(f"Duplicate cache duration: {settings.duplicate_cache_days} days")
    logger.info(f"Max attachment size: {settings.max_attachment_size_mb} MB")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down Email Classification API")
    await close_db()


if __name__ == "__main__":
    # Start server
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=settings.port, 
        reload=True
    )