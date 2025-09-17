# app/modules/auth/auth_router.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_token
from app.modules.auth.auth_dto import SignInDto, SignUpDto
from app.modules.auth.auth_service import AuthService

from fastapi.responses import JSONResponse

auth_router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()
security = HTTPBearer()

def user_guard(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return user


def admin_guard(user: dict = Depends(user_guard)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403)
    return user


@auth_router.post("/sign-in")
def sign_in(data: SignInDto):
    result = service.sign_in(data)
    # в ответе JSON и хедер Authorization
    response = JSONResponse(content=result)
    response.headers["Authorization"] = f"Bearer {result['access_token']}"
    return response

@auth_router.post("/sign-up", dependencies=[Depends(admin_guard)])
def sign_up(data: SignUpDto):
    return service.sign_up(data)

@auth_router.get("/me")
def me(user: dict = Depends(user_guard)):
    return user
