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
