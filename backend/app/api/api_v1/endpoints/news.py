from fastapi import APIRouter, Depends

from dependencies import get_news_engine

router = APIRouter()


@router.get("/all")
async def get_all_news(news_engine=Depends(get_news_engine)):
    """Public feed of all news events."""
    return {"news": news_engine.get_all_news()}


@router.get("/candidates")
async def get_candidate_news(news_engine=Depends(get_news_engine)):
    """Public feed of news that is eligible to be activated."""
    return {"news": news_engine.get_candidate_news()}


@router.get("/status")
async def get_news_status(news_engine=Depends(get_news_engine)):
    """Get current news engine status including simulation time."""
    news_engine.update_simulation_time()
    return {
        "sim_time_ms": news_engine.sim_time_ms,
        "sim_time_seconds": news_engine.sim_time_ms / 1000,
        "active_news_count": len(news_engine.active_news_ids),
        "active_news_ids": list(news_engine.active_news_ids),
    }
