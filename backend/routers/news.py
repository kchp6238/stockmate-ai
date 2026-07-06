"""GET /api/news/{ticker} - 뉴스 조회"""
import logging
from fastapi import APIRouter, HTTPException, Request
from limiter import limiter
from cache import cache
from services.stock_data import get_stock_data
from services.news_service import get_news

logger = logging.getLogger(__name__)
router = APIRouter(tags=["news"])


@router.get("/news/{ticker}")
@limiter.limit("15/minute")
async def news(ticker: str, request: Request):
    key = f"news:{ticker.upper()}"
    cached = cache.get(key, ttl=600)  # 10분 캐시
    if cached:
        return cached

    try:
        data   = get_stock_data(ticker)
        result = get_news(data["ticker"], data.get("display_name", ticker))
        cache.set(key, result)
        return result
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"[{ticker}] news 오류: {e}", exc_info=True)
        raise HTTPException(500, "뉴스 조회 중 오류가 발생했습니다.")
