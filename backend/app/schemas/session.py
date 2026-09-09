from pydantic import BaseModel
from typing import Optional


class StartSessionRequest(BaseModel):
    recipe_id: str


class ChatMessageRequest(BaseModel):
    message: str


class SessionOut(BaseModel):
    session_id: str
    recipe_title: str
    current_step: int
    total_steps: int
    completed: bool
