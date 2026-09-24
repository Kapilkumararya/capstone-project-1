from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.user import UserOut
from app.api.deps import get_current_superuser

router = APIRouter()

@router.get("/users", response_model=list[UserOut])
async def get_all_users_admin(
    current_admin: User = Depends(get_current_superuser)
):
    """
    Get all users. Only accessible by superusers.
    """
    users = await User.find_all().to_list()
    return [{"id": str(u.id), "username": u.username, "email": u.email, "dietary_preferences": getattr(u, "dietary_preferences", []), "max_prep_time": getattr(u, "max_prep_time", 30)} for u in users]
