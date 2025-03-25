from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId
from ..db.session import db

class SubRequestType(BaseModel):
    _id: str
    name: str
    definition: str
    required_attributes: List[str]

class RequestType(BaseModel):
    name: str
    definition: str
    support_group: str
    sub_request_types: List[SubRequestType]

request_type_collection = db['request_types']