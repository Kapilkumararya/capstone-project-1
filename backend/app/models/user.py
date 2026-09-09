from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class User(Document):
    username: str
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
