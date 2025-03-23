from bson import ObjectId

from ..schemas.request_types import request_type_collection


# Models
class RequestTypeModel:
    @staticmethod
    async def create_request_type(request_type_data):
        if "sub_request_types" in request_type_data:
            for subrequest in request_type_data["sub_request_types"]:
                if "_id" not in subrequest:
                    subrequest["_id"] = str(ObjectId())
        result = await request_type_collection.insert_one(request_type_data)
        return str(result.inserted_id)

    @staticmethod
    async def get_request_type(request_type_id):
        request_type = await request_type_collection.find_one({"_id": ObjectId(request_type_id)})
        if request_type:
            return request_type
        return None
    
    @staticmethod
    async def get_all_request_types():
        request_types = await request_type_collection.find().to_list(length=None)
        return request_types

    @staticmethod
    async def get_all_subrequest_types(request_type_id):
        request_type = await request_type_collection.find_one({"_id": ObjectId(request_type_id)}, {"subrequest_types": 1})
        if request_type and "subrequest_types" in request_type:
            return request_type["subrequest_types"]
        return []

    @staticmethod
    async def update_request_type(request_type_id, update_data):
        if "sub_request_types" in update_data:
            for subrequest in update_data["sub_request_types"]:
                if "_id" not in subrequest:
                    subrequest["_id"] = str(ObjectId())
        result = await request_type_collection.update_one(
            {"_id": ObjectId(request_type_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    @staticmethod
    async def delete_request_type(request_type_id):
        result = await request_type_collection.delete_one({"_id": ObjectId(request_type_id)})
        return result.deleted_count > 0

    @staticmethod
    async def add_subrequest_type(request_type_id, subrequest_type_data):
        if "_id" not in subrequest_type_data:
            subrequest_type_data["_id"] = str(ObjectId())
        result = await request_type_collection.update_one(
            {"_id": ObjectId(request_type_id)},
            {"$push": {"sub_request_types": subrequest_type_data}}
        )
        return result.modified_count > 0

    @staticmethod
    async def remove_subrequest_type(request_type_id, subrequest_type_id):
        result = await request_type_collection.update_one(
            {"_id": ObjectId(request_type_id)},
            {"$pull": {"sub_request_types": {"_id": subrequest_type_id}}}
        )
        return result.modified_count > 0

    @staticmethod
    async def update_subrequest_type(request_type_id, subrequest_type_id, update_data):
        result = await request_type_collection.update_one(
            {"_id": ObjectId(request_type_id), "sub_request_types._id": subrequest_type_id},
            {"$set": {f"sub_request_types.$.{key}": value for key, value in update_data.items()}}
        )
        return result.modified_count > 0