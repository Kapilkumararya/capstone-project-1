from pydantic import BaseModel, model_validator
from typing import List, Optional, Any
from datetime import datetime


class RecipeCreate(BaseModel):
    title: str
    ingredients: List[str]
    quantities: List[str]
    steps: List[str]
    tags: Optional[List[str]] = []
    time: Optional[int] = 0


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    ingredients: Optional[List[str]] = None
    quantities: Optional[List[str]] = None
    steps: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    time: Optional[int] = None


class RecipeOut(BaseModel):
    id: str
    title: str
    ingredients: List[str]
    quantities: List[str]
    steps: List[str]
    tags: List[str]
    time: int
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def coerce_id(cls, data: Any) -> Any:
        if hasattr(data, "id"):
            data = {
                "id": str(data.id),
                "title": data.title,
                "ingredients": data.ingredients,
                "quantities": data.quantities,
                "steps": data.steps,
                "tags": data.tags,
                "time": data.time,
                "created_at": data.created_at,
            }
        return data

    class Config:
        populate_by_name = True
