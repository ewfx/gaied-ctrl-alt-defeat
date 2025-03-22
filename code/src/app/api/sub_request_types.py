from fastapi import APIRouter, HTTPException, status

from ..models.request_types import RequestTypeModel
from ..models.sub_request_types import SubRequestTypeModel
from ..schemas.request_types import SubRequestTypeSchema

router = APIRouter()

@router.post("/{parent_request_id}", response_description="Create a new sub request type")
async def create_sub_request_type(sub_request_type: SubRequestTypeSchema, parent_request_id: str):
    parent_request = await RequestTypeModel.get_by_id(parent_request_id)
    if parent_request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent request not found")
    
    new_sub_request_type = await SubRequestTypeModel.create(sub_request_type)
    await RequestTypeModel.map_to_parent(new_sub_request_type.id, parent_request_id)
    return sub_request_type

@router.get("/", response_description="List all sub request types")
async def list_sub_request_types():
    sub_request_types = await SubRequestTypeModel.get_all()
    return sub_request_types

@router.get("/{id}", response_description="Get a single sub request type by ID")
async def get_sub_request_type(id: str):
    sub_request_type = await SubRequestTypeModel.get_by_id(id)
    if sub_request_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sub request type not found")
    return sub_request_type

@router.put("/{id}", response_description="Update a sub request type")
async def update_sub_request_type(id: str, update_data: SubRequestTypeSchema):
    update_result = await SubRequestTypeModel.update(id, update_data)
    if not update_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sub request type not found")
    return {"message": "Sub request type updated successfully"}

@router.delete("/{id}", response_description="Delete a sub request type")
async def delete_sub_request_type(id: str):
    delete_result = await SubRequestTypeModel.delete(id)
    if not delete_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sub request type not found")
    return {"message": "Sub request type deleted successfully"}