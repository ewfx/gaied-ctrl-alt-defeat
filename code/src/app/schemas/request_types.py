
from beanie import Document, Link, PydanticObjectId
from typing import List, Optional
from pydantic import BaseModel, Field

class SubRequestTypeSchema(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    name: str
    definition: str
    required_attributes: List[str]

    class Settings:
        collection = "sub_request_types"

class RequestTypeSchema(Document):
    id: Optional[PydanticObjectId] = Field(default_factory=PydanticObjectId, alias="_id")
    name: str
    definition: str
    sub_request_types: List[Link[SubRequestTypeSchema]] = []  # References instead of embedding

    class Settings:
        collection = "request_types"
        populate_links = True
