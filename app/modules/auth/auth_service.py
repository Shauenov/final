from datetime import timedelta
from fastapi import HTTPException
from app.core.logger import logger
from app.modules.auth.auth_dto import SignInDto, SignUpDto
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.modules.organization.organization_service import OrganizationService
from fastapi.responses import JSONResponse
from captcha.image import ImageCaptcha
import base64
from io import BytesIO
import random
import string
import uuid
from app.core.redis import r


class AuthService():
  def __init__(self):
    self.service = OrganizationService()

  def sign_in(self, data: SignInDto):
    try:
      org = self.service.findOne(number=data.number)
      if not org:
        raise HTTPException(status_code=404)
      hashed_pwd = org.password
      verified = verify_password(data.password, hashed_pwd)
      if not verified:
        raise HTTPException(status_code=401)
      payload = {
        "id": str(org.id),
        "name": org.name,
        "number": org.number,
      }
      token = create_access_token(payload, expires_delta=timedelta(days=7))
      refresh_token = create_refresh_token(payload, expires_delta=timedelta(days=14))
      return { 
        "organization_id": str(org.id),
        "organization_name": org.name,
        "access_token": token,
        "refresh_token": refresh_token
      }
    except HTTPException as e:
      raise e
    except Exception as e:
      logger.error("error %s", e)
      raise HTTPException(status_code=500)

  def sign_up(self, data: SignUpDto):
    try:
      is_verified = self.verify_captcha(data.captcha_id, data.captcha_text)
      if not is_verified:
        raise HTTPException(status_code=422, detail="Invalid captcha text")
      else:
        return self.service.create(data)
    except HTTPException as e:
      raise e
    except Exception as e:
      logger.error("error %s", e)
      raise HTTPException(status_code=500)


  def get_captcha(self):
    image = ImageCaptcha(width=280, height=90)
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    data = image.generate(text)
    image_bytes = BytesIO(data.read())

    unique_catpcha_id = uuid.uuid4()
    b64_str = base64.b64encode(image_bytes.getvalue()).decode("utf-8")
    captcha_id = f"captcha-{unique_catpcha_id}"

    r.set(captcha_id, text, ex=300)
    data = {
      "id": str(unique_catpcha_id),
      "image": b64_str
    }
    print(text)
    return JSONResponse(content={
        "id": str(unique_catpcha_id),
        "image": f"data:image/png;base64,{b64_str}"
    })

  def verify_captcha(self, id: str, text: str) -> bool:
    captcha_id = f"captcha-{id}"
    captcha_text = r.get(captcha_id)
    if captcha_text is None:
        return False 
    captcha_text = captcha_text.decode("utf-8")
    print("Stored:", captcha_text, "Provided:", text)
    return captcha_text == text.upper()