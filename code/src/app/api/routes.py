from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional
import logging
import time

from app.models.response_models import ClassificationResponse
from app.services.classification_service import ClassificationService
from app.config import get_settings
from app.services.IntelligentDuplicateDetector import LRUCache

# Initialize logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Get settings
settings = get_settings()
lru_cache = LRUCache(capacity=settings.duplicate_cache_size)

# Create a function to get a ClassificationService instance
def get_classification_service():
    # Import dependencies here to avoid circular imports
    from app.core.llm_handler import LLMHandler
    from app.core.api_manager import ApiManager
    from app.services.email_processor import EmailProcessor
    from app.services.IntelligentDuplicateDetector import IntelligentDuplicateDetector
    from app.services.data_extractor import DataExtractor
    
    # Create service dependencies
    api_manager = ApiManager()
    llm_handler = LLMHandler(api_manager=api_manager)
    email_processor = EmailProcessor(max_attachment_size_mb=settings.max_attachment_size_mb)
    
    # Initialize the IntelligentDuplicateDetector with appropriate settings
    duplicate_detector = IntelligentDuplicateDetector(
        cache_duration_days=settings.duplicate_cache_days,
        cache_size=settings.duplicate_cache_size,
        semantic_threshold=settings.semantic_threshold,
        metadata_weight=settings.metadata_weight,
        subject_weight=settings.subject_weight,
        content_weight=settings.content_weight,
        time_window_hours=settings.time_window_hours,
        email_cache=lru_cache
    )
    
    data_extractor = DataExtractor(llm_handler=llm_handler)
    
    # Create and return a ClassificationService instance
    return ClassificationService(
        llm_handler=llm_handler,
        email_processor=email_processor,
        duplicate_detector=duplicate_detector,
        data_extractor=data_extractor
    )


@router.get("/", tags=["Status"])
async def root():
    """Root endpoint to check if API is running"""
    return {"message": "Email Classification API is running", "version": "1.0.0"}

@router.post("/classify-email-chain", response_model=ClassificationResponse, tags=["Classification"])
async def classify_email_chain(
    email_chain_file: UploadFile = File(...),
    attachments: List[UploadFile] = File(None),
    thread_id: Optional[str] = Form(None),
    classification_service: ClassificationService = Depends(get_classification_service)
):
    """
    Classify an email chain from a PDF file along with separate attachments.
    
    - **email_chain_file**: PDF file containing the email chain
    - **attachments**: Optional list of file attachments
    - **thread_id**: Optional thread ID for duplicate detection
    """
    try:
        # Read and process the email chain file
        email_chain_content = await email_chain_file.read()
        
        # Process attachments if any
        processed_attachments = []
        if attachments:
            for attachment in attachments:
                content = await attachment.read()
                processed_attachments.append({
                    "filename": attachment.filename,
                    "content_type": attachment.content_type,
                    "content": content
                })
        
        # Process the email chain - file size check moved to the service layer
        result = await classification_service.process_email_chain(
            email_chain_file=email_chain_content,
            email_chain_filename=email_chain_file.filename,
            email_chain_content_type=email_chain_file.content_type,
            attachments=processed_attachments,
            thread_id=thread_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing email chain: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/classify-eml", response_model=ClassificationResponse, tags=["Classification"])
async def classify_eml(
    eml_file: UploadFile = File(...),
    thread_id: Optional[str] = Form(None),
    classification_service: ClassificationService = Depends(get_classification_service)
):
    """
    Classify an email from an EML file.
    
    - **eml_file**: EML file containing the email with attachments
    - **thread_id**: Optional thread ID for duplicate detection
    """
    try:
        # Read and process the EML file
        eml_content = await eml_file.read()
        
        # Process the EML file - file size check moved to the service layer
        result = await classification_service.process_eml(
            eml_content=eml_content,
            thread_id=thread_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing EML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))