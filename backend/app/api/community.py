from fastapi import APIRouter, Depends, HTTPException
from beanie import PydanticObjectId
from typing import List

from app.models.user import User
from app.models.recipe import Recipe
from app.models.community import CommunityPost, Comment
from app.schemas.community import CommunityPostCreate, CommunityPostOut, CommentCreate, CommentOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/posts", response_model=List[CommunityPostOut])
async def get_posts(skip: int = 0, limit: int = 50):
    posts = await CommunityPost.find_all().sort("-created_at").skip(skip).limit(limit).to_list()
    
    out_posts = []
    for p in posts:
        out_posts.append({
            "id": str(p.id),
            "author_name": p.author_name,
            "title": p.title,
            "content": p.content,
            "image_url": p.image_url,
            "video_url": p.video_url,
            "recipe_id": str(p.recipe_id.id) if p.recipe_id else None,
            "embedded_recipe": p.embedded_recipe,
            "votes": p.votes,
            "tags": p.tags,
            "created_at": p.created_at,
            "comments": [{"author_name": c.author_name, "content": c.content, "created_at": c.created_at} for c in p.comments]
        })
    return out_posts

@router.post("/posts", response_model=CommunityPostOut)
async def create_post(
    post_in: CommunityPostCreate,
    current_user: User = Depends(get_current_user)
):
    recipe = None
    if post_in.recipe_id:
        recipe = await Recipe.get(PydanticObjectId(post_in.recipe_id))

    post = CommunityPost(
        author_name=current_user.username,
        author_id=current_user.id,
        recipe_id=recipe.id if recipe else None,
        title=post_in.title,
        content=post_in.content,
        image_url=post_in.image_url,
        video_url=post_in.video_url,
        embedded_recipe=post_in.embedded_recipe,
        tags=post_in.tags
    )
    await post.insert()
    
    return {
        "id": str(post.id),
        "author_name": post.author_name,
        "title": post.title,
        "content": post.content,
        "image_url": post.image_url,
        "video_url": post.video_url,
        "recipe_id": str(post.recipe_id.id) if post.recipe_id else None,
        "embedded_recipe": post.embedded_recipe,
        "votes": post.votes,
        "tags": post.tags,
        "created_at": post.created_at,
        "comments": []
    }

@router.post("/posts/{post_id}/vote")
async def vote_post(
    post_id: PydanticObjectId,
    current_user: User = Depends(get_current_user)
):
    post = await CommunityPost.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.votes += 1
    await post.save()
    return {"message": "Voted successfully", "votes": post.votes}

@router.post("/posts/{post_id}/comment", response_model=CommentOut)
async def comment_on_post(
    post_id: PydanticObjectId,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user)
):
    post = await CommunityPost.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    new_comment = Comment(
        author_name=current_user.username,
        content=comment_in.content
    )
    
    post.comments.append(new_comment)
    await post.save()
    
    return new_comment

@router.get("/creators/popular")
async def get_popular_creators():
    # Rank creators by the total real votes on their posts
    posts = await CommunityPost.find_all().to_list()
    author_votes = {}
    for p in posts:
        author_votes[p.author_name] = author_votes.get(p.author_name, 0) + p.votes
        
    sorted_authors = sorted(author_votes.items(), key=lambda x: x[1], reverse=True)
    # Return real calculated votes
    return [{"name": name, "followers": votes} for name, votes in sorted_authors[:5]]

@router.get("/recipes/trending")
async def get_trending_recipes():
    # Fetch latest recipes without fake upvotes.
    # If there is no real upvote field on Recipe, we just return the actual data.
    recipes = await Recipe.find_all().sort("-created_at").limit(5).to_list()
    return [{"id": str(r.id), "title": r.title, "upvotes": 0, "image_url": None} for r in recipes]
