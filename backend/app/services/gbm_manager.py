from app.models.instrument import Instrument


class GBMManager:
    def __init__(self, instrument_manager: InstrumentManager):
        self.instruments: list[Instrument] = instrument_manager.get_all_instruments()
        self.gbmas_instances = {
            ticker.ticker: GeometricBrownianMotionAssetSimulator(
                ticker.s_0, ticker.mean, ticker.variance, 1 / 252
            )
            for ticker in self.instruments
        }

    async def run(self):
        self.is_running = True
        while self.is_running:
            try:
                for _, gbm_instance in self.gbmas_instances.items():
                    # this updates the current_price field of the gbm_instance
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
