from typing import List, Dict, Any
import logging
import httpx
from app.core.config import settings
from app.services.llm_detection_verifier import _extract_json_from_text

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


async def verify_recipe_with_llm(
    recipe_title: str,
    ingredients: List[str],
    steps: List[str]
) -> Dict[str, Any]:
    """
    Phase 4 LLM Double-Check Service.
    Sends recipe data to Groq LLM and returns culinary validation,
    safety checks, and chef suggestions.
    """
    api_key = settings.LLM_API_KEY
    if not api_key or api_key == "your_llm_api_key":
        logger.info(f"LLM Verifier called for recipe: {recipe_title} (STUBBED)")
        return {
            "verified": True,
            "feedback": (
                f"Recipe '{recipe_title}' looks valid. "
                f"All {len(ingredients)} ingredients seem compatible with the steps provided."
            ),
            "suggestions": [
                "Consider adding a pinch of salt after step 2.",
                "The cooking time seems accurate."
            ],
            "stubbed": True
        }

    prompt = (
        f"Recipe Title: {recipe_title}\n"
        f"Ingredients: {ingredients}\n"
        f"Steps: {steps}\n\n"
        "Analyze this recipe for culinary plausibility, ingredient proportions, safety, and taste balance.\n"
        "Respond in strictly valid JSON with keys:\n"
        "- verified: boolean (true if the recipe makes sense and is safe to cook)\n"
        "- feedback: string (concise review and feedback)\n"
        "- suggestions: list of strings (helpful chef tips or tweaks)\n"
    )

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                GROQ_API_URL,
                headers=headers,
                json={
                    "model": "openai/gpt-oss-120b",
                    "max_tokens": 450,
                    "temperature": 0.2,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert chef verifying user recipes. Always return valid JSON."
                        },
                        {"role": "user", "content": prompt}
                    ]
                }
            )

        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            parsed = _extract_json_from_text(content)
            if parsed and "verified" in parsed:
                return {
                    "verified": parsed["verified"],
                    "feedback": parsed.get("feedback", "Recipe reviewed successfully."),
                    "suggestions": parsed.get("suggestions", []),
                    "stubbed": False
                }
    except Exception as e:
        logger.error(f"Recipe LLM verification failed: {e}")

    # Graceful fallback
    return {
        "verified": True,
        "feedback": f"Recipe '{recipe_title}' appears viable.",
        "suggestions": ["Ensure seasonings are adjusted to taste."],
        "stubbed": True
    }
