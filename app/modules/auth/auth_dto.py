import uuid
from pydantic import BaseModel, Field

class SignInDto(BaseModel):
  number: str = Field(
    pattern=r"^\+7\d{10}$",
    examples=["+77474156800"]
  )
  password: str = Field(
    min_length=8,
    examples=["admin123"]
  )

class SignUpDto(BaseModel):
  name: str = Field(
    min_length=2,
    examples=["Hello"]
  )
  fullname: str = Field(
    min_length=2,
    examples=["Chingizkhan Json"]
  )
  password: str = Field(
    min_length=8,
    examples=["admin123"]
  )
  number: str = Field(
    pattern=r"^\+7\d{10}$",
    examples=["+77474156800"]
  )
  captcha_id: uuid.UUID = Field()
  captcha_text: str = Field()