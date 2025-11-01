import asyncio
import time

from app.core.logging import get_logger

logger = get_logger(__name__)


class NewsShockSimulator:
    def __init__(self):
        self.news_objects = []
        self.NEWS_TICK_DELAY = 60

    """
    Exponential decay formula
    """

    def calculate(self, news):
        try:
            if not news:
                return 0

            now_s = time.time()
            t0_s = news.get("ts_release_ms", 0) / 1000

            if now_s > t0_s:  # News has not been released, impossible
                return 0

            halflife_s = news.get("decay_halflife_s", 1)
            magnitude = news.get("magnitude", 0)
            time_delta_s = now_s - t0_s

            if halflife_s <= 0:  # Prevent division by zero or negative halflife
                halflife_s = 1

            decay = 2 ** (-(time_delta_s) / halflife_s)
            eff = magnitude * decay
            return eff
        except Exception as e:
            logger.error(f"Error calculating news effect: {e}", exc_info=True)
            return 0

    def get_total_eff(self):
        total_eff = 0  # 0 is the baseline
        for news_object in self.news_objects:
            total_eff += self.calculate(news_object)
        return total_eff

    def add_news_ad_hoc(self, news_object):
        if news_object is None:
            return
        required_fields = ["ts_release_ms", "decay_halflife_s", "magnitude"]
        if not all(field in news_object for field in required_fields):
            raise ValueError("News object is missing required fields")
        self.news_objects.append(news_object)

    async def add_news_on_tick(self):
        self.is_running = True
        while self.is_running:
            try:
                # Replace with actual DB query when ready
                # For now, we're not adding any news automatically
                # news = await self.db.get_latest_news()  # Example
                # if news:
                #     self.add_news_ad_hoc(news)
                await asyncio.sleep(self.NEWS_TICK_DELAY)
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Error in add_news_on_tick: {e}", exc_info=True)
                await asyncio.sleep(1)
