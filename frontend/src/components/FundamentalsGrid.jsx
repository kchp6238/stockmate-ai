import { fmt } from '../utils/format'

function Cell({ label, value, color }) {
  return (
    <div className="bg-bg border border-border rounded-lg p-3">
      <p className="text-xs text-dim mb-1">{label}</p>
      <p className={`font-mono font-semibold text-sm ${color || 'text-bright'}`}>{value}</p>
    </div>
  )
}

export default function FundamentalsGrid({ price, fundamentals, indicators, currency = 'USD' }) {
  const f = fundamentals || {}
  const p = price || {}
  const i = indicators || {}

  return (
    <div className="card animate-fadeUp">
      <h3 className="font-display font-semibold text-bright mb-4">기본 정보</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
        <Cell label="현재가"       value={fmt.price(p.current, currency)} />
        <Cell label="시가"         value={fmt.price(p.open, currency)} />
        <Cell label="고가"         value={fmt.price(p.high, currency)} color="text-green" />
        <Cell label="저가"         value={fmt.price(p.low, currency)}  color="text-red" />
        <Cell label="52주 최고"    value={fmt.price(p.high_52w, currency)} color="text-green" />
        <Cell label="52주 최저"    value={fmt.price(p.low_52w, currency)}  color="text-red" />
        <Cell label="시가총액"     value={fmt.cap(p.market_cap, currency)} />
        <Cell label="거래량"       value={fmt.num(p.volume)} />
        <Cell label="평균 거래량"  value={fmt.num(p.avg_volume)} />
        <Cell label="PER (후행)"   value={f.pe_ratio ?? 'N/A'} />
        <Cell label="PER (선행)"   value={f.forward_pe ?? 'N/A'} />
        <Cell label="PBR"          value={f.pb_ratio ?? 'N/A'} />
        <Cell label="EPS"          value={f.eps ?? 'N/A'} />
        {/* ✅ 수정: yfinance 1.x는 배당률을 이미 % 단위로 반환 (×100 제거) */}
        <Cell label="배당수익률"   value={fmt.divYield(f.dividend_yield)} color="text-amber" />
        <Cell label="베타"         value={f.beta ?? 'N/A'} />
        <Cell label="ROE"          value={f.roe ? `${(f.roe * 100).toFixed(1)}%` : 'N/A'} />
        <Cell label="RSI (14)"     value={i.rsi?.toFixed(1) ?? 'N/A'}
              color={i.rsi < 30 ? 'text-green' : i.rsi > 70 ? 'text-red' : 'text-text'} />
        <Cell label="MACD"         value={i.macd?.toFixed(3) ?? 'N/A'}
              color={i.macd > i.macd_signal ? 'text-green' : 'text-red'} />
        <Cell label="SMA 20"       value={fmt.price(i.sma20, currency)} />
        <Cell label="SMA 50"       value={fmt.price(i.sma50, currency)} />
      </div>
    </div>
  )
}
