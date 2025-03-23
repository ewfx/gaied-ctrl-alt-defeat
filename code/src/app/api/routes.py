from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Body, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import json
import time
import logging
import base64
from datetime import datetime

from app.models.request_models import EmailProcessRequest, EmailAttachment, EmailSource
from app.models.response_models import ClassificationResponse, HealthCheckResponse, HealthStatus, ApiKeyUsageInfo
from app.services.classification_service import ClassificationService
from app.config import get_settings, get_request_types, get_extraction_rules

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

@router.get("/health", response_model=HealthCheckResponse, tags=["Status"])
async def health_check(classification_service: ClassificationService = Depends(lambda: ClassificationService)):
    """Health check endpoint"""
    # Get API key usage information
    api_usage = classification_service.llm_handler.api_manager.get_usage_info()
    
    # Format API key usage info
    api_keys_info = []
    for service, keys in api_usage.items():
        for key_masked, data in keys.items():
            expires_in = None
            if data['expiry'] is not None:
                expires_in = max(0, int(data['expiry'] - time.time()))
                
            api_keys_info.append(ApiKeyUsageInfo(
                service=service,
                key_masked=key_masked,
                count=data['count'],
                limit=data['limit'],
                period_minutes=data['period'],
                expires_in_seconds=expires_in
            ))
    
    # Determine overall health status
    overall_status = HealthStatus.OK
    
    # Check API key usage
    for api_key in api_keys_info:
        if api_key.count >= api_key.limit:
            overall_status = HealthStatus.DEGRADED
            break
    
    # Return health check response
    return HealthCheckResponse(
        status=overall_status,
        version="1.0.0",
        api_keys=api_keys_info,
        components={
            "classification": HealthStatus.OK,
            "extraction": HealthStatus.OK,
            "duplicate_detection": HealthStatus.OK
        },
        uptime_seconds=int(time.time())
    )

@router.post("/classify-email", response_model=ClassificationResponse, tags=["Classification"])
async def classify_email(
    email_content: str = Form(...),
    sender: str = Form(...),
    subject: str = Form(...),
    received_date: str = Form(...),
    thread_id: Optional[str] = Form(None),
    source: Optional[str] = Form("api"),
    attachments: List[UploadFile] = File(None),
    classification_service: ClassificationService = Depends(lambda: ClassificationService)
):
    """
    Classify email content and attachments to determine request types and extract data.
    
    - **email_content**: The body content of the email
    - **sender**: Email address of the sender
    - **subject**: Email subject line
    - **received_date**: Date when the email was received (ISO format)
    - **thread_id**: Optional thread ID for duplicate detection
    - **source**: Source of the email (outlook, gmail, api, other)
    - **attachments**: Optional list of file attachments
    """
    try:
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
        
        # Parse received date
        try:
            received_date_parsed = datetime.fromisoformat(received_date.replace('Z', '+00:00'))
            received_date_str = received_date_parsed.isoformat()
        except ValueError:
            received_date_str = received_date
        
        # Process the email
        result = await classification_service.process_email(
            email_content=email_content,
            sender=sender,
            subject=subject,
            received_date=received_date_str,
            attachments=processed_attachments,
            thread_id=thread_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/classify-email-json", response_model=ClassificationResponse, tags=["Classification"])
async def classify_email_json(
    request: EmailProcessRequest,
    classification_service: ClassificationService = Depends(lambda: ClassificationService)
):
    """
    Classify email content and attachments to determine request types and extract data.
    Uses JSON request format instead of form data.
    """
    try:
        # Process attachments if any
        processed_attachments = []
        for attachment in request.attachments:
            # Decode base64 content
            content = base64.b64decode(attachment.content_b64)
            
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
        
        # Process the email
        result = await classification_service.process_email(
            email_content=request.content,
            sender=request.sender,
            subject=request.subject,
            received_date=request.received_date.isoformat(),
            attachments=processed_attachments,
            thread_id=request.thread_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-api-keys", tags=["Administration"])
async def reset_api_keys(
    classification_service: ClassificationService = Depends(lambda: ClassificationService)
):
    """Reset all API key usage counters"""
    try:
        classification_service.llm_handler.api_manager.reset()
        return {"message": "API key usage counters reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting API keys: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))