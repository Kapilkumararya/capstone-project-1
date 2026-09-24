from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, Any


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPreferencesUpdate(BaseModel):
    dietary_preferences: list[str]
    max_prep_time: int

class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    dietary_preferences: list[str] = []
    max_prep_time: int = 30

    @model_validator(mode="before")
    @classmethod
    def coerce_id(cls, data: Any) -> Any:
        if hasattr(data, "id"):
            data = {
                "id": str(data.id),
                "username": data.username,
                "email": data.email,
                "dietary_preferences": getattr(data, "dietary_preferences", []),
                "max_prep_time": getattr(data, "max_prep_time", 30),
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
