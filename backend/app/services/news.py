import asyncio
import random
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
        self.active_news_ids: Set[int] = set()
        self.activated_news_ids: Set[int] = (
            set()
        )  # Track which news have been activated already

        # Simulation clock (in milliseconds)
        self.sim_time_ms = 0
        self.sim_start_time = time.time()  # Real-world time when simulation started

        # Cache for news factor relationships
        self.news_factor_map = {}  # {news_id: [factor_ids]}
        self.instrument_factor_betas = {}  # {(instrument_id, factor_id): beta}

        # Initialize all news and factor relationships
        self.pull_news_from_db()
        self.load_factor_relationships()

    def pull_news_from_db(self):
        with Session(engine) as session:
            result = session.exec(select(NewsEvent))
            self.news_objects = result.all()

    def load_factor_relationships(self):
        """Load news-factor and instrument-factor relationships"""
        from app.models.instrument_factor_exposure import InstrumentFactorExposure
        from app.models.news_event_factor import NewsEventFactor

        with Session(engine) as session:
            # Load news -> factors
            news_factors = session.exec(select(NewsEventFactor)).all()
            for nf in news_factors:
                if nf.news_event_id not in self.news_factor_map:
                    self.news_factor_map[nf.news_event_id] = []
                self.news_factor_map[nf.news_event_id].append(nf.factor_id)

            # Load instrument -> factor betas
            inst_factors = session.exec(select(InstrumentFactorExposure)).all()
            for ife in inst_factors:
                self.instrument_factor_betas[(ife.instrument_id, ife.factor_id)] = (
                    ife.beta
                )

            logger.info(f"Loaded {len(self.news_factor_map)} news factor mappings")
            logger.info(
                f"Loaded {len(self.instrument_factor_betas)} instrument factor betas"
            )

    def get_all_news(self):
        return self.news_objects

    def get_candidate_news(self) -> List[NewsEvent]:
        """Get news that should be released at current simulation time"""
        return [
            news
            for news in self.news_objects
            if news.ts_release_ms <= self.sim_time_ms
            and news.id not in self.activated_news_ids  # Not yet activated
        ]

    def get_random_news(self) -> Optional[NewsEvent]:
        candidates = self.get_candidate_news()
        if not candidates:
            return None

        randomized_event = random.choice(candidates)
        return randomized_event

    """
    Exponential decay formula
    """

    def calculate(self, news: NewsEvent) -> float:
        try:
            if not news:
                return 0.0

            # Use simulation time for decay calculation
            t0_s = news.ts_release_ms / 1000
            sim_time_s = self.sim_time_ms / 1000

            # News hasn't been released yet
            if sim_time_s < t0_s:
                return 0.0

            halflife_s = news.decay_halflife_s
            # Use average of magnitude_top and magnitude_bottom
            magnitude = (news.magnitude_top + news.magnitude_bottom) / 2
            time_delta_s = sim_time_s - t0_s

            if halflife_s <= 0:  # Prevent division by zero or negative halflife
                halflife_s = 1

            decay = 2 ** (-(time_delta_s) / halflife_s)
            eff = magnitude * decay
            return eff
        except Exception as e:
            logger.error(f"Error calculating news effect: {e}", exc_info=True)
            return 0.0

    def get_total_eff(self) -> float:
        """Legacy method - kept for compatibility but not used"""
        total_eff = 0.0  # 0.0 is the baseline
        for news_object in self.get_all_news():

            # Effect should only be calculated based on currently ACTIVE news in effect
            if news_object.id not in self.active_news_ids:
                continue

            total_eff += self.calculate(news_object)

        return total_eff

    def get_instrument_drift(self, instrument_id: str) -> float:
        """
        Calculate drift for a specific instrument based on active news.
        Drift = sum(news_effect * beta) for all active news and factors.
        """
        total_drift = 0.0

        for news in self.news_objects:
            # Skip inactive news
            if news.id not in self.active_news_ids:
                continue

            # Get news effect (decays over time)
            news_effect = self.calculate(news)
            if news_effect == 0:
                continue

            # Get factors affected by this news
            affected_factors = self.news_factor_map.get(news.id, [])

            # For each factor, apply instrument's beta exposure
            for factor_id in affected_factors:
                beta = self.instrument_factor_betas.get((instrument_id, factor_id), 0.0)
                total_drift += news_effect * beta

        return total_drift

    def add_news_ad_hoc(self, news_object: Optional[NewsEvent]):
        if news_object is None:
            return
        required_fields = ["ts_release_ms", "decay_halflife_s", "magnitude"]
        if not all(field in news_object for field in required_fields):
            raise ValueError("News object is missing required fields")
        self.news_objects.append(news_object)

        # News added ad-hoc are immediately active
        self.active_news_ids.add(news_object.id)

    def update_simulation_time(self):
        """Update simulation time based on real elapsed time"""
        elapsed_real_seconds = time.time() - self.sim_start_time
        self.sim_time_ms = int(elapsed_real_seconds * 1000)

    def check_and_activate_news(self):
        """Check if any news should be activated at current simulation time"""
        self.update_simulation_time()

        # Group candidates by their release time
        candidates = self.get_candidate_news()
        if not candidates:
            return None

        # Group by time bucket (every 100 seconds)
        time_buckets = {}
        for news in candidates:
            bucket = (
                news.ts_release_ms // 100000
            ) * 100000  # Round down to nearest 100s
            if bucket not in time_buckets:
                time_buckets[bucket] = []
            time_buckets[bucket].append(news)

        # Activate one random news from each time bucket that's passed
        activated = []
        for bucket_time, bucket_news in time_buckets.items():
            # Pick one random news from this bucket if not already activated
            available = [n for n in bucket_news if n.id not in self.activated_news_ids]
            if available:
                selected = random.choice(available)
                self.active_news_ids.add(selected.id)
                self.activated_news_ids.add(selected.id)
                activated.append(selected)
                logger.info(
                    f"Activated news {selected.id}: {selected.headline} (sim_time: {self.sim_time_ms}ms)"
                )

        return activated

    async def run(self):
        """Main loop that checks for news activation every second"""
        self.is_running = True
        logger.info("News engine started")

        while self.is_running:
            try:
                self.check_and_activate_news()
                await asyncio.sleep(1)  # Check every second
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Error in news engine: {e}", exc_info=True)
                await asyncio.sleep(1)
