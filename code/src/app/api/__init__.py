from fastapi import APIRouter

from .request_types import router as request_types_router

router = APIRouter()

router.include_router(request_types_router, prefix="")
