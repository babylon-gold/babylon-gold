'use client'

import { useEffect, useState } from 'react'
import { AlertCircle, Play, Pause, RefreshCw, Activity, Clock } from 'lucide-react'

interface SchedulerStatus {
  running: boolean
  jobs: Array<{
    id: string
    name: string
    next_run_time: string
  }>
}

interface RefreshStatus {
  status: string
  last_refresh: string | null
  duration_seconds?: number
  error_count: number
}

interface HealthData {
  data: {
    is_loaded: boolean
    data_type: string
    data_age_hours: number
    candle_counts: Record<string, number>
  }
  refresh: RefreshStatus
  scheduler: SchedulerStatus
}

export default function AdminPage() {
  const [health, setHealth] = useState<HealthData | null>(null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

  const loadHealth = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/admin/system/health-detailed`)
      if (!response.ok) throw new Error('Failed to load system health')
      const data = await response.json()
      setHealth(data.scheduler ? {
        ...data.scheduler,
        data: data.data,
        refresh: data.refresh,
      } : null)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'خطأ في تحميل البيانات')
    } finally {
      setLoading(false)
    }
  }

  const triggerRefresh = async () => {
    try {
      setRefreshing(true)
      setError(null)
      const response = await fetch(`${API_URL}/admin/data/refresh`, { method: 'POST' })
      if (!response.ok) throw new Error('فشل تحديث البيانات')
      setSuccessMessage('✅ تم تحديث البيانات بنجاح')
      setTimeout(() => loadHealth(), 1000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'خطأ في التحديث')
    } finally {
      setRefreshing(false)
    }
  }

  const toggleScheduler = async (action: 'start' | 'stop') => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`${API_URL}/admin/scheduler/${action}`, { method: 'POST' })
      if (!response.ok) throw new Error(`فشل ${action === 'start' ? 'بدء' : 'إيقاف'} المجدول`)
      setSuccessMessage(`✅ ${action === 'start' ? 'تم بدء' : 'تم إيقاف'} المجدول`)
      setTimeout(() => loadHealth(), 500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'خطأ في المجدول')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHealth()
    const interval = setInterval(loadHealth, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000)
      return () => clearTimeout(timer)
    }
    return
  }, [successMessage])

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gold-400 mb-2">
            لوحة الإدارة
          </h1>
          <p className="text-slate-400">
            إدارة التحديثات التلقائية والمجدول للبيانات
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="card bg-red-900/20 border-red-700 p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="text-red-300">{error}</div>
          </div>
        )}

        {successMessage && (
          <div className="card bg-emerald-900/20 border-emerald-700 p-4 mb-6 flex items-start gap-3">
            <Activity className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <div className="text-emerald-300">{successMessage}</div>
          </div>
        )}

        {loading ? (
          <div className="card text-center py-12">
            <div className="animate-spin inline-block w-6 h-6 border-2 border-gold-400 border-t-transparent rounded-full"></div>
            <p className="text-slate-400 mt-4">جاري التحميل...</p>
          </div>
        ) : health ? (
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={triggerRefresh}
                disabled={refreshing}
                className="card hover:bg-slate-700/50 transition cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex items-center gap-3">
                  <RefreshCw className={`w-6 h-6 text-gold-400 ${refreshing ? 'animate-spin' : ''}`} />
                  <div className="text-right">
                    <div className="font-semibold text-slate-100">تحديث البيانات</div>
                    <div className="text-sm text-slate-400">تشغيل يدوي للتحديث</div>
                  </div>
                </div>
              </button>

              <button
                onClick={() => toggleScheduler(health?.scheduler?.running ? 'stop' : 'start')}
                disabled={loading}
                className="card hover:bg-slate-700/50 transition cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex items-center gap-3">
                  {health?.scheduler?.running ? (
                    <Pause className="w-6 h-6 text-amber-400" />
                  ) : (
                    <Play className="w-6 h-6 text-emerald-400" />
                  )}
                  <div className="text-right">
                    <div className="font-semibold text-slate-100">
                      {health?.scheduler?.running ? 'إيقاف المجدول' : 'بدء المجدول'}
                    </div>
                    <div className="text-sm text-slate-400">
                      {health?.scheduler?.running ? 'إيقاف التحديثات التلقائية' : 'تفعيل التحديثات التلقائية'}
                    </div>
                  </div>
                </div>
              </button>
            </div>

            {/* Data Status */}
            <div className="card">
              <div className="card-header border-b border-slate-700/50 pb-4">
                <h2 className="text-xl font-semibold text-gold-400">حالة البيانات</h2>
              </div>
              <div className="card-body grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-slate-400 mb-1">نوع البيانات</div>
                  <div className="text-lg font-semibold text-slate-100">{health.data.data_type}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-400 mb-1">عمر البيانات</div>
                  <div className="text-lg font-semibold text-slate-100">{health.data.data_age_hours} ساعة</div>
                </div>
                <div className="md:col-span-2">
                  <div className="text-sm text-slate-400 mb-2">عدد الشموع</div>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(health.data.candle_counts).map(([interval, count]) => (
                      <div key={interval} className="bg-slate-900/50 rounded p-2">
                        <div className="text-xs text-slate-400">{interval}</div>
                        <div className="text-sm font-semibold text-gold-300">{count.toLocaleString()}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Scheduler Status */}
            <div className="card">
              <div className="card-header border-b border-slate-700/50 pb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gold-400">المجدول</h2>
                <div className={`inline-block px-3 py-1 rounded text-sm font-semibold ${
                  health?.scheduler?.running
                    ? 'bg-emerald-500/20 border border-emerald-700 text-emerald-300'
                    : 'bg-amber-500/20 border border-amber-700 text-amber-300'
                }`}>
                  {health?.scheduler?.running ? '🟢 مشغل' : '🔴 موقف'}
                </div>
              </div>
              <div className="card-body space-y-3">
                {health?.scheduler?.jobs?.map((job) => (
                  <div key={job.id} className="bg-slate-900/50 rounded p-3 border border-slate-700/30">
                    <div className="flex items-start gap-3">
                      <Clock className="w-4 h-4 text-gold-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <div className="font-semibold text-slate-200">{job.name}</div>
                        <div className="text-sm text-slate-400 mt-1">
                          التشغيل التالي: {new Date(job.next_run_time).toLocaleString('ar-SA', {
                            dateStyle: 'short',
                            timeStyle: 'short',
                            timeZone: 'Asia/Baghdad'
                          })}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Refresh Status */}
            <div className="card">
              <div className="card-header border-b border-slate-700/50 pb-4">
                <h2 className="text-xl font-semibold text-gold-400">آخر تحديث</h2>
              </div>
              <div className="card-body space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-400">الحالة</span>
                  <span className={`font-semibold ${
                    health.refresh.status === 'completed_successfully'
                      ? 'text-emerald-400'
                      : health.refresh.status === 'completed_with_warnings'
                      ? 'text-amber-400'
                      : 'text-red-400'
                  }`}>
                    {health.refresh.status === 'completed_successfully' ? '✅ نجح' :
                     health.refresh.status === 'completed_with_warnings' ? '⚠️ تحذيرات' :
                     health.refresh.status === 'never_run' ? '⏭️ لم يتم' : '❌ فشل'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">آخر تحديث</span>
                  <span className="text-slate-200">
                    {health.refresh.last_refresh
                      ? new Date(health.refresh.last_refresh).toLocaleString('ar-SA', {
                          dateStyle: 'short',
                          timeStyle: 'short',
                          timeZone: 'Asia/Baghdad'
                        })
                      : 'لم يتم'}
                  </span>
                </div>
                {health.refresh.duration_seconds && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">المدة</span>
                    <span className="text-slate-200">{health.refresh.duration_seconds.toFixed(2)}s</span>
                  </div>
                )}
              </div>
            </div>

            {/* Info Box */}
            <div className="card bg-slate-900/50 border border-slate-700/30">
              <div className="text-sm text-slate-400 space-y-2">
                <p><strong>📅 جدول التحديثات:</strong></p>
                <ul className="list-disc list-inside space-y-1 text-slate-500 mr-2">
                  <li>يومي في الساعة 2:00 صباحًا UTC (9:00 صباحًا بتوقيت بغداد)</li>
                  <li>كل 4 ساعات خلال اليوم</li>
                  <li>يمكن تشغيل التحديث يدويًا في أي وقت</li>
                </ul>
                <p className="mt-3"><strong>⚙️ ما يتم تحديثه:</strong></p>
                <ul className="list-disc list-inside space-y-1 text-slate-500 mr-2">
                  <li>تحميل بيانات OHLC الجديدة</li>
                  <li>حساب المؤشرات الفنية</li>
                  <li>توليد الإشارات</li>
                  <li>تقييم الأداء</li>
                </ul>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </main>
  )
}
