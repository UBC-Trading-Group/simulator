from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.leaderboard import Leaderboard
from dependencies import get_leaderboard

router = APIRouter()

@router.get("/competitions/{competition_id}/leaderboard")
async def get_leaderboard(
    competition_id: str,
    limit: int = 100,
    leaderboard: Leaderboard = Depends(get_leaderboard),
    current_user: User = Depends(get_current_active_user),
) -> List[dict]:
    return await leaderboard.get_leaderboard(competition_id, limit)

@router.get("/competitions/{competition_id}/rank/{user_id}")
async def get_user_rank(
    competition_id: str,
    user_id: str,
    leaderboard: Leaderboard = Depends(get_leaderboard),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    rank = await leaderboard.get_user_rank(competition_id, user_id)
    if rank is None:
        raise HTTPException(status_code=404, detail="User not found in leaderboard")
    return {"user_id": user_id, "rank": rank, "competition_id": competition_id}
