from fastapi import APIRouter, Depends, Query

from app.services.order_book import OrderBook
from dependencies import get_order_book

router = APIRouter()


@router.get("/{ticker}")
def get_orderbook(
        ticker: str,
        orderbook: OrderBook = Depends(get_order_book)):

    return {
        "ticker": ticker,
        "bids": orderbook.get_bids(ticker),
        "asks": orderbook.get_asks(ticker),
    }
