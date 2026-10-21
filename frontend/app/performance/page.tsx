'use client'

import { useEffect, useState } from 'react'
import { AlertCircle } from 'lucide-react'
import { fetchPerformanceStats } from '@/lib/api'

interface PerformanceData {
  overall_stats: {
    total_signals: number
    wins: number
    losses: number
    win_rate_pct: number
    net_expectancy_r: number
  }
  by_strategy: Record<string, {
    signals: number
    wins: number
    losses: number
    win_rate_pct: number
    net_expectancy_r: number
  }>
  by_regime: Record<string, {
    signals: number
    wins: number
    losses: number
    win_rate_pct: number
    net_expectancy_r: number
  }>
}

export default function PerformancePage() {
  const [data, setData] = useState<PerformanceData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadStats = async () => {
      try {
        setLoading(true)
        const stats = await fetchPerformanceStats()
        setData(stats)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'خطأ في تحميل الإحصائيات')
      } finally {
        setLoading(false)
      }
    }
    loadStats()
  }, [])

  const getWinRateColor = (rate: number) => {
    if (rate >= 50) return 'text-emerald-400'
    if (rate >= 40) return 'text-amber-400'
    return 'text-red-400'
  }

  const getExpectancyColor = (expectancy: number) => {
    if (expectancy > 0.5) return 'text-emerald-400'
    if (expectancy > 0) return 'text-amber-400'
    return 'text-red-400'
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gold-400 mb-2">
            تقييم الأداء التاريخي
          </h1>
          <p className="text-slate-400">
            إحصائيات شاملة للإشارات المقيّمة - البيانات التاريخية فقط
          </p>
        </div>

        {/* Disclaimer Banner */}
        <div className="bg-red-900/30 border border-red-700/50 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-300 mb-1">تحذير مهم</h3>
            <p className="text-red-200 text-sm">
              الأداء التاريخي لا يضمن النتائج المستقبلية. هذه البيانات محاكاة تاريخية فقط.
              لا تعتمد على هذه الأرقام لاتخاذ قرارات تداول حقيقية.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="card text-center py-12">
            <div className="animate-spin inline-block w-6 h-6 border-2 border-gold-400 border-t-transparent rounded-full"></div>
            <p className="text-slate-400 mt-4">جاري التحميل...</p>
          </div>
        ) : error ? (
          <div className="card bg-red-900/20 border-red-700 p-6 text-center">
            <div className="flex items-center justify-center gap-3 text-red-400">
              <AlertCircle className="w-6 h-6" />
              <span>{error}</span>
            </div>
          </div>
        ) : data ? (
          <div className="space-y-6">
            {/* Overall Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="card">
                <div className="text-sm text-slate-400 mb-2">إجمالي الإشارات</div>
                <div className="text-3xl font-bold text-gold-400">
                  {data.overall_stats.total_signals}
                </div>
              </div>
              <div className="card">
                <div className="text-sm text-slate-400 mb-2">الإشارات الرابحة</div>
                <div className="flex items-baseline gap-2">
                  <div className="text-3xl font-bold text-emerald-400">
                    {data.overall_stats.wins}
                  </div>
                  <div className="text-sm text-slate-400">من {data.overall_stats.total_signals}</div>
                </div>
              </div>
              <div className="card">
                <div className="text-sm text-slate-400 mb-2">الإشارات الخاسرة</div>
                <div className="text-3xl font-bold text-red-400">
                  {data.overall_stats.losses}
                </div>
              </div>
              <div className="card">
                <div className="text-sm text-slate-400 mb-2">نسبة النجاح</div>
                <div className={`text-3xl font-bold ${getWinRateColor(data.overall_stats.win_rate_pct)}`}>
                  {data.overall_stats.win_rate_pct.toFixed(1)}%
                </div>
              </div>
              <div className="card">
                <div className="text-sm text-slate-400 mb-2">العائد المتوقع (R)</div>
                <div className={`text-3xl font-bold ${getExpectancyColor(data.overall_stats.net_expectancy_r)}`}>
                  {data.overall_stats.net_expectancy_r.toFixed(2)}R
                </div>
              </div>
            </div>

            {/* By Strategy */}
            {Object.keys(data.by_strategy).length > 0 && (
              <div className="card">
                <div className="card-header border-b border-slate-700/50 pb-4">
                  <h2 className="text-xl font-semibold text-gold-400">الإحصائيات حسب الاستراتيجية</h2>
                </div>
                <div className="card-body">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(data.by_strategy).map(([strategy, stats]) => (
                      <div key={strategy} className="bg-slate-900/50 rounded p-4 border border-slate-700/30">
                        <h3 className="text-sm font-semibold text-gold-300 mb-3">
                          الاستراتيجية: {strategy}
                        </h3>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-slate-400">الإشارات:</span>
                            <span className="text-slate-200">{stats.signals}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">الرابحة / الخاسرة:</span>
                            <span className="text-slate-200">{stats.wins} / {stats.losses}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">نسبة النجاح:</span>
                            <span className={getWinRateColor(stats.win_rate_pct)}>
                              {stats.win_rate_pct.toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between pt-2 border-t border-slate-700/30">
                            <span className="text-slate-400">العائد المتوقع:</span>
                            <span className={`font-semibold ${getExpectancyColor(stats.net_expectancy_r)}`}>
                              {stats.net_expectancy_r.toFixed(2)}R
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* By Regime */}
            {Object.keys(data.by_regime).length > 0 && (
              <div className="card">
                <div className="card-header border-b border-slate-700/50 pb-4">
                  <h2 className="text-xl font-semibold text-gold-400">الإحصائيات حسب نظام السوق</h2>
                </div>
                <div className="card-body">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(data.by_regime).map(([regime, stats]) => (
                      <div key={regime} className="bg-slate-900/50 rounded p-4 border border-slate-700/30">
                        <h3 className="text-sm font-semibold text-gold-300 mb-3">
                          {regime}
                        </h3>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-slate-400">الإشارات:</span>
                            <span className="text-slate-200">{stats.signals}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">الرابحة / الخاسرة:</span>
                            <span className="text-slate-200">{stats.wins} / {stats.losses}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">نسبة النجاح:</span>
                            <span className={getWinRateColor(stats.win_rate_pct)}>
                              {stats.win_rate_pct.toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between pt-2 border-t border-slate-700/30">
                            <span className="text-slate-400">العائد المتوقع:</span>
                            <span className={`font-semibold ${getExpectancyColor(stats.net_expectancy_r)}`}>
                              {stats.net_expectancy_r.toFixed(2)}R
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Metrics Explanation */}
            <div className="card bg-slate-900/50">
              <div className="card-header border-b border-slate-700/50 pb-4">
                <h3 className="text-lg font-semibold text-gold-300">شرح المقاييس</h3>
              </div>
              <div className="card-body space-y-3 text-sm">
                <div>
                  <h4 className="font-semibold text-slate-300 mb-1">نسبة النجاح (Win Rate)</h4>
                  <p className="text-slate-400">
                    نسبة عدد الإشارات الرابحة من إجمالي الإشارات. القيمة أعلاه من 50% تعني أن الاستراتيجية تحقق أرباح أكثر من الخسائر إحصائيًا.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-300 mb-1">العائد المتوقع (Expectancy)</h4>
                  <p className="text-slate-400">
                    متوسط الربح/الخسارة بوحدات المخاطرة المخطط لها (R). مثال: 0.5R تعني أن الإشارة تحقق نصف المخاطرة كربح متوسطي.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-300 mb-1">نظام السوق (Market Regime)</h4>
                  <p className="text-slate-400">
                    حالة السوق في وقت الإشارة: اتجاهي صاعد، اتجاهي هابط، عرضي، أو انتقالي.
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </main>
  )
}
