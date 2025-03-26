from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.analytics import Analytics, analytics_collection
from ..schemas.analytics import DuplicateAnalytics, duplicate_analytics_collection

router = APIRouter()

@router.get("/analytics", response_model=List[Analytics])
async def get_all_analytics():
    analytics = []
    async for analytic in analytics_collection.find():
        analytics.append(Analytics(**analytic))
    if not analytics:
        raise HTTPException(status_code=404, detail="No analytics found")
    return analytics

@router.get("/duplicate-analytics", response_model=List[DuplicateAnalytics])
async def get_all_duplicate_analytics():
    duplicate_analytics = []
    async for duplicate_analytic in duplicate_analytics_collection.find():
        duplicate_analytics.append(DuplicateAnalytics(**duplicate_analytic))
    if not duplicate_analytics:
        raise HTTPException(status_code=404, detail="No duplicate analytics found")
    return duplicate_analytics