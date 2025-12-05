from fastapi import APIRouter, Depends, HTTPException

from app.services.order_book import OrderBook
from dependencies import get_order_book

router = APIRouter()


@router.get("/{ticker}")
def get_orderbook(ticker: str, orderbook: OrderBook = Depends(get_order_book)):

    if not orderbook.has_ticker(ticker):
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{ticker}' does not exist"
        )

    return {
        "ticker": ticker,
        "bids": orderbook.get_bids(ticker),
        "asks": orderbook.get_asks(ticker),
    }
