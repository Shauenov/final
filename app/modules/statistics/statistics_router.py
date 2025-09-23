from typing import Annotated
from fastapi import APIRouter, Path

from .statistics_dto import StatisticsPublic, StatisticsCreate
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

@statistics_router.get("/", response_model=list[StatisticsPublic])
def get_statisticss(
    skip: int | None = None,
    limit: int | None = None,
):
    return service.findAll(skip=skip, limit=limit)

@statistics_router.post("/", response_model=StatisticsPublic)
async def create_statistics(data: StatisticsCreate):
    return await service.create(data)
