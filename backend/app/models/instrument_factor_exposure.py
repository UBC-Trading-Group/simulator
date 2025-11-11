"""
Instrument Factor Exposure model (junction table)
"""

from sqlmodel import Field, ForeignKey, SQLModel


class InstrumentFactorExposure(SQLModel, table=True):
    __tablename__ = "instrument_factor_exposure"

    instrument_id: str = Field(foreign_key="instruments.id", primary_key=True)
    factor_id: str = Field(foreign_key="macro_factors.id", primary_key=True)
    beta: float = Field(nullable=False)
