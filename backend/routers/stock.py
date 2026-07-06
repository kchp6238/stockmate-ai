"""
GET /api/stock/{ticker}         - 기본정보 + 기술적 지표 + 히스토리
GET /api/stock/{ticker}/full    - 기본정보 + 기술적 지표 + AI 분석 + 예측 + 뉴스 통합
"""
import logging
from fastapi import APIRouter, HTTPException, Request
from limiter import limiter
from cache import cache
from services.stock_data import get_stock_data, resolve_ticker
from services.prophet_service import run_forecast
from services.ai_service import analyze_stock
from services.news_service import get_news

logger = logging.getLogger(__name__)
router = APIRouter(tags=["stock"])


@router.get("/stock/{ticker}")
@limiter.limit("20/minute")
async def stock_info(ticker: str, request: Request):
    """기본 정보 + 기술적 지표 + 차트 데이터"""
    key = f"stock:{ticker.upper()}"
    cached = cache.get(key, ttl=180)  # 3분 캐시
    if cached:
        cached["cached"] = True
        return cached

    try:
        data = get_stock_data(ticker)
        data["cached"] = False
        cache.set(key, data)
        return data
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"[{ticker}] stock_info 오류: {e}", exc_info=True)
        raise HTTPException(500, "데이터 조회 중 오류가 발생했습니다.")


@router.get("/stock/{ticker}/full")
@limiter.limit("5/minute")
async def stock_full(ticker: str, request: Request):
    """
    기본정보 + AI 분석 + Prophet 예측 + 뉴스 통합 응답
    (무거운 작업 포함 → 캐시 TTL 5분)
    """
    key = f"full:{ticker.upper()}"
    cached = cache.get(key, ttl=300)
    if cached:
        cached["cached"] = True
        return cached

    try:
        # 1. 기본 데이터
        data        = get_stock_data(ticker)
        ticker_yf   = data["ticker"]

        # 2. Prophet 예측
        try:
            forecast = run_forecast(ticker_yf)
        except Exception as e:
            logger.warning(f"[{ticker}] Prophet 실패: {e}")
            forecast = {"current_price": data["price"]["current"],
                        "predicted_price": None, "change_pct": None, "forecast": []}

        # 3. AI 분석
        analysis = analyze_stock(data, forecast)

        # 4. 뉴스
        news = get_news(ticker_yf, data.get("display_name", ticker))

        result = {**data, "forecast": forecast, "analysis": analysis, "news": news, "cached": False}
        cache.set(key, result)
        return result

    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"[{ticker}] stock_full 오류: {e}", exc_info=True)
        raise HTTPException(500, "분석 중 오류가 발생했습니다.")
