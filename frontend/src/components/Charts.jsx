import {
  ComposedChart, LineChart, BarChart,
  Line, Bar, Area, XAxis, YAxis, Tooltip,
  CartesianGrid, ResponsiveContainer, ReferenceLine, Legend
} from 'recharts'
import { useState } from 'react'

const TOOLTIP_STYLE = {
  contentStyle: { background: '#0D1320', border: '1px solid #1A2332', borderRadius: 8, fontSize: 12 },
  labelStyle:   { color: '#4A6080' },
}

function ChartCard({ title, children }) {
  return (
    <div className="card">
      <h4 className="font-display font-semibold text-text mb-4 text-sm">{title}</h4>
      {children}
    </div>
  )
}

/* ── 가격 + 볼린저 + SMA ─────────────────────────────── */
export function PriceChart({ history }) {
  if (!history?.length) return null
  return (
    <ChartCard title="📈 가격 차트  (SMA20 · SMA50 · 볼린저 밴드)">
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={history} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1A2332" />
          <XAxis dataKey="date" tick={{ fill: '#4A6080', fontSize: 10 }}
                 interval={Math.floor(history.length / 6)} />
          <YAxis tick={{ fill: '#4A6080', fontSize: 10 }}
                 domain={['auto', 'auto']} tickFormatter={v => `$${v}`} width={60} />
          <Tooltip {...TOOLTIP_STYLE}
            formatter={(v, n) => [`$${Number(v).toFixed(2)}`,
              { close:'종가', sma20:'SMA20', sma50:'SMA50', bb_upper:'BB상단', bb_lower:'BB하단' }[n] || n]} />
          <Legend wrapperStyle={{ fontSize: 11, color: '#4A6080' }}
            formatter={n => ({ close:'종가', sma20:'SMA20', sma50:'SMA50', bb_upper:'BB상단', bb_lower:'BB하단' }[n] || n)} />

          {/* 볼린저 밴드 영역 */}
          <Area type="monotone" dataKey="bb_upper" stroke="#3B82F6" strokeWidth={0.8}
                fill="#3B82F6" fillOpacity={0.04} dot={false} legendType="none" />
          <Area type="monotone" dataKey="bb_lower" stroke="#3B82F6" strokeWidth={0.8}
                fill="#0D1320" fillOpacity={1}   dot={false} legendType="none" />

          {/* 이동평균 */}
          <Line type="monotone" dataKey="sma20" stroke="#F59E0B" strokeWidth={1.2} dot={false} connectNulls />
          <Line type="monotone" dataKey="sma50" stroke="#8B5CF6" strokeWidth={1.2} dot={false} connectNulls />

          {/* 가격 */}
          <Line type="monotone" dataKey="close" stroke="#3B82F6" strokeWidth={2} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}

/* ── 거래량 차트 ────────────────────────────────────── */
export function VolumeChart({ history }) {
  if (!history?.length) return null
  return (
    <ChartCard title="📊 거래량 차트">
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={history} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1A2332" />
          <XAxis dataKey="date" tick={{ fill: '#4A6080', fontSize: 10 }}
                 interval={Math.floor(history.length / 6)} />
          <YAxis tick={{ fill: '#4A6080', fontSize: 10 }}
                 tickFormatter={v => `${(v / 1e6).toFixed(0)}M`} width={50} />
          <Tooltip {...TOOLTIP_STYLE}
            formatter={v => [(v / 1e6).toFixed(2) + 'M', '거래량']} />
          <Bar dataKey="volume" fill="#2A3A52" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}

/* ── RSI 차트 ───────────────────────────────────────── */
export function RsiChart({ history }) {
  if (!history?.length) return null
  return (
    <ChartCard title="📉 RSI (14)">
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={history} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1A2332" />
          <XAxis dataKey="date" tick={{ fill: '#4A6080', fontSize: 10 }}
                 interval={Math.floor(history.length / 6)} />
          <YAxis domain={[0, 100]} tick={{ fill: '#4A6080', fontSize: 10 }} width={35} />
          <Tooltip {...TOOLTIP_STYLE} formatter={v => [v?.toFixed(1), 'RSI']} />
          <ReferenceLine y={70} stroke="#EF4444" strokeDasharray="4 2" label={{ value:'70', fill:'#EF4444', fontSize:10, position:'right' }} />
          <ReferenceLine y={30} stroke="#10B981" strokeDasharray="4 2" label={{ value:'30', fill:'#10B981', fontSize:10, position:'right' }} />
          <Line type="monotone" dataKey="rsi" stroke="#8B5CF6"
                strokeWidth={2} dot={false} connectNulls />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}

/* ── MACD 차트 ──────────────────────────────────────── */
export function MacdChart({ history }) {
  if (!history?.length) return null
  const colored = history.map(d => ({
    ...d,
    macd_hist_pos: d.macd_hist >= 0 ? d.macd_hist : 0,
    macd_hist_neg: d.macd_hist <  0 ? d.macd_hist : 0,
  }))
  return (
    <ChartCard title="📊 MACD">
      <ResponsiveContainer width="100%" height={200}>
        <ComposedChart data={colored} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1A2332" />
          <XAxis dataKey="date" tick={{ fill: '#4A6080', fontSize: 10 }}
                 interval={Math.floor(history.length / 6)} />
          <YAxis tick={{ fill: '#4A6080', fontSize: 10 }} width={50} />
          <Tooltip {...TOOLTIP_STYLE}
            formatter={(v, n) => [v?.toFixed(3), { macd:'MACD', macd_signal:'Signal', macd_hist_pos:'양봉', macd_hist_neg:'음봉' }[n] || n]} />
          <ReferenceLine y={0} stroke="#2A3A52" />
          <Bar dataKey="macd_hist_pos" fill="#10B981" radius={[1,1,0,0]} />
          <Bar dataKey="macd_hist_neg" fill="#EF4444" radius={[1,1,0,0]} />
          <Line type="monotone" dataKey="macd"        stroke="#3B82F6" strokeWidth={1.5} dot={false} connectNulls />
          <Line type="monotone" dataKey="macd_signal" stroke="#F59E0B" strokeWidth={1.5} dot={false} connectNulls />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}

/* ── 예측 차트 ──────────────────────────────────────── */
export function ForecastChart({ forecast, currentPrice }) {
  if (!forecast?.length) return null
  const isUp = forecast[forecast.length - 1]?.predicted > currentPrice

  return (
    <ChartCard title="🔮 30일 예측 (Prophet ML)  · 음영: 80% 신뢰구간">
      <div className="text-xs text-dim mb-3">
        현재가 <span className="text-text font-mono">${currentPrice}</span>
        &nbsp;→&nbsp; 예측가&nbsp;
        <span className={`font-mono font-semibold ${isUp ? 'text-green' : 'text-red'}`}>
          ${forecast[forecast.length - 1]?.predicted?.toFixed(2)}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={forecast} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="fcGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor={isUp ? '#10B981' : '#EF4444'} stopOpacity={0.15} />
              <stop offset="95%" stopColor={isUp ? '#10B981' : '#EF4444'} stopOpacity={0.01} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1A2332" />
          <XAxis dataKey="date" tick={{ fill: '#4A6080', fontSize: 10 }}
                 interval={Math.floor(forecast.length / 5)} />
          <YAxis tick={{ fill: '#4A6080', fontSize: 10 }}
                 domain={['auto', 'auto']} tickFormatter={v => `$${v}`} width={60} />
          <Tooltip {...TOOLTIP_STYLE}
            formatter={(v, n) => [`$${Number(v).toFixed(2)}`,
              { predicted:'예측가', upper:'신뢰 상단', lower:'신뢰 하단' }[n] || n]} />
          <ReferenceLine y={currentPrice} stroke="#4A6080" strokeDasharray="4 4" />
          <Area type="monotone" dataKey="upper" stroke="none" fill="url(#fcGrad)" />
          <Area type="monotone" dataKey="lower" stroke="none" fill="#080C14" />
          <Line type="monotone" dataKey="predicted"
                stroke={isUp ? '#10B981' : '#EF4444'} strokeWidth={2.5} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}
