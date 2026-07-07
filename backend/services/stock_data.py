"""
주식 데이터 수집 + 기술적 지표 계산 서비스
"""
import logging
import warnings
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

# 한국 주식 티커 매핑 (종목명 → yfinance 티커)
KR_TICKERS = {
    # 반도체·IT
    "삼성전자": "005930.KS", "삼성전자우": "005935.KS",
    "SK하이닉스": "000660.KS", "삼성SDI": "006400.KS",
    "LG전자": "066570.KS", "삼성전기": "009150.KS",
    "SK이노베이션": "096770.KS",

    # 자동차
    "현대차": "005380.KS", "기아": "000270.KS",
    "현대모비스": "012330.KS", "한온시스템": "018880.KS",

    # 2차전지·에너지
    "LG에너지솔루션": "373220.KS", "LG화학": "051910.KS",
    "에코프로": "086520.KQ", "에코프로비엠": "247540.KQ",
    "포스코퓨처엠": "003670.KS", "엘앤에프": "066970.KQ",

    # 인터넷·플랫폼
    "카카오": "035720.KS", "NAVER": "035420.KS",
    "카카오뱅크": "323410.KS", "카카오페이": "377300.KS",
    "크래프톤": "259960.KS", "넥슨게임즈": "225570.KQ",

    # 바이오·제약
    "셀트리온": "068270.KS", "삼성바이오로직스": "207940.KS",
    "유한양행": "000100.KS", "한미약품": "128940.KS",
    "종근당": "185750.KS", "대웅제약": "069620.KS",

    # 철강·소재
    "POSCO홀딩스": "005490.KS", "고려아연": "010130.KS",
    "현대제철": "004020.KS",

    # 금융·보험
    "KB금융": "105560.KS", "신한지주": "055550.KS",
    "하나금융지주": "086790.KS", "우리금융지주": "316140.KS",
    "삼성생명": "032830.KS", "삼성화재": "000810.KS",
    "미래에셋증권": "006800.KS", "키움증권": "039490.KS",

    # 건설·방산·항공
    "한화": "000880.KS", "한화에어로스페이스": "012450.KS",
    "한화솔루션": "009830.KS", "한화시스템": "272210.KS",
    "현대건설": "000720.KS", "대한항공": "003490.KS",
    "아시아나항공": "020560.KS", "한국항공우주": "047810.KS",

    # 유통·소비재
    "CJ제일제당": "097950.KS", "오리온": "271560.KS",
    "롯데쇼핑": "023530.KS", "이마트": "139480.KS",
    "신세계": "004170.KS", "BGF리테일": "282330.KS",

    # 통신
    "SK텔레콤": "017670.KS", "KT": "030200.KS",
    "LG유플러스": "032640.KS",

    # 기타
    "현대중공업": "329180.KS", "두산에너빌리티": "034020.KS",
    "한국전력": "015760.KS", "KT&G": "033780.KS",
    "롯데케미칼": "011170.KS", "OCI홀딩스": "010060.KS",
}

def resolve_ticker(raw: str) -> str:
    """
    한국어 종목명 → yfinance 티커 변환
    - 정확한 이름 우선 매칭
    - 부분 검색: 입력값이 포함된 첫 번째 종목 반환
    """
    # 1. 정확히 일치하는 경우
    if raw in KR_TICKERS:
        return KR_TICKERS[raw]

    # 2. 부분 일치 (예: "한화" → "한화에어로스페이스" 등 첫 번째 매칭)
    matches = [(k, v) for k, v in KR_TICKERS.items() if raw in k]
    if matches:
        # 가장 짧은 이름(가장 유사한 것) 우선
        matches.sort(key=lambda x: len(x[0]))
        logger.info(f"부분 매칭: '{raw}' → '{matches[0][0]}' ({matches[0][1]})")
        return matches[0][1]

    # 3. 영문 티커 그대로 사용
    return raw.upper()

def _safe(s: pd.Series) -> Optional[float]:
    v = s.iloc[-1]
    return None if pd.isna(v) else round(float(v), 2)

def _calc_rsi(close: pd.Series, n: int = 14) -> Optional[float]:
    d    = close.diff()
    gain = d.clip(lower=0).rolling(n).mean()
    loss = (-d.clip(upper=0)).rolling(n).mean()
    rs   = gain / loss.replace(0, np.nan)
    return _safe(100 - 100 / (1 + rs))

def _signal_score(rsi, macd, macd_sig, price, sma20, sma50) -> str:
    s = 0
    if rsi:
        if rsi < 30: s += 2
        elif rsi < 45: s += 1
        elif rsi > 70: s -= 2
        elif rsi > 55: s -= 1
    if macd and macd_sig:
        s += 1 if macd > macd_sig else -1
    if price and sma20 and sma50:
        if price > sma20 > sma50: s += 2
        elif price > sma20: s += 1
        elif price < sma20 < sma50: s -= 2
        elif price < sma20: s -= 1
    if s >= 4:   return "strong_buy"
    elif s >= 2: return "buy"
    elif s <= -4: return "strong_sell"
    elif s <= -2: return "sell"
    return "neutral"


