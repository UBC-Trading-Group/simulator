from sqlmodel import Session, select

from app.db.database import engine
from app.models.instrument import Instrument


class InstrumentManager:
    def __init__(self):
        self.instruments: list[Instrument] = []
        self.valid_instrument_ids: set[str] = set()
        self.initialize_instruments()

    def initialize_instruments(self):
        with Session(engine) as session:
            result = session.exec(select(Instrument))
            self.instruments = result.all()
            self.valid_instrument_ids = set([i.id for i in self.instruments])

    def is_valid_instrument(self, ticker: str) -> bool:
        return ticker in self.valid_instrument_ids

    def get_all_instruments(self) -> list[Instrument]:
        return self.instruments
