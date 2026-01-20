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
        # Track liquidity bot orders by ticker
        self.liquidity_bot_orders = {}

    def clear_old_liquidity_orders(self, ticker: str):
        """Remove all previous liquidity bot orders for a ticker"""
        if ticker not in self.liquidity_bot_orders:
            return
        
        for order in self.liquidity_bot_orders[ticker]:
            try:
                self.order_book.remove_order(order)
            except Exception:
                pass  # Order may have been filled/removed already
        
        self.liquidity_bot_orders[ticker] = []

    def process_book_snapshot(self, snapshot: dict):
        ticker = snapshot["instrumentId"]
        
        # Clear old liquidity bot orders for this ticker
        self.clear_old_liquidity_orders(ticker)
        
        # Add new orders using is_liquidity_bot=True to prevent matching
        for bid_price, depth in snapshot["bids"]:
            order = OrderModel(
                price=bid_price,
                quantity=depth,
                side=OrderSide.BUY,
                user_id=f"liquidity_bot_{ticker}",
                ticker=ticker,
            )
            # Use is_liquidity_bot=True to add directly to book without matching
            self.order_book.match_order(order, is_liquidity_bot=True)
            
            # Track this order
            if ticker not in self.liquidity_bot_orders:
                self.liquidity_bot_orders[ticker] = []
            self.liquidity_bot_orders[ticker].append(order)
            
        for ask_price, depth in snapshot["asks"]:
            order = OrderModel(
                price=ask_price,
                quantity=depth,
                side=OrderSide.SELL,
                user_id=f"liquidity_bot_{ticker}",
                ticker=ticker,
            )
            # Use is_liquidity_bot=True to add directly to book without matching
            self.order_book.match_order(order, is_liquidity_bot=True)
            
            # Track this order
            if ticker not in self.liquidity_bot_orders:
                self.liquidity_bot_orders[ticker] = []
            self.liquidity_bot_orders[ticker].append(order)

    async def run(self):
        self.is_running = True
        while self.is_running:
            try:
                for ticker, liquidity_bot in self.liquidity_bots.items():
                    # drift_term = 0 for liquidity bots (they don't respond to news)
                    book_snapshot = liquidity_bot.generate_order_book(0)
                    print("Liquidity bot generated snapshot for", ticker)
                    print(book_snapshot)
                    self.process_book_snapshot(book_snapshot)
                # Update every 1 second for smooth, realistic price movement
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception as e:
                print(f"Error in liquidity bot manager: {e}")
                await asyncio.sleep(1.0)
