from pydantic import BaseModel
from ..db.session import db
from datetime import datetime


class Analytics(BaseModel):
    request_type: str
    sub_request_type: str
    support_group: str
    timestamp: str = datetime.now().isoformat()

analytics_collection = db['analytics']