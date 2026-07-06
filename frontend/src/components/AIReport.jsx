export default function AIReport({ analysis, loading }) {
  if (loading) return (
    <div className="card animate-pulse">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-6 h-6 rounded-full bg-muted" />
        <div className="h-4 w-40 bg-muted rounded" />
      </div>
      {[1,2,3,4].map(i => <div key={i} className={`h-3 bg-muted rounded mb-2 ${i===4?'w-1/2':''}`} />)}
    </div>
  )
  if (!analysis) return null

  const REC_COLOR = { '매수': 'text-green bg-green/10 border-green/20',
                      '매도': 'text-red   bg-red/10   border-red/20',
                      '관망': 'text-amber bg-amber/10 border-amber/20' }
  const recStyle = REC_COLOR[analysis.recommendation] || 'text-dim bg-muted border-border'

  // 마크다운 → 렌더링
  function renderLine(line, i) {
    const isH    = /^\*\*[^*]+\*\*$/.test(line.trim()) || /^#{1,3}\s/.test(line)
    const isBull = /^[-*]\s/.test(line)
    const clean  = line.replace(/^#{1,3}\s*/, '').replace(/^[-*]\s/, '')

    const parts = clean.split(/(\*\*[^*]+\*\*)/g).map((p, j) =>
      p.startsWith('**') && p.endsWith('**')
        ? <strong key={j} className="text-bright font-semibold">{p.slice(2,-2)}</strong>
        : p
    )

    return (
      <div key={i} className={`leading-relaxed ${
        isH   ? 'text-text font-semibold text-sm mt-4 mb-1' :
        isBull? 'text-dim text-sm pl-4 before:content-["•"] before:mr-2 before:text-accent' :
                'text-dim text-sm'
      }`}>
        {parts}
      </div>
    )
  }

  const lines = (analysis.summary || '').split('\n').filter(l => l.trim())

  return (
    <div className="card animate-fadeUp">
      {/* 헤더 */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <h3 className="font-display font-semibold text-bright">🤖 AI 분석 리포트</h3>
        <span className={`border text-xs font-semibold px-3 py-1 rounded-full ${recStyle}`}>
          {analysis.recommendation}
        </span>
        {analysis.target_price && (
          <span className="text-xs text-dim">
            목표가 <span className="text-text font-mono">${analysis.target_price}</span>
          </span>
        )}
        <span className="ml-auto text-xs text-dim">
          신뢰도 <span className="text-text font-mono">{analysis.confidence}%</span>
        </span>
      </div>

      {/* 신뢰도 바 */}
      <div className="h-1 bg-muted rounded mb-5 overflow-hidden">
        <div className="h-full rounded transition-all duration-700"
             style={{
               width: `${analysis.confidence}%`,
               background: analysis.recommendation === '매수' ? '#10B981'
                         : analysis.recommendation === '매도' ? '#EF4444' : '#F59E0B'
             }} />
      </div>

      {/* 분석 내용 */}
      <div className="space-y-0.5">{lines.map(renderLine)}</div>

      <p className="mt-5 text-xs text-muted border-t border-border pt-4">
        ※ 본 분석은 AI가 생성한 참고 자료이며 투자 권유가 아닙니다. 투자 결정은 본인 책임하에 이루어져야 합니다.
      </p>
    </div>
  )
}
