"""
Claude AI 기반 주식 분석 서비스
- ANTHROPIC_API_KEY가 없거나 호출 실패 시,
  계산된 기술적 지표를 바탕으로 규칙 기반 상세 리포트를 생성 (폴백)
"""
import re
import logging
import anthropic
from config import settings

logger = logging.getLogger(__name__)

CUR_SYMBOL = {"KRW": "₩", "USD": "$", "JPY": "¥", "EUR": "€"}


def analyze_stock(stock_data: dict, forecast: dict) -> dict:
    """
    종목 데이터 + 예측 결과 → AI(or 규칙 기반) 분석 텍스트 생성
    """
    if not settings.ANTHROPIC_API_KEY:
        return _fallback(stock_data, forecast)

    p     = stock_data["price"]
    ind   = stock_data["indicators"]
    fund  = stock_data["fundamentals"]
    name  = stock_data["company_name"]
    tick  = stock_data["ticker"]
    curr  = p["current"]
    sig   = ind["overall_signal"]

    prompt = f"""당신은 월스트리트 수준의 전문 주식 애널리스트입니다.
아래 데이터를 바탕으로 {name} ({tick}) 에 대한 심층 분석 리포트를 **한국어**로 작성해 주세요.

## 가격 정보
- 현재가: {p['currency'] if 'currency' in stock_data else 'USD'} {curr}
- 전일 대비: {p['change_pct']:+.2f}%
- 52주 고/저: {p['high_52w']} / {p['low_52w']}
- 시가총액: {p.get('market_cap', 'N/A')}

## 기술적 지표
- RSI(14): {ind.get('rsi', 'N/A')} → {'과매도' if ind.get('rsi') and ind['rsi'] < 30 else '과매수' if ind.get('rsi') and ind['rsi'] > 70 else '중립 구간'}
- MACD: {ind.get('macd', 'N/A')} / Signal: {ind.get('macd_signal', 'N/A')} → {'골든크로스(강세)' if ind.get('macd') and ind.get('macd_signal') and ind['macd'] > ind['macd_signal'] else '데드크로스(약세)'}
- SMA20: {ind.get('sma20', 'N/A')} / SMA50: {ind.get('sma50', 'N/A')}
- 볼린저 상단: {ind.get('bb_upper', 'N/A')} / 하단: {ind.get('bb_lower', 'N/A')}
- 종합 기술적 신호: **{sig}**

## 기본적 지표
- PER: {fund.get('pe_ratio', 'N/A')}
- PBR: {fund.get('pb_ratio', 'N/A')}
- EPS: {fund.get('eps', 'N/A')}
- 배당수익률: {fund.get('dividend_yield', 'N/A')}
- 베타: {fund.get('beta', 'N/A')}

## Prophet ML 예측 (30일)
- 현재가: {forecast.get('current_price', 'N/A')} → 예측가: {forecast.get('predicted_price', 'N/A')} ({forecast.get('change_pct', 0):+.2f}%)

## 작성 형식 (반드시 이 구조 그대로)
**📊 현재 추세 분석**
[3~4문장으로 현재 기술적·기본적 상황 설명]

**📈 상승 요인**
- [요인 1: 구체적 수치와 근거 포함]
- [요인 2]
- [요인 3]

**📉 하락 요인**
- [요인 1: 구체적 수치와 근거 포함]
- [요인 2]

**⚠️ 위험 요소**
- [리스크 1]
- [리스크 2]

**💡 종합 의견**
[3~4문장의 투자 전략 제안, 구체적인 가격대 언급 포함]

마지막 줄 (반드시 이 형식):
결론: [매수|관망|매도] / 신뢰도: [숫자]% / 목표가: [숫자]"""

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg    = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse(msg.content[0].text, stock_data)

    except anthropic.AuthenticationError:
        logger.error("Anthropic API 키가 유효하지 않습니다.")
        return _fallback(stock_data, forecast)
    except anthropic.RateLimitError:
        logger.warning("Anthropic API Rate Limit 초과")
        return _fallback(stock_data, forecast)
    except Exception as e:
        logger.error(f"AI 분석 오류: {e}")
        return _fallback(stock_data, forecast)


