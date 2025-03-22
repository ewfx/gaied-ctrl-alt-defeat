from bson import ObjectId

from ..schemas.request_types import RequestTypeSchema, SubRequestTypeSchema
from .request_types import RequestTypeModel


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
        sub_request = await SubRequestTypeSchema.get(ObjectId(sub_request_type_id))
        
        if sub_request:
            # Remove sub_request_type_id from all RequestTypeSchema documents
            await RequestTypeSchema.find(
                {"sub_request_types": ObjectId(sub_request_type_id)}
            ).update(
                {"$pull": {"sub_request_types": ObjectId(sub_request_type_id)}}
            )

            # Delete the sub-request type
            return await sub_request.delete()

        return None
