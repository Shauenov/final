from fastapi import HTTPException
from app.core.logger import logger
from app.schemas import CreateDevice, UpdateDevice, DevicePublic
from app.modules.device.device_repository import DeviceRepository


class DeviceService():
    def __init__(self):
        self.repo = DeviceRepository()

    def create(self, data: CreateDevice, org_id: str) -> DevicePublic:
        try:
            return self.repo.create(data, org_id)
        except Exception as e:
            logger.error("error %s", e)
            raise HTTPException(status_code=500, detail="Failed to create device")

    def findById(self, id: str, org_id: str) -> DevicePublic | None:
        try:
            device = self.repo.findById(id, org_id)
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            return device
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("error %s", e)
            raise HTTPException(status_code=500, detail="Failed to get device")

    def findAll(self, org_id: str, skip: int | None = None, limit: int | None = None) -> list[DevicePublic]:
        try:
            return self.repo.findAll(org_id, skip, limit)
        except Exception as e:
            logger.error("error %s", e)
            raise HTTPException(status_code=500, detail="Failed to get devices")

    def updateById(self, id: str, data: UpdateDevice, org_id: str) -> DevicePublic:
        try:
            device = self.findById(id, org_id)
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            return self.repo.updateById(id, data, org_id)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("%s", e)
            raise HTTPException(status_code=500, detail="Failed to update device")

    def deleteById(self, id: str, org_id: str) -> DevicePublic | None:
        try:
            device = self.findById(id, org_id)
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            return self.repo.deleteById(id, org_id)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("%s", e)
            raise HTTPException(status_code=500, detail="Failed to delete device")
