from sqlmodel import Session, select
from app.models import Device
from app.core.db import engine
from app.schemas import DevicePublic, UpdateDevice, CreateDevice


class DeviceRepository:
    def create(self, data: CreateDevice, org_id: str) -> DevicePublic:
        with Session(engine) as session:
            device = Device(**data.model_dump(), organization_id=org_id)
            session.add(device)
            session.commit()
            session.refresh(device)
            return DevicePublic.model_validate(device, from_attributes=True)

    def findById(self, id: str, org_id: str) -> DevicePublic | None:
        with Session(engine) as session:
            stmt = select(Device).where(Device.id == id, Device.organization_id == org_id)
            result = session.exec(stmt).first()
            if not result:
                return None
            return DevicePublic.model_validate(result, from_attributes=True)

    def findAll(self, org_id: str, skip: int | None = None, limit: int | None = None) -> list[DevicePublic]:
        with Session(engine) as session:
            stmt = select(Device).where(Device.organization_id == org_id)
            if skip:
                stmt = stmt.offset(skip)
            if limit:
                stmt = stmt.limit(limit)

            results = session.exec(stmt).all()
            return [DevicePublic.model_validate(r, from_attributes=True) for r in results]

    def updateById(self, id: str, data: UpdateDevice, org_id: str) -> DevicePublic | None:
        with Session(engine) as session:
            stmt = select(Device).where(Device.id == id, Device.organization_id == org_id)
            device = session.exec(stmt).first()
            if not device:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(device, key, value)

            session.add(device)
            session.commit()
            session.refresh(device)
            return DevicePublic.model_validate(device, from_attributes=True)

    def deleteById(self, id: str, org_id: str) -> DevicePublic | None:
        with Session(engine) as session:
            stmt = select(Device).where(Device.id == id, Device.organization_id == org_id)
            device = session.exec(stmt).first()
            if not device:
                return None
            session.delete(device)
            session.commit()
            return DevicePublic.model_validate(device, from_attributes=True)
