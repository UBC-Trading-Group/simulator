from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dependencies import get_news_engine

router = APIRouter()


class NewsRequest(BaseModel):
    id: int
    ts_release_ms: int
    decay_halflife_s: int
    magnitude: float
    headline: str


@router.post("/news")
async def create_news(news: NewsRequest, news_engine=Depends(get_news_engine)):
    news_engine.add_news_ad_hoc(dict(news))
    return {"message": "News created successfully"}


@router.get("/news/all")
async def get_all_news(news_engine=Depends(get_news_engine)):
    return {"news": news_engine.get_all_news()}


@router.get("/news/candidates")
async def get_candidate_news(news_engine=Depends(get_news_engine)):
    return {"news": news_engine.get_candidate_news()}


@router.post("/news/activate/{news_id}")
async def activate_news(news_id: int, news_engine=Depends(get_news_engine)):
    """Manually activate a news event"""
    news_engine.active_news_ids.add(news_id)
    return {
        "message": f"News {news_id} activated",
        "active_news": list(news_engine.active_news_ids),
    }


@router.get("/news/active")
async def get_active_news(news_engine=Depends(get_news_engine)):
    """Get currently active news IDs"""
    return {"active_news_ids": list(news_engine.active_news_ids)}


@router.get("/debug/drift")
async def get_drift_debug(news_engine=Depends(get_news_engine)):
    """Debug endpoint to check drift calculations"""
    import time

    from dependencies import get_instrument_manager

    instrument_manager = get_instrument_manager()

    drift_values = {}
    news_details = []

    # Get details about active news
    for news in news_engine.news_objects:
        if news.id in news_engine.active_news_ids:
            effect = news_engine.calculate(news)
            factors = news_engine.news_factor_map.get(news.id, [])
            news_details.append(
                {
                    "id": news.id,
                    "headline": news.headline[:60],
                    "magnitude": (news.magnitude_top + news.magnitude_bottom) / 2,
                    "effect": effect,
                    "factors": factors,
                    "age_seconds": time.time() - (news.ts_release_ms / 1000),
                }
            )

    for instrument in instrument_manager.get_all_instruments():
        drift = news_engine.get_instrument_drift(instrument.id)
        drift_values[instrument.id] = drift

    return {
        "active_news_count": len(news_engine.active_news_ids),
        "active_news_ids": list(news_engine.active_news_ids),
        "news_details": news_details,
        "factor_map_size": len(news_engine.news_factor_map),
        "beta_map_size": len(news_engine.instrument_factor_betas),
        "drift_by_instrument": drift_values,
    }
