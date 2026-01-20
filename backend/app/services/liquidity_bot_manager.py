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
                instrument.id, instrument.s_0, 0  # Start with 0 inventory
            )
            for instrument in instruments
        }
        self.order_book = order_book
        # Track liquidity bot orders by ticker with original quantity
        self.liquidity_bot_orders = {}
        # Track original quantities to detect fills
        self.original_quantities = {}

    def clear_old_liquidity_orders(self, ticker: str):
        """
        Remove all previous liquidity bot orders for a ticker.
        Also update bot inventory based on filled orders.
        """
        if ticker not in self.liquidity_bot_orders:
            return
        
        liquidity_bot = self.liquidity_bots.get(ticker)
        if not liquidity_bot:
            return
        
        for order in self.liquidity_bot_orders[ticker]:
            original_qty = self.original_quantities.get(order.id, order.quantity)
            
            # Check if order still exists in order book (might be filled)
            if order.id in self.order_book.order_mapping:
                current_order = self.order_book.order_mapping[order.id]
                filled_quantity = original_qty - current_order.quantity
                
                if filled_quantity > 0:
                    # Order was partially or fully filled
                    if order.side == OrderSide.BUY:
                        # Bot bought (inventory increases)
                        liquidity_bot.update_inventory(filled_quantity)
                        print(f"[{ticker}] Bot bought {filled_quantity} @ {order.price:.2f}, inventory now: {liquidity_bot.inventory}")
                    else:
                        # Bot sold (inventory decreases)
                        liquidity_bot.update_inventory(-filled_quantity)
                        print(f"[{ticker}] Bot sold {filled_quantity} @ {order.price:.2f}, inventory now: {liquidity_bot.inventory}")
                
                # Remove the order
                try:
                    self.order_book.remove_order(order)
                except Exception:
                    pass
            else:
                # Order was fully filled and removed
                if order.side == OrderSide.BUY:
                    liquidity_bot.update_inventory(original_qty)
                    print(f"[{ticker}] Bot bought {original_qty} @ {order.price:.2f}, inventory now: {liquidity_bot.inventory}")
                else:
                    liquidity_bot.update_inventory(-original_qty)
                    print(f"[{ticker}] Bot sold {original_qty} @ {order.price:.2f}, inventory now: {liquidity_bot.inventory}")
            
            # Clean up tracked quantity
            if order.id in self.original_quantities:
                del self.original_quantities[order.id]
        
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
            
            # Track this order and its original quantity
            if ticker not in self.liquidity_bot_orders:
                self.liquidity_bot_orders[ticker] = []
            self.liquidity_bot_orders[ticker].append(order)
            self.original_quantities[order.id] = depth
            
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
            
            # Track this order and its original quantity
            if ticker not in self.liquidity_bot_orders:
                self.liquidity_bot_orders[ticker] = []
            self.liquidity_bot_orders[ticker].append(order)
            self.original_quantities[order.id] = depth

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
                # Update every 0.75 seconds for active price movement
                await asyncio.sleep(0.75)
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception as e:
                print(f"Error in liquidity bot manager: {e}")
                await asyncio.sleep(1.0)
