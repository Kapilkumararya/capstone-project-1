from typing import List, Dict, Any
from app.models.recipe import Recipe


async def get_recommendations_by_ingredients(
    ingredients: List[str],
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Phase 3 Recommendation Engine:
    Finds recipes where the most provided ingredients match.
    Uses a simple ingredient-overlap scoring strategy for now.
    Can be upgraded to a vector-similarity or ML model later.
    """
    # Fetch all recipes from DB
    all_recipes = await Recipe.find_all().to_list()

    scored = []
    ingredients_lower = [i.lower() for i in ingredients]

    for recipe in all_recipes:
        recipe_ingredients_lower = [i.lower() for i in recipe.ingredients]
        # Count how many of the provided ingredients are in the recipe
        matches = sum(1 for ing in ingredients_lower if any(ing in r for r in recipe_ingredients_lower))
        if matches > 0:
            score = matches / max(len(recipe_ingredients_lower), 1)
            scored.append({
                "recipe": recipe,
                "score": round(score, 2),
                "matched_ingredients": matches,
                "total_ingredients": len(recipe_ingredients_lower)
            })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:limit]
