from bson import ObjectId
from beanie import PydanticObjectId


from ..schemas.request_types import RequestTypeSchema, SubRequestTypeSchema
from .request_types import RequestTypeModel
from ..db.session import db


class SubRequestTypeModel:

    @staticmethod
    async def create(sub_request_type: SubRequestTypeSchema):
        return await SubRequestTypeSchema.insert_one(sub_request_type)

    @staticmethod
    async def get_all():
        sub_request_types = await SubRequestTypeSchema.find({}).to_list(None)
        return sub_request_types

    @staticmethod
    async def get_by_id(sub_request_type_id: str):
        return await SubRequestTypeSchema.find_one({"_id": ObjectId(sub_request_type_id)})

    @staticmethod
    async def update(sub_request_type_id: str, update_data: dict):
        return await SubRequestTypeSchema.find_one({"_id": ObjectId(sub_request_type_id)}).update({"$set": update_data})

    @staticmethod
    async def delete(sub_request_type_id: str):
        
        # Convert string ID to ObjectId
        sub_request_type_id = ObjectId(sub_request_type_id)
                
        # Get collections
        request_types_collection = db["RequestTypeSchema"]
        sub_request_types_collection = db["SubRequestTypeSchema"]
        
        # Check if the sub-request type exists
        sub_request = await sub_request_types_collection.find_one({"_id": sub_request_type_id})
        if not sub_request:
            return None
        
        # Remove references from all request types
        await request_types_collection.update_many(
            {"sub_request_types": {"$elemMatch": {"id": sub_request_type_id}}},
            {"$pull": {"sub_request_types": {"id": sub_request_type_id}}}
        )
        
        # Delete the sub-request type
        result = await sub_request_types_collection.delete_one({"_id": sub_request_type_id})
        
        return result.deleted_count > 0