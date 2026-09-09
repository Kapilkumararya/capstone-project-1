from beanie import Document, Link
from pydantic import Field
from typing import List, Optional
from datetime import datetime
from app.models.user import User

class Recipe(Document):
    title: str
    ingredients: List[str]
    quantities: List[str]
    steps: List[str]
    tags: List[str] = []
    time: int = 0  # Time in minutes
    author_id: Link[User]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "recipes"
