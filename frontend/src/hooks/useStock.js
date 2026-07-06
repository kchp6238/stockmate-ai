import { useState, useCallback } from 'react'
import api from '../utils/api'

export function useStock() {
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState(null)
  const [data,     setData]     = useState(null)
  const [tab,      setTab]      = useState('overview')

  const search = useCallback(async (ticker) => {
    const t = ticker?.trim()
    if (!t) return
    setLoading(true); setError(null); setData(null)
    try {
      // 기본 데이터 먼저 (빠름)
      const basic = await api.get(`/api/stock/${encodeURIComponent(t)}`)
      setData({ ...basic.data, _phase: 'basic' })

      // 관심 종목 최근 기록 추가
      api.post(`/api/recent/${encodeURIComponent(t)}`).catch(() => {})

      // 전체 분석 (느림 - Prophet + AI)
      const full = await api.get(`/api/stock/${encodeURIComponent(t)}/full`)
      setData({ ...full.data, _phase: 'full' })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  return { loading, error, data, tab, setTab, search }
}

export function useWatchlist() {
  const [list,   setList]   = useState([])
  const [recent, setRecent] = useState([])

  const load = useCallback(async () => {
    try {
      const r = await api.get('/api/watchlist')
      setList(r.data.watchlist || [])
      setRecent(r.data.recent  || [])
    } catch {}
  }, [])

  const add = async (t) => {
    await api.post(`/api/watchlist/${t}`)
    await load()
  }
  const remove = async (t) => {
    await api.delete(`/api/watchlist/${t}`)
    await load()
  }

  return { list, recent, load, add, remove }
}

export function useRecommend() {
  const [items,   setItems]   = useState([])
  const [loading, setLoading] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const r = await api.get('/api/recommend')
      setItems(r.data)
    } catch {}
    finally { setLoading(false) }
  }, [])

  return { items, loading, load }
}
