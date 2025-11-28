"""
Trading endpoints (example of protected endpoints)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.schemas.order import TradingOrderRequest
from app.schemas.user import UserInDB
from app.services.latency_profile import normalize_latency_curve

router = APIRouter()


@router.get("/portfolio")
def get_portfolio(
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get user's portfolio (requires authentication)
    """
    # This is just an example - in a real app you'd query the database
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "portfolio_value": 10000.0,
        "positions": [
            {"symbol": "AAPL", "quantity": 10, "value": 1500.0},
            {"symbol": "GOOGL", "quantity": 5, "value": 5000.0},
        ],
        "cash": 3500.0,
    }


@router.post("/orders")
def create_order(
    order: TradingOrderRequest,
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Create a trading order (requires authentication)
    """
    latency_curve: Optional[List[float]] = None
    if order.latency_profile:
        latency_curve = normalize_latency_curve(order.latency_profile)

    # This is just an example - in a real app you'd validate and create the order
    return {
        "order_id": f"order_{current_user.id}_{order.symbol}_{order.quantity}",
        "user_id": current_user.id,
        "symbol": order.symbol,
        "quantity": order.quantity,
        "type": order.order_type,
        "status": "pending",
        "latency_profile": order.latency_profile,
        "latency_curve": latency_curve,
        "message": "Order created successfully",
    }


@router.get("/orders")
def get_orders(
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[dict]:
    """
    Get user's orders (requires authentication)
    """
    # This is just an example - in a real app you'd query the database
    return [
        {
            "order_id": f"order_{current_user.id}_AAPL_10",
            "symbol": "AAPL",
            "quantity": 10,
            "type": "buy",
            "status": "filled",
            "price": 150.0,
        },
        {
            "order_id": f"order_{current_user.id}_GOOGL_5",
            "symbol": "GOOGL",
            "quantity": 5,
            "type": "buy",
            "status": "pending",
            "price": 2500.0,
        },
    ]
