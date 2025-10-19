from app.websocket.price_engine import PriceEngine
from app.services.news import NewsShockSimulator
from app.services.leaderboard import Leaderboard

"""
For dependency injections, these are all singletons
"""

news_engine = NewsShockSimulator()
price_engine = PriceEngine(news_engine=news_engine)
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)
leaderboard = Leaderboard(redis_client)

def get_price_engine() -> PriceEngine:
    return price_engine

def get_news_engine() -> NewsShockSimulator:
    return news_engine

def get_leaderboard() -> Leaderboard:
    return leaderboard
    