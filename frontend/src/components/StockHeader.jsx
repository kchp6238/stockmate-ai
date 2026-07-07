import { Star, TrendingUp, TrendingDown, Target } from 'lucide-react'
import { fmt } from '../utils/format'

export default function StockHeader({ data, inWatchlist, onToggleWatchlist }) {
  const p      = data.price
  const sig    = fmt.signal(data.indicators?.overall_signal)
  const isUp   = p.change_pct >= 0
  const cur    = data.currency || 'USD'

  // 예측 데이터
  const fc = data.forecast || {}
  const hasForecast = fc.predicted_price != null && fc.change_pct != null
  const fcUp = fc.change_pct >= 0

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

      {/* 예측 가격 배너 */}
      {hasForecast && (
        <div className={`mt-4 p-4 rounded-xl border ${fcUp
          ? 'bg-green/5 border-green/20'
          : 'bg-red/5 border-red/20'}`}>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Target className={`w-5 h-5 ${fcUp ? 'text-green' : 'text-red'}`} />
              <span className="text-sm font-display text-dim">30일 AI 예측 목표가</span>
            </div>
            <div className="flex items-center gap-4">
              <span className={`font-display text-2xl font-bold ${fcUp ? 'text-green' : 'text-red'}`}>
                {fmt.price(fc.predicted_price, cur)}
              </span>
              <span className={`font-mono text-sm font-semibold px-3 py-1 rounded-lg ${fcUp
                ? 'bg-green/10 text-green'
                : 'bg-red/10 text-red'}`}>
                {fcUp ? '▲' : '▼'} {fc.change_pct > 0 ? '+' : ''}{fc.change_pct?.toFixed(2)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 하단: 지표 바 + 신호 + 즐겨찾기 */}
      <div className="mt-4 pt-4 border-t border-border flex flex-wrap items-center gap-4">
        <span className={sig.cls}>{sig.label}</span>

        <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-dim">
          <span>시가총액 <b className="text-text">{fmt.cap(p.market_cap, cur)}</b></span>
          <span>거래량 <b className="text-text">{fmt.num(p.volume)}</b></span>
          <span>52주 고 <b className="text-green">{fmt.price(p.high_52w, cur)}</b></span>
          <span>52주 저 <b className="text-red">{fmt.price(p.low_52w, cur)}</b></span>
          {data.fundamentals?.pe_ratio && (
            <span>PER <b className="text-text">{data.fundamentals.pe_ratio}</b></span>
          )}
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
