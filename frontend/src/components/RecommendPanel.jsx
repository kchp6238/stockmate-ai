import { useEffect } from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { useRecommend } from '../hooks/useStock'
import { fmt } from '../utils/format'

export default function RecommendPanel({ onSelect }) {
  const { items, loading, load } = useRecommend()
  useEffect(() => { load() }, [load])

  const RISK_COLOR = { '낮음':'text-green', '중간':'text-amber', '높음':'text-red',
                       '높음 (과매수)':'text-red', '높음 (매도 신호)':'text-red' }

  if (loading) return (
    <div className="card">
      <div className="h-5 w-40 bg-muted rounded mb-4 animate-pulse" />
      {[...Array(5)].map((_,i) => (
        <div key={i} className="flex gap-3 mb-3 animate-pulse">
          <div className="w-8 h-8 bg-muted rounded" />
          <div className="flex-1 space-y-1">
            <div className="h-3 bg-muted rounded w-1/3" />
            <div className="h-3 bg-muted rounded w-2/3" />
          </div>
        </div>
      ))}
    </div>
  )

  return (
    <div className="card animate-fadeUp">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display font-semibold text-bright">🏆 AI 추천 종목 TOP 10</h3>
        <button onClick={load} className="text-xs text-dim hover:text-accent transition-colors">새로고침</button>
      </div>

      <div className="space-y-2">
        {items.map((item, i) => {
          const sig = fmt.signal(item.signal)
          const isUp = item.change_pct >= 0

          return (
            <button key={item.ticker} onClick={() => onSelect(item.ticker)}
              className="w-full flex items-center gap-3 p-3 rounded-lg border border-border
                         hover:border-accent/40 hover:bg-surface/60 transition-all text-left group">

              {/* 순위 */}
              <div className="w-6 text-center font-display text-xs font-bold text-dim group-hover:text-accent">
                {i + 1}
              </div>

              {/* 점수 */}
              <div className="relative w-8 h-8 flex-shrink-0">
                <svg viewBox="0 0 36 36" className="w-8 h-8 -rotate-90">
                  <circle cx="18" cy="18" r="14" fill="none" stroke="#1A2332" strokeWidth="3" />
                  <circle cx="18" cy="18" r="14" fill="none"
                    stroke={item.score >= 70 ? '#10B981' : item.score >= 50 ? '#F59E0B' : '#EF4444'}
                    strokeWidth="3" strokeDasharray={`${item.score * 0.879} 100`} strokeLinecap="round" />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center font-mono text-[9px] text-bright">
                  {item.score}
                </span>
              </div>

              {/* 종목 정보 */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="font-mono font-semibold text-bright text-sm">{item.ticker}</span>
                  <span className={sig.cls + ' py-0 text-[10px]'}>{sig.label}</span>
                </div>
                <p className="text-xs text-dim truncate">{item.reason}</p>
              </div>

              {/* 가격·변동 */}
              <div className="text-right flex-shrink-0">
                <div className="font-mono text-sm text-text">${item.price?.toFixed(2)}</div>
                <div className={`flex items-center justify-end gap-0.5 text-xs font-mono ${isUp ? 'text-green' : 'text-red'}`}>
                  {isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  {fmt.pct(item.change_pct)}
                </div>
              </div>

              {/* 리스크 */}
              <div className={`text-right flex-shrink-0 text-xs ${RISK_COLOR[item.risk] || 'text-dim'}`}>
                <div>위험</div>
                <div className="font-semibold">{item.risk?.replace(' (과매수)', '').replace(' (매도 신호)', '')}</div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
