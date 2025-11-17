from enum import Enum
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
    price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    ticker: str
    side: OrderSide
    user_id: str

    id: UUID = Field(default_factory=uuid4)

    class Config:
        validate_assignment = True
