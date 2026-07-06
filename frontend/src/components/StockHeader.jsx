import { Star, TrendingUp, TrendingDown } from 'lucide-react'
import { fmt } from '../utils/format'

export default function StockHeader({ data, inWatchlist, onToggleWatchlist }) {
  const p      = data.price
  const sig    = fmt.signal(data.indicators?.overall_signal)
  const isUp   = p.change_pct >= 0
  const cur    = data.currency || 'USD'

  return (
    <div className="card animate-fadeUp">
      <div className="flex flex-wrap items-start justify-between gap-4">
        {/* 왼쪽: 종목명 + 신호 */}
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h2 className="font-display text-2xl font-bold text-bright">{data.company_name}</h2>
            <span className="font-mono text-dim text-sm bg-muted px-2 py-0.5 rounded">{data.ticker}</span>
            {data.cached && (
              <span className="text-xs text-dim border border-border px-2 py-0.5 rounded">캐시</span>
            )}
          </div>
          <div className="flex items-center gap-2 text-sm text-dim">
            <span>{data.sector}</span>
            {data.sector && data.industry && <span>·</span>}
            <span>{data.industry}</span>
          </div>
        </div>

        {/* 오른쪽: 가격 */}
        <div className="text-right">
          <div className="font-display text-3xl font-bold text-bright mb-1">
            {fmt.price(p.current, cur)}
          </div>
          <div className={`flex items-center justify-end gap-1 font-mono text-sm font-semibold
                           ${isUp ? 'text-green' : 'text-red'}`}>
            {isUp ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            {fmt.pct(p.change_pct)}
            <span className="text-dim font-normal ml-1">({fmt.price(p.change, cur)})</span>
          </div>
        </div>
      </div>

      {/* 하단: 지표 바 + 신호 + 즐겨찾기 */}
      <div className="mt-4 pt-4 border-t border-border flex flex-wrap items-center gap-4">
        <span className={sig.cls}>{sig.label}</span>

        <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-dim">
          {/* ✅ 수정: 시가총액에 통화(cur) 전달 — KRW 종목은 ₩ 표시 */}
          <span>시가총액 <b className="text-text">{fmt.cap(p.market_cap, cur)}</b></span>
          <span>거래량 <b className="text-text">{fmt.num(p.volume)}</b></span>
          <span>52주 고 <b className="text-green">{fmt.price(p.high_52w, cur)}</b></span>
          <span>52주 저 <b className="text-red">{fmt.price(p.low_52w, cur)}</b></span>
          {data.fundamentals?.pe_ratio && (
            <span>PER <b className="text-text">{data.fundamentals.pe_ratio}</b></span>
          )}
          {/* ✅ 수정: yfinance 1.x는 배당률을 이미 % 단위로 반환 (×100 제거) */}
          {data.fundamentals?.dividend_yield != null && (
            <span>배당 <b className="text-amber">{fmt.divYield(data.fundamentals.dividend_yield)}</b></span>
          )}
        </div>

        <button onClick={onToggleWatchlist}
          className="ml-auto flex items-center gap-1.5 text-xs text-dim hover:text-amber transition-colors">
          <Star className={`w-4 h-4 ${inWatchlist ? 'fill-amber text-amber' : ''}`} />
          {inWatchlist ? '관심 종목 해제' : '관심 종목 추가'}
        </button>
      </div>
    </div>
  )
}
