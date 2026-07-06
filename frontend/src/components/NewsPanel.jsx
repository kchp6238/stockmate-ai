import { ExternalLink, Shield } from 'lucide-react'

export default function NewsPanel({ news, loading }) {
  if (loading) return (
    <div className="card space-y-3">
      <div className="h-4 w-32 bg-muted rounded animate-pulse" />
      {[1,2,3].map(i => (
        <div key={i} className="animate-pulse space-y-1">
          <div className="h-3 bg-muted rounded w-3/4" />
          <div className="h-3 bg-muted rounded w-1/2" />
        </div>
      ))}
    </div>
  )

  if (!news?.length) return (
    <div className="card text-center text-dim text-sm py-8">뉴스 데이터가 없습니다.</div>
  )

  return (
    <div className="card animate-fadeUp">
      <h3 className="font-display font-semibold text-bright mb-4">📰 관련 뉴스</h3>
      <div className="space-y-4">
        {news.map((item, i) => (
          <a key={i} href={item.url} target="_blank" rel="noopener noreferrer"
             className="block group border-b border-border pb-4 last:border-0 last:pb-0 hover:border-accent/30 transition-colors">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <p className="text-text text-sm group-hover:text-bright transition-colors line-clamp-2 mb-1.5">
                  {item.title}
                </p>
                {item.summary && (
                  <p className="text-dim text-xs line-clamp-2 mb-2">{item.summary}</p>
                )}
                <div className="flex items-center gap-2 text-xs text-dim">
                  {item.trusted && (
                    <span className="flex items-center gap-1 text-green">
                      <Shield className="w-3 h-3" /> 신뢰 언론
                    </span>
                  )}
                  <span className="font-semibold text-dim">{item.source}</span>
                  {item.published && <span>· {item.published}</span>}
                </div>
              </div>
              <ExternalLink className="w-4 h-4 text-dim flex-shrink-0 mt-0.5
                                       group-hover:text-accent transition-colors" />
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
