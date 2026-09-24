from beanie import Document, Link
from pydantic import Field, BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.user import User
from app.models.recipe import Recipe

class Comment(BaseModel):
    author_name: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityPost(Document):
    author_name: str
    author_id: Link[User]
    recipe_id: Optional[Link[Recipe]] = None
    title: str
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    embedded_recipe: Optional[str] = None
    votes: int = 0
    comments: List[Comment] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "community_posts"
