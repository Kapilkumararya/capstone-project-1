from beanie import Document, Link
from pydantic import Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from app.models.user import User

class DetectionRun(Document):
    user_id: Link[User]
    # Primary ingredients (prioritized by LLM confirmation)
    ingredients: List[str]
    # Raw detections from computer vision detector (e.g. YOLOv8)
    raw_ingredients: List[str] = []
    confidence_scores: List[float] = []
    bounding_boxes: List[Any] = []
    # LLM Confirmation & Priority details
    llm_confirmed: bool = False
    llm_reasoning: Optional[str] = None
    llm_removed: List[str] = []
    llm_added: List[str] = []
    model_used: Optional[str] = None
    # Local image preprocessing metrics (size reduction, dimensions)
    image_meta: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "detection_runs"