def _parse(text: str, stock_data: dict) -> dict:
    rec, conf, target = "관망", 50, None
    m = re.search(
        r"결론\s*[:：]\s*(매수|관망|매도)\s*/\s*신뢰도\s*[:：]\s*(\d+)%\s*/\s*목표가\s*[:：]\s*([\d,.]+)",
        text
    )
    if m:
        rec    = m.group(1)
        conf   = min(100, max(0, int(m.group(2))))
        try: target = float(m.group(3).replace(",", ""))
        except: pass

    summary = re.sub(r"\n결론\s*[:：].*", "", text).strip()
    return {
        "summary":        summary,
        "recommendation": rec,
        "confidence":     conf,
        "target_price":   target,
    }


# ═══════════════════════════════════════════════════════════════
#  규칙 기반 폴백 분석
#  Claude API 없이도 RSI / MACD / 이동평균 / 볼린저밴드 / Prophet 예측을
#  근거로 "상승 요인 / 하락 요인 / 위험 요소 / 종합 의견"을 자동 생성
# ═══════════════════════════════════════════════════════════════

def _calc_score(rsi, macd, macd_sig, price, sma20, sma50) -> int:
    """
    기술적 지표 종합 점수 (-5 ~ +5)
    stock_data.py의 overall_signal 계산과 동일한 로직으로,
    신뢰도(confidence)를 점수의 절대값에 비례해 산출하기 위해 사용.
    """
    s = 0
    if rsi is not None:
        if rsi < 30:   s += 2
        elif rsi < 45: s += 1
        elif rsi > 70: s -= 2
        elif rsi > 55: s -= 1
    if macd is not None and macd_sig is not None:
        s += 1 if macd > macd_sig else -1
    if price and sma20 and sma50:
        if price > sma20 > sma50:   s += 2
        elif price > sma20:         s += 1
        elif price < sma20 < sma50: s -= 2
        elif price < sma20:         s -= 1
    return s


