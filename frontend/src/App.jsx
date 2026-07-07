import { useEffect } from 'react'
import { BarChart2, Loader2, AlertCircle } from 'lucide-react'
import SearchBar        from './components/SearchBar.jsx'
import StockHeader      from './components/StockHeader.jsx'
import FundamentalsGrid from './components/FundamentalsGrid.jsx'
import { PriceChart, VolumeChart, RsiChart, MacdChart, ForecastChart } from './components/Charts.jsx'
import AIReport         from './components/AIReport.jsx'
import NewsPanel        from './components/NewsPanel.jsx'
import RecommendPanel   from './components/RecommendPanel.jsx'
import { useStock, useWatchlist } from './hooks/useStock.js'

const TABS = [
  { id: 'overview',  label: '📊 개요' },
  { id: 'charts',    label: '📈 차트' },
  { id: 'ai',        label: '🤖 AI 분석' },
  { id: 'news',      label: '📰 뉴스' },
  { id: 'recommend', label: '🏆 추천' },
]

export default function App() {
  const { loading, error, data, tab, setTab, search } = useStock()
  const { list, recent, load: loadWL, add, remove }   = useWatchlist()

  useEffect(() => { loadWL() }, [loadWL])
const handleSearch = async (ticker) => {
    await search(ticker)
    loadWL()
  }
  const inWatchlist = list.includes(data?.ticker || '')
  const toggleWL    = () => (inWatchlist ? remove : add)(data?.ticker)

  const isFullLoaded = data?._phase === 'full'

  return (
    <div className="min-h-screen bg-bg font-body">

      {/* ── 헤더 ───────────────────────────────────────── */}
      <header className="border-b border-border sticky top-0 z-50 bg-bg/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-accent" />
            <span className="font-display font-bold text-bright tracking-tight">StockAI</span>
            <span className="text-xs text-dim border border-border px-2 py-0.5 rounded ml-1">Beta</span>
          </div>
          <span className="text-xs text-dim hidden sm:block">
            미국·한국 주식 AI 분석 플랫폼
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-6">

        {/* ── 검색 ───────────────────────────────────────── */}
        <section className="card animate-fadeUp">
         <SearchBar onSearch={handleSearch} watchlist={list} recent={recent} />
        </section>

        {/* ── 에러 ───────────────────────────────────────── */}
        {error && (
          <div className="flex items-center gap-3 bg-red/10 border border-red/20 rounded-xl px-5 py-4 text-red animate-fadeUp">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* ── 로딩 ───────────────────────────────────────── */}
        {loading && !data && (
          <div className="card text-center py-20 animate-fadeUp">
            <Loader2 className="w-10 h-10 text-accent mx-auto mb-4 animate-spin" />
            <p className="text-text font-display">데이터 수집 중...</p>
            <p className="text-dim text-sm mt-2">기술적 지표 → Prophet 예측 → Claude AI 분석</p>
            <p className="text-muted text-xs mt-1">약 20~40초 소요됩니다</p>
          </div>
        )}

        {/* ── 결과 ───────────────────────────────────────── */}
        {data && (
          <>
            {/* 종목 헤더 */}
            <StockHeader data={data} inWatchlist={inWatchlist} onToggleWatchlist={toggleWL} />

            {/* 탭 네비게이션 */}
            <div className="flex gap-1 border-b border-border overflow-x-auto">
              {TABS.map(t => (
                <button key={t.id} onClick={() => setTab(t.id)}
                  className={`px-4 py-2.5 text-sm font-display whitespace-nowrap transition-colors
                    ${tab === t.id ? 'tab-active' : 'tab-inactive'}`}>
                  {t.label}
                </button>
              ))}
            </div>

            {/* ── 개요 탭 ──────────────────────────────── */}
            {tab === 'overview' && (
              <div className="space-y-5">
                <FundamentalsGrid
                  price={data.price} fundamentals={data.fundamentals}
                  indicators={data.indicators} currency={data.currency} />
                <PriceChart history={data.history} currency={data.currency} />
                {/* 기본 로드 후 AI 요약도 보여줌 */}
                {isFullLoaded && data.analysis && (
                  <AIReport analysis={data.analysis} />
                )}
                {loading && !isFullLoaded && (
                  <AIReport loading={true} />
                )}
              </div>
            )}

            {/* ── 차트 탭 ──────────────────────────────── */}
            {tab === 'charts' && (
              <div className="space-y-5">
                <PriceChart    history={data.history} currency={data.currency} />
                <VolumeChart   history={data.history} currency={data.currency} />
                <RsiChart      history={data.history} currency={data.currency} />
                <MacdChart     history={data.history} currency={data.currency} />
                {isFullLoaded && data.forecast?.forecast?.length > 0 && (
                  <ForecastChart
                    forecast={data.forecast.forecast}
                    currentPrice={data.forecast.current_price}
                    currency={data.currency} />
                )}
                {loading && !isFullLoaded && (
                  <div className="card text-center py-8 text-dim text-sm">
                    <Loader2 className="w-6 h-6 mx-auto mb-2 animate-spin text-accent" />
                    Prophet 예측 계산 중...
                  </div>
                )}
              </div>
            )}

            {/* ── AI 분석 탭 ───────────────────────────── */}
            {tab === 'ai' && (
              <AIReport analysis={isFullLoaded ? data.analysis : null} loading={loading && !isFullLoaded} />
            )}

            {/* ── 뉴스 탭 ──────────────────────────────── */}
            {tab === 'news' && (
              <NewsPanel news={isFullLoaded ? data.news : null} loading={loading && !isFullLoaded} />
            )}

            {/* ── 추천 탭 ──────────────────────────────── */}
            {tab === 'recommend' && (
              <RecommendPanel onSelect={t => { search(t); setTab('overview') }} />
            )}
          </>
        )}

        {/* ── 초기 화면: 추천 종목 ─────────────────────── */}
        {!data && !loading && !error && (
          <RecommendPanel onSelect={search} />
        )}

      </main>

      {/* ── 푸터 ───────────────────────────────────────── */}
      <footer className="border-t border-border mt-16 py-6 text-center text-xs text-muted">
        StockAI · 데이터 출처: Yahoo Finance · AI: Claude · 본 서비스는 투자 권유가 아닙니다
      </footer>
    </div>
  )
}
