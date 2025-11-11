"""
Macro Factor model
"""

from sqlmodel import Field, SQLModel


class MacroFactor(SQLModel, table=True):
    __tablename__ = "macro_factors"

    id: str = Field(primary_key=True)
    name: str = Field(nullable=False, index=True)
    cap_up: float = Field(nullable=False)
    cap_down: float = Field(nullable=False)
