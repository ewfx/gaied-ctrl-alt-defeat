from fastapi import APIRouter

from .request_types import router as request_types_router
from .sub_request_types import router as sub_request_types_router

router = APIRouter()

router.include_router(request_types_router, prefix="/reqtypes")
router.include_router(sub_request_types_router, prefix="/subreqtypes")