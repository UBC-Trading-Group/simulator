"""
Trading endpoints (example of protected endpoints)
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.deps import get_current_active_user
from app.db.database import get_db
from app.schemas.order import OrderCreate, OrderModel, OrderSide, OrderType
from app.schemas.user import UserInDB
from dependencies import (
    get_instrument_manager,
    get_order_book,
    order_book,
    price_engine,
)
from app.services.order_processor import OrderProcessor

router = APIRouter()


def get_order_processor_service():
    """Dependency to get order processor"""
    return OrderProcessor(order_book, price_engine)


def _serialize_order(order):
    """Utility to expose only safe fields from an order."""
    return {"price": order.price, "quantity": order.quantity}


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
    order_data: OrderCreate,
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    order_processor=Depends(get_order_processor_service),
    order_book=Depends(get_order_book),
) -> dict:
    """
    Create a trading order (requires authentication)
    Supports both market and limit orders.
    """
    # Validate limit order has price
    if order_data.order_type == OrderType.LIMIT:
        if order_data.price is None or order_data.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price is required for limit orders",
            )
        order_price = order_data.price
    else:
        # Market order: get current market price
        market_price = order_book.mid_price(order_data.symbol)
        if market_price is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to get market price for {order_data.symbol}",
            )
        order_price = market_price

    # Create OrderModel
    order = OrderModel(
        price=order_price,
        quantity=order_data.quantity,
        ticker=order_data.symbol,
        side=order_data.side,
        user_id=str(current_user.id),
    )

    # Process the order
    result = order_processor.process_order(order)

    # Handle status - it could be OrderStatus enum or string
    status_value = result["status"]
    if hasattr(status_value, "value"):
        status_str = status_value.value
    else:
        status_str = str(status_value)

    return {
        "order_id": str(order.id),
        "user_id": current_user.id,
        "symbol": order_data.symbol,
        "quantity": order_data.quantity,
        "side": order_data.side.value,
        "order_type": order_data.order_type.value,
        "price": order_price,
        "status": status_str,
        "message": result.get("message", "Order processed"),
        "unprocessed_quantity": result.get("unprocessed_quantity", 0),
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


@router.get("/orderbook/{symbol}")
def get_order_book_snapshot(
    symbol: str,
    depth: int = Query(default=5, ge=1, le=20),
    current_user: UserInDB = Depends(get_current_active_user),
    order_book=Depends(get_order_book),
    instrument_manager=Depends(get_instrument_manager),
):
    """
    Return a lightweight order book snapshot and mid-price for a given symbol.
    Depth is clamped to avoid returning an overly large payload.
    """
    if not instrument_manager.is_valid_instrument(symbol):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown symbol: {symbol}",
        )

    best_bid = order_book.best_bid(symbol)
    best_ask = order_book.best_ask(symbol)
    mid_price = order_book.mid_price(symbol)

    # Materialize top-of-book ladders without mutating the heaps
    raw_bids = order_book.buys.get(symbol, [])
    raw_asks = order_book.sells.get(symbol, [])

    bids = [
        {"price": -price, "quantity": quantity}
        for price, quantity, _ in sorted(raw_bids, key=lambda x: x[0])[:depth]
    ]
    asks = [
        {"price": price, "quantity": quantity}
        for price, quantity, _ in sorted(raw_asks, key=lambda x: x[0])[:depth]
    ]

    return {
        "symbol": symbol,
        "mid_price": mid_price,
        "best_bid": _serialize_order(best_bid) if best_bid else None,
        "best_ask": _serialize_order(best_ask) if best_ask else None,
        "bids": bids,
        "asks": asks,
    }
