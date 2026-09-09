from typing import Dict, Any, List
import logging
import httpx
from app.models.session import CookingSession
from app.models.recipe import Recipe
from app.core.config import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


async def process_chat_message(
    session: CookingSession,
    recipe: Recipe,
    user_message: str
) -> Dict[str, Any]:
    """
    Phase 5 Cooking Assistant Service.
    Takes the session context (current step, chat history, recipe details)
    and uses Groq LLM to provide intelligent, contextual guidance.
    """
    current_step_idx = session.current_step
    steps = recipe.steps or []
    total_steps = len(steps)
    current_step_text = steps[current_step_idx] if current_step_idx < total_steps else "All steps complete"

    msg_lower = user_message.lower().strip()

    # Step navigation shortcuts
    if any(kw in msg_lower for kw in ["next step", "continue", "step done", "done with this step", "next"]):
        if current_step_idx < total_steps - 1:
            new_step = current_step_idx + 1
            return {
                "response": f"Moving to step {new_step + 1}: {steps[new_step]}",
                "advance_step": True,
                "new_step": new_step,
                "completed": False,
                "stubbed": False
            }
        else:
            return {
                "response": f"🎉 Congratulations! You have completed all {total_steps} steps of '{recipe.title}'! Enjoy your dish!",
                "advance_step": False,
                "new_step": current_step_idx,
                "completed": True,
                "stubbed": False
            }

    if any(kw in msg_lower for kw in ["repeat step", "what step", "remind me what step"]):
        return {
            "response": f"You are currently on step {current_step_idx + 1} of {total_steps}: {current_step_text}",
            "advance_step": False,
            "new_step": current_step_idx,
            "completed": False,
            "stubbed": False
        }

    # Contextual LLM Chef Assistant
    api_key = settings.LLM_API_KEY
    if api_key and api_key != "your_llm_api_key":
        try:
            # Build conversation history from session
            recent_history = session.chat_history[-6:] if session.chat_history else []
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an encouraging, professional culinary assistant guiding someone who is actively cooking.\n"
                        f"Dish: {recipe.title}\n"
                        f"Ingredients: {recipe.ingredients}\n"
                        f"Current Step ({current_step_idx + 1} of {total_steps}): {current_step_text}\n"
                        f"All Steps: {steps}\n\n"
                        "Give concise, practical kitchen advice (1-3 sentences). "
                        "Keep your tone helpful, alert, and friendly."
                    )
                }
            ]
            for h in recent_history:
                messages.append({"role": h.role, "content": h.message})
            messages.append({"role": "user", "content": user_message})

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    GROQ_API_URL,
                    headers=headers,
                    json={
                        "model": "openai/gpt-oss-120b",
                        "max_tokens": 250,
                        "temperature": 0.4,
                        "messages": messages
                    }
                )

            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"].strip()
                return {
                    "response": answer,
                    "advance_step": False,
                    "new_step": current_step_idx,
                    "completed": False,
                    "stubbed": False
                }
            else:
                logger.warning(f"Assistant LLM API returned {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"Assistant LLM call failed: {e}")

    # Fallback response
    return {
        "response": f"On step {current_step_idx + 1}: '{current_step_text}'. Need help with timing, technique, or ingredients?",
        "advance_step": False,
        "new_step": current_step_idx,
        "completed": False,
        "stubbed": True
    }
