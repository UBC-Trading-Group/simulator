import asyncio
import time
from typing import List, Optional, Set

from sqlmodel import Session, select

from app.core.deps import get_logger
from app.db.database import engine
from app.models.news_event import NewsEvent

logger = get_logger(__name__)


class NewsShockSimulator:
    def __init__(self):
        self.news_objects: List[NewsEvent] = []
        self.NEWS_TICK_DELAY = 60  # choose news at start of minute
        self.active_news_ids: Set[int] = set()

        # Initialize all news
        self.pull_news_from_db()

    def pull_news_from_db(self):
        with Session(engine) as session:
            result = session.exec(select(NewsEvent))
            self.news_objects = result.all()

    def get_all_news(self):
        return self.news_objects

    def get_candidate_news(self) -> List[NewsEvent]:
        curr_time_ms = int(time.time() * 1000)
        return [
            news
            for news in self.news_objects
            if news.ts_release_ms <= curr_time_ms
            and news.id not in self.active_news_ids
        ]

    def get_random_news(self) -> Optional[NewsEvent]:
        candidates = self.get_candidate_news()
        if not candidates:
            return None

        randomized_event = random.choice(candidates)
        self.active_news_ids.add(randomized_event.id)
        return randomized_event

    """
    Exponential decay formula
    """

    def calculate(self, news: NewsEvent) -> float:
        try:
            if not news:
                return 0.0

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
            return 0.0

    def get_total_eff(self) -> float:
        total_eff = 0.0  # 0.0 is the baseline
        for news_object in self.get_all_news():

            # Effect should only be calculated based on currently ACTIVE news in effect
            if news_object.id not in self.active_news_ids:
                continue

            total_eff += self.calculate(news_object)

        return total_eff

    def add_news_ad_hoc(self, news_object: Optional[NewsEvent]):
        if news_object is None:
            return
        required_fields = ["ts_release_ms", "decay_halflife_s", "magnitude"]
        if not all(field in news_object for field in required_fields):
            raise ValueError("News object is missing required fields")
        self.news_objects.append(news_object)

        # News added ad-hoc are immediately active
        self.active_news_ids.add(news_object["id"])

    async def activate_news_after_delay(self, news: NewsEvent):
        delay = random.randint(0, self.NEWS_TICK_DELAY)
        await asyncio.sleep(delay)
        self.active_news_ids.add(news["id"])

    async def add_news_on_tick(self):
        self.is_running = True
        while self.is_running:
            try:
                news = self.get_random_news()
                if news:
                    self.news_objects.append(news)
                    # Schedule background job -> news should be activated randomly within the minute
                    asyncio.create_task(self.activate_news_after_delay(news))
                await asyncio.sleep(self.NEWS_TICK_DELAY)
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Error in add_news_on_tick: {e}", exc_info=True)
                await asyncio.sleep(1)
