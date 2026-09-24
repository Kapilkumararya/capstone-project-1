from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class User(Document):
    username: str
    email: str
    hashed_password: str
    dietary_preferences: List[str] = Field(default_factory=list)
    max_prep_time: int = 30
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
