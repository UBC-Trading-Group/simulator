"""
Database population script - Populates tables with initial data
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, SQLModel, select

from app.core.deps import get_logger
from app.core.logging import setup_logging
from app.db.database import engine
from app.models.instrument import Instrument
from app.models.instrument_factor_exposure import InstrumentFactorExposure
from app.models.instrument_sector_exposure import InstrumentSectorExposure
from app.models.macro_factor import MacroFactor
from app.models.news_event import NewsEvent
from app.models.news_event_factor import NewsEventFactor
from app.models.sector import Sector

setup_logging()
logger = get_logger(__name__)


def populate_instruments():
    """Populate instruments table with initial data"""
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)
        # Instruments data
        instruments_data = [
            {
                "id": "INDX",
                "full_name": "TG5 Equal Weight Market Index",
                "s_0": 100.0,
                "mean": 0.03,
                "variance": 0.0324,
            },
            {
                "id": "NOVA",
                "full_name": "NovaScale Systems Inc.",
                "s_0": 178.0,
                "mean": 0.14,
                "variance": 0.2116,
            },
            {
                "id": "TRAX",
                "full_name": "Traxline Logistics",
                "s_0": 55.0,
                "mean": 0.05,
                "variance": 0.09,
            },
            {
                "id": "GENX",
                "full_name": "Genixa Biotechnologies",
                "s_0": 40.0,
                "mean": 0.1,
                "variance": 0.36,
            },
            {
                "id": "ARCO",
                "full_name": "Arclight Energy",
                "s_0": 70.0,
                "mean": 0.04,
                "variance": 0.0784,
            },
            {
                "id": "AURA",
                "full_name": "Aurora Financial Group",
                "s_0": 45.0,
                "mean": 0.06,
                "variance": 0.0625,
            },
        ]

        # Check and add instruments
        added_count = 0
        for instrument_data in instruments_data:
            # Check if instrument already exists
            statement = select(Instrument).where(Instrument.id == instrument_data["id"])
            existing_instrument = session.exec(statement).first()

            if existing_instrument:
                logger.info(
                    f"Instrument {instrument_data['id']} already exists, skipping"
                )
                continue

            # Create new instrument
            instrument = Instrument(**instrument_data)
            session.add(instrument)
            added_count += 1
            logger.info(
                f"Added instrument: {instrument_data['id']} - {instrument_data['full_name']}"
            )

        session.commit()
        logger.info(
            f"Instruments population completed. Added {added_count} new instruments."
        )


def populate_sectors():
    """Populate sectors table with initial data"""
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)
        # Sectors data
        sectors_data = [
            {
                "id": "TECH",
                "description": "Technology",
            },
            {
                "id": "FIN",
                "description": "Banks / Insurers",
            },
            {
                "id": "IND",
                "description": "Industrials and Transport",
            },
            {
                "id": "BIO",
                "description": "Biotech / Pharma",
            },
            {
                "id": "ENG",
                "description": "Energy",
            },
        ]

        # Check and add sectors
        added_count = 0
        for sector_data in sectors_data:
            # Check if sector already exists
            statement = select(Sector).where(Sector.id == sector_data["id"])
            existing_sector = session.exec(statement).first()

            if existing_sector:
                logger.info(f"Sector {sector_data['id']} already exists, skipping")
                continue

            # Create new sector
            sector = Sector(**sector_data)
            session.add(sector)
            added_count += 1
            logger.info(
                f"Added sector: {sector_data['id']} - {sector_data['description']}"
            )

        session.commit()
        logger.info(f"Sectors population completed. Added {added_count} new sectors.")


def populate_instrument_sector_exposure():
    """Populate instrument_sector_exposure table with initial data"""
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)
        # Instrument sector exposure data
        exposure_data = [
            {
                "instrument_id": "NOVA",
                "sector_id": "TECH",
                "weight": 0.96,
            },
            {
                "instrument_id": "NOVA",
                "sector_id": "FIN",
                "weight": 0.04,
            },
            {
                "instrument_id": "TRAX",
                "sector_id": "IND",
                "weight": 1.0,
            },
            {
                "instrument_id": "GENX",
                "sector_id": "BIO",
                "weight": 0.87,
            },
            {
                "instrument_id": "GENX",
                "sector_id": "TECH",
                "weight": 0.13,
            },
            {
                "instrument_id": "ARCO",
                "sector_id": "ENG",
                "weight": 0.79,
            },
            {
                "instrument_id": "ARCO",
                "sector_id": "IND",
                "weight": 0.21,
            },
            {
                "instrument_id": "AURA",
                "sector_id": "FIN",
                "weight": 0.82,
            },
            {
                "instrument_id": "AURA",
                "sector_id": "TECH",
                "weight": 0.18,
            },
        ]

        # Check and add instrument sector exposures
        added_count = 0
        for exposure in exposure_data:
            # Check if exposure already exists (composite primary key)
            statement = select(InstrumentSectorExposure).where(
                InstrumentSectorExposure.instrument_id == exposure["instrument_id"],
                InstrumentSectorExposure.sector_id == exposure["sector_id"],
            )
            existing_exposure = session.exec(statement).first()

            if existing_exposure:
                logger.info(
                    f"Exposure {exposure['instrument_id']}-{exposure['sector_id']} already exists, skipping"
                )
                continue

            # Create new exposure
            instrument_sector_exposure = InstrumentSectorExposure(**exposure)
            session.add(instrument_sector_exposure)
            added_count += 1
            logger.info(
                f"Added exposure: {exposure['instrument_id']}-{exposure['sector_id']} (weight: {exposure['weight']})"
            )

        session.commit()
        logger.info(
            f"Instrument sector exposure population completed. Added {added_count} new exposures."
        )


def populate_macro_factors():
    """Populate macro_factors table with initial data"""
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)
        # Macro factors data
        macro_factors_data = [
            {
                "id": "MKT",
                "name": "market",
                "cap_up": 0.01,
                "cap_down": -0.01,
            },
            {
                "id": "RATE",
                "name": "rate",
                "cap_up": 0.01,
                "cap_down": -0.01,
            },
            {
                "id": "INFL",
                "name": "inflation",
                "cap_up": 0.04,
                "cap_down": -0.04,
            },
            {
                "id": "VIX",
                "name": "volatility_index",
                "cap_up": 0.03,
                "cap_down": -0.03,
            },
            {
                "id": "FGI",
                "name": "fear_greed_index",
                "cap_up": 0.05,
                "cap_down": -0.05,
            },
            {
                "id": "FIN_CONDS",
                "name": "financial_conditions",
                "cap_up": 0.02,
                "cap_down": -0.02,
            },
            {
                "id": "TECH_HYPE",
                "name": "technology_hype",
                "cap_up": 0.1,
                "cap_down": 0.0,
            },
            {
                "id": "HEALTH_TRIAL",
                "name": "health_trial",
                "cap_up": 0.08,
                "cap_down": -0.1,
            },
            {
                "id": "INDU_SUPPLY",
                "name": "industrial_supply",
                "cap_up": 0.03,
                "cap_down": -0.03,
            },
            {
                "id": "ENERGY_OIL",
                "name": "energy_oil",
                "cap_up": 0.08,
                "cap_down": -0.08,
            },
            {
                "id": "REG",
                "name": "regulation",
                "cap_up": -0.01,
                "cap_down": -0.05,
            },
            {
                "id": "TRANS",
                "name": "transactions",
                "cap_up": 0.09,
                "cap_down": -0.03,
            },
            {
                "id": "TRADE",
                "name": "trade",
                "cap_up": -0.01,
                "cap_down": -0.05,
            },
            {
                "id": "CYBER",
                "name": "cyber_security",
                "cap_up": -0.01,
                "cap_down": -0.05,
            },
            {
                "id": "LABOR",
                "name": "labor_market",
                "cap_up": 0.0,
                "cap_down": -0.04,
            },
            {
                "id": "WEATHER",
                "name": "weather",
                "cap_up": 0.1,
                "cap_down": -0.1,
            },
            {
                "id": "FISCAL",
                "name": "fiscal_policy",
                "cap_up": 0.05,
                "cap_down": 0.0,
            },
        ]

        # Check and add macro factors
        added_count = 0
        for factor_data in macro_factors_data:
            # Check if macro factor already exists
            statement = select(MacroFactor).where(MacroFactor.id == factor_data["id"])
            existing_factor = session.exec(statement).first()

            if existing_factor:
                logger.info(
                    f"Macro factor {factor_data['id']} already exists, skipping"
                )
                continue

            # Create new macro factor
            macro_factor = MacroFactor(**factor_data)
            session.add(macro_factor)
            added_count += 1
            logger.info(
                f"Added macro factor: {factor_data['id']} - {factor_data['name']}"
            )

        session.commit()
        logger.info(
            f"Macro factors population completed. Added {added_count} new macro factors."
        )


def populate_instrument_factor_exposure():
    """Populate instrument_factor_exposure table with initial data"""
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)
        # Instrument factor exposure data
        exposure_data = [
            # ARCO exposures
            {"instrument_id": "ARCO", "factor_id": "MKT", "beta": 0.9},
            {"instrument_id": "ARCO", "factor_id": "RATE", "beta": 0.33},
            {"instrument_id": "ARCO", "factor_id": "INFL", "beta": 0.12},
            {"instrument_id": "ARCO", "factor_id": "VIX", "beta": -0.089},
            {"instrument_id": "ARCO", "factor_id": "FGI", "beta": 0.08},
            {"instrument_id": "ARCO", "factor_id": "FIN_CONDS", "beta": 0.001},
            {"instrument_id": "ARCO", "factor_id": "TECH_HYPE", "beta": 0.195},
            {"instrument_id": "ARCO", "factor_id": "HEALTH_TRIAL", "beta": 0.0},
            {"instrument_id": "ARCO", "factor_id": "INDU_SUPPLY", "beta": 0.15},
            {"instrument_id": "ARCO", "factor_id": "ENERGY_OIL", "beta": 0.596},
            {"instrument_id": "ARCO", "factor_id": "REG", "beta": -0.18},
            {"instrument_id": "ARCO", "factor_id": "TRANS", "beta": 0.06},
            {"instrument_id": "ARCO", "factor_id": "TRADE", "beta": -0.05},
            {"instrument_id": "ARCO", "factor_id": "CYBER", "beta": -0.06},
            {"instrument_id": "ARCO", "factor_id": "LABOR", "beta": -0.1},
            {"instrument_id": "ARCO", "factor_id": "WEATHER", "beta": 0.12},
            {"instrument_id": "ARCO", "factor_id": "FISCAL", "beta": 0.1},
            # AURA exposures
            {"instrument_id": "AURA", "factor_id": "MKT", "beta": 0.7},
            {"instrument_id": "AURA", "factor_id": "RATE", "beta": 0.013},
            {"instrument_id": "AURA", "factor_id": "INFL", "beta": -0.05},
            {"instrument_id": "AURA", "factor_id": "VIX", "beta": -0.04},
            {"instrument_id": "AURA", "factor_id": "FGI", "beta": 0.1},
            {"instrument_id": "AURA", "factor_id": "FIN_CONDS", "beta": 0.002},
            {"instrument_id": "AURA", "factor_id": "TECH_HYPE", "beta": 0.056},
            {"instrument_id": "AURA", "factor_id": "HEALTH_TRIAL", "beta": 0.0},
            {"instrument_id": "AURA", "factor_id": "INDU_SUPPLY", "beta": 0.02},
            {"instrument_id": "AURA", "factor_id": "ENERGY_OIL", "beta": 0.025},
            {"instrument_id": "AURA", "factor_id": "REG", "beta": -0.25},
            {"instrument_id": "AURA", "factor_id": "TRANS", "beta": 0.12},
            {"instrument_id": "AURA", "factor_id": "TRADE", "beta": -0.08},
            {"instrument_id": "AURA", "factor_id": "CYBER", "beta": -0.25},
            {"instrument_id": "AURA", "factor_id": "LABOR", "beta": -0.04},
            {"instrument_id": "AURA", "factor_id": "WEATHER", "beta": -0.02},
            {"instrument_id": "AURA", "factor_id": "FISCAL", "beta": 0.08},
            # GENX exposures
            {"instrument_id": "GENX", "factor_id": "MKT", "beta": 2.0},
            {"instrument_id": "GENX", "factor_id": "RATE", "beta": -0.253},
            {"instrument_id": "GENX", "factor_id": "INFL", "beta": -0.25},
            {"instrument_id": "GENX", "factor_id": "VIX", "beta": -0.167},
            {"instrument_id": "GENX", "factor_id": "FGI", "beta": 0.25},
            {"instrument_id": "GENX", "factor_id": "FIN_CONDS", "beta": 0.004},
            {"instrument_id": "GENX", "factor_id": "TECH_HYPE", "beta": 0.613},
            {"instrument_id": "GENX", "factor_id": "HEALTH_TRIAL", "beta": 0.6},
            {"instrument_id": "GENX", "factor_id": "INDU_SUPPLY", "beta": 0.05},
            {"instrument_id": "GENX", "factor_id": "ENERGY_OIL", "beta": 0.113},
            {"instrument_id": "GENX", "factor_id": "REG", "beta": -0.15},
            {"instrument_id": "GENX", "factor_id": "TRANS", "beta": 0.08},
            {"instrument_id": "GENX", "factor_id": "TRADE", "beta": -0.15},
            {"instrument_id": "GENX", "factor_id": "CYBER", "beta": -0.12},
            {"instrument_id": "GENX", "factor_id": "LABOR", "beta": -0.08},
            {"instrument_id": "GENX", "factor_id": "WEATHER", "beta": -0.04},
            {"instrument_id": "GENX", "factor_id": "FISCAL", "beta": 0.12},
            # NOVA exposures
            {"instrument_id": "NOVA", "factor_id": "MKT", "beta": 1.3},
            {"instrument_id": "NOVA", "factor_id": "RATE", "beta": 0.428},
            {"instrument_id": "NOVA", "factor_id": "INFL", "beta": -0.2},
            {"instrument_id": "NOVA", "factor_id": "VIX", "beta": -0.224},
            {"instrument_id": "NOVA", "factor_id": "FGI", "beta": 0.2},
            {"instrument_id": "NOVA", "factor_id": "FIN_CONDS", "beta": 0.001},
            {"instrument_id": "NOVA", "factor_id": "TECH_HYPE", "beta": 0.92},
            {"instrument_id": "NOVA", "factor_id": "HEALTH_TRIAL", "beta": 0.05},
            {"instrument_id": "NOVA", "factor_id": "INDU_SUPPLY", "beta": 0.07},
            {"instrument_id": "NOVA", "factor_id": "ENERGY_OIL", "beta": 0.293},
            {"instrument_id": "NOVA", "factor_id": "REG", "beta": -0.35},
            {"instrument_id": "NOVA", "factor_id": "TRANS", "beta": 0.15},
            {"instrument_id": "NOVA", "factor_id": "TRADE", "beta": -0.25},
            {"instrument_id": "NOVA", "factor_id": "CYBER", "beta": -0.3},
            {"instrument_id": "NOVA", "factor_id": "LABOR", "beta": -0.05},
            {"instrument_id": "NOVA", "factor_id": "WEATHER", "beta": -0.03},
            {"instrument_id": "NOVA", "factor_id": "FISCAL", "beta": 0.2},
            # TRAX exposures
            {"instrument_id": "TRAX", "factor_id": "MKT", "beta": 1.1},
            {"instrument_id": "TRAX", "factor_id": "RATE", "beta": 0.033},
            {"instrument_id": "TRAX", "factor_id": "INFL", "beta": -0.05},
            {"instrument_id": "TRAX", "factor_id": "VIX", "beta": -0.117},
            {"instrument_id": "TRAX", "factor_id": "FGI", "beta": 0.12},
            {"instrument_id": "TRAX", "factor_id": "FIN_CONDS", "beta": 0.03},
            {"instrument_id": "TRAX", "factor_id": "TECH_HYPE", "beta": 0.357},
            {"instrument_id": "TRAX", "factor_id": "HEALTH_TRIAL", "beta": 0.0},
            {"instrument_id": "TRAX", "factor_id": "INDU_SUPPLY", "beta": 0.5},
            {"instrument_id": "TRAX", "factor_id": "ENERGY_OIL", "beta": 0.146},
            {"instrument_id": "TRAX", "factor_id": "REG", "beta": -0.1},
            {"instrument_id": "TRAX", "factor_id": "TRANS", "beta": 0.1},
            {"instrument_id": "TRAX", "factor_id": "TRADE", "beta": -0.3},
            {"instrument_id": "TRAX", "factor_id": "CYBER", "beta": -0.1},
            {"instrument_id": "TRAX", "factor_id": "LABOR", "beta": -0.3},
            {"instrument_id": "TRAX", "factor_id": "WEATHER", "beta": -0.2},
            {"instrument_id": "TRAX", "factor_id": "FISCAL", "beta": 0.15},
        ]

        # Check and add instrument factor exposures
        added_count = 0
        for exposure in exposure_data:
            # Check if exposure already exists (composite primary key)
            statement = select(InstrumentFactorExposure).where(
                InstrumentFactorExposure.instrument_id == exposure["instrument_id"],
                InstrumentFactorExposure.factor_id == exposure["factor_id"],
            )
            existing_exposure = session.exec(statement).first()

            if existing_exposure:
                logger.info(
                    f"Exposure {exposure['instrument_id']}-{exposure['factor_id']} already exists, skipping"
                )
                continue

            # Create new exposure
            instrument_factor_exposure = InstrumentFactorExposure(**exposure)
            session.add(instrument_factor_exposure)
            added_count += 1
            logger.info(
                f"Added exposure: {exposure['instrument_id']}-{exposure['factor_id']} (beta: {exposure['beta']})"
            )

        session.commit()
        logger.info(
            f"Instrument factor exposure population completed. Added {added_count} new exposures."
        )


def populate_news_events():
    """Populate news_events table with initial data"""
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)
        # News events data
        news_events_data = [
            {
                "id": 1,
                "headline": "Central Authority raises benchmark rate by 50 bp to counter persistent inflation",
                "description": "The Monetary Policy Board raised its policy rate by 0.50 ppts to 5.25 %% after three months of core inflation above 3 %%. Short-term borrowing costs and business loan rates rose as policymakers aimed to anchor expectations.",
                "decay_halflife_s": 360.0,
                "ts_release_ms": 200000,
            },
            {
                "id": 2,
                "headline": "Monetary Authority cuts rates by 25 bp as growth momentum softens",
                "description": "Benchmark rate lowered by 25 bp to preserve labor gains amid slowing output and hiring; yields fell and liquidity improved.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 300000,
            },
            {
                "id": 3,
                "headline": "Market volatility rises as traders pare risk before economic data",
                "description": "Price swings widened and spreads doubled as traders reduced risk ahead of key releases; liquidity thinned and hedging demand rose.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 100000,
            },
            {
                "id": 4,
                "headline": "Calm returns after strong auction restores liquidity to credit markets",
                "description": "Bond and equity trading stabilized following a successful government auction; volatility eased and spreads narrowed.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 300000,
            },
            {
                "id": 5,
                "headline": "Short-term funding costs ease as credit demand improves",
                "description": "Interbank rates declined 12 bp, loan demand rose, and liquidity strengthened amid improved credit conditions.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 100000,
            },
            {
                "id": 6,
                "headline": "Liquidity tightens as quarter-end cash demand lifts overnight rates",
                "description": "Overnight borrowing costs rose 25 bp as banks built cash buffers; mild market stress but limited systemic risk.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 350000,
            },
            {
                "id": 7,
                "headline": "Government approves $40 billion infrastructure modernization plan",
                "description": "Two-year infrastructure plan boosts logistics and digital investment; expected +0.2 pp GDP growth next year.",
                "decay_halflife_s": 480.0,
                "ts_release_ms": 100000,
            },
            {
                "id": 8,
                "headline": "Budget shortfall widens as revenue growth slows",
                "description": "Fiscal deficit rose to 3.4 %% of GDP on weak tax receipts and delayed spending; limited room for stimulus.",
                "decay_halflife_s": 480.0,
                "ts_release_ms": 200000,
            },
            {
                "id": 9,
                "headline": "Consumer prices rise 0.4 %% m/m versus 0.2 %% expected; core inflation stays firm",
                "description": "Inflation surprised upward; housing & transport costs drove prices higher, delaying easing expectations.",
                "decay_halflife_s": 360.0,
                "ts_release_ms": 300000,
            },
            {
                "id": 10,
                "headline": "Inflation eases to 0.1 %% m/m, lowest monthly increase in over a year",
                "description": "Inflation slowed broadly; supports disinflation path and potential future rate cuts.",
                "decay_halflife_s": 360.0,
                "ts_release_ms": 400000,
            },
            {
                "id": 11,
                "headline": "Investor sentiment improves as data signal steady growth",
                "description": "Survey showed 8 %% rise in bullish investors; equities gained 0.6 %% led by cyclicals.",
                "decay_halflife_s": 600.0,
                "ts_release_ms": 100000,
            },
            {
                "id": 12,
                "headline": "Confidence weakens as business leaders cut outlooks for next quarter",
                "description": "Corporate outlooks turned cautious; TG5 Index fell 0.5 %% on softer guidance and global demand.",
                "decay_halflife_s": 600.0,
                "ts_release_ms": 400000,
            },
            {
                "id": 13,
                "headline": "NovaScale announces $2.4 B defense contract for secure analytics systems",
                "description": "Defense contract expands NovaScale's AI portfolio by 20 %%; validates long-term growth pipeline.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 150000,
            },
            {
                "id": 14,
                "headline": "Technology sector under pressure as regulators review AI data practices",
                "description": "Authorities opened review into AI training data use; tech shares down 2.3 %%.",
                "decay_halflife_s": 480.0,
                "ts_release_ms": 300000,
            },
            {
                "id": 15,
                "headline": "Regulator grants fast-track status to Genixa's automated cell therapy platform",
                "description": "Fast-track designation cuts review times ≈30 %%; boosts biotech sentiment.",
                "decay_halflife_s": 240.0,
                "ts_release_ms": 100000,
            },
            {
                "id": 16,
                "headline": "Clinical partner reports delay in cell manufacturing validation tests",
                "description": "Manufacturing delays may push regulatory submission back months; tempered optimism.",
                "decay_halflife_s": 240.0,
                "ts_release_ms": 400000,
            },
            {
                "id": 17,
                "headline": "Manufacturing output expands as PMI rises to 52.4 from 50.8",
                "description": "Factory utilization rose to 78 %% and delivery times shortened; steady industrial recovery.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 500000,
            },
            {
                "id": 18,
                "headline": "Freight congestion worsens as port delays extend average transit by 36 hours",
                "description": "Port backlogs increased; logistics operators warn of delivery disruptions and higher costs.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 200000,
            },
            {
                "id": 19,
                "headline": "Oil prices rise 3.2 %% after output cuts announced by major producers",
                "description": "Major producers extend output cuts → crude up 3.2 %% to $88.4 ; energy equities rose.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 250000,
            },
            {
                "id": 20,
                "headline": "Storm system disrupts offshore operations; energy output down 7 %% week-over-week",
                "description": "Category-3 storm temporarily cut offshore production 7 %%; repairs underway.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 300000,
            },
            {
                "id": 21,
                "headline": "Competition authority opens review into algorithmic data-sharing practices",
                "description": "Regulators investigate data-sharing in tech/logistics; tech stocks -1.2 %%.",
                "decay_halflife_s": 480.0,
                "ts_release_ms": 100000,
            },
            {
                "id": 22,
                "headline": "Financial commission eases reporting rules for medium-sized firms",
                "description": "Reform reduces compliance costs and supports small-cap listings.",
                "decay_halflife_s": 480.0,
                "ts_release_ms": 250000,
            },
            {
                "id": 23,
                "headline": "Aurora Financial acquires regional brokerage in $1.8 B deal",
                "description": "Aurora buys brokerage to expand retail clearing reach; integration risk moderate.",
                "decay_halflife_s": 360.0,
                "ts_release_ms": 250000,
            },
            {
                "id": 24,
                "headline": "Traxline withdraws planned $900 M IPO amid market volatility",
                "description": "Traxline postponed subsidiary IPO due to weak conditions; industrial sentiment fell.",
                "decay_halflife_s": 360.0,
                "ts_release_ms": 400000,
            },
            {
                "id": 25,
                "headline": "Authorities impose 5 %% import tariff on foreign industrial components",
                "description": "New 5 %% duty on machinery to boost domestic chains; industrial equities fell slightly.",
                "decay_halflife_s": 360.0,
                "ts_release_ms": 250000,
            },
            {
                "id": 26,
                "headline": "Tariff rollback agreed as trade partners reach new logistics accord",
                "description": "Trade accord cuts import duties by ≈70 %%; improves shipping efficiency.",
                "decay_halflife_s": 360.0,
                "ts_release_ms": 350000,
            },
            {
                "id": 27,
                "headline": "Minor network outage disrupts order-routing systems for 40 minutes",
                "description": "Temporary failure hit trading/logistics for 40 min; volumes -15 %%, normalized later.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 100000,
            },
            {
                "id": 28,
                "headline": "Cybersecurity breach exposes limited corporate client data",
                "description": "Limited data breach at cloud provider; heightened regulatory attention expected.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 200000,
            },
            {
                "id": 29,
                "headline": "Port workers reach tentative deal after brief strike",
                "description": "Two-day strike ended with 4 %% wage increase; shipping delays ≈24 h.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 300000,
            },
            {
                "id": 30,
                "headline": "Industrial workers vote for nationwide strike over contract dispute",
                "description": "Nationwide 72-hour strike threatens 15 %% freight throughput; negotiations urged.",
                "decay_halflife_s": 360.0,
                "ts_release_ms": 350000,
            },
            {
                "id": 31,
                "headline": "Tropical storm disrupts shipping routes; minor energy outages reported",
                "description": "Storm temporarily closed ports and cut 2 %% of energy output; markets steady after initial drop.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 400000,
            },
            {
                "id": 32,
                "headline": "Unseasonably mild temperatures reduce near-term energy demand",
                "description": "Mild weather cut fuel use and energy prices; transport firms benefited.",
                "decay_halflife_s": 300.0,
                "ts_release_ms": 500000,
            },
        ]

        # Check and add news events
        added_count = 0
        for event_data in news_events_data:
            # Check if news event already exists
            statement = select(NewsEvent).where(NewsEvent.id == event_data["id"])
            existing_event = session.exec(statement).first()

            if existing_event:
                logger.info(f"News event {event_data['id']} already exists, skipping")
                continue

            # Create new news event
            news_event = NewsEvent(**event_data)
            session.add(news_event)
            added_count += 1
            logger.info(
                f"Added news event: {event_data['id']} - {event_data['headline']}"
            )

        session.commit()
        logger.info(
            f"News events population completed. Added {added_count} new news events."
        )


def populate_news_event_factors():
    """Populate news_event_factors table with initial data"""
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)
        # News event factors data (id: factor_ids as comma-separated string)
        news_event_factors_data = {
            1: "RATE,MKT,FGI",
            2: "RATE,MKT,FGI",
            3: "VIX",
            4: "VIX",
            5: "FIN_CONDS,MKT,FGI",
            6: "FIN_CONDS,MKT,FGI",
            7: "FISCAL,INDU_SUPPLY",
            8: "FISCAL,MKT",
            9: "INFL,RATE,MKT",
            10: "INFL,RATE,MKT",
            11: "FGI,MKT",
            12: "FGI,MKT",
            13: "TECH_HYPE,TRANS",
            14: "REG,TECH_HYPE",
            15: "HEALTH_TRIAL",
            16: "HEALTH_TRIAL,INDU_SUPPLY",
            17: "INDU_SUPPLY,MKT,FGI",
            18: "INDU_SUPPLY,LABOR",
            19: "ENERGY_OIL,INFL",
            20: "WEATHER,ENERGY_OIL",
            21: "REG,MKT",
            22: "REG,MKT",
            23: "TRANS,FIN_CONDS",
            24: "TRANS,MKT",
            25: "TRADE,INDU_SUPPLY",
            26: "TRADE,MKT",
            27: "CYBER,VIX",
            28: "CYBER,REG",
            29: "LABOR,INDU_SUPPLY",
            30: "LABOR,INDU_SUPPLY",
            31: "WEATHER,ENERGY_OIL",
            32: "WEATHER,ENERGY_OIL",
        }

        # Check and add news event factors
        added_count = 0
        for news_event_id, factor_ids_str in news_event_factors_data.items():
            # Parse comma-separated factor IDs
            factor_ids = [fid.strip() for fid in factor_ids_str.split(",")]

            for factor_id in factor_ids:
                # Check if news event factor already exists (composite primary key)
                statement = select(NewsEventFactor).where(
                    NewsEventFactor.news_event_id == news_event_id,
                    NewsEventFactor.factor_id == factor_id,
                )
                existing_factor = session.exec(statement).first()

                if existing_factor:
                    logger.info(
                        f"News event factor {news_event_id}-{factor_id} already exists, skipping"
                    )
                    continue

                # Create new news event factor
                news_event_factor = NewsEventFactor(
                    news_event_id=news_event_id, factor_id=factor_id
                )
                session.add(news_event_factor)
                added_count += 1
                logger.info(f"Added news event factor: {news_event_id}-{factor_id}")

        session.commit()
        logger.info(
            f"News event factors population completed. Added {added_count} new news event factors."
        )


if __name__ == "__main__":
    populate_instruments()
    populate_sectors()
    populate_instrument_sector_exposure()
    populate_macro_factors()
    populate_instrument_factor_exposure()
    populate_news_events()
    populate_news_event_factors()
