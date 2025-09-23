from fastapi import HTTPException
from app.core.logger import logger
from .statistics_dto import  StatisticsPublic, StatisticsCreate
from app.modules.statistics.statistics_repository import StatisticsRepository


class StatisticsService():
    def __init__(self):
        self.repo = StatisticsRepository()

    async def create(self, data: StatisticsCreate) -> StatisticsPublic:
        try:
            return self.repo.create(data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("error %s", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def findById(self, id: str) -> StatisticsPublic | None:
        try:
            statistics = self.repo.findById(id)
            if not statistics:
                raise HTTPException(status_code=404, detail="Statistics not found")
            return statistics
        except HTTPException:
            raise
        except Exception as e:
            logger.error("error %s", e)
            raise HTTPException(status_code=500)

    def findAll(self, skip: int | None = None, limit: int | None = None) -> list[StatisticsPublic]:
        try:
            statisticss = self.repo.findAll(skip, limit)
            return statisticss
        except Exception as e:
            logger.error("error %s", e)
            raise HTTPException(status_code=500)
