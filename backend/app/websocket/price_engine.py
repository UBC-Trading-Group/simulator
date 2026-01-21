import asyncio

from fastapi import WebSocket

from app.core.deps import get_logger

logger = get_logger(__name__)


class PriceEngine:
    def __init__(self, news_engine=None, order_book=None, instrument_manager=None):
        # TODO: convert to map, should be ticker -> connections
        # also add another map ticker -> gbm simulator
        self.active_connections = []
        self.is_running = False
        self.news_engine = news_engine
        self.order_book = order_book
        self.instrument_manager = instrument_manager

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def get_additional_drift(self):
        # Inject into calculate
        if not self.news_engine:
            return 0
        return self.news_engine.get_total_eff()

    async def broadcast(self, message):
        # None connected
        if not self.active_connections:
            return

        coros = []
        for connection in self.active_connections:
            coros.append(self._safe_send(connection, message))

        # Run all concurrently instead of sequentially
        await asyncio.gather(*coros, return_exceptions=True)

    async def _safe_send(self, connection: WebSocket, message):
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to connection: {e}", exc_info=True)
            self.disconnect(connection)

    async def run(self):
        self.is_running = True
        while self.is_running:
            try:
                broadcast_unit = {}
                for ticker in self.instrument_manager.get_all_instruments():
                    # Try mid price first
                    price = self.order_book.mid_price(ticker.id)

                    # Fallback to best bid/ask if mid price not available
                    if price is None:
                        best_bid = self.order_book.best_bid(ticker.id)
                        best_ask = self.order_book.best_ask(ticker.id)

                        if best_bid and best_ask:
                            price = (best_bid.price + best_ask.price) / 2
                        elif best_bid:
                            price = best_bid.price
                        elif best_ask:
                            price = best_ask.price

                    # Only include if we have a valid price
                    if price is not None:
                        broadcast_unit[ticker.id] = price

                await self.broadcast(broadcast_unit)
                await asyncio.sleep(0.5)  # Broadcast every 0.5 seconds
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Error in price engine: {e}")
                await asyncio.sleep(0.5)