def get_stock_data(ticker: str) -> dict:
    """
    종목 기본정보 + 기술적 지표 반환
    """
    ticker_yf = resolve_ticker(ticker)
    stock = yf.Ticker(ticker_yf)

    # OHLCV 1년치
    df = yf.download(ticker_yf, period="1y", progress=False, auto_adjust=True)
    if df is None or df.empty:
        raise ValueError(f"'{ticker}' 데이터를 찾을 수 없습니다. 티커 코드를 확인해 주세요.")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.sort_index()

    if len(df) < 60:
        raise ValueError(f"데이터가 부족합니다 ({len(df)}일, 최소 60일 필요).")

    close  = df["Close"]
    curr   = float(close.iloc[-1])
    prev   = float(close.iloc[-2])
    chg    = (curr - prev) / prev * 100

    # 기본 정보
    info = {}
    try:
        info = stock.info or {}
    except Exception:
        pass

    # 기술적 지표
    sma20 = _safe(close.rolling(20).mean())
    sma50 = _safe(close.rolling(50).mean())
    ema20 = _safe(close.ewm(span=20, adjust=False).mean())
    ema12 = _safe(close.ewm(span=12, adjust=False).mean())
    ema26 = _safe(close.ewm(span=26, adjust=False).mean())

    macd_line = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    macd_sig  = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - macd_sig

    bb_mid   = close.rolling(20).mean()
    bb_std   = close.rolling(20).std()
    bb_upper = _safe(bb_mid + 2 * bb_std)
    bb_lower = _safe(bb_mid - 2 * bb_std)

    rsi    = _calc_rsi(close)
    macd_v = _safe(macd_line)
    sig_v  = _safe(macd_sig)

    # 차트용 히스토리 (최근 180일)
    hist_df = df.tail(180)
    sma20_arr = close.rolling(20).mean()
    sma50_arr = close.rolling(50).mean()
    ema20_arr = close.ewm(span=20, adjust=False).mean()
    bb_u_arr  = bb_mid + 2 * bb_std
    bb_l_arr  = bb_mid - 2 * bb_std
    macd_arr  = macd_line
    sig_arr   = macd_sig
    hist_arr  = macd_hist
    rsi_arr   = 100 - 100 / (1 + close.diff().clip(lower=0).rolling(14).mean() /
                              (-close.diff().clip(upper=0)).rolling(14).mean().replace(0, np.nan))

    offset = len(df) - len(hist_df)

    history = []
    for i, (idx, row) in enumerate(hist_df.iterrows()):
        j = offset + i
        def sv(s): return None if pd.isna(s.iloc[j]) else round(float(s.iloc[j]), 2)
        history.append({
            "date":   idx.strftime("%Y-%m-%d"),
            "open":   round(float(row["Open"]),  2),
            "high":   round(float(row["High"]),  2),
            "low":    round(float(row["Low"]),   2),
            "close":  round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
            "sma20":  sv(sma20_arr),
            "sma50":  sv(sma50_arr),
            "ema20":  sv(ema20_arr),
            "bb_upper": sv(bb_u_arr),
            "bb_lower": sv(bb_l_arr),
            "bb_mid":   sv(bb_mid),
            "macd":     sv(macd_arr),
            "macd_signal": sv(sig_arr),
            "macd_hist":   sv(hist_arr),
            "rsi":      sv(rsi_arr),
        })

    def info_float(key):
        v = info.get(key)
        try: return round(float(v), 2) if v else None
        except: return None

    return {
        "ticker":       ticker_yf,
        "display_name": ticker,
        "company_name": info.get("longName") or info.get("shortName") or ticker,
        "sector":       info.get("sector", ""),
        "industry":     info.get("industry", ""),
        "country":      info.get("country", ""),
        "currency":     info.get("currency", "KRW" if ticker_yf.endswith((".KS", ".KQ")) else "USD"),
        "price": {
            "current":    round(curr, 2),
            "prev_close": round(prev, 2),
            "change":     round(curr - prev, 2),
            "change_pct": round(chg, 2),
            "open":       round(float(df["Open"].iloc[-1]), 2),
            "high":       round(float(df["High"].iloc[-1]), 2),
            "low":        round(float(df["Low"].iloc[-1]),  2),
            "volume":     int(df["Volume"].iloc[-1]),
            "avg_volume": info_float("averageVolume"),
            "high_52w":   round(float(close.tail(252).max()), 2),
            "low_52w":    round(float(close.tail(252).min()), 2),
            "market_cap": info.get("marketCap"),
        },
        "fundamentals": {
            "pe_ratio":       info_float("trailingPE"),
            "forward_pe":     info_float("forwardPE"),
            "pb_ratio":       info_float("priceToBook"),
            "eps":            info_float("trailingEps"),
            "dividend_yield": info_float("dividendYield"),
            "beta":           info_float("beta"),
            "profit_margin":  info_float("profitMargins"),
            "roe":            info_float("returnOnEquity"),
        },
        "indicators": {
            "rsi":         rsi,
            "macd":        macd_v,
            "macd_signal": sig_v,
            "macd_hist":   _safe(macd_hist),
            "sma20": sma20, "sma50": sma50, "ema20": ema20,
            "bb_upper": bb_upper, "bb_lower": bb_lower, "bb_mid": _safe(bb_mid),
            "overall_signal": _signal_score(rsi, macd_v, sig_v, curr, sma20, sma50),
        },
        "history": history,
    }
