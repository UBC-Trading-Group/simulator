import asyncio

from app.models.instrument import Instrument
from app.services.gbm import GeometricBrownianMotionAssetSimulator
from app.services.instrument_manager import InstrumentManager


class GBMManager:
    def __init__(self, instrument_manager: InstrumentManager, news_engine=None):
        self.instruments: list[Instrument] = instrument_manager.get_all_instruments()
        self.news_engine = news_engine
        self.gbmas_instances = {
            instrument.id: GeometricBrownianMotionAssetSimulator(
                instrument.s_0, instrument.mean, instrument.variance, 1 / 252
            )
            for instrument in self.instruments
        }

    async def run(self):
        self.is_running = True
        while self.is_running:
            try:
                for ticker, gbm_instance in self.gbmas_instances.items():
                    # Get news-based drift for this instrument
                    drift = 0.0
                    if self.news_engine:
                        drift = self.news_engine.get_instrument_drift(ticker)

                    # Update the GBM with news drift
                    gbm_instance.set_drift(drift)

                    # This updates the current_price field of the gbm_instance
                    gbm_instance()
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception as e:
                # continue
                await asyncio.sleep(1)

    def get_ticker_current_gbm_price(self, ticker: str) -> float:
        return self.gbmas_instances[ticker].get_current_price()
