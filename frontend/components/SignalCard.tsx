'use client'

import { Signal } from '@/lib/api'
import { ArrowUp, ArrowDown, AlertCircle, CheckCircle } from 'lucide-react'

interface SignalCardProps {
  signal: Signal
}

export default function SignalCard({ signal }: SignalCardProps) {
  const isConfirmed = signal.state === 'CONFIRMED'
  const isWatch = signal.state === 'WATCH'
  const isBuy = signal.direction === 'BUY'

  return (
    <div className={`card ${
      isBuy ? 'border-emerald-600' : 'border-red-600'
    }`}>
      <div className="card-header">
        <h3 className="font-semibold">الإشارة الحالية</h3>
      </div>
      <div className="card-body space-y-4">
        {/* Direction */}
        <div className="flex items-center justify-between">
          <span className="text-slate-400">الاتجاه</span>
          <div className={`flex items-center gap-2 text-lg font-bold ${
            isBuy ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {isBuy ? <ArrowUp className="w-5 h-5" /> : <ArrowDown className="w-5 h-5" />}
            {isBuy ? 'شراء' : 'بيع'}
          </div>
        </div>

        {/* Signal State */}
        <div className="flex items-center justify-between">
          <span className="text-slate-400">الحالة</span>
          <div className="flex items-center gap-2">
            {isConfirmed && <CheckCircle className="w-4 h-4 text-emerald-400" />}
            {isWatch && <AlertCircle className="w-4 h-4 text-amber-400" />}
            <span className={`text-sm font-medium ${
              isConfirmed ? 'text-emerald-400' :
              isWatch ? 'text-amber-400' :
              'text-red-400'
            }`}>
              {signal.state === 'CONFIRMED' ? 'تأكيد' :
               signal.state === 'WATCH' ? 'مراقبة' :
               signal.state === 'RISK_BLOCK' ? 'محظور' : 'ملغى'}
            </span>
          </div>
        </div>

        {/* Confidence */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm">درجة الثقة</span>
            <span className="text-sm font-semibold text-gold-400">
              {(signal.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-gold-500 to-gold-400 h-full transition-all"
              style={{ width: `${signal.confidence * 100}%` }}
            />
          </div>
        </div>

        {/* Entry/Exit Levels */}
        {signal.entry_price && (
          <>
            <div className="pt-2 border-t border-slate-700">
              <p className="text-slate-400 text-xs uppercase mb-2">مستويات الدخول والخروج</p>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">الدخول</span>
                  <span className="font-semibold text-gold-400">
                    ${signal.entry_price.toFixed(2)}
                  </span>
                </div>
                {signal.stop_loss && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">وقف الخسارة</span>
                    <span className="font-semibold text-red-400">
                      ${signal.stop_loss.toFixed(2)}
                    </span>
                  </div>
                )}
                {signal.take_profit && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">جني الأرباح</span>
                    <span className="font-semibold text-emerald-400">
                      ${signal.take_profit.toFixed(2)}
                    </span>
                  </div>
                )}
                {signal.risk_reward_ratio && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">نسبة المخاطرة</span>
                    <span className="font-semibold text-slate-100">
                      1:{signal.risk_reward_ratio.toFixed(2)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* Evidence */}
        {signal.evidence && signal.evidence.length > 0 && (
          <div className="pt-2 border-t border-slate-700">
            <p className="text-slate-400 text-xs uppercase mb-2">الأدلة</p>
            <ul className="space-y-1 text-xs text-slate-300">
              {signal.evidence.map((item, idx) => (
                <li key={idx} className="flex gap-2">
                  <span className="text-gold-400 flex-shrink-0">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
