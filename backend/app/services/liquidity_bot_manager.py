import asyncio

from app.models.instrument import Instrument
from app.schemas.order import OrderModel, OrderSide
from app.services.liquidity_bot import LiquidityBot
from app.services.order_book import OrderBook


class LiquidityBotManager:
    def __init__(self, instruments: list[Instrument], order_book: OrderBook):
        # Maps instrument id to liquidity bot
        self.liquidity_bots = {
            instrument.id: LiquidityBot(
                instrument.id, instrument.s_0, 5
            )  # TODO: adjust inventory
            for instrument in instruments
        }
        self.order_book = order_book

    def process_book_snapshot(self, snapshot: dict):
        for bid_price, depth in snapshot["bids"]:
            self.order_book.match_order(
                OrderModel(
                    price=bid_price,
                    quantity=depth,
                    side=OrderSide.BUY,
                    user_id=f"liquidity_bot_{snapshot['instrumentId']}",
                    ticker=snapshot["instrumentId"],
                )
            )
        for ask_price, depth in snapshot["asks"]:
            self.order_book.match_order(
                OrderModel(
                    price=ask_price,
                    quantity=depth,
                    side=OrderSide.SELL,
                    user_id=f"liquidity_bot_{snapshot['instrumentId']}",
                    ticker=snapshot["instrumentId"],
                )
            )

    async def run(self):
        self.is_running = True
        while self.is_running:
            try:
                for ticker, liquidity_bot in self.liquidity_bots.items():
                    book_snapshot = liquidity_bot.generate_order_book(
                        0
                    )  # TODO: adjust drift term
                    print("Liquidity bot generated snapshot for", ticker)
                    print(book_snapshot)
                    self.process_book_snapshot(book_snapshot)
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception as e:
                await asyncio.sleep(2)
