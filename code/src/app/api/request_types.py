from fastapi import APIRouter, HTTPException, status

from ..models.request_types import RequestTypeModel
from ..schemas.request_types import RequestTypeSchema

router = APIRouter()

@router.post("/", response_description="Add new request type")
async def create_request_type(request_type: RequestTypeSchema):
    new_request_type = await RequestTypeModel.create(request_type)
    return new_request_type

@router.get("/", response_description="List all request types")
async def list_request_types():
    request_types = await RequestTypeModel.get_all()
    return request_types

@router.get("/{id}", response_description="Get a single request type")
async def get_request_type(id: str):
    request_type = await RequestTypeModel.get_by_id(id)
    if request_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type not found")
    return request_type

@router.put("/{id}", response_description="Update a request type")
async def update_request_type(id: str, update_data: RequestTypeSchema):
    update_result = await RequestTypeModel.update(id, update_data)
    if not update_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type not found")
    return {"message": "Request type updated successfully"}

@router.delete("/{id}", response_description="Delete a request type")
async def delete_request_type(id: str):
    delete_result = await RequestTypeModel.delete(id)
    if not delete_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type not found")
    return {"message": "Request type deleted successfully"}

@router.get("/{id}/subrequests", response_description="List all sub request types of a request type")
async def list_sub_request_types(id: str):
    request_type = await RequestTypeModel.get_by_id(id)
    if request_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type not found")
    sub_request_types = await RequestTypeModel.get_sub_requests(id)
    return sub_request_types

