import { useState } from 'react'
import { Search, Star, Clock } from 'lucide-react'

const US_POPULAR  = ['AAPL','NVDA','TSLA','MSFT','GOOGL','AMZN','META','JPM']
const KR_POPULAR  = ['삼성전자','SK하이닉스','현대차','카카오','NAVER','LG에너지솔루션']

export default function SearchBar({ onSearch, watchlist = [], recent = [] }) {
  const [val, setVal] = useState('')

  function submit(t) {
    const v = t || val
    if (!v.trim()) return
    setVal(v)
    onSearch(v.trim())
  }

  return (
    <div className="space-y-4">
      {/* 검색창 */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dim" />
          <input
            value={val}
            onChange={e => setVal(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === 'Enter' && submit()}
            placeholder="종목 코드 또는 이름 입력  (예: AAPL, 삼성전자)"
            className="w-full pl-11 pr-4 py-3 bg-surface border border-border rounded-xl
                       text-bright placeholder:text-dim focus:outline-none focus:border-accent
                       font-mono text-sm transition-colors"
          />
        </div>
        <button onClick={() => submit()} className="btn-primary px-8">
          분석
        </button>
      </div>

      {/* 빠른 선택 - 미국 */}
      <div>
        <p className="text-xs text-dim mb-2 font-display">🇺🇸 미국 주식</p>
        <div className="flex flex-wrap gap-2">
          {US_POPULAR.map(t => (
            <button key={t} onClick={() => submit(t)}
              className="px-3 py-1.5 bg-surface border border-border hover:border-accent
                         hover:text-accent text-text text-xs rounded-lg transition-all font-mono">
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* 빠른 선택 - 한국 */}
      <div>
        <p className="text-xs text-dim mb-2 font-display">🇰🇷 한국 주식</p>
        <div className="flex flex-wrap gap-2">
          {KR_POPULAR.map(t => (
            <button key={t} onClick={() => submit(t)}
              className="px-3 py-1.5 bg-surface border border-border hover:border-accent
                         hover:text-accent text-text text-xs rounded-lg transition-all">
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* 최근 조회 / 관심 종목 */}
      {(recent.length > 0 || watchlist.length > 0) && (
        <div className="flex gap-6">
          {recent.length > 0 && (
            <div>
              <p className="text-xs text-dim mb-2 flex items-center gap-1">
                <Clock className="w-3 h-3" /> 최근 조회
              </p>
              <div className="flex flex-wrap gap-2">
                {recent.slice(0, 5).map(t => (
                  <button key={t} onClick={() => submit(t)}
                    className="px-3 py-1 text-xs text-dim hover:text-accent border border-border
                               hover:border-accent rounded-lg transition-all font-mono">
                    {t}
                  </button>
                ))}
              </div>
            </div>
          )}
          {watchlist.length > 0 && (
            <div>
              <p className="text-xs text-dim mb-2 flex items-center gap-1">
                <Star className="w-3 h-3 fill-amber text-amber" /> 관심 종목
              </p>
              <div className="flex flex-wrap gap-2">
                {watchlist.map(t => (
                  <button key={t} onClick={() => submit(t)}
                    className="px-3 py-1 text-xs text-amber border border-amber/20
                               hover:border-amber/50 rounded-lg transition-all font-mono">
                    {t}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
