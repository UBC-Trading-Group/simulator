import redis.asyncio as redis

from app.core.config import settings
from app.services.gbm_manager import GBMManager
from app.services.instrument_manager import InstrumentManager
from app.services.leaderboard import Leaderboard
from app.services.liquidity_bot_manager import LiquidityBotManager
from app.services.news import NewsShockSimulator
from app.services.order_book import OrderBook
from app.services.order_generator import OrderGenerator
from app.websocket.price_engine import PriceEngine

"""
For dependency injections, these are all singletons
"""

news_engine = NewsShockSimulator()
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)
leaderboard = Leaderboard(redis_client)
order_book = OrderBook()
instrument_manager = InstrumentManager()
price_engine = PriceEngine(
    news_engine=news_engine,
    order_book=order_book,
    instrument_manager=instrument_manager,
)
gbm_manager = GBMManager(
    instrument_manager, news_engine
)  # Pass news engine to calculate drift
order_generator = OrderGenerator(
    instrument_manager=instrument_manager,
    order_book=order_book,
    gbm_manager=gbm_manager,
)
lb_manager = LiquidityBotManager(
    instruments=instrument_manager.get_all_instruments(),
    order_book=order_book,
    gbm_manager=gbm_manager,
)


def get_price_engine() -> PriceEngine:
    return price_engine


def get_news_engine() -> NewsShockSimulator:
    return news_engine


def get_leaderboard() -> Leaderboard:
    return leaderboard


def get_order_book() -> OrderBook:
    return order_book


def get_instrument_manager() -> InstrumentManager:
    return instrument_manager


def get_gbm_manager() -> GBMManager:
    return gbm_manager


def get_order_generator() -> OrderGenerator:
    return order_generator


def get_liquidity_bot_manager() -> LiquidityBotManager:
    return lb_manager
