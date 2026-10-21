'use client'

import { useEffect, useState } from 'react'
import { AlertCircle, Clock, TrendingUp, TrendingDown, Zap, BarChart3 } from 'lucide-react'
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
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Babylonian Background */}
      <div className="fixed inset-0 opacity-10">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 1200 400%22><defs><pattern id=%22arch%22 x=%220%22 y=%220%22 width=%22200%22 height=%22400%22 patternUnits=%22userSpaceOnUse%22><rect x=%2220%22 y=%2220%22 width=%22160%22 height=%22360%22 fill=%22none%22 stroke=%22%23fbbf24%22 stroke-width=%222%22/><circle cx=%22100%22 cy=%22100%22 r=%2230%22 fill=%22none%22 stroke=%22%23fbbf24%22 stroke-width=%221%22/><path d=%22M 40 200 Q 100 150 160 200%22 fill=%22none%22 stroke=%22%23fbbf24%22 stroke-width=%221%22/></pattern></defs><rect width=%221200%22 height=%22400%22 fill=%22%231e293b%22/><rect width=%221200%22 height=%22400%22 fill=%22url(%23arch)%22/></svg>')]"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 py-8">
        {/* Premium Header */}
        <div className="text-center mb-12">
          <div className="inline-block mb-4">
            <div className="flex items-center justify-center gap-3">
              <div className="text-5xl font-bold bg-gradient-to-r from-gold-300 via-gold-400 to-gold-500 bg-clip-text text-transparent">
                بابل الذهب
              </div>
              <div className="text-4xl">🏛️</div>
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-gold-400 mb-3">
            منصة تحليل الذهب المتقدمة
          </h1>
          <p className="text-xl text-blue-200 mb-2">
            XAU/USD تحليل احترافي في الوقت الفعلي
          </p>
          <p className="text-slate-400">
            ذكاء اصطناعي متقدم | بيانات تاريخية حقيقية | إشارات تداول مدعومة بالمؤشرات الفنية
          </p>
        </div>

        {/* Premium Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
          <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/20 border border-gold-500/30 rounded-lg p-4 text-center backdrop-blur">
            <div className="text-gold-400 font-bold text-2xl">88,958</div>
            <div className="text-slate-300 text-sm">شموع تاريخية</div>
          </div>
          <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/20 border border-gold-500/30 rounded-lg p-4 text-center backdrop-blur">
            <div className="text-emerald-400 font-bold text-2xl">4</div>
            <div className="text-slate-300 text-sm">أطر زمنية</div>
          </div>
          <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/20 border border-gold-500/30 rounded-lg p-4 text-center backdrop-blur">
            <div className="text-blue-400 font-bold text-2xl">12+</div>
            <div className="text-slate-300 text-sm">مؤشر فني</div>
          </div>
          <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/20 border border-gold-500/30 rounded-lg p-4 text-center backdrop-blur">
            <div className="text-amber-400 font-bold text-2xl">Real-Time</div>
            <div className="text-slate-300 text-sm">تحديث مباشر</div>
          </div>
        </div>

        {/* Warning Banner - Premium Style */}
        <div className="bg-gradient-to-r from-amber-900/40 to-orange-900/30 border border-gold-500/40 rounded-xl p-5 mb-8 backdrop-blur">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-gold-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-gold-300 mb-2">📋 إخلاء مسؤولية تعليمي</h3>
              <p className="text-blue-100 text-sm">
                هذه المنصة مخصصة للتحليل التعليمي والبحثي فقط. البيانات قد تكون تاريخية. لا تشكل نصيحة استثمارية. استشر متخصصاً مالياً قبل أي تداول.
              </p>
            </div>
          </div>
        </div>

        {/* Controls - Premium Style */}
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between mb-8">
          <div className="flex-1">
            <TimeframeSelector
              selected={selectedTimeframe}
              onChange={setSelectedTimeframe}
              disabled={loading}
            />
          </div>
          {lastUpdate && (
            <div className="text-sm text-blue-200 flex items-center gap-2 bg-blue-900/30 px-4 py-2 rounded-lg border border-blue-700/30 backdrop-blur">
              <Clock className="w-4 h-4 text-gold-400" />
              <span>آخر تحديث: {lastUpdate.toLocaleTimeString('ar-SA')}</span>
            </div>
          )}
        </div>

        {/* Main Content Grid */}
        {loading && !analysis ? (
          <LoadingSpinner />
        ) : error ? (
          <div className="card bg-gradient-to-br from-red-900/30 to-red-800/20 border border-red-600/40 p-8 text-center backdrop-blur rounded-xl">
            <div className="flex items-center justify-center gap-3 text-red-300">
              <AlertCircle className="w-8 h-8" />
              <span className="text-lg">{error}</span>
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
