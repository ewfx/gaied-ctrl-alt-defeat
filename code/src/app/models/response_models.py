from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class RequestTypeResult(BaseModel):
    """Model for a single request type classification result"""
    request_type: str
    sub_request_type: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    is_primary: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_type": "Money Movement-Inbound",
                "sub_request_type": "Principal",
                "confidence": 0.95,
                "reasoning": "Email explicitly mentions transferring funds to an account, which aligns with inbound money movement.",
                "is_primary": True
            }
        }

class ExtractedField(BaseModel):
    """Model for extracted field data"""
    field_name: str
    value: Any
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str = Field(..., description="Where the data was extracted from (email_body/attachment_1/etc)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "field_name": "amount",
                "value": 50000,
                "confidence": 0.98,
                "source": "email_body"
            }
        }

class ClassificationResponse(BaseModel):
    """Model for the complete classification response"""
    request_types: List[RequestTypeResult]
    extracted_fields: List[ExtractedField]
    is_duplicate: bool = False
    duplicate_reason: Optional[str] = None
    processing_time_ms: Optional[float] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_types": [
                    {
                        "request_type": "Money Movement-Inbound",
                        "sub_request_type": "Principal",
                        "confidence": 0.95,
                        "reasoning": "Email explicitly mentions transferring funds to an account",
                        "is_primary": True
                    }
                ],
                "extracted_fields": [
                    {
                        "field_name": "amount",
                        "value": 50000,
                        "confidence": 0.98,
                        "source": "email_body"
                    },
                    {
                        "field_name": "account_number",
                        "value": "XYZ",
                        "confidence": 0.85,
                        "source": "email_body"
                    }
                ],
                "is_duplicate": False,
                "duplicate_reason": None,
                "processing_time_ms": 1250.5
            }
        }

class ApiKeyUsageInfo(BaseModel):
    """Model for API key usage information"""
    service: str
    key_masked: str
    count: int
    limit: int
    period_minutes: int
    expires_in_seconds: Optional[int] = None

class HealthStatus(str, Enum):
    """Enum for service health status"""
    OK = "ok"
    DEGRADED = "degraded"
    ERROR = "error"

class HealthCheckResponse(BaseModel):
    """Model for health check response"""
    status: HealthStatus
    version: str
    api_keys: List[ApiKeyUsageInfo]
    components: Dict[str, HealthStatus]
    uptime_seconds: int