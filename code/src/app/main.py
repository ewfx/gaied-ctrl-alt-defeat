import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.routes import router
from app.core.api_manager import ApiManager
from app.core.llm_handler import LLMHandler
from app.services.email_processor import EmailProcessor
from app.services.duplicate_detector import DuplicateDetector
from app.services.data_extractor import DataExtractor
from app.services.classification_service import ClassificationService
from app.config import get_settings, get_request_types, get_extraction_rules

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

# Load data
request_types = get_request_types()
extraction_rules = get_extraction_rules()

# Initialize services
api_manager = ApiManager()
llm_handler = LLMHandler(api_manager=api_manager)
email_processor = EmailProcessor(max_attachment_size_mb=settings.max_attachment_size_mb)
duplicate_detector = DuplicateDetector(cache_duration_days=settings.duplicate_cache_days)
data_extractor = DataExtractor(llm_handler=llm_handler)

# Create classification service dependency
def get_classification_service():
    return ClassificationService(
        llm_handler=llm_handler,
        email_processor=email_processor,
        duplicate_detector=duplicate_detector,
        data_extractor=data_extractor,
        request_types=request_types,
        extraction_rules=extraction_rules
    )

# Add dependency to app state
app.state.classification_service = get_classification_service()

# Include routes
app.include_router(router)

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
    
    # Log configuration
    logger.info(f"Loaded {len(request_types)} request types")
    logger.info(f"Loaded extraction rules for {len(extraction_rules)} request types")
    logger.info(f"Duplicate cache duration: {settings.duplicate_cache_days} days")
    logger.info(f"Max attachment size: {settings.max_attachment_size_mb} MB")
    
    # Test LLM connections
    try:
        service = app.state.classification_service
        llm = service.llm_handler.get_llm("email_classification")
        logger.info(f"Successfully initialized LLM: {llm.model}")
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down Email Classification API")

if __name__ == "__main__":
    import uvicorn
    
    # Start server
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=settings.port, 
        reload=True
    )