def _fallback(stock_data: dict, forecast: dict | None = None) -> dict:
    forecast = forecast or {}
    p    = stock_data["price"]
    ind  = stock_data["indicators"]
    fund = stock_data.get("fundamentals", {})

    cur_sym = CUR_SYMBOL.get(stock_data.get("currency", "USD"), "$")
    cur     = p["current"]
    chg     = p.get("change_pct", 0)

    rsi      = ind.get("rsi")
    macd     = ind.get("macd")
    macd_sig = ind.get("macd_signal")
    sma20    = ind.get("sma20")
    sma50    = ind.get("sma50")
    bb_upper = ind.get("bb_upper")
    bb_lower = ind.get("bb_lower")
    sig      = ind.get("overall_signal", "neutral")

    bullish, bearish, risks = [], [], []

    def fp(v):  # 가격 포맷
        return f"{cur_sym}{v:,.2f}" if v is not None else "N/A"

    # ── RSI ──────────────────────────────────────────────
    if rsi is not None:
        if rsi < 30:
            bullish.append(f"RSI가 {rsi:.1f}로 과매도 구간에 진입해 있어, 통계적으로 단기 반등이 나올 가능성이 높습니다.")
        elif rsi < 45:
            bullish.append(f"RSI가 {rsi:.1f}로 매도 압력이 줄어드는 구간에 위치해 있습니다.")
        elif rsi > 70:
            bearish.append(f"RSI가 {rsi:.1f}로 과매수 구간에 진입해 있어, 단기적으로 차익 매물이 출회될 가능성이 있습니다.")
            risks.append("RSI 과매수 구간에서는 추가 상승보다 단기 조정 위험이 더 커질 수 있습니다.")
        elif rsi > 55:
            bearish.append(f"RSI가 {rsi:.1f}로 매수 동력이 다소 약해지는 구간에 위치해 있습니다.")
        else:
            bullish.append(f"RSI가 {rsi:.1f}로 과매수·과매도 어느 쪽에도 치우치지 않은 안정적인 구간입니다.")

    # ── MACD ─────────────────────────────────────────────
    if macd is not None and macd_sig is not None:
        if macd > macd_sig:
            bullish.append(
                f"MACD({macd:.2f})가 시그널선({macd_sig:.2f}) 위에 위치한 골든크로스 상태로, "
                f"단기 상승 모멘텀이 살아있음을 나타냅니다."
            )
        else:
            bearish.append(
                f"MACD({macd:.2f})가 시그널선({macd_sig:.2f}) 아래에 위치한 데드크로스 상태로, "
                f"단기 하락 모멘텀이 우세함을 나타냅니다."
            )

    # ── 이동평균 (SMA20 / SMA50) ───────────────────────────
    if sma20 is not None and sma50 is not None:
        if cur > sma20 > sma50:
            bullish.append(
                f"현재가({fp(cur)})가 SMA20({fp(sma20)})과 SMA50({fp(sma50)}) 위에 위치해 "
                f"단기·중기 추세가 모두 상승 흐름을 보이고 있습니다."
            )
        elif cur < sma20 < sma50:
            bearish.append(
                f"현재가({fp(cur)})가 SMA20({fp(sma20)})과 SMA50({fp(sma50)}) 아래에 위치해 "
                f"단기·중기 추세가 모두 하락 흐름을 보이고 있습니다."
            )
            risks.append("주요 이동평균선을 모두 하회하고 있어 추세 반전 신호가 나오기 전까지 약세가 이어질 수 있습니다.")
        elif cur > sma20:
            bullish.append(f"현재가가 SMA20({fp(sma20)}) 위에 위치해 단기 흐름은 양호한 편입니다.")
        elif cur < sma20:
            bearish.append(f"현재가가 SMA20({fp(sma20)}) 아래에 위치해 단기 흐름이 다소 약한 편입니다.")

    # ── 볼린저 밴드 ────────────────────────────────────────
    if bb_upper is not None and bb_lower is not None:
        if cur >= bb_upper:
            bearish.append(f"볼린저밴드 상단({fp(bb_upper)})에 근접하거나 이를 상회해 단기 과열 신호로 해석될 수 있습니다.")
            risks.append("볼린저밴드 상단을 이탈한 이후에는 평균 회귀(되돌림) 압력이 커질 수 있습니다.")
        elif cur <= bb_lower:
            bullish.append(f"볼린저밴드 하단({fp(bb_lower)})에 근접하거나 이를 하회해 기술적 반등 가능성이 있습니다.")
        else:
            band_pos = (cur - bb_lower) / (bb_upper - bb_lower) * 100 if bb_upper != bb_lower else 50
            if band_pos > 75:
                bearish.append("볼린저밴드 상단 부근에서 거래되고 있어 단기적으로는 상승 여력이 제한적일 수 있습니다.")
            elif band_pos < 25:
                bullish.append("볼린저밴드 하단 부근에서 거래되고 있어 추가 하락 시 매수 관점의 접근이 유효할 수 있습니다.")

    # ── Prophet 예측 ──────────────────────────────────────
    fc_chg   = forecast.get("change_pct")
    fc_price = forecast.get("predicted_price")
    if fc_chg is not None:
        if fc_chg > 2:
            bullish.append(f"Prophet ML 모델은 30일 후 가격을 {fp(fc_price)}({fc_chg:+.2f}%)로 예측하며, 추가 상승 가능성을 시사합니다.")
        elif fc_chg < -2:
            bearish.append(f"Prophet ML 모델은 30일 후 가격을 {fp(fc_price)}({fc_chg:+.2f}%)로 예측하며, 추가 하락 가능성을 시사합니다.")
        else:
            risks.append(f"Prophet ML 모델은 30일간 {fc_chg:+.2f}% 수준의 변동을 예측해, 뚜렷한 방향성보다는 횡보 가능성을 시사합니다.")

    # ── 기본적 지표 기반 위험 요소 ───────────────────────────
    beta = fund.get("beta")
    if beta is not None and beta > 1.3:
        risks.append(f"베타 값이 {beta}로 시장 평균보다 변동성이 커, 시장 충격 시 가격 변동폭이 더 클 수 있습니다.")

    pe = fund.get("pe_ratio")
    if pe is not None and pe > 35:
        risks.append(f"PER이 {pe}로 비교적 높은 편이라, 실적이 기대에 못 미칠 경우 밸류에이션 조정 압력이 커질 수 있습니다.")
    elif pe is not None and pe < 8 and pe > 0:
        bullish.append(f"PER이 {pe}로 동종업계 대비 저평가되어 있을 가능성이 있습니다.")

    div = fund.get("dividend_yield")
    if div is not None and div > 2:
        bullish.append(f"배당수익률이 {div:.2f}%로 안정적인 현금흐름을 기대할 수 있습니다.")

    # 기본값 (해당 카테고리에 내용이 없을 때)
    if not bullish:
        bullish.append("현재 시점에서 뚜렷한 추가 상승 신호는 관찰되지 않았습니다.")
    if not bearish:
        bearish.append("현재 시점에서 뚜렷한 하락 압력 신호는 관찰되지 않았습니다.")
    if not risks:
        risks.append("현재 두드러진 기술적 위험 신호는 감지되지 않았으나, 시장 전반의 변동성에는 항상 유의해야 합니다.")

    # ── 종합 신호 → 추천 / 의견 문구 ─────────────────────────
    sig_map = {
        "strong_buy":  ("매수", "다수의 기술적 지표가 동시에 강한 상승 신호를 보이고 있어, 현재 구간은 매수 관점에서 접근할 수 있는 시점으로 판단됩니다."),
        "buy":         ("매수", "주요 지표들이 상승 쪽에 다소 무게를 두고 있어, 단기적으로 매수 우위의 흐름이 이어질 가능성이 있습니다."),
        "neutral":     ("관망", "상승 신호와 하락 신호가 혼재되어 있어, 뚜렷한 방향성이 확인되기 전까지는 관망하며 추가 지표 변화를 지켜보는 것이 안전합니다."),
        "sell":        ("매도", "주요 지표들이 하락 쪽에 다소 무게를 두고 있어, 단기적으로는 신규 매수보다 보수적인 접근이 권장됩니다."),
        "strong_sell": ("매도", "다수의 기술적 지표가 동시에 약한 하락 신호를 보이고 있어, 추세 전환이 확인되기 전까지는 매도 또는 관망이 권장됩니다."),
    }
    rec, opinion = sig_map.get(sig, ("관망", ""))

    # ✅ 수정: 신뢰도를 지표 강도(score)에 비례해 동적으로 계산
    # score 범위: 약 -5 ~ +5 → 신뢰도 35% ~ 90%로 변환
    score = _calc_score(rsi, macd, macd_sig, cur, sma20, sma50)
    conf  = min(90, max(35, 50 + abs(score) * 8))

    # 보조 지표(예측 방향, 위험 요소 개수)도 신뢰도에 소폭 반영
    if fc_chg is not None:
        if (score > 0 and fc_chg > 0) or (score < 0 and fc_chg < 0):
            conf = min(90, conf + 4)   # 기술적 신호와 예측 방향 일치 → 신뢰도 ↑
        elif (score > 0 and fc_chg < 0) or (score < 0 and fc_chg > 0):
            conf = max(35, conf - 4)   # 신호와 예측이 반대 → 신뢰도 ↓


    rsi_txt  = f"{rsi:.1f}" if rsi is not None else "N/A"
    macd_txt = ("골든크로스(강세)" if (macd is not None and macd_sig is not None and macd > macd_sig)
                else "데드크로스(약세)" if (macd is not None and macd_sig is not None) else "N/A")

    summary = (
        f"**📊 현재 추세 분석**\n"
        f"현재가는 {fp(cur)}로 전일 대비 {chg:+.2f}% 변동했습니다. "
        f"RSI(14)는 {rsi_txt}, MACD는 {macd_txt} 상태이며, 종합 기술적 신호는 **{sig}** 로 나타났습니다. "
        f"아래 항목들은 계산된 지표를 근거로 자동 생성된 분석입니다.\n\n"

        f"**📈 상승 요인**\n"
        + "\n".join(f"- {b}" for b in bullish) + "\n\n"

        f"**📉 하락 요인**\n"
        + "\n".join(f"- {b}" for b in bearish) + "\n\n"

        f"**⚠️ 위험 요소**\n"
        + "\n".join(f"- {r}" for r in risks) + "\n\n"

        f"**💡 종합 의견**\n"
        f"{opinion}\n\n"
        f"(신뢰도 {conf}%는 RSI·MACD·이동평균(SMA20/50) 등 핵심 기술 지표들이 "
        f"서로 같은 방향을 가리키는 정도를 기준으로 산정되었습니다. "
        f"지표들이 한 방향으로 강하게 모일수록 신뢰도가 높아지고, "
        f"신호가 엇갈릴수록 50% 근처로 수렴합니다.)\n\n"
        f"※ 이 리포트는 기술적 지표를 규칙 기반으로 해석한 자동 분석입니다. "
        f"더 깊은 맥락(뉴스, 산업 동향 등)을 반영한 Claude AI 분석을 받으려면 "
        f".env 파일에 ANTHROPIC_API_KEY를 설정해 주세요."
    )

    return {
        "summary":        summary,
        "recommendation": rec,
        "confidence":     conf,
        "target_price":   fc_price,
    }
