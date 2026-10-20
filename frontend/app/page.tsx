'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import Dashboard from '@/components/Dashboard'
import AnalysisPanel from '@/components/AnalysisPanel'
import SignalCard from '@/components/SignalCard'
import TimeframeSelector from '@/components/TimeframeSelector'
import LoadingSpinner from '@/components/LoadingSpinner'
import { fetchAnalysis } from '@/lib/api'

type Timeframe = '5min' | '15min' | '1h' | '4h'

export default function Home() {
  const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe>('15min')
  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const loadAnalysis = async (timeframe: Timeframe) => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchAnalysis(timeframe)
      setAnalysis(data)
      setLastUpdate(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'خطأ في تحميل البيانات')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAnalysis(selectedTimeframe)
    const interval = setInterval(() => {
      loadAnalysis(selectedTimeframe)
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [selectedTimeframe])

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gold-400 mb-2">
            ذكاء بابل لتحليل الذهب
          </h1>
          <p className="text-slate-400">
            منصة تحليل XAU/USD احترافية في الوقت الفعلي
          </p>
        </div>

        {/* Warning Banner */}
        <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-amber-300 mb-1">تنبيه مهم</h3>
            <p className="text-amber-200 text-sm">
              هذا النظام مخصص للتحليل التعليمي فقط. لا يقدم إشارات تداول حقيقية ولا ينفذ صفقات.
              قد تكون البيانات المعروضة اصطناعية أو تاريخية. استشر مستشارك المالي قبل التداول.
            </p>
          </div>
        </div>

        {/* Controls */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <TimeframeSelector
            selected={selectedTimeframe}
            onChange={setSelectedTimeframe}
            disabled={loading}
          />

          {lastUpdate && (
            <div className="text-sm text-slate-400 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              آخر تحديث: {lastUpdate.toLocaleTimeString('ar-SA')}
            </div>
          )}
        </div>

        {/* Main Content */}
        {loading && !analysis ? (
          <LoadingSpinner />
        ) : error ? (
          <div className="card bg-red-900/20 border-red-700 p-6 text-center">
            <div className="flex items-center justify-center gap-3 text-red-400">
              <AlertCircle className="w-6 h-6" />
              <span>{error}</span>
            </div>
          </div>
        ) : analysis ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Dashboard */}
            <div className="lg:col-span-2">
              <Dashboard analysis={analysis} timeframe={selectedTimeframe} />
            </div>

            {/* Right Sidebar */}
            <div className="space-y-6">
              {/* Signal Card */}
              {analysis.signal && (
                <SignalCard signal={analysis.signal} />
              )}

              {/* Risk Assessment */}
              {analysis.risk_assessment && (
                <div className="card">
                  <div className="card-header flex items-center justify-between">
                    <h3 className="font-semibold text-lg">إدارة المخاطر</h3>
                    {analysis.risk_assessment.is_blocked ? (
                      <span className="badge badge-danger">محظور</span>
                    ) : analysis.risk_assessment.recommendation === 'PROCEED' ? (
                      <span className="badge badge-success">متقدم</span>
                    ) : (
                      <span className="badge badge-warning">{analysis.risk_assessment.recommendation}</span>
                    )}
                  </div>
                  <div className="card-body space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">حجم الموضع</span>
                      <span className="font-semibold text-gold-400">
                        {analysis.risk_assessment.position_size_pct.toFixed(2)}%
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">مخاطر الحساب</span>
                      <span className={`font-semibold ${
                        analysis.risk_assessment.account_risk_pct > 2 ? 'text-red-400' : 'text-emerald-400'
                      }`}>
                        {analysis.risk_assessment.account_risk_pct.toFixed(2)}%
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">وقف الخسارة (نقطة)</span>
                      <span className="font-semibold text-slate-100">
                        {analysis.risk_assessment.stop_loss_distance_pips.toFixed(1)}
                      </span>
                    </div>
                    {analysis.risk_assessment.block_reason && (
                      <div className="bg-red-900/30 border border-red-700/50 rounded p-2 text-sm text-red-300">
                        {analysis.risk_assessment.block_reason}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : null}

        {/* Arabic Analysis */}
        {analysis?.arabic_summary && (
          <AnalysisPanel summary={analysis.arabic_summary} />
        )}
      </div>
    </main>
  )
}
