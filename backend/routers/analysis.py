"""GET /api/analysis/{ticker} - AI 분석만 단독 요청"""
import logging
from fastapi import APIRouter, HTTPException, Request
from limiter import limiter
from cache import cache
from services.stock_data import get_stock_data
from services.prophet_service import run_forecast
from services.ai_service import analyze_stock

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analysis"])


@router.get("/analysis/{ticker}")
@limiter.limit("5/minute")
async def get_analysis(ticker: str, request: Request):
    key = f"analysis:{ticker.upper()}"
    cached = cache.get(key, ttl=300)
    if cached:
        return cached

    try:
        data     = get_stock_data(ticker)
        forecast = run_forecast(data["ticker"])
        result   = analyze_stock(data, forecast)
        cache.set(key, result)
        return result
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"[{ticker}] analysis 오류: {e}", exc_info=True)
        raise HTTPException(500, "AI 분석 중 오류가 발생했습니다.")
