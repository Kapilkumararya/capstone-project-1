from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


async def verify_recipe_with_llm(
    recipe_title: str,
    ingredients: List[str],
    steps: List[str]
) -> Dict[str, Any]:
    """
    Phase 4 LLM Double-Check Service.
    Sends recipe data to an LLM and gets a verification response.

    Currently STUBBED — returns a mock response.
    To activate: import your LLM client here and replace the stub below.
    """
    logger.info(f"LLM Verifier called for recipe: {recipe_title} (STUBBED)")

    # --- STUB RESPONSE ---
    # Replace this block with real LLM API call once API key is configured.
    # Example structure of what the real call would look like:
    #
    # from app.core.config import settings
    # import google.generativeai as genai
    # genai.configure(api_key=settings.LLM_API_KEY)
    # model = genai.GenerativeModel("gemini-1.5-pro")
    # prompt = f"Verify this recipe: {recipe_title} with ingredients {ingredients}..."
    # response = model.generate_content(prompt)
    # return {"verified": True, "feedback": response.text, "stubbed": False}

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
        "stubbed": True  # Remove this flag once real LLM is connected
    }
