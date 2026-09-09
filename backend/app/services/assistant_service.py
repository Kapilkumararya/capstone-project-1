from typing import Dict, Any, List
from app.models.session import CookingSession
from app.models.recipe import Recipe
import logging

logger = logging.getLogger(__name__)


async def process_chat_message(
    session: CookingSession,
    recipe: Recipe,
    user_message: str
) -> str:
    """
    Phase 5 Cooking Assistant Service.
    Takes the session context (current step, chat history) and the user's message,
    then returns a helpful response.

    Currently STUBBED — returns contextual mock responses.
    To activate: pass messages + recipe context to your LLM (Gemini/OpenAI/etc.)
    """
    logger.info(f"Assistant called for session {session.id} (STUBBED)")

    current_step_idx = session.current_step
    steps = recipe.steps
    total_steps = len(steps)

    # Simple intent detection on the stub
    msg_lower = user_message.lower()

    if any(kw in msg_lower for kw in ["next", "continue", "done", "ok", "got it"]):
        if current_step_idx < total_steps - 1:
            new_step = current_step_idx + 1
            return {
                "response": f"Great! Moving to step {new_step + 1}: {steps[new_step]}",
                "advance_step": True,
                "new_step": new_step,
                "completed": False,
                "stubbed": True
            }
        else:
            return {
                "response": f"🎉 You've completed all {total_steps} steps! Enjoy your meal!",
                "advance_step": False,
                "new_step": current_step_idx,
                "completed": True,
                "stubbed": True
            }

    elif any(kw in msg_lower for kw in ["repeat", "again", "what was", "remind"]):
        current_step_text = steps[current_step_idx] if steps else "No steps defined."
        return {
            "response": f"Sure! Here's step {current_step_idx + 1} again: {current_step_text}",
            "advance_step": False,
            "new_step": current_step_idx,
            "completed": False,
            "stubbed": True
        }

    else:
        # Generic assistant response (real LLM would go here)
        # Replace with actual LLM call:
        # from app.core.config import settings
        # prompt = f"You are a cooking assistant. The user is on step {current_step_idx + 1}: '{steps[current_step_idx]}'. They asked: '{user_message}'. Help them."
        # response = await call_llm(prompt)
        current_step_text = steps[current_step_idx] if steps else "No steps defined."
        return {
            "response": (
                f"You're on step {current_step_idx + 1}: '{current_step_text}'. "
                f"I'm here to help! (Full LLM response will be available once API key is configured.)"
            ),
            "advance_step": False,
            "new_step": current_step_idx,
            "completed": False,
            "stubbed": True
        }
