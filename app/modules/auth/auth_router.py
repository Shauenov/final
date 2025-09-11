from fastapi import APIRouter, HTTPException, Depends
from app.modules.auth.auth_service import AuthService
from app.modules.organization.organization_service import OrganizationService
from app.modules.auth.auth_dto import SignInDto, SignUpDto
from app.core.security import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

service = AuthService()
org_service = OrganizationService()
auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post('/sign-in')
def sign_in(data: SignInDto):
  return service.sign_in(data)

@auth_router.post('/sign-up')
def sign_up(data: SignUpDto):
  return service.sign_up(data)

security = HTTPBearer()

def organization_guard(credentials: HTTPAuthorizationCredentials = Depends(security)):
  token = credentials.credentials
  user = decode_token(token)
  if not user:
    raise HTTPException(status_code=401)
  return user

@auth_router.get('/me')
def me(user: dict = Depends(organization_guard)):
  return user

@auth_router.get('/captcha')
def get_captcha():
  return service.get_captcha()