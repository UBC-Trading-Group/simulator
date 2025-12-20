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
