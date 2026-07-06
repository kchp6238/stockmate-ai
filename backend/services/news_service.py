"""
주식 관련 뉴스 수집 서비스
- yfinance 내장 뉴스 (기본)
- Finnhub API (API 키 있을 때)

⚠️ yfinance 1.x부터 뉴스 데이터가 "content" 키 안에 중첩되는 구조로 변경됨
   예: {"id": "...", "content": {"title": "...", "provider": {"displayName": "..."}, ...}}
"""
import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

TRUSTED_SOURCES = {
    "Reuters", "Bloomberg", "CNBC", "Yahoo Finance", "MarketWatch",
    "The Wall Street Journal", "Financial Times", "Forbes", "Benzinga",
    "Seeking Alpha", "Motley Fool", "Business Insider", "Associated Press",
    "Investopedia", "Barron's", "TipRanks", "Zacks",
}


def get_news(ticker_yf: str, display_name: str = "", limit: int = 10) -> list[dict]:
    """
    뉴스 수집: Finnhub 우선, 없으면 yfinance 내장 뉴스
    """
    if settings.FINNHUB_API_KEY:
        try:
            result = _from_finnhub(ticker_yf, limit)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Finnhub 뉴스 실패: {e}")

    try:
        return _from_yfinance(ticker_yf, limit)
    except Exception as e:
        logger.warning(f"yfinance 뉴스 실패: {e}")
        return []


def _from_yfinance(ticker_yf: str, limit: int) -> list[dict]:
    import yfinance as yf
    stock = yf.Ticker(ticker_yf)
    raw = stock.news or []

    result = []
    for item in raw[:limit]:
        parsed = _parse_news_item(item)
        if parsed and parsed["title"]:
            result.append(parsed)
    return result


def _parse_news_item(item: dict):
    """
    yfinance 뉴스 아이템 파싱
    - 신규 형식 (1.x): item["content"] 안에 모든 정보
    - 구버전 형식: item 최상위에 정보
    """
    # 신규 형식: content 키 안에 데이터
    content = item.get("content")
    if isinstance(content, dict):
        title    = content.get("title", "")
        summary  = content.get("summary") or content.get("description") or ""

        provider = content.get("provider") or {}
        source   = provider.get("displayName") or provider.get("name") or "Unknown"

        # URL: canonicalUrl 또는 clickThroughUrl
        url = ""
        for key in ("canonicalUrl", "clickThroughUrl"):
            link_obj = content.get(key)
            if isinstance(link_obj, dict) and link_obj.get("url"):
                url = link_obj["url"]
                break

        # 날짜: pubDate (ISO 8601 문자열)
        published = _parse_iso_date(content.get("pubDate") or content.get("displayTime"))

        return {
            "title": title, "source": source, "url": url,
            "published": published, "summary": summary,
            "trusted": source in TRUSTED_SOURCES,
        }

    # 구버전 형식 (fallback)
    title   = item.get("title", "")
    source  = item.get("publisher", "Unknown")
    url     = item.get("link", "")
    summary = item.get("summary", "")
    published = _ts(item.get("providerPublishTime", 0))

    return {
        "title": title, "source": source, "url": url,
        "published": published, "summary": summary,
        "trusted": source in TRUSTED_SOURCES,
    }


def _from_finnhub(ticker_yf: str, limit: int) -> list[dict]:
    import datetime
    ticker_clean = ticker_yf.split(".")[0]
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)

    url = (
        f"https://finnhub.io/api/v1/company-news"
        f"?symbol={ticker_clean}"
        f"&from={week_ago}&to={today}"
        f"&token={settings.FINNHUB_API_KEY}"
    )
    with httpx.Client(timeout=10) as client:
        r = client.get(url)
        r.raise_for_status()
        data = r.json()

    result = []
    for item in data[:limit]:
        result.append({
            "title":     item.get("headline", ""),
            "source":    item.get("source", "Unknown"),
            "url":       item.get("url", ""),
            "published": _ts(item.get("datetime", 0)),
            "summary":   item.get("summary", ""),
            "trusted":   item.get("source", "") in TRUSTED_SOURCES,
        })
    return result


def _ts(ts: int) -> str:
    """Unix timestamp → 'YYYY-MM-DD HH:MM'"""
    if not ts:
        return ""
    import datetime
    try:
        return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def _parse_iso_date(date_str) -> str:
    """ISO 8601 문자열 ('2024-01-01T12:00:00Z') → 'YYYY-MM-DD HH:MM'"""
    if not date_str:
        return ""
    try:
        import datetime
        dt = datetime.datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(date_str)[:16].replace("T", " ")
