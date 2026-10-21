'use client'

import { useEffect, useState } from 'react'
import { AlertCircle, TrendingUp, TrendingDown } from 'lucide-react'
import { fetchSignalsHistory } from '@/lib/api'

interface Signal {
  signal_id: string
  strategy: string
  direction: string
  created_utc: string
  state: string
  level: number | null
  invalidation: number | null
  confirmed_utc: string | null
  entry: number | null
  target: number | null
  result: string
  r_multiple: number | null
  notes: string
}

export default function SignalsPage() {
  const [signals, setSignals] = useState<Signal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalSignals, setTotalSignals] = useState(0)

  useEffect(() => {
    const loadSignals = async () => {
      try {
        setLoading(true)
        const data = await fetchSignalsHistory(100)
        setSignals(data.signals || [])
        setTotalSignals(data.total_signals || 0)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'خطأ في تحميل الإشارات')
      } finally {
        setLoading(false)
      }
    }
    loadSignals()
  }, [])

  const getStateColor = (state: string) => {
    switch (state.toUpperCase()) {
      case 'CONFIRMED':
        return 'bg-emerald-900/30 border-emerald-700/50 text-emerald-300'
      case 'WATCH':
        return 'bg-blue-900/30 border-blue-700/50 text-blue-300'
      case 'INVALIDATED':
        return 'bg-red-900/30 border-red-700/50 text-red-300'
      case 'EXPIRED':
        return 'bg-amber-900/30 border-amber-700/50 text-amber-300'
      default:
        return 'bg-slate-700/30 border-slate-600/50 text-slate-300'
    }
  }

  const getStateLabel = (state: string) => {
    const stateMap: Record<string, string> = {
      CONFIRMED: 'مؤكد',
      WATCH: 'مراقبة',
      INVALIDATED: 'ملغى',
      EXPIRED: 'انتهى'
    }
    return stateMap[state.toUpperCase()] || state
  }

  const getDirectionIcon = (direction: string) => {
    if (direction === 'صاعد') return <TrendingUp className="w-4 h-4" />
    if (direction === 'هابط') return <TrendingDown className="w-4 h-4" />
    return null
  }

  const formatTime = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleString('ar-SA', {
        dateStyle: 'short',
        timeStyle: 'short',
        timeZone: 'Asia/Baghdad'
      })
    } catch {
      return dateStr
    }
  }

  const formatNumber = (num: number | null) => {
    if (num === null) return '—'
    return num.toFixed(2)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gold-400 mb-2">
            سجل الإشارات التاريخي
          </h1>
          <p className="text-slate-400">
            بيانات تاريخية - جميع الإشارات المُنشأة والمُقيّمة
          </p>
        </div>

        {/* Warning Banner */}
        <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-amber-300 mb-1">بيانات تاريخية</h3>
            <p className="text-amber-200 text-sm">
              هذه الإشارات محفوظة من التحليل التاريخي. النتائج الماضية لا تضمن النتائج المستقبلية.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div className="card">
            <div className="text-sm text-slate-400">إجمالي الإشارات</div>
            <div className="text-3xl font-bold text-gold-400">{totalSignals}</div>
          </div>
          <div className="card">
            <div className="text-sm text-slate-400">الإشارات المعروضة</div>
            <div className="text-3xl font-bold text-emerald-400">{signals.length}</div>
          </div>
          <div className="card">
            <div className="text-sm text-slate-400">نوع البيانات</div>
            <div className="text-lg text-slate-300">تاريخية</div>
          </div>
        </div>

        {/* Signals Table */}
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
        ) : signals.length === 0 ? (
          <div className="card text-center py-12 text-slate-400">
            لا توجد إشارات متاحة
          </div>
        ) : (
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-slate-700/50">
                <tr className="text-slate-300 text-right">
                  <th className="px-4 py-3 text-right">المعرف</th>
                  <th className="px-4 py-3 text-right">الاستراتيجية</th>
                  <th className="px-4 py-3 text-right">الاتجاه</th>
                  <th className="px-4 py-3 text-right">الوقت (UTC)</th>
                  <th className="px-4 py-3 text-right">الحالة</th>
                  <th className="px-4 py-3 text-right">المستوى</th>
                  <th className="px-4 py-3 text-right">الدخول</th>
                  <th className="px-4 py-3 text-right">النتيجة</th>
                  <th className="px-4 py-3 text-right">R متعدد</th>
                </tr>
              </thead>
              <tbody>
                {signals.map((signal, idx) => (
                  <tr key={`${signal.signal_id}-${idx}`} className="border-b border-slate-700/30 hover:bg-slate-700/10 transition">
                    <td className="px-4 py-3 text-slate-300 font-mono text-xs">
                      {signal.signal_id}
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {signal.strategy}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {getDirectionIcon(signal.direction)}
                        <span className="text-slate-300">{signal.direction}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-xs">
                      {formatTime(signal.created_utc)}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-block px-2 py-1 rounded border text-xs ${getStateColor(signal.state)}`}>
                        {getStateLabel(signal.state)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {formatNumber(signal.level)}
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {formatNumber(signal.entry)}
                    </td>
                    <td className="px-4 py-3">
                      <span className={signal.result === 'WIN' ? 'text-emerald-400' : signal.result === 'LOSS' ? 'text-red-400' : 'text-slate-400'}>
                        {signal.result}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {formatNumber(signal.r_multiple)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Notes Section */}
        <div className="card mt-6 bg-slate-900/50">
          <div className="text-sm text-slate-400 space-y-2">
            <p><strong>معلومات إضافية:</strong></p>
            <ul className="list-disc list-inside space-y-1 text-slate-500">
              <li>جميع الأوقات بالتوقيت العالمي (UTC)</li>
              <li>الحالات: مؤكد (تحقق شروطه), مراقبة (ينتظر التأكيد), ملغى (فشل), انتهى (خرج الوقت)</li>
              <li>R متعدد: نسبة الربح/الخسارة إلى المخاطرة المخطط لها</li>
              <li>هذه البيانات للمراجعة التاريخية فقط</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  )
}
