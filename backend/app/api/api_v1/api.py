"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter, Depends

from app.api.api_v1.endpoints import (
    admin,
    auth,
    leaderboard,
    orderbook,
    portfolio,
    trading,
    users,
)
from app.core.deps import get_current_active_superuser

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(orderbook.router, prefix="/orderbook", tags=["orderbook"])
api_router.include_router(
    leaderboard.router, prefix="/leaderboard", tags=["leaderboard"]
)
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_active_superuser)],
)
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
