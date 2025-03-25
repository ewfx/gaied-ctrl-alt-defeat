from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.analytics import Analytics, analytics_collection

router = APIRouter()

@router.get("/analytics", response_model=List[Analytics])
async def get_all_analytics():
    analytics = []
    async for analytic in analytics_collection.find():
        analytics.append(Analytics(**analytic))
    if not analytics:
        raise HTTPException(status_code=404, detail="No analytics found")
    return analytics