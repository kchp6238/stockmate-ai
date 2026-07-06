const CUR_SYMBOL = { KRW: '₩', USD: '$', JPY: '¥', EUR: '€' }

export const fmt = {
  price: (v, cur = 'USD') => {
    if (v == null) return 'N/A'
    const sym = CUR_SYMBOL[cur] || '$'
    return `${sym}${Number(v).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  },
  pct: (v) => v == null ? 'N/A' : `${v > 0 ? '+' : ''}${Number(v).toFixed(2)}%`,
  num: (v) => v == null ? 'N/A' : Number(v).toLocaleString(),

  // ✅ 수정: 통화에 맞는 기호 사용 ($ / ₩ 등)
  cap: (v, cur = 'USD') => {
    if (v == null) return 'N/A'
    const sym = CUR_SYMBOL[cur] || '$'
    if (v >= 1e12) return `${sym}${(v / 1e12).toFixed(2)}T`
    if (v >= 1e9)  return `${sym}${(v / 1e9).toFixed(2)}B`
    if (v >= 1e6)  return `${sym}${(v / 1e6).toFixed(2)}M`
    return `${sym}${v.toLocaleString()}`
  },

  // ✅ 추가: 배당수익률 - yfinance 1.x는 이미 % 단위 값을 반환함 (예: 0.58 → 0.58%)
  // 0~100 사이 숫자를 그대로 %로 표시 (기존처럼 *100 하지 않음)
  divYield: (v) => {
    if (v == null) return 'N/A'
    return `${Number(v).toFixed(2)}%`
  },

  signal: (s) => ({
    strong_buy:  { label: '강력 매수', cls: 'tag-buy',     dot: 'bg-green'  },
    buy:         { label: '매수',      cls: 'tag-buy',     dot: 'bg-green'  },
    neutral:     { label: '중립',      cls: 'tag-neutral', dot: 'bg-dim'    },
    sell:        { label: '매도',      cls: 'tag-sell',    dot: 'bg-red'    },
    strong_sell: { label: '강력 매도', cls: 'tag-sell',    dot: 'bg-red'    },
  }[s] || { label: s, cls: 'tag-neutral', dot: 'bg-dim' }),
}
