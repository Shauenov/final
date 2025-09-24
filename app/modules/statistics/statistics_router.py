from datetime import date
from typing import Annotated, Optional
import uuid
from fastapi import APIRouter, Path, Query

from .statistics_dto import StatisticsPublic, StatisticsCreate, AggregatedStatistics
from app.modules.statistics.statistics_service import StatisticsService

service = StatisticsService()

statistics_router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"],
)

@statistics_router.get("/{id}", response_model=StatisticsPublic | None)
def get_statistics_by_id(
    id: Annotated[str, Path(description="The id of statistics")],
):
    return service.findById(id)

@statistics_router.get("/", response_model=AggregatedStatistics)
def get_statisticss(
    start_date: Optional[date] = Query(None, description="Start date, format YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="End date, format YYYY-MM-DD"),
    ad_id: uuid.UUID = Query(None, description="ID of Ad"),
    skip: int | None = None,
    limit: int | None = None,
):
    return service.getAggregatedStatistics(skip=skip, limit=limit, start_date=start_date, ad_id=ad_id, end_date=end_date)

@statistics_router.post("/", response_model=StatisticsPublic)
async def create_statistics(data: StatisticsCreate):
    return await service.create(data)
