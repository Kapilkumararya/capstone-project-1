from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CommentCreate(BaseModel):
    content: str

class CommentOut(BaseModel):
    author_name: str
    content: str
    created_at: datetime

class CommunityPostCreate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    recipe_id: Optional[str] = None
    embedded_recipe: Optional[str] = None
    tags: List[str] = []

class CommunityPostOut(BaseModel):
    id: str
    author_name: str
    title: str
    content: str
    image_url: Optional[str]
    video_url: Optional[str]
    recipe_id: Optional[str]
    embedded_recipe: Optional[str]
    votes: int
    comments: List[CommentOut]
    tags: List[str]
    created_at: datetime
