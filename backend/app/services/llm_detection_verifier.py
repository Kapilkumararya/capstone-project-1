import json
import logging
import re
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are an expert culinary vision and ingredient verification AI. "
    "Your job is to examine an image and provide the authoritative, final list of ingredients visible in the image.\n"
    "CRITICAL INSTRUCTION: The candidate ingredients provided to you may be from a dummy simulator and might be completely incorrect. "
    "You MUST completely ignore the candidate ingredients if they do not match what you see in the image. "
    "Rely solely on your own visual analysis of the image to determine the actual ingredients present.\n"
    "CRITICAL INSTRUCTION 2: YOU MUST NOT output any `<think>` blocks, reasoning, or explanations. You MUST immediately start your response with `{` and end it with `}` and provide nothing else.\n"
    "Rules:\n"
    "1. Identify all food ingredients clearly visible in the image.\n"
    "2. Remove non-food items, containers, cutlery, or erroneous detections.\n"
    "3. Standardize common ingredient names (e.g. 'yellow onion' -> 'onion', 'clove of garlic' -> 'garlic').\n"
    "4. Return strictly valid JSON with no extra commentary:\n"
    "{\n"
    '  "confirmed_ingredients": ["ingredient1", "ingredient2"],\n'
    '  "removed_candidates": ["item1"],\n'
    '  "added_ingredients": ["item2"],\n'
    '  "reasoning": "Brief explanation of changes made"\n'
    "}"
)


def _extract_json_from_text(text: Optional[str]) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON from model output, handling markdown blocks or thoughts."""
    if not text:
        logger.warning("LLM response content was empty or None.")
        return None
    try:
        # Strip potential think tags from reasoning models
        text_clean = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        
        # Check for ```json ... ``` code block
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text_clean, re.DOTALL)
        if match:
            return json.loads(match.group(1))
            
        # Check for raw { ... }
        match_raw = re.search(r"(\{.*\})", text_clean, re.DOTALL)
        if match_raw:
            return json.loads(match_raw.group(1))
            
        return json.loads(text_clean)
    except Exception as e:
        logger.warning(f"Could not parse JSON from LLM response: {e}. Raw content was: {repr(text)}")
        return None


async def verify_and_prioritize_ingredients_with_llm(
    candidate_ingredients: List[str],
    image_data_uri: Optional[str] = None,
    confidence_scores: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Sends the candidate ingredients (and optimized image if available)
    to Groq LLM to verify, clean, and prioritize ingredients.
    The LLM has final authority/priority over the detector.
    """
    api_key = settings.LLM_API_KEY
    if not api_key or api_key == "your_llm_api_key":
        logger.warning("No LLM_API_KEY set. Falling back to detector ingredients.")
        return {
            "confirmed_ingredients": candidate_ingredients,
            "removed_candidates": [],
            "added_ingredients": [],
            "reasoning": "LLM_API_KEY not configured. Used raw detector output.",
            "llm_confirmed": False,
            "model_used": "detector_only"
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt_text = (
        f"Simulated candidate ingredients (MAY BE WRONG): {candidate_ingredients}.\n"
        f"Simulated confidence scores: {confidence_scores if confidence_scores else 'N/A'}.\n"
        "Please inspect the provided image carefully. If the simulated candidates do not match "
        "what you see in the image, completely ignore them and output only the actual ingredients "
        "visible in the image."
    )

    # Strategy 1: Attempt Multimodal Vision Call if image provided
    if image_data_uri:
        try:
            logger.info("Calling Groq Vision model (qwen/qwen3.6-27b) for ingredient confirmation...")
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": image_data_uri}}
                    ]
                }
            ]
            
            async with httpx.AsyncClient(timeout=25.0) as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers=headers,
                    json={
                        "model": "qwen/qwen3.6-27b",
                        "max_tokens": 850,
                        "temperature": 0.1,
                        "messages": messages
                    }
                )

            if response.status_code == 200:
                raw_content = response.json()["choices"][0]["message"]["content"]
                parsed = _extract_json_from_text(raw_content)
                if parsed and "confirmed_ingredients" in parsed:
                    confirmed = [str(x).strip().lower() for x in parsed["confirmed_ingredients"] if str(x).strip()]
                    if confirmed:
                        return {
                            "confirmed_ingredients": confirmed,
                            "removed_candidates": parsed.get("removed_candidates", []),
                            "added_ingredients": parsed.get("added_ingredients", []),
                            "reasoning": parsed.get("reasoning", "Confirmed by vision LLM."),
                            "llm_confirmed": True,
                            "model_used": "qwen/qwen3.6-27b (vision)"
                        }
            else:
                logger.warning(f"Groq Vision returned status {response.status_code}: {response.text}")
        except Exception as err:
            logger.warning(f"Groq Vision call failed or timed out: {err}. Falling back to text LLM.")

    # Strategy 2: Fast Text LLM Verification (openai/gpt-oss-120b)
    try:
        logger.info("Calling Groq Text model (openai/gpt-oss-120b) for ingredient validation...")
        text_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text}
        ]

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                GROQ_API_URL,
                headers=headers,
                json={
                    "model": "openai/gpt-oss-120b",
                    "max_tokens": 1024,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"},
                    "messages": text_messages
                }
            )

        if response.status_code == 200:
            raw_content = response.json()["choices"][0]["message"]["content"]
            parsed = _extract_json_from_text(raw_content)
            if parsed and "confirmed_ingredients" in parsed:
                confirmed = [str(x).strip().lower() for x in parsed["confirmed_ingredients"] if str(x).strip()]
                if confirmed:
                    return {
                        "confirmed_ingredients": confirmed,
                        "removed_candidates": parsed.get("removed_candidates", []),
                        "added_ingredients": parsed.get("added_ingredients", []),
                        "reasoning": parsed.get("reasoning", "Confirmed by LLM reasoning engine."),
                        "llm_confirmed": True,
                        "model_used": "openai/gpt-oss-120b (text)"
                    }
        else:
            logger.error(f"Groq Text LLM error: {response.status_code} - {response.text}")
    except Exception as err:
        logger.error(f"Text LLM verification failed: {err}")

    # Fallback to detector candidates if both LLM attempts failed
    return {
        "confirmed_ingredients": candidate_ingredients,
        "removed_candidates": [],
        "added_ingredients": [],
        "reasoning": "LLM calls failed or rate-limited. Falling back to detector candidates.",
        "llm_confirmed": False,
        "model_used": "fallback"
    }
