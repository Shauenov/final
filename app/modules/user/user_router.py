from typing import Annotated
import uuid
from pydantic import Field
from fastapi import Form, APIRouter, UploadFile, Depends, Path

from app.models import ActivityType
from app.modules.user.user_service import UserService
from app.schemas import CreateUser, UpdateUser, UserPublic
from app.modules.organization.organization_service import organization_guard

service = UserService()

user_router = APIRouter(
    prefix="/organization/{org_id}/users",
    tags=["User"],
)

@user_router.get("/{id}", response_model=UserPublic | None)
def get_user_by_id(
    id: Annotated[str, Path(description="The id of user")],
    org=Depends(organization_guard)
):
    return service.findById(id, org_id=org["id"])

@user_router.get("/", response_model=list[UserPublic])
def get_users(
    skip: int | None = None,
    limit: int | None = None,
    org=Depends(organization_guard)
):
    return service.findAll(org_id=org["id"], skip=skip, limit=limit)

@user_router.post("/", response_model=UserPublic)
async def create_user(
    name: Annotated[
        str,
        Form(...),
        Field(min_length=2, examples=["Chingizkhan Johnson"])
    ],
    number: Annotated[
        str,
        Form(...),
        Field(pattern=r"^\+7\d{10}$", examples=["+77474156800"])
    ],
    image: UploadFile,
    org=Depends(organization_guard)
):
    return await service.create(
        CreateUser(name=name, number=number, organization_id=org["id"]),
        image
    )

@user_router.delete("/{id}", response_model=UserPublic)
def delete_user(
    id: Annotated[uuid.UUID, Path(description="The id of user")],
    org=Depends(organization_guard)
):
    return service.deleteById(id, org_id=org["id"])

@user_router.patch("/{id}", response_model=UserPublic)
def update_user(
    id: Annotated[uuid.UUID, Path(description="The id of user")],
    data: UpdateUser,
    org=Depends(organization_guard)
):
    return service.updateById(id, org_id=org["id"], data=data)

@user_router.post("/recognize", response_model=list[UserPublic])
async def recognize_face(
    image: UploadFile,
    org=Depends(organization_guard)
):
    return await service.recognizeFace(image, org_id=org["id"])

@user_router.post("/validate/{qr}", response_model=UserPublic | None)
async def validate_qr_code(
    qr: Annotated[uuid.UUID, Form(...), Path(description="QR code of user")],
    org=Depends(organization_guard),
) -> UserPublic | None:
    return await service.findOne(qr, org_id=org["id"])

@user_router.post("/record-action/{id}", response_model=UserPublic | None)
def record_action(
    id: Annotated[uuid.UUID, Form(...), Path(description="ID of user")],
    action: Annotated[ActivityType, Form(...)],
    image: UploadFile,
    org=Depends(organization_guard),
) -> UserPublic | None:
    # return await self.userActivity.create(CreateUserActivity(user_id=user.id, type=ActivityType.ENTRY.value if user.at_work else ActivityType.EXIT.value))
    return service.updateById(id, org_id=org["id"], data=UpdateUser(at_work=True if action == ActivityType.ENTRY else False))
