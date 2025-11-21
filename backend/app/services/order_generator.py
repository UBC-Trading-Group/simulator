import asyncio
from typing import Optional

from app.schemas.order import OrderModel, OrderSide
from app.services.gbm_manager import GBMManager
from app.services.instrument_manager import InstrumentManager
from app.services.order_book import OrderBook


class OrderGenerator:
    def __init__(
        self,
        instrument_manager: InstrumentManager,
        order_book: OrderBook,
        gbm_manager: GBMManager,
        interval_seconds: float = 5.0,
        user_id: str = "generator",
        default_quantity: int = 1,
    ):
        self.instrument_manager = instrument_manager
        self.order_book = order_book
        self.gbm_manager = gbm_manager
        self.interval_seconds = interval_seconds
        self.user_id = user_id
        self.default_quantity = default_quantity
        self.is_running = False

    def _current_spread(self, ticker: str) -> Optional[float]:
        spread = self.order_book.clamped_spread(ticker)
        return spread

    def _derive_spread(self, ticker: str, mid_price: float) -> float:
        spread = self._current_spread(ticker)
        if spread is not None and spread > 0:
            return spread
        return None  # TODO: how to handle this case when we don't have a spread yet?

    def _process_ticker(self, ticker: str):
        mid_gbm = self.gbm_manager.get_ticker_current_gbm_price(ticker)
        if mid_gbm is None:
            return

        spread = self._derive_spread(ticker, mid_gbm)

        # place buy and sell orders at new mid-price calculated by GBM +/- spread
        target_bid = mid_gbm - (spread / 2)
        target_ask = mid_gbm + (spread / 2)

        bid_upper = self.order_book.bid_clamp(ticker)
        ask_lower = self.order_book.ask_clamp(ticker)

        best_ask_w_clamp = self.order_book.best_ask_within_clamp(ticker)
        best_bid_w_clamp = self.order_book.best_bid_within_clamp(ticker)

        # TODO: handle the case to shift beyond best ask and bid
        buy_order = OrderModel(
            price=round(target_bid, 2),
            quantity=self.default_quantity,
            ticker=ticker,
            side=OrderSide.BUY,
            user_id=self.user_id,
        )
        self.order_book.match_order(buy_order)

        sell_order = OrderModel(
            price=round(target_ask, 2),
            quantity=self.default_quantity,
            ticker=ticker,
            side=OrderSide.SELL,
            user_id=self.user_id,
        )
        self.order_book.match_order(sell_order)

    async def run(self):
        self.is_running = True
        while self.is_running:
            try:
                for instrument in self.instrument_manager.get_all_instruments():
                    ticker = instrument.id

                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception:
                await asyncio.sleep(self.interval_seconds)
