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
from dependencies import get_instrument_manager, get_order_book

router = APIRouter()


@router.get("/instruments")
def list_instruments(db: Session = Depends(get_db)) -> List[dict]:
    """
    Return all tradable instruments with id and full name.
    """
    instruments = db.exec(select(Instrument)).all()
    return [{"id": inst.id, "full_name": inst.full_name} for inst in instruments]


@router.get("/")
def get_portfolio(
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    order_book=Depends(get_order_book),
    instrument_manager=Depends(get_instrument_manager),
) -> dict:
    """
    Get user's portfolio with current positions and real-time metrics
    """
    user_state = order_book._get_user_state(str(current_user.id))

    # Get current market prices
    current_prices = {}
    for instrument in instrument_manager.get_all_instruments():
        mid_price = order_book.mid_price(instrument.id)
        if mid_price is None:
            best_bid = order_book.best_bid(instrument.id)
            best_ask = order_book.best_ask(instrument.id)
            if best_bid and best_ask:
                mid_price = (best_bid.price + best_ask.price) / 2
            elif best_bid:
                mid_price = best_bid.price
            elif best_ask:
                mid_price = best_ask.price

        if mid_price:
            current_prices[instrument.id] = mid_price

    # Build portfolio positions
    portfolio_items = []

    for ticker, lots in user_state.portfolio.items():
        if not lots:
            continue

        # Get instrument details
        instrument = db.exec(select(Instrument).where(Instrument.id == ticker)).first()

        if not instrument or ticker not in current_prices:
            continue

        current_price = current_prices[ticker]
        total_qty = sum(qty for qty, _ in lots)
        avg_buy_price = (
            sum(qty * price for qty, price in lots) / total_qty if total_qty > 0 else 0
        )

        position_value = total_qty * current_price
        cost_basis = sum(qty * price for qty, price in lots)
        pnl = position_value - cost_basis
        pnl_percentage = (pnl / cost_basis * 100) if cost_basis > 0 else 0

        portfolio_items.append(
            {
                "symbol": ticker,
                "full_name": instrument.full_name,
                "sector": "TECH",  # Could be enhanced with actual sector
                "quantity": total_qty,
                "price": current_price,
                "avg_buy_price": avg_buy_price,
                "total_position": position_value,
                "pnl": pnl,
                "pnl_percentage": pnl_percentage,
            }
        )

    # Calculate metrics
    cash = user_state.get_cash()
    realized_pnl = user_state.get_total_realized_pnl()
    unrealized_pnl = user_state.calculate_unrealized_pnl(current_prices)
    portfolio_market_value = user_state.get_portfolio_market_value(current_prices)
    total_value = cash + portfolio_market_value

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "cash": cash,
        "realized_pnl": realized_pnl,
        "unrealized_pnl": unrealized_pnl,
        "portfolio_market_value": portfolio_market_value,
        "total_value": total_value,
        "positions": portfolio_items,
    }
