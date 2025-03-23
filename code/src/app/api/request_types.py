from fastapi import APIRouter, HTTPException, status

from ..models.request_types import RequestTypeModel
from ..schemas.request_types import RequestType

router = APIRouter()

@router.post("/request-types", response_model=dict)
async def create_request_type(request_type: RequestType):
    request_type_id = await RequestTypeModel.create_request_type(request_type.dict())
    return {"request_type_id": request_type_id}

@router.get("/request-types/{request_type_id}", response_model=RequestType)
async def get_request_type(request_type_id: str):
    request_type = await RequestTypeModel.get_request_type(request_type_id)
    if not request_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type not found")
    return request_type

@router.get("/request-types", response_model=list)
async def get_all_request_types():
    request_types = await RequestTypeModel.get_all_request_types()
    for request_type in request_types:
        request_type["_id"] = str(request_type["_id"])
    return request_types

@router.get("/request-types/{request_type_id}/sub-request-types", response_model=list)
async def get_all_subrequest_types(request_type_id: str):
    subrequest_types = await RequestTypeModel.get_all_subrequest_types(request_type_id)
    if subrequest_types is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type not found")
    return subrequest_types

@router.put("/request-types/{request_type_id}", response_model=dict)
async def update_request_type(request_type_id: str, update_data: RequestType):
    success = await RequestTypeModel.update_request_type(request_type_id, update_data.dict())
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type not found")
    return {"success": success}

@router.delete("/request-types/{request_type_id}", response_model=dict)
async def delete_request_type(request_type_id: str):
    success = await RequestTypeModel.delete_request_type(request_type_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type not found")
    return {"success": success}

@router.post("/request-types/{request_type_id}/sub-request-types", response_model=dict)
async def add_subrequest_type(request_type_id: str, subrequest_type_data: dict):
    success = await RequestTypeModel.add_subrequest_type(request_type_id, subrequest_type_data)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type not found")
    return {"success": success}

@router.delete("/request-types/{request_type_id}/sub-request-types/{subrequest_type_id}", response_model=dict)
async def remove_subrequest_type(request_type_id: str, subrequest_type_id: str):
    success = await RequestTypeModel.remove_subrequest_type(request_type_id, subrequest_type_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type or subrequest type not found")
    return {"success": success}

@router.put("/request-types/{request_type_id}/sub-request-types/{subrequest_type_id}", response_model=dict)
async def update_subrequest_type(request_type_id: str, subrequest_type_id: str, update_data: dict):
    success = await RequestTypeModel.update_subrequest_type(request_type_id, subrequest_type_id, update_data)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request type or subrequest type not found")
    return {"success": success}

