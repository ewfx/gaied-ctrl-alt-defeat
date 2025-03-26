from pydantic import BaseModel
from ..db.session import db
from datetime import datetime


class Analytics(BaseModel):
    request_type: str
    sub_request_type: str
    support_group: str
    confidence: float
    timestamp: str = datetime.now().isoformat()

class DuplicateAnalytics(BaseModel):
    timestamp: str = datetime.now().isoformat()
    duplicate_confidence: float

analytics_collection = db['analytics']
duplicate_analytics_collection = db['duplicate_analytics']