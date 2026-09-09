from pydantic import BaseModel
from typing import List

class RecommendationRequest(BaseModel):
    ingredients: List[str]
    limit: int = 10

class LLMVerifyRequest(BaseModel):
    recipe_id: str
