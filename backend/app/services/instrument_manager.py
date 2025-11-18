from app.db.database import engine
from app.models.instrument import Instrument


class InstrumentManager:
    def __init__(self):
        self.instruments: list[Instrument] = []
        self.valid_instrument_tickers: set[str] = set()

    def initialize_instruments(self):
        with Session(engine) as session:
            result = session.exec(select(Instrument))
            self.instruments = result.all()
            self.valid_instrument_tickers = set([i.ticker for i in self.instruments])

    def is_valid_instrument(self, ticker: str) -> bool:
        return ticker in self.valid_instrument_tickers

    def get_all_instruments(self) -> list[Instrument]:
        return self.instruments
