'use client'

import useSWR from 'swr'
import { useState } from 'react'
import { AlertCircle, Send, CheckCircle } from 'lucide-react'

interface NotificationStatus {
  telegram_enabled: boolean
  telegram_configured: boolean
  notifications_enabled: {
    signals: boolean
    analysis: boolean
    risks: boolean
    system: boolean
  }
}

export default function NotificationsPage() {
  const [saving, setSaving] = useState(false)
  const [testSending, setTestSending] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [preferences, setPreferences] = useState({
    signals: true,
    analysis: false,
    risks: true,
    system: false,
  })

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

  const { data: status, error: loadError, mutate: reloadStatus, isLoading } = useSWR<{ status: NotificationStatus }>(
    `${API_URL}/notifications/status`,
    async (url) => {
      const response = await fetch(url)
      if (!response.ok) throw new Error('Failed to load notification status')
      const data = await response.json()
      setPreferences(data.status.notifications_enabled)
      return data
    },
    { dedupingInterval: 5000 }
  )

  const savePreferences = async () => {
    try {
      setSaving(true)
      const response = await fetch(`${API_URL}/notifications/preferences`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preferences),
      })
      if (!response.ok) throw new Error('Failed to save preferences')
      setSuccessMessage('✅ تم حفظ التفضيلات بنجاح')
      setTimeout(() => setSuccessMessage(null), 3000)
      await reloadStatus()
    } catch (err) {
      setSuccessMessage(err instanceof Error ? err.message : 'خطأ في الحفظ')
    } finally {
      setSaving(false)
    }
  }

  const sendTest = async (type: string) => {
    try {
      setTestSending(type)
      const response = await fetch(`${API_URL}/notifications/test-${type}`, {
        method: 'POST',
      })
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to send test')
      }
      setSuccessMessage(`✅ تم إرسال تنبيه اختبار ${type} بنجاح`)
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setSuccessMessage(err instanceof Error ? err.message : 'خطأ في الإرسال')
    } finally {
      setTestSending(null)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gold-400 mb-2">
            إشعارات التداول
          </h1>
          <p className="text-slate-400">
            إدارة إشعارات Telegram والتنبيهات المخصصة
          </p>
        </div>

        {/* Alerts */}
        {loadError && (
          <div className="card bg-red-900/20 border-red-700 p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="text-red-300">{loadError.message || 'خطأ في تحميل الحالة'}</div>
          </div>
        )}

        {successMessage && (
          <div className="card bg-emerald-900/20 border-emerald-700 p-4 mb-6 flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <div className="text-emerald-300">{successMessage}</div>
          </div>
        )}

        {isLoading ? (
          <div className="card text-center py-12">
            <div className="animate-spin inline-block w-6 h-6 border-2 border-gold-400 border-t-transparent rounded-full"></div>
            <p className="text-slate-400 mt-4">جاري التحميل...</p>
          </div>
        ) : status?.status ? (
          <div className="space-y-6">
            {/* Status Card */}
            <div className="card">
              <div className="card-header border-b border-slate-700/50 pb-4">
                <h2 className="text-xl font-semibold text-gold-400">حالة النظام</h2>
              </div>
              <div className="card-body space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Telegram Bot:</span>
                  <div className="flex items-center gap-2">
                    {status.status.telegram_enabled ? (
                      <>
                        <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
                        <span className="text-emerald-400">🟢 متصل</span>
                      </>
                    ) : (
                      <>
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        <span className="text-red-400">🔴 غير متصل</span>
                      </>
                    )}
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">التكوين:</span>
                  <span className={status.status.telegram_configured ? 'text-emerald-400' : 'text-red-400'}>
                    {status.status.telegram_configured ? '✅ مكتمل' : '❌ غير مكتمل'}
                  </span>
                </div>
              </div>
            </div>

            {/* Setup Guide */}
            {!status.status.telegram_enabled && (
              <div className="card bg-amber-900/20 border-amber-700/50">
                <div className="card-header border-b border-amber-700/30 pb-3">
                  <h3 className="font-semibold text-amber-300">⚙️ إعداد Telegram</h3>
                </div>
                <div className="card-body text-sm space-y-3 text-slate-300">
                  <p>لتفعيل الإشعارات، اتبع الخطوات التالية:</p>
                  <ol className="list-decimal list-inside space-y-2 ml-2">
                    <li>
                      تحدث إلى{' '}
                      <a href="https://t.me/BotFather" target="_blank" rel="noopener noreferrer" className="text-gold-300 hover:text-gold-400 underline">
                        @BotFather
                      </a>{' '}
                      وأنشئ bot جديد
                    </li>
                    <li>
                      احصل على Chat ID من{' '}
                      <a href="https://t.me/userinfobot" target="_blank" rel="noopener noreferrer" className="text-gold-300 hover:text-gold-400 underline">
                        @userinfobot
                      </a>
                    </li>
                    <li>
                      عيّن متغيرات البيئة:
                      <div className="bg-slate-900/50 rounded p-2 mt-2 font-mono text-xs">
                        TELEGRAM_BOT_TOKEN=your_token<br />
                        TELEGRAM_CHAT_ID=your_chat_id
                      </div>
                    </li>
                    <li>أعد تشغيل الخادم الخلفي</li>
                  </ol>
                </div>
              </div>
            )}

            {/* Notification Preferences */}
            <div className="card">
              <div className="card-header border-b border-slate-700/50 pb-4">
                <h2 className="text-xl font-semibold text-gold-400">تفضيلات الإشعارات</h2>
              </div>
              <div className="card-body space-y-4">
                {[
                  { key: 'signals', label: 'إشارات التداول', description: 'إخطار عند توليد إشارة جديدة' },
                  { key: 'analysis', label: 'تحديثات التحليل', description: 'تحديثات منتظمة لتحليل السوق' },
                  { key: 'risks', label: 'تنبيهات المخاطر', description: 'تنبيه عند تجاوز حدود المخاطرة' },
                  { key: 'system', label: 'حالة النظام', description: 'تنبيهات صحة النظام' },
                ].map(({ key, label, description }) => (
                  <label key={key} className="flex items-start gap-3 cursor-pointer p-3 bg-slate-900/30 rounded hover:bg-slate-900/50 transition">
                    <input
                      type="checkbox"
                      checked={preferences[key as keyof typeof preferences]}
                      onChange={(e) => setPreferences({
                        ...preferences,
                        [key]: e.target.checked,
                      })}
                      className="w-5 h-5 rounded border-slate-600 mt-1"
                    />
                    <div>
                      <div className="font-semibold text-slate-200">{label}</div>
                      <div className="text-sm text-slate-400">{description}</div>
                    </div>
                  </label>
                ))}
              </div>
              <div className="border-t border-slate-700/50 p-4">
                <button
                  onClick={savePreferences}
                  disabled={saving}
                  className="w-full bg-gold-500/20 hover:bg-gold-500/30 border border-gold-500/50 text-gold-300 py-2 rounded font-semibold transition disabled:opacity-50"
                >
                  {saving ? 'جاري الحفظ...' : '💾 حفظ التفضيلات'}
                </button>
              </div>
            </div>

            {/* Test Notifications */}
            {status?.status?.telegram_enabled && (
              <div className="card">
                <div className="card-header border-b border-slate-700/50 pb-4">
                  <h2 className="text-xl font-semibold text-gold-400">اختبار الإشعارات</h2>
                </div>
                <div className="card-body space-y-2">
                  <p className="text-sm text-slate-400 mb-4">أرسل إشعارات اختبار للتحقق من التكوين:</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {[
                      { id: 'signal', label: '🎯 إشارة تداول' },
                      { id: 'analysis', label: '📊 تحليل السوق' },
                      { id: 'risk', label: '⚠️ تنبيه المخاطر' },
                      { id: 'system', label: '⚙️ حالة النظام' },
                    ].map(({ id, label }) => (
                      <button
                        key={id}
                        onClick={() => sendTest(id)}
                        disabled={testSending === id}
                        className="flex items-center justify-center gap-2 bg-slate-700/50 hover:bg-slate-600/50 py-2 px-4 rounded transition disabled:opacity-50 text-slate-300 text-sm"
                      >
                        <Send className="w-4 h-4" />
                        {testSending === id ? 'جاري الإرسال...' : label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Info */}
            <div className="card bg-slate-900/50">
              <div className="text-sm text-slate-400 space-y-2">
                <p><strong>ℹ️ معلومات:</strong></p>
                <ul className="list-disc list-inside space-y-1 text-slate-500 ml-2">
                  <li>الإشعارات ترسل عبر Telegram مباشرة لهاتفك أو قناتك</li>
                  <li>تأكد من إضافة Bot إلى مجموعتك أو قناتك إن أردت الإشعارات هناك</li>
                  <li>يمكن تفعيل/تعطيل كل نوع إشعار بشكل مستقل</li>
                  <li>الإشعارات آمنة تماما وغير مرتبطة بأي حساب حقيقي</li>
                </ul>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </main>
  )
}
