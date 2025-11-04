"""
Trading endpoints (example of protected endpoints)
"""
from app.services.trading import TradingService

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.schemas.user import UserInDB

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
        "cash": 3500.0, "lmao": "lmao"
    }


@router.post("/orders")
def create_order(
    symbol: str,
    quantity: int,
    order_type: str = "buy",
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Create a trading order (requires authentication)
    """
    if order_type not in ["buy", "sell"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order type must be 'buy' or 'sell'",
        )

    # This is just an example - in a real app you'd validate and create the order
    return {
        "order_id": f"order_{current_user.id}_{symbol}_{quantity}",
        "user_id": current_user.id,
        "symbol": symbol,
        "quantity": quantity,
        "type": order_type,
        "status": "pending",
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
