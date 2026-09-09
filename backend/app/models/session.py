from beanie import Document, Link
from pydantic import Field
from typing import List, Dict, Any
from datetime import datetime
from app.models.user import User
from app.models.recipe import Recipe


class CookingSession(Document):
    user_id: Link[User]
    recipe_id: Link[Recipe]
    current_step: int = 0  # Which step the user is on
    messages: List[Dict[str, str]] = []  # {"role": "user" | "assistant", "content": "..."}
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "cooking_sessions"
