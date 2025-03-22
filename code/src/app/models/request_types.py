from bson import ObjectId

from ..schemas.request_types import RequestTypeSchema, SubRequestTypeSchema


# Models
class RequestTypeModel:

    @staticmethod
    async def create(request_type: RequestTypeSchema):
        return await RequestTypeSchema.insert_one(request_type)

    @staticmethod
    async def get_all():
        request_types = await RequestTypeSchema.find_all(with_children=True).to_list()
        for request_type in request_types:
            await request_type.fetch_all_links()
        
        return request_types

    @staticmethod
    async def get_by_id(request_type_id: str):
        request_type =  await RequestTypeSchema.find_one({"_id": ObjectId(request_type_id)})
        if request_type:
            await request_type.fetch_all_links()
        return request_type

    @staticmethod
    async def update(request_type_id: str, update_data: dict):
        return await RequestTypeSchema.find_one({"_id": ObjectId(request_type_id)}).update({"$set": update_data})
    
    @staticmethod
    async def add_sub_request_type(request_type_id: str, sub_request_type_id: str):
        request_type = await RequestTypeModel.get_by_id(request_type_id)
        if request_type:
            return await request_type.update(
                {"$push": {"sub_request_types": sub_request_type_id}}
            )
        return None
        
    @staticmethod
    async def remove_sub_request_type(request_type_id: str, sub_request_type_id: str):
        return await RequestTypeSchema.update(
            {"_id": ObjectId(request_type_id)},
            {"$pull": {"sub_request_types": sub_request_type_id}}
        )

    @staticmethod
    async def delete(request_type_id: str):
        request_type = await RequestTypeModel.get_by_id(request_type_id)
        if request_type:
            for sub_request_type in request_type.sub_request_types:
                print(sub_request_type)
                await SubRequestTypeSchema.delete(sub_request_type)
        
            return await request_type.delete()
        else:
            return None
    
    @staticmethod
    async def map_to_parent(sub_request_type_id: str, parent_request_type_id: str):
        return await RequestTypeModel.add_sub_request_type(parent_request_type_id, sub_request_type_id)


    @staticmethod
    async def get_sub_request_types(request_type_id: str):
        request_type = await RequestTypeModel.get_by_id(request_type_id)
        if request_type:
            sub_request_type_ids = request_type.get("sub_request_types", [])
            if sub_request_type_ids:
                sub_request_types = await SubRequestTypeSchema.find(
                    {"_id": {"$in": [ObjectId(id) for id in sub_request_type_ids]}}
                ).to_list(None)
                return sub_request_types
        return []
