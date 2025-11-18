import redis.asyncio as redis

from app.core.config import settings
from app.services.gbm_manager import GBMManager
from app.services.instrument_manager import InstrumentManager
from app.services.leaderboard import Leaderboard
from app.services.news import NewsShockSimulator
from app.services.order_book import OrderBook
from app.websocket.price_engine import PriceEngine

"""
For dependency injections, these are all singletons
"""

news_engine = NewsShockSimulator()
price_engine = PriceEngine(news_engine=news_engine)
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)
leaderboard = Leaderboard(redis_client)
order_book = OrderBook()
instrument_manager = InstrumentManager()
gbm_manager = GBMManager(
    instrument_manager
)  # need to be injected to avoid circular dependency


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
