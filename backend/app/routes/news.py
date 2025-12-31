from fastapi import APIRouter, HTTPException
from app.models import NewsResponse, NewsListResponse
from app.services.news_service import news_service
from typing import Optional

router = APIRouter()

@router.get("/", response_model=NewsListResponse)
async def get_all_news(limit: int = 50):
    try:
        news_list = news_service.get_all_news(limit=limit)
        return NewsListResponse(total=len(news_list), news=news_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_by_id(news_id: str):
    try:
        news = news_service.get_news_by_id(news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        return news
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@router.post("/fetch-rss")
async def fetch_rss():
    try:
        result = news_service.fetch_and_process_rss()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching RSS: {str(e)}")
