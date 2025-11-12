"""

Revision ID: 2ed36e234faf
Revises: 967eaa697b4e
Create Date: 2025-11-11 23:11:03.639447

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2ed36e234faf"
down_revision: Union[str, Sequence[str], None] = "967eaa697b4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop dependent tables that have foreign keys to tables we're modifying
    op.drop_table("instrument_factor_exposure")
    op.drop_table("news_event_factors")

    # Drop and recreate macro_factors table with VARCHAR id (no alpha column)
    op.drop_table("macro_factors")
    op.create_table(
        "macro_factors",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("cap_up", sa.Float(), nullable=False),
        sa.Column("cap_down", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_macro_factors_name"), "macro_factors", ["name"], unique=False
    )

    # Drop and recreate news_events table with INTEGER id and new schema
    op.drop_table("news_events")
    op.create_table(
        "news_events",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("headline", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("magnitude_top", sa.Float(), nullable=False),
        sa.Column("magnitude_bottom", sa.Float(), nullable=False),
        sa.Column("decay_halflife_s", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Recreate instrument_factor_exposure table with correct types
    op.create_table(
        "instrument_factor_exposure",
        sa.Column("instrument_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("factor_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("beta", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["factor_id"],
            ["macro_factors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["instrument_id"],
            ["instruments.id"],
        ),
        sa.PrimaryKeyConstraint("instrument_id", "factor_id"),
    )

    # Recreate news_event_factors table with correct types
    op.create_table(
        "news_event_factors",
        sa.Column("news_event_id", sa.Integer(), nullable=False),
        sa.Column("factor_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["factor_id"],
            ["macro_factors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["news_event_id"],
            ["news_events.id"],
        ),
        sa.PrimaryKeyConstraint("news_event_id", "factor_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Drop dependent tables
    op.drop_table("news_event_factors")
    op.drop_table("instrument_factor_exposure")

    # Drop and recreate macro_factors table with UUID id (with alpha column)
    op.drop_table("macro_factors")
    op.create_table(
        "macro_factors",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("alpha", sa.Float(), nullable=False),
        sa.Column("cap_up", sa.Float(), nullable=False),
        sa.Column("cap_down", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_macro_factors_name"), "macro_factors", ["name"], unique=False
    )

    # Drop and recreate news_events table with UUID id and old schema
    op.drop_table("news_events")
    op.create_table(
        "news_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ts_release_ms", sa.Integer(), nullable=False),
        sa.Column("headline", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("magnitude", sa.Float(), nullable=False),
        sa.Column("decay_halflife_s", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_news_events_ts_release_ms"),
        "news_events",
        ["ts_release_ms"],
        unique=False,
    )

    # Recreate instrument_factor_exposure table with UUID types
    op.create_table(
        "instrument_factor_exposure",
        sa.Column("instrument_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("factor_id", sa.UUID(), nullable=False),
        sa.Column("beta", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["factor_id"],
            ["macro_factors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["instrument_id"],
            ["instruments.id"],
        ),
        sa.PrimaryKeyConstraint("instrument_id", "factor_id"),
    )

    # Recreate news_event_factors table with UUID types
    op.create_table(
        "news_event_factors",
        sa.Column("news_event_id", sa.UUID(), nullable=False),
        sa.Column("factor_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["factor_id"],
            ["macro_factors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["news_event_id"],
            ["news_events.id"],
        ),
        sa.PrimaryKeyConstraint("news_event_id", "factor_id"),
    )
    # ### end Alembic commands ###
