const CUR_SYMBOL = { KRW: '₩', USD: '$', JPY: '¥', EUR: '€' }

export const fmt = {
  price: (v, cur = 'USD') => {
    if (v == null) return 'N/A'
    const sym = CUR_SYMBOL[cur] || '$'
    const digits = (cur === 'KRW' || cur === 'JPY') ? 0 : 2
    return `${sym}${Number(v).toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits })}`
  },
  pct: (v) => v == null ? 'N/A' : `${v > 0 ? '+' : ''}${Number(v).toFixed(2)}%`,
  num: (v) => v == null ? 'N/A' : Number(v).toLocaleString(),

  cap: (v, cur = 'USD') => {
    if (v == null) return 'N/A'
    const sym = CUR_SYMBOL[cur] || '$'
    if (v >= 1e12) return `${sym}${(v / 1e12).toFixed(2)}T`
    if (v >= 1e9)  return `${sym}${(v / 1e9).toFixed(2)}B`
    if (v >= 1e6)  return `${sym}${(v / 1e6).toFixed(2)}M`
    return `${sym}${v.toLocaleString()}`
  },

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
