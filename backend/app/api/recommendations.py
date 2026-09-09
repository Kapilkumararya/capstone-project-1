from fastapi import APIRouter, Depends, HTTPException
from beanie import PydanticObjectId
from typing import List

from app.models.user import User
from app.models.recipe import Recipe
from app.schemas.recommendation import RecommendationRequest, LLMVerifyRequest
from app.schemas.recipe import RecipeOut
from app.api.deps import get_current_user
from app.services.recommendation_service import get_recommendations_by_ingredients
from app.services.llm_verifier_service import verify_recipe_with_llm

router = APIRouter()


@router.post("/")
async def recommend_recipes(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Phase 3: Returns a ranked list of recipes based on the provided ingredient list.
    """
    results = await get_recommendations_by_ingredients(
        ingredients=request.ingredients,
        limit=request.limit
    )

    if not results:
        return {"message": "No matching recipes found for your ingredients.", "results": []}

    # Shape the response
    response = []
    for r in results:
        recipe: Recipe = r["recipe"]
        response.append({
            "recipe_id": str(recipe.id),
            "title": recipe.title,
            "match_score": r["score"],
            "matched_ingredients": r["matched_ingredients"],
            "total_ingredients": r["total_ingredients"],
            "tags": recipe.tags,
            "time": recipe.time
        })

    return {"results": response}


@router.post("/verify/{recipe_id}")
async def verify_recipe(
    recipe_id: PydanticObjectId,
    current_user: User = Depends(get_current_user)
):
    """
    Phase 4: LLM Double-Check — verifies a recipe's steps and ingredient compatibility.
    """
    recipe = await Recipe.get(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    verification = await verify_recipe_with_llm(
        recipe_title=recipe.title,
        ingredients=recipe.ingredients,
        steps=recipe.steps
    )

    return {
        "recipe_id": str(recipe.id),
        "title": recipe.title,
        **verification
    }
