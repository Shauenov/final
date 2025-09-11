from app.models import User
from app.core.db import engine
from sqlmodel import Session, select
from app.schemas import UserPublic, UpdateUser
import numpy as np

def normalize(vec: list[float]) -> list[float]:
    v = np.array(vec, dtype=np.float32)
    return (v / np.linalg.norm(v)).tolist()

class UserRepository():
  def create(self, data: User) -> UserPublic:
    with Session(engine) as session:
        session.add(data)
        session.commit()
        session.refresh(data)
        return UserPublic.model_validate(data)
  
  def findById(self, id: str, org_id: str) -> UserPublic | None:
    with Session(engine) as session:
        stmt = select(User).where(User.id == id).where(User.organization_id == org_id)
        result = session.exec(stmt).first()
        if not result:
           return None 
        return UserPublic.model_validate(result)
    
  def findOne(self, qr_code: str, org_id: str) -> UserPublic | None:
    with Session(engine) as session:
        stmt = select(User).where(User.qr_code == qr_code).where(User.organization_id == org_id)
        result = session.exec(stmt).first()
        if not result:
           return None 
        return UserPublic.model_validate(result)

  def findByEmbedding(self, org_id: str, embedding: list[float], top_k: int = 5) -> list[UserPublic]:
    with Session(engine) as session:
        stmt = (
            select(User, User.embedding.cosine_distance(embedding).label("distance"))
            .where(User.organization_id == org_id)
            .order_by(User.embedding.cosine_distance(embedding))
            .limit(top_k)
        )
        rows = session.exec(stmt).all()
        results = []
        for user, distance in rows:
            print(distance)
            if distance <= 0.6:
                results.append(UserPublic.model_validate(user))
        return results
  
  def findAll(self, org_id: str, skip: int | None = None, limit: int | None = None) -> list[UserPublic]:
    with Session(engine) as session:
        stmt = select(User).where(User.organization_id == org_id)
        if skip:
            stmt = stmt.offset(skip)
        if limit:
            stmt = stmt.limit(limit)
        results = session.exec(stmt).all()
        return [UserPublic.model_validate(user) for user in results]
    
  def updateById(self, id: str, org_id: str, data: UpdateUser) -> UserPublic | None:
    with Session(engine) as session:
        stmt = select(User).where(User.id == id).where(User.organization_id == org_id)
        user = session.exec(stmt).first()
        if not user:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        session.add(user)
        session.commit()
        session.refresh(user)
        return UserPublic.model_validate(user)
    
  def deleteById(self, id: str, org_id: str) -> UserPublic | None:
    with Session(engine) as session:
        stmt = select(User).where(User.id == id, User.organization_id == org_id)
        user = session.exec(stmt).first()
        if not user:
            return None
        session.delete(user)
        session.commit()
        return UserPublic.model_validate(user)
