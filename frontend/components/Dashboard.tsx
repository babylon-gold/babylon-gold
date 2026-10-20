'use client'

import { Analysis } from '@/lib/api'
import CandlestickChart from '@/components/CandlestickChart'
import IndicatorPanel from '@/components/IndicatorPanel'

interface DashboardProps {
  analysis: Analysis
  timeframe: string
}

export default function Dashboard({ analysis, timeframe }: DashboardProps) {
  if (!analysis) return null

  return (
    <div className="space-y-6">
      {/* Price Display */}
      <div className="card">
        <div className="p-6">
          <div className="flex items-end justify-between mb-4">
            <div>
              <p className="text-slate-400 text-sm mb-1">السعر الحالي - XAU/USD</p>
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-bold text-gold-400">
                  ${analysis.current_price.toFixed(2)}
                </span>
                <span className="text-slate-400 text-lg">/أونصة</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-slate-400 text-sm mb-1">الإطار الزمني</p>
              <p className="text-2xl font-semibold text-slate-100">{timeframe}</p>
            </div>
          </div>

          {/* Key Levels */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-700">
            <div>
              <p className="text-slate-400 text-xs uppercase mb-1">الدعم</p>
              <p className="text-lg font-semibold text-emerald-400">
                ${analysis.indicators.support_level?.toFixed(2) || 'N/A'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-slate-400 text-xs uppercase mb-1">المقاومة</p>
              <p className="text-lg font-semibold text-red-400">
                ${analysis.indicators.resistance_level?.toFixed(2) || 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Placeholder */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold">الرسم البياني - الشموع</h3>
        </div>
        <div className="card-body">
          <CandlestickChart analysis={analysis} />
        </div>
      </div>

      {/* Indicators */}
      <IndicatorPanel indicators={analysis.indicators} />
    </div>
  )
}
