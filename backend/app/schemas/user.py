from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, Any


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr

    @model_validator(mode="before")
    @classmethod
    def coerce_id(cls, data: Any) -> Any:
        if hasattr(data, "id"):
            data = {
                "id": str(data.id),
                "username": data.username,
                "email": data.email
            }
        return data

    class Config:
        populate_by_name = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
