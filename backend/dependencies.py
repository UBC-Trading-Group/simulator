from app.services.news import NewsShockSimulator
from app.services.order_book import OrderBook
from app.websocket.price_engine import PriceEngine

"""
For dependency injections, these are all singletons
"""

news_engine = NewsShockSimulator()
price_engine = PriceEngine(news_engine=news_engine)
order_book = OrderBook()


def get_price_engine() -> PriceEngine:
    return price_engine


def get_news_engine() -> NewsShockSimulator:
    return news_engine


def get_order_book() -> OrderBook:
    return order_book
