"""
LLM Detection Verifier — Multi-Provider Vision Engine

Architecture:
  1. YOLOv8 produces candidate ingredients from image detection.
  2. This verifier sends the candidates + image to an LLM with vision
     capability to verify, correct, and finalize the ingredient list.
  3. It auto-discovers which configured API provider supports vision
     models and routes the request there.

Provider priority for VISION verification:
  1. Gemini  (gemini-3.6-flash — native multimodal, fast, free tier)
  2. OpenRouter (google/gemini-2.5-flash-lite — fallback vision via OpenRouter)
  3. Groq text-only fallback (qwen/qwen3.8-27b — no image, text verification only)
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── API Endpoints ────────────────────────────────────────────────
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# ─── System Prompt ────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are an expert culinary vision and ingredient verification AI. "
    "Your job is to examine an image and provide the authoritative, final list of ingredients visible in the image.\n"
    "CRITICAL INSTRUCTION: The candidate ingredients provided to you may be from a basic object detector and might be incomplete or incorrect. "
    "You MUST rely primarily on your own visual analysis of the image to determine the actual ingredients present. "
    "Use the candidate list only as hints.\n"
    "CRITICAL INSTRUCTION 2: YOU MUST NOT output any `<think>` blocks, reasoning, or explanations. "
    "You MUST immediately start your response with `{` and end it with `}` and provide nothing else.\n"
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

TEXT_ONLY_SYSTEM_PROMPT = (
    "You are an expert culinary ingredient verification AI. "
    "A user has uploaded an image of food ingredients and an object detector has identified some candidates. "
    "Based on the candidate list and confidence scores, verify and refine the ingredient list.\n"
    "YOU MUST NOT output any `<think>` blocks, reasoning, or explanations. "
    "You MUST immediately start your response with `{` and end it with `}` and provide nothing else.\n"
    "Rules:\n"
    "1. Keep plausible food ingredients and remove unlikely false positives.\n"
    "2. Standardize common ingredient names (e.g. 'yellow onion' -> 'onion').\n"
    "3. Return strictly valid JSON:\n"
    "{\n"
    '  "confirmed_ingredients": ["ingredient1", "ingredient2"],\n'
    '  "removed_candidates": ["item1"],\n'
    '  "added_ingredients": ["item2"],\n'
    '  "reasoning": "Brief explanation of changes made"\n'
    "}"
)


# ─── JSON Parser ──────────────────────────────────────────────────

def _extract_json_from_text(text: Optional[str]) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON from model output, handling markdown blocks or think tags."""
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


# ─── Provider Implementations ────────────────────────────────────

