import asyncio

from app.models.instrument import Instrument
from app.services.order_book import OrderBook


class LiquidityBotManager:
    def __init__(self, instruments: list[Instrument], order_book: OrderBook):
        # Maps instrument id to liquidity bot
        self.liquidity_bots = {
            instrument.id: LiquidityBot(instrument.id, instrument.s_0, 5)
            for instrument in instruments
        }
        self.order_book = order_book

    def process_book_snapshot(self, snapshot: dict):
        for bid_price, depth in snapshot["bids"]:
            self.order_book.match_order(
                OrderModel(price=bid_price, quantity=depth, side=OrderSide.BUY)
            )
        for ask_price, depth in snapshot["asks"]:
            self.order_book.match_order(
                OrderModel(price=ask_price, quantity=depth, side=OrderSide.SELL)
            )

    async def run(self):
        self.is_running = True
        while self.is_running:
            try:
                for _, liquidity_bot in self.liquidity_bots.items():
                    book_snapshot = liquidity_bot.generate_order_book()
                    self.process_book_snapshot(book_snapshot)
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception:
                await asyncio.sleep(10)
