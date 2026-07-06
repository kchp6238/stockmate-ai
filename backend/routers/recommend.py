"""GET /api/recommend - AI 추천 종목 TOP 10"""
import logging
from fastapi import APIRouter, Request
from limiter import limiter
from cache import cache
from services.stock_data import get_stock_data

logger = logging.getLogger(__name__)
router = APIRouter(tags=["recommend"])

CANDIDATES = ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "TSLA",
              "JPM", "V", "JNJ", "UNH", "XOM", "WMT", "PG"]


@router.get("/recommend")
@limiter.limit("5/minute")
async def recommend(request: Request):
    """
    후보 종목들의 기술적 신호를 스코어링해서 TOP 10 추천
    """
    cached = cache.get("recommend", ttl=600)
    if cached:
        return cached

    results = []
    for t in CANDIDATES:
        try:
            d   = get_stock_data(t)
            ind = d["indicators"]
            p   = d["price"]

            # 점수 계산
            score = _score(ind)
            rsi   = ind.get("rsi")
            chg   = p.get("change_pct", 0)

            results.append({
                "ticker":       t,
                "company_name": d["company_name"],
                "price":        p["current"],
                "change_pct":   chg,
                "score":        score,
                "signal":       ind["overall_signal"],
                "rsi":          rsi,
                "reason":       _reason(ind, p),
                "risk":         _risk(ind, p),
                "expected":     _expected(ind, p),
            })
        except Exception as e:
            logger.warning(f"[{t}] 추천 스코어 실패: {e}")

    # 점수 내림차순 정렬 후 TOP 10
    results.sort(key=lambda x: x["score"], reverse=True)
    top10 = results[:10]

    cache.set("recommend", top10)
    return top10


def _score(ind: dict) -> int:
    s = 50
    rsi = ind.get("rsi")
    if rsi:
        if rsi < 30:   s += 20
        elif rsi < 45: s += 10
        elif rsi > 70: s -= 20
        elif rsi > 55: s -= 10

    macd, sig = ind.get("macd"), ind.get("macd_signal")
    if macd and sig:
        s += 10 if macd > sig else -10

    overall = ind.get("overall_signal", "neutral")
    bonus = {"strong_buy": 25, "buy": 15, "neutral": 0, "sell": -15, "strong_sell": -25}
    s += bonus.get(overall, 0)
    return max(0, min(100, s))


def _reason(ind: dict, p: dict) -> str:
    parts = []
    rsi = ind.get("rsi")
    if rsi and rsi < 35:
        parts.append(f"RSI {rsi:.1f} 과매도 구간 (반등 가능성)")
    macd, sig = ind.get("macd"), ind.get("macd_signal")
    if macd and sig and macd > sig:
        parts.append("MACD 골든크로스 (상승 모멘텀)")
    curr = p.get("current", 0)
    sma20 = ind.get("sma20")
    sma50 = ind.get("sma50")
    if sma20 and sma50 and curr > sma20 > sma50:
        parts.append("가격이 SMA20·SMA50 위 (강세 추세)")
    return " / ".join(parts) if parts else "기술적 지표 종합 분석"


def _risk(ind: dict, p: dict) -> str:
    rsi = ind.get("rsi")
    if rsi and rsi > 70:
        return "높음 (과매수)"
    sig = ind.get("overall_signal", "neutral")
    if sig in ("sell", "strong_sell"):
        return "높음 (매도 신호)"
    if sig in ("neutral",):
        return "중간"
    return "낮음"


def _expected(ind: dict, p: dict) -> str:
    sig = ind.get("overall_signal", "neutral")
    curr = p.get("current", 0)
    bb_upper = ind.get("bb_upper")
    if bb_upper and curr < bb_upper:
        upside = (bb_upper - curr) / curr * 100
        return f"볼린저 상단까지 +{upside:.1f}% 상승 여력"
    return {"strong_buy": "단기 강세 예상", "buy": "완만한 상승 기대",
            "neutral": "횡보 예상", "sell": "하락 가능성", "strong_sell": "단기 약세 예상"}.get(sig, "")
