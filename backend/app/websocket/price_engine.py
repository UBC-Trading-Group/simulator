import asyncio

from fastapi import WebSocket

from app.core.logging import get_logger
from app.services.gbm import GeometricBrownianMotionAssetSimulator

logger = get_logger(__name__)


class PriceEngine:
    def __init__(self, news_engine=None):
        # TODO: convert to map, should be ticker -> connections
        # also add another map ticker -> gbm simulator
        self.active_connections = set()
        self.is_running = False
        self.tickers = [
            {"ticker": "AAPL", "s_0": 180.0, "mean": 0.07, "variance": 0.25},
            {"ticker": "TSLA", "s_0": 250.0, "mean": 0.10, "variance": 0.40},
            {"ticker": "GOOG", "s_0": 340.0, "mean": 0.06, "variance": 0.22},
            {"ticker": "AMZN", "s_0": 100.0, "mean": 0.08, "variance": 0.30},
        ]

        self.gbmas_instances = {
            ticker["ticker"]: GeometricBrownianMotionAssetSimulator(
                ticker["s_0"], ticker["mean"], ticker["variance"], 1 / 252
            )
            for ticker in self.tickers
        }
        self.news_engine = news_engine

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

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
        for connection in list(self.active_connections):
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
                await self.broadcast(
                    {ticker: gbmas() for ticker, gbmas in self.gbmas_instances.items()}
                )
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception as e:
                # continue
                await asyncio.sleep(1)
