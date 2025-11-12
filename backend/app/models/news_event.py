"""
News Event model
"""

from typing import Optional

from sqlmodel import Field, SQLModel


class NewsEvent(SQLModel, table=True):
    __tablename__ = "news_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    headline: str = Field(nullable=False)
    description: str = Field(nullable=False)
    magnitude_top: float = Field(nullable=False, default=0.0)
    magnitude_bottom: float = Field(nullable=False, default=0.0)
    decay_halflife_s: float = Field(nullable=False)
