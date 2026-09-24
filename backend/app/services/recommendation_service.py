from typing import List, Dict, Any
import json
import httpx
from app.models.recipe import Recipe
from app.models.user import User
from app.core.config import settings

class RecipeTool:
    """Base class for recommendation tools."""
    async def execute(self, ingredients: List[str], limit: int) -> List[Dict[str, Any]]:
        raise NotImplementedError

class DatabaseSearchTool(RecipeTool):
    """Searches the database for matching recipes."""
    async def execute(self, ingredients: List[str], limit: int) -> List[Dict[str, Any]]:
        all_recipes = await Recipe.find_all().to_list()
        scored = []
        ingredients_lower = [i.lower() for i in ingredients]
        
        for recipe in all_recipes:
            recipe_ingredients_lower = [i.lower() for i in recipe.ingredients]
            matches = sum(1 for ing in ingredients_lower if any(ing in r for r in recipe_ingredients_lower))
            if matches > 0:
                score = matches / max(len(recipe_ingredients_lower), 1)
                scored.append({
                    "recipe": recipe,
                    "score": round(score, 2),
                    "matched_ingredients": matches,
                    "total_ingredients": len(recipe_ingredients_lower)
                })
        
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

class LLMRecipeGeneratorTool(RecipeTool):
    """Generates new recipes using an LLM if database search isn't enough."""
    async def execute(self, ingredients: List[str], limit: int) -> List[Dict[str, Any]]:
        # Get a system user to author generated recipes
        system_user = await User.find_one(User.email == "system@cookai.local")
        if not system_user:
            return [] # fallback if no system user

        prompt = f"""
        You are a master chef AI.
        Generate {limit} creative recipes using these ingredients: {', '.join(ingredients)}.
        Return ONLY a JSON array of objects.
        Each object must have exactly: 
        - title (string)
        - ingredients (list of strings)
        - quantities (list of strings, matching ingredients)
        - steps (list of strings)
        - tags (list of strings)
        - time (integer, minutes)
        
        Output only JSON, no markdown blocks.
        """
        
        # We try Gemini via OpenRouter first
        api_key = settings.OPENROUTER_API_KEY
        if not api_key:
            return []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "google/gemini-2.5-flash-lite",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7
                    }
                )
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                
                # Cleanup potential markdown
                content = content.replace("```json", "").replace("```", "").strip()
                generated_recipes = json.loads(content)
                
                scored_results = []
                for idx, r in enumerate(generated_recipes):
                    # Save to DB so they have an ID
                    new_recipe = Recipe(
                        title=r["title"],
                        ingredients=r["ingredients"],
                        quantities=r["quantities"],
                        steps=r["steps"],
                        tags=r["tags"],
                        time=r["time"],
                        author_id=system_user.id
                    )
                    await new_recipe.insert()
                    
                    # Assume high match for generated ones
                    scored_results.append({
                        "recipe": new_recipe,
                        "score": 0.95 - (idx * 0.05), # Slightly decrement score for ranking
                        "matched_ingredients": len(ingredients),
                        "total_ingredients": len(r["ingredients"])
                    })
                return scored_results
        except Exception as e:
            print(f"LLM Generation failed: {e}")
            return []

class RecommendationEngine:
    def __init__(self):
        self.tools: List[RecipeTool] = [
            DatabaseSearchTool(),
            LLMRecipeGeneratorTool()
            # Add more tools here later (e.g. GoogleSearchTool)
        ]

    async def run(self, ingredients: List[str], limit: int) -> List[Dict[str, Any]]:
        results = []
        needed = limit
        
        for tool in self.tools:
            if needed <= 0:
                break
            tool_results = await tool.execute(ingredients, needed)
            
            # Filter out duplicates by title
            existing_titles = {r["recipe"].title for r in results}
            for tr in tool_results:
                if tr["recipe"].title not in existing_titles:
                    results.append(tr)
                    existing_titles.add(tr["recipe"].title)
                    needed -= 1
                    
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

engine = RecommendationEngine()

async def get_recommendations_by_ingredients(
    ingredients: List[str],
    limit: int = 10
) -> List[Dict[str, Any]]:
    return await engine.run(ingredients, limit)
