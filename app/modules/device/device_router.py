from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, HTTPException, Path, Depends

from app.schemas import CreateDevice, UpdateDevice, DevicePublic
from app.modules.device.device_service import DeviceService
from app.modules.organization.organization_service import organization_guard

service = DeviceService()
device_router = APIRouter(prefix="/organization/{org_id}/device", tags=["Device"])


@device_router.get("/{id}", response_model=DevicePublic | None)
def get_device_by_id(
    id: Annotated[UUID, Path(description="The id of device")],
    organization=Depends(organization_guard),
):
    device = service.findById(str(id), organization.id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@device_router.get("/", response_model=list[DevicePublic])
def get_devices(
    skip: int | None = None,
    limit: int | None = None,
    organization=Depends(organization_guard),
):
    return service.findAll(organization.id, skip, limit)


@device_router.post("/", response_model=DevicePublic)
def create_device(
    data: CreateDevice,
    organization=Depends(organization_guard),
) -> DevicePublic:
    return service.create(data, organization.id)


@device_router.delete("/{id}", response_model=DevicePublic)
def delete_device(
    id: Annotated[UUID, Path(description="The id of device")],
    organization=Depends(organization_guard),
):
    return service.deleteById(str(id), organization.id)


@device_router.patch("/{id}", response_model=DevicePublic)
def update_device(
    id: Annotated[UUID, Path(description="The id of device")],
    data: UpdateDevice,
    organization=Depends(organization_guard),
):
    return service.updateById(str(id), data, organization.id)
