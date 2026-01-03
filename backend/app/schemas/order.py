from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderModel(BaseModel):
    price: float = Field(..., ge=0)  # gt will throw error when matching order
    quantity: int = Field(..., ge=0)
    ticker: str
    side: OrderSide
    user_id: str

    id: UUID = Field(default_factory=uuid4)

    class Config:
        validate_assignment = True


class OrderCreate(BaseModel):
    """Request schema for creating an order"""

    symbol: str = Field(..., description="Ticker symbol")
    quantity: int = Field(..., gt=0, description="Order quantity")
    side: OrderSide = Field(..., description="Order side: buy or sell")
    order_type: OrderType = Field(..., description="Order type: market or limit")
    price: Optional[float] = Field(
        None,
        ge=0,
        description="Limit price (required for limit orders, ignored for market orders)",
    )

    class Config:
        validate_assignment = True
