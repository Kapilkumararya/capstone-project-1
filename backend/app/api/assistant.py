from fastapi import APIRouter, Depends, HTTPException
from beanie import PydanticObjectId
from datetime import datetime

from app.models.user import User
from app.models.recipe import Recipe
from app.models.session import CookingSession
from app.schemas.session import StartSessionRequest, ChatMessageRequest, SessionOut
from app.api.deps import get_current_user
from app.services.assistant_service import process_chat_message

router = APIRouter()


@router.post("/sessions", response_model=SessionOut)
async def start_session(
    request: StartSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Phase 5: Start a new cooking session for a given recipe.
    Returns the session context including the first step.
    """
    recipe = await Recipe.get(PydanticObjectId(request.recipe_id))
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Create a new session
    session = CookingSession(
        user_id=current_user.id,
        recipe_id=recipe.id,
        current_step=0,
        messages=[{
            "role": "assistant",
            "content": (
                f"Welcome! Let's cook '{recipe.title}'. "
                f"There are {len(recipe.steps)} steps in total.\n\n"
                f"Step 1: {recipe.steps[0] if recipe.steps else 'No steps defined.'}"
            )
        }]
    )
    await session.insert()

    return SessionOut(
        session_id=str(session.id),
        recipe_title=recipe.title,
        current_step=session.current_step,
        total_steps=len(recipe.steps),
        completed=session.completed
    )


@router.post("/sessions/{session_id}/chat")
async def chat(
    session_id: PydanticObjectId,
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Phase 5: Send a message to the cooking assistant within a session.
    """
    session = await CookingSession.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Cooking session not found")

    if session.user_id.ref.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your session")

    if session.completed:
        return {"response": "This cooking session has already been completed!", "completed": True}

    # Fetch recipe (resolve link)
    recipe = await Recipe.get(session.recipe_id.ref.id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe for this session not found")

    # Append user's message
    session.messages.append({"role": "user", "content": request.message})

    # Get assistant response
    result = await process_chat_message(session, recipe, request.message)

    # Advance step if needed
    if result.get("advance_step"):
        session.current_step = result["new_step"]

    if result.get("completed"):
        session.completed = True

    # Append assistant response to messages
    session.messages.append({"role": "assistant", "content": result["response"]})
    session.updated_at = datetime.utcnow()
    await session.save()

    return {
        "session_id": str(session.id),
        "response": result["response"],
        "current_step": session.current_step,
        "completed": session.completed
    }


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: PydanticObjectId,
    current_user: User = Depends(get_current_user)
):
    """
    Get the full history and state of a cooking session.
    """
    session = await CookingSession.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id.ref.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your session")

    return {
        "session_id": str(session.id),
        "current_step": session.current_step,
        "completed": session.completed,
        "messages": session.messages,
        "created_at": session.created_at,
        "updated_at": session.updated_at
    }


@router.get("/sessions")
async def list_sessions(current_user: User = Depends(get_current_user)):
    """
    List all cooking sessions for the current user.
    """
    sessions = await CookingSession.find(
        CookingSession.user_id.ref.id == current_user.id
    ).to_list()

    return [
        {
            "session_id": str(s.id),
            "current_step": s.current_step,
            "completed": s.completed,
            "created_at": s.created_at
        }
        for s in sessions
    ]
