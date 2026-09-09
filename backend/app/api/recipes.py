from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from app.models.user import User
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[RecipeOut])
async def get_recipes(skip: int = 0, limit: int = 100):
    recipes = await Recipe.find_all().skip(skip).limit(limit).to_list()
    return recipes

@router.post("/", response_model=RecipeOut)
async def create_recipe(
    recipe_in: RecipeCreate,
    current_user: User = Depends(get_current_user)
):
    recipe = Recipe(
        **recipe_in.model_dump(),
        author_id=current_user.id
    )
    await recipe.insert()
    return recipe

@router.get("/{id}", response_model=RecipeOut)
async def get_recipe(id: PydanticObjectId):
    recipe = await Recipe.get(id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.put("/{id}", response_model=RecipeOut)
async def update_recipe(
    id: PydanticObjectId,
    recipe_in: RecipeUpdate,
    current_user: User = Depends(get_current_user)
):
    recipe = await Recipe.get(id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if recipe.author_id.ref.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this recipe")

    update_data = recipe_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recipe, field, value)
    
    await recipe.save()
    return recipe

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    id: PydanticObjectId,
    current_user: User = Depends(get_current_user)
):
    recipe = await Recipe.get(id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if recipe.author_id.ref.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this recipe")
        
    await recipe.delete()
