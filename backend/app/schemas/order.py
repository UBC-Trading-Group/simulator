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


class OrderModel(BaseModel):
    price: float = Field(..., ge=0)  # gt will throw error when matching order
    quantity: int = Field(..., ge=0)
    ticker: str
    side: OrderSide
    user_id: str

    id: UUID = Field(default_factory=uuid4)

    class Config:
        validate_assignment = True


class TradingOrderRequest(BaseModel):
    symbol: str
    quantity: int = Field(..., ge=1)
    order_type: OrderSide = OrderSide.BUY
    latency_profile: Optional[str] = None
