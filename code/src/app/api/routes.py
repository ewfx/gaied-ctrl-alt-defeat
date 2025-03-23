from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional
import logging
import time

from app.models.response_models import ClassificationResponse
from app.services.classification_service import ClassificationService
from app.config import get_settings

# Initialize logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Get settings
settings = get_settings()


@router.get("/", tags=["Status"])
async def root():
    """Root endpoint to check if API is running"""
    return {"message": "Email Classification API is running", "version": "1.0.0"}

@router.post("/classify-email-chain", response_model=ClassificationResponse, tags=["Classification"])
async def classify_email_chain(
    email_chain_file: UploadFile = File(...),

    attachments: List[UploadFile] = File(None),
    thread_id: Optional[str] = Form(None),
    classification_service: ClassificationService = Depends(lambda: ClassificationService)
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
        
        # Check file size
        if len(email_chain_content) > settings.max_attachment_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413, 
                detail=f"Email chain file exceeds maximum size of {settings.max_attachment_size_mb}MB"
            )
        
        # Process attachments if any
        processed_attachments = []
        if attachments:
            for attachment in attachments:
                content = await attachment.read()
                
                # Check file size
                if len(content) > settings.max_attachment_size_mb * 1024 * 1024:
                    raise HTTPException(
                        status_code=413, 
                        detail=f"Attachment {attachment.filename} exceeds maximum size of {settings.max_attachment_size_mb}MB"
                    )
                
                processed_attachments.append({
                    "filename": attachment.filename,
                    "content_type": attachment.content_type,
                    "content": content
                })
        
        # Process the email chain
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
    classification_service: ClassificationService = Depends(lambda: ClassificationService)
):
    """
    Classify an email from an EML file.
    
    - **eml_file**: EML file containing the email with attachments
    - **thread_id**: Optional thread ID for duplicate detection
    """
    try:
        # Read and process the EML file
        eml_content = await eml_file.read()
        
        # Check file size
        if len(eml_content) > settings.max_attachment_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413, 
                detail=f"EML file exceeds maximum size of {settings.max_attachment_size_mb}MB"
            )
        
        # Process the EML file
        result = await classification_service.process_eml(
            eml_content=eml_content,
            thread_id=thread_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing EML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))