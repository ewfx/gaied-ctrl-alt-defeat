from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import base64

class EmailAttachment(BaseModel):
    """Model representing an email attachment"""
    filename: str
    content_type: str
    content_b64: str
    
    @property
    def content(self) -> bytes:
        """Decode base64 content to bytes"""
        return base64.b64decode(self.content_b64)

class EmailSource(str, Enum):
    """Enum for email source"""
    OUTLOOK = "outlook"
    GMAIL = "gmail"
    API = "api"
    OTHER = "other"

class EmailProcessRequest(BaseModel):
    """Model for email processing request"""
    sender: EmailStr
    subject: str
    content: str
    received_date: datetime
    attachments: Optional[List[EmailAttachment]] = []
    source: Optional[EmailSource] = EmailSource.API
    thread_id: Optional[str] = None
    
    @validator('content')
    def content_not_empty(cls, v):
        if not v or v.isspace():
            raise ValueError("Email content cannot be empty")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "sender": "client@example.com",
                "subject": "Request for funds transfer",
                "content": "Hello, We need to transfer $50,000 to account XYZ. Best regards, Client",
                "received_date": "2023-11-15T10:30:00Z",
                "attachments": [],
                "source": "outlook",
                "thread_id": "thread-12345"
            }
        }

class EmailChainRequest(BaseModel):
    """Model for email chain processing request"""
    email_chain_file_b64: str
    email_chain_filename: str
    email_chain_content_type: str
    attachments: Optional[List[EmailAttachment]] = []
    thread_id: Optional[str] = None
    
    @property
    def email_chain_content(self) -> bytes:
        """Decode base64 content to bytes"""
        return base64.b64decode(self.email_chain_file_b64)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email_chain_filename": "email_thread.pdf",
                "email_chain_content_type": "application/pdf",
                "email_chain_file_b64": "JVBERi0xLjUK...",
                "attachments": [],
                "thread_id": "thread-12345"
            }
        }

class EmlRequest(BaseModel):
    """Model for EML file processing request"""
    eml_file_b64: str
    thread_id: Optional[str] = None
    
    @property
    def eml_content(self) -> bytes:
        """Decode base64 content to bytes"""
        return base64.b64decode(self.eml_file_b64)
    
    class Config:
        json_schema_extra = {
            "example": {
                "eml_file_b64": "UmVjZWl2ZWQ6IGZyb20...",
                "thread_id": "thread-12345"
            }
        }

class RequestTypeDefinition(BaseModel):
    """Model for request type definition input"""
    request_type: str
    sub_request_types: List[str]
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_type": "Money Movement-Inbound",
                "sub_request_types": ["Principal", "Interest", "Principal + Interest"],
                "description": "Requests related to incoming funds",
                "keywords": ["transfer", "deposit", "funding"]
            }
        }

class ExtractionRule(BaseModel):
    """Model for field extraction rule"""
    priority_sources: List[str]
    fields: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "priority_sources": ["email_body", "attachment"],
                "fields": ["amount", "account_number", "value_date", "transaction_id"]
            }
        }