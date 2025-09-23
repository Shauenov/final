from app.models import Statistics
from app.core.db import engine
from sqlmodel import Session, select
from .statistics_dto import StatisticsCreate, StatisticsPublic

class StatisticsRepository():
  def create(self, data: StatisticsCreate) -> StatisticsPublic:
    with Session(engine) as session:
        data = Statistics(**data.model_dump())
        session.add(data)
        session.commit()
        session.refresh(data)
        return StatisticsPublic.model_validate(data)
  
  def findById(self, id: str) -> StatisticsPublic | None:
    with Session(engine) as session:
        stmt = select(Statistics).where(Statistics.id == id)
        result = session.exec(stmt).first()
        if not result:
           return None 
        return StatisticsPublic.model_validate(result)
  
  def findAll(self, skip: int | None = None, limit: int | None = None) -> list[StatisticsPublic]:
    with Session(engine) as session:
        stmt = select(Statistics)
        if skip:
            stmt = stmt.offset(skip)
        if limit:
            stmt = stmt.limit(limit)
        results = session.exec(stmt).all()
        return [StatisticsPublic.model_validate(result) for result in results]
