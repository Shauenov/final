# app/modules/auth/auth_router.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from app.core.security import decode_token
from app.modules.auth.auth_dto import SignInDto, SignUpDto
from app.modules.auth.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


def _extract_token_from_request(request: Request) -> str:
    auth_value = request.headers.get("Authorization")
    if not auth_value:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    val = auth_value.strip()
    # поддерживаем и "Bearer <token>", и просто "<token>"
    if val.lower().startswith("bearer "):
        val = val[7:].strip()
    if not val:
        raise HTTPException(status_code=401, detail="Empty token")
    return val


def any_user_guard(request: Request):
    """Пускаем любого авторизованного пользователя (access token)."""
    token = _extract_token_from_request(request)
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def admin_guard(user: dict = Depends(any_user_guard)):
    """Только админ."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user


@auth_router.post("/sign-in")
def sign_in(data: SignInDto):
    """
    Логин: возвращаем JSON с токенами и дублируем access в заголовок Authorization,
    чтобы Swagger UI мог автоматически авторизоваться.
    """
    result = service.sign_in(data)
    resp = JSONResponse(content=result)
    resp.headers["Authorization"] = f"Bearer {result['access_token']}"
    return resp


@auth_router.post("/sign-up")
def sign_up(data: SignUpDto, _=Depends(admin_guard)):
    """Регистрацию может делать только админ."""
    return service.sign_up(data)


@auth_router.get("/me")
def me(user: dict = Depends(any_user_guard)):
    """Информация о текущем пользователе (любой авторизованный)."""
    return user
