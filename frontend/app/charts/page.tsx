'use client'

import { useState } from 'react'
import { AlertCircle } from 'lucide-react'
import EnhancedCandlestickChart from '@/components/EnhancedCandlestickChart'
import IndicatorCharts from '@/components/IndicatorCharts'
import TimeframeSelector from '@/components/TimeframeSelector'

type Timeframe = '5min' | '15min' | '1h' | '4h'

export default function ChartsPage() {
  const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe>('15min')

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gold-400 mb-2">
            الرسوم البيانية المتقدمة
          </h1>
          <p className="text-slate-400">
            تحليل تفصيلي للأسعار والمؤشرات الفنية
          </p>
        </div>

        {/* Warning */}
        <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-amber-300 mb-1">معلومات مهمة</h3>
            <p className="text-amber-200 text-sm">
              هذه الرسوم البيانية تعرض بيانات تاريخية. استخدم أدوات التكبير والتمرير للملاحة.
              الأسعار التاريخية فقط للتحليل التعليمي.
            </p>
          </div>
        </div>

        {/* Controls */}
        <div className="mb-6">
          <TimeframeSelector
            selected={selectedTimeframe}
            onChange={setSelectedTimeframe}
          />
        </div>

        {/* Enhanced Candlestick Chart */}
        <div className="card mb-8">
          <div className="card-header border-b border-slate-700/50 pb-4">
            <h2 className="text-xl font-semibold text-gold-400">
              الرسم البياني - {selectedTimeframe}
            </h2>
          </div>
          <div className="card-body p-6">
            <EnhancedCandlestickChart timeframe={selectedTimeframe} />
          </div>
        </div>

        {/* Technical Indicators */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gold-400 mb-4">المؤشرات الفنية التفصيلية</h2>
          <IndicatorCharts timeframe={selectedTimeframe} />
        </div>

        {/* Analysis Tips */}
        <div className="card bg-slate-900/50">
          <div className="card-header border-b border-slate-700/50 pb-4">
            <h3 className="font-semibold text-slate-300">💡 نصائح التحليل</h3>
          </div>
          <div className="card-body text-sm text-slate-400 space-y-3">
            <div>
              <strong className="text-slate-300">EMA Crossovers:</strong> When EMA 20 crosses above EMA 50, watch for uptrend. Crosses below signal downtrend.
            </div>
            <div>
              <strong className="text-slate-300">Support/Resistance:</strong> Green dashed = support (buy zone), Red dashed = resistance (sell zone).
            </div>
            <div>
              <strong className="text-slate-300">RSI Strategy:</strong> Above 70 = overbought (sell signal), Below 30 = oversold (buy signal).
            </div>
            <div>
              <strong className="text-slate-300">ADX Trend:</strong> Higher ADX = stronger trend. Use with EMA for trend confirmation.
            </div>
            <div>
              <strong className="text-slate-300">ATR Volatility:</strong> Rising ATR = increasing volatility. Lower ATR = consolidation/quiet market.
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