async def _verify_with_gemini(
    candidate_ingredients: List[str],
    image_data_uri: Optional[str],
    confidence_scores: Optional[List[float]],
    prompt_text: str,
) -> Optional[Dict[str, Any]]:
    """
    Use Google Gemini API (native multimodal) for vision-based verification.
    Gemini supports image input natively via the generateContent endpoint.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None

    model = "gemini-3.6-flash"
    url = f"{GEMINI_API_URL}/{model}:generateContent?key={api_key}"

    # Build request parts
    parts = [{"text": f"{SYSTEM_PROMPT}\n\n{prompt_text}"}]

    # Add image if available
    if image_data_uri and image_data_uri.startswith("data:"):
        try:
            # Parse data URI: data:image/jpeg;base64,<data>
            header, b64_data = image_data_uri.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_data
                }
            })
        except Exception as e:
            logger.warning(f"Failed to parse image data URI for Gemini: {e}")

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
        }
    }

    try:
        logger.info(f"Calling Gemini ({model}) for vision-based ingredient verification...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                text_parts = content.get("parts", [])
                raw_text = "".join(p.get("text", "") for p in text_parts)
                parsed = _extract_json_from_text(raw_text)
                if parsed and "confirmed_ingredients" in parsed:
                    confirmed = [
                        str(x).strip().lower()
                        for x in parsed["confirmed_ingredients"]
                        if str(x).strip()
                    ]
                    if confirmed:
                        return {
                            "confirmed_ingredients": confirmed,
                            "removed_candidates": parsed.get("removed_candidates", []),
                            "added_ingredients": parsed.get("added_ingredients", []),
                            "reasoning": parsed.get("reasoning", "Confirmed by Gemini vision."),
                            "llm_confirmed": True,
                            "model_used": f"gemini/{model} (vision)",
                            "provider": "gemini",
                        }
            logger.warning(f"Gemini returned 200 but response could not be parsed.")
        else:
            logger.warning(f"Gemini returned status {response.status_code}: {response.text[:300]}")
    except Exception as err:
        logger.warning(f"Gemini vision call failed: {err}")

    return None


async def _verify_with_openrouter(
    candidate_ingredients: List[str],
    image_data_uri: Optional[str],
    confidence_scores: Optional[List[float]],
    prompt_text: str,
) -> Optional[Dict[str, Any]]:
    """
    Use OpenRouter API for vision-based verification.
    OpenRouter provides access to many vision models via an OpenAI-compatible API.
    """
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        return None

    # Use a cheap, fast, vision-capable model available on OpenRouter
    model = "google/gemini-2.5-flash-lite"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://cookai.app",
        "X-Title": "CookAI Ingredient Detector",
    }

    # Build message content with image
    user_content = []
    user_content.append({"type": "text", "text": prompt_text})

    if image_data_uri:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": image_data_uri}
        })

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    payload = {
        "model": model,
        "max_tokens": 1024,
        "temperature": 0.1,
        "messages": messages,
    }

    try:
        logger.info(f"Calling OpenRouter ({model}) for vision-based ingredient verification...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            raw_content = response.json()["choices"][0]["message"]["content"]
            parsed = _extract_json_from_text(raw_content)
            if parsed and "confirmed_ingredients" in parsed:
                confirmed = [
                    str(x).strip().lower()
                    for x in parsed["confirmed_ingredients"]
                    if str(x).strip()
                ]
                if confirmed:
                    return {
                        "confirmed_ingredients": confirmed,
                        "removed_candidates": parsed.get("removed_candidates", []),
                        "added_ingredients": parsed.get("added_ingredients", []),
                        "reasoning": parsed.get("reasoning", "Confirmed by OpenRouter vision."),
                        "llm_confirmed": True,
                        "model_used": f"openrouter/{model} (vision)",
                        "provider": "openrouter",
                    }
        else:
            logger.warning(f"OpenRouter returned status {response.status_code}: {response.text[:300]}")
    except Exception as err:
        logger.warning(f"OpenRouter vision call failed: {err}")

    return None


async def _verify_with_groq_text(
    candidate_ingredients: List[str],
    confidence_scores: Optional[List[float]],
    prompt_text: str,
) -> Optional[Dict[str, Any]]:
    """
    Fallback: Use Groq API for text-only verification (no vision).
    This is used when no vision-capable provider is available.
    """
    api_key = settings.LLM_API_KEY
    if not api_key or api_key == "your_llm_api_key":
        return None

    model = "qwen/qwen3.8-27b"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    messages = [
        {"role": "system", "content": TEXT_ONLY_SYSTEM_PROMPT},
        {"role": "user", "content": prompt_text},
    ]

    try:
        logger.info(f"Calling Groq ({model}) for text-only ingredient verification...")
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                GROQ_API_URL,
                headers=headers,
                json={
                    "model": model,
                    "max_tokens": 850,
                    "temperature": 0.1,
                    "messages": messages,
                },
            )

        if response.status_code == 200:
            raw_content = response.json()["choices"][0]["message"]["content"]
            parsed = _extract_json_from_text(raw_content)
            if parsed and "confirmed_ingredients" in parsed:
                confirmed = [
                    str(x).strip().lower()
                    for x in parsed["confirmed_ingredients"]
                    if str(x).strip()
                ]
                if confirmed:
                    return {
                        "confirmed_ingredients": confirmed,
                        "removed_candidates": parsed.get("removed_candidates", []),
                        "added_ingredients": parsed.get("added_ingredients", []),
                        "reasoning": parsed.get("reasoning", "Confirmed by Groq text LLM."),
                        "llm_confirmed": True,
                        "model_used": f"groq/{model} (text-only)",
                        "provider": "groq",
                    }
        else:
            logger.warning(f"Groq returned status {response.status_code}: {response.text[:300]}")
    except Exception as err:
        logger.warning(f"Groq text call failed: {err}")

    return None


# ─── Main Orchestrator ────────────────────────────────────────────

async def verify_and_prioritize_ingredients_with_llm(
    candidate_ingredients: List[str],
    image_data_uri: Optional[str] = None,
    confidence_scores: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Multi-provider LLM verification engine.

    Flow:
      1. Try Gemini (vision) — best for multimodal, free tier available
      2. Try OpenRouter (vision) — fallback vision via many providers
      3. Try Groq (text-only) — no image support, text verification only
      4. Return raw YOLO candidates if all providers fail

    The engine automatically discovers which provider has a vision-capable
    model and routes the image + candidates there for verification.
    """
    prompt_text = (
        f"YOLO detector candidate ingredients: {candidate_ingredients}.\n"
        f"Confidence scores: {confidence_scores if confidence_scores else 'N/A'}.\n"
        "Please inspect the provided image carefully. "
        "Verify which candidates are actually food ingredients visible in the image. "
        "Add any ingredients you can see that the detector missed. "
        "Remove any false positives (non-food items or incorrect detections)."
    )

    # ── Strategy 1: Gemini Vision (preferred — native multimodal) ──
    if settings.GEMINI_API_KEY:
        result = await _verify_with_gemini(
            candidate_ingredients, image_data_uri, confidence_scores, prompt_text
        )
        if result:
            return result
        logger.info("Gemini vision failed, trying next provider...")

    # ── Strategy 2: OpenRouter Vision (fallback vision) ──
    if settings.OPENROUTER_API_KEY:
        result = await _verify_with_openrouter(
            candidate_ingredients, image_data_uri, confidence_scores, prompt_text
        )
        if result:
            return result
        logger.info("OpenRouter vision failed, trying next provider...")

    # ── Strategy 3: Groq Text-Only (no vision, text verification) ──
    if settings.LLM_API_KEY:
        result = await _verify_with_groq_text(
            candidate_ingredients, confidence_scores, prompt_text
        )
        if result:
            return result
        logger.info("Groq text verification failed.")

    # ── Fallback: Return raw YOLO candidates ──
    logger.warning("All LLM providers failed. Returning raw YOLO detector output.")
    return {
        "confirmed_ingredients": candidate_ingredients,
        "removed_candidates": [],
        "added_ingredients": [],
        "reasoning": "All LLM verification providers failed. Using raw YOLO detector output.",
        "llm_confirmed": False,
        "model_used": "yolov8 (unverified)",
        "provider": "none",
    }
