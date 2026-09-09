from beanie import Document, Link
from pydantic import Field
from typing import List, Optional, Any
from datetime import datetime
from app.models.user import User

class DetectionRun(Document):
    user_id: Link[User]
    ingredients: List[str]
    confidence_scores: List[float] = []
    bounding_boxes: List[Any] = []  # Can be detailed later
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "detection_runs"
