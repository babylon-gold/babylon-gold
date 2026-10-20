'use client'

import { IndicatorValues } from '@/lib/api'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface IndicatorPanelProps {
  indicators: IndicatorValues
}

export default function IndicatorPanel({ indicators }: IndicatorPanelProps) {
  const rsi = indicators.rsi

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="font-semibold">المؤشرات الفنية</h3>
      </div>
      <div className="card-body">
        <div className="grid grid-cols-2 gap-4">
          {/* EMA 20 */}
          <div>
            <p className="text-slate-400 text-xs uppercase mb-1">EMA 20</p>
            <p className="text-lg font-semibold text-gold-400">
              ${indicators.ema_20?.toFixed(2) || 'N/A'}
            </p>
          </div>

          {/* EMA 50 */}
          <div>
            <p className="text-slate-400 text-xs uppercase mb-1">EMA 50</p>
            <p className="text-lg font-semibold text-gold-400">
              ${indicators.ema_50?.toFixed(2) || 'N/A'}
            </p>
          </div>

          {/* EMA 200 */}
          <div>
            <p className="text-slate-400 text-xs uppercase mb-1">EMA 200</p>
            <p className="text-lg font-semibold text-gold-400">
              ${indicators.ema_200?.toFixed(2) || 'N/A'}
            </p>
          </div>

          {/* RSI */}
          <div>
            <p className="text-slate-400 text-xs uppercase mb-1">RSI(14)</p>
            <div className="flex items-center gap-2">
              <p className="text-lg font-semibold">
                {rsi ? rsi.toFixed(1) : 'N/A'}
              </p>
              {rsi && (
                <span className={`text-xs font-medium px-2 py-1 rounded ${
                  rsi > 70 ? 'bg-red-900/50 text-red-300' :
                  rsi < 30 ? 'bg-emerald-900/50 text-emerald-300' :
                  'bg-slate-700 text-slate-300'
                }`}>
                  {rsi > 70 ? 'مرتفع' : rsi < 30 ? 'منخفض' : 'محايد'}
                </span>
              )}
            </div>
          </div>

          {/* ATR */}
          <div>
            <p className="text-slate-400 text-xs uppercase mb-1">ATR(14)</p>
            <p className="text-lg font-semibold text-slate-100">
              {indicators.atr?.toFixed(2) || 'N/A'}
            </p>
          </div>

          {/* ADX */}
          <div>
            <p className="text-slate-400 text-xs uppercase mb-1">ADX(14)</p>
            <p className="text-lg font-semibold text-slate-100">
              {indicators.adx?.toFixed(1) || 'N/A'}
            </p>
          </div>

          {/* Market Regime */}
          <div className="col-span-2">
            <p className="text-slate-400 text-xs uppercase mb-2">نوع السوق</p>
            <div className="flex items-center gap-2">
              {indicators.market_regime === 'uptrend' && (
                <>
                  <TrendingUp className="w-5 h-5 text-emerald-400" />
                  <span className="badge badge-success">صعود قوي</span>
                </>
              )}
              {indicators.market_regime === 'downtrend' && (
                <>
                  <TrendingDown className="w-5 h-5 text-red-400" />
                  <span className="badge badge-danger">هبوط قوي</span>
                </>
              )}
              {indicators.market_regime === 'ranging' && (
                <span className="badge badge-info">تذبذب جانبي</span>
              )}
              {!indicators.market_regime && (
                <span className="text-slate-400">غير محدد</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
