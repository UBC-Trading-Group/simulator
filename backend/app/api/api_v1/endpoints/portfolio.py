"""
Portfolio endpoints
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.deps import get_current_active_user, get_db
from app.models.bot_position import BotPosition
from app.models.instrument import Instrument
from app.schemas.user import UserInDB

router = APIRouter()


@router.get("/")
def get_portfolio(
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get user's portfolio with current positions
    """
    # Get all positions for the user's bot
    # Assuming user has a bot_id - adjust based on your actual schema
    statement = select(BotPosition).where(BotPosition.bot_id == current_user.id)
    positions = db.exec(statement).all()

    portfolio_items = []
    total_value = 0.0

    for position in positions:
        # Get instrument details
        instrument = db.exec(
            select(Instrument).where(Instrument.id == position.instrument_id)
        ).first()

        if not instrument:
            continue

        # Calculate position value
        current_price = instrument.s_0  # Use current price from instrument
        position_value = position.qty * current_price
        total_value += position_value

        # Calculate P&L (assuming you track entry price somewhere)
        # For now, using a simple calculation
        pnl = position_value - (position.cash if position.cash else 0)

        portfolio_items.append(
            {
                "symbol": instrument.id,
                "full_name": instrument.full_name,
                "sector": "TECH",  # You may need to add sector to Instrument model
                "quantity": position.qty,
                "price": current_price,
                "total_position": position_value,
                "pnl": pnl,
                "pnl_percentage": (
                    (pnl / position.cash * 100)
                    if position.cash and position.cash > 0
                    else 0
                ),
            }
        )

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "total_value": total_value,
        "cash": 0.0,  # Add cash balance if available in your model
        "positions": portfolio_items,
    }
