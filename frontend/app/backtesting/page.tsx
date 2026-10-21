'use client'

import { useState } from 'react'
import { AlertCircle, Play, RotateCcw, TrendingUp, TrendingDown } from 'lucide-react'

interface BacktestResult {
  total_trades: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  total_return: number
  max_drawdown: number
  sharpe_ratio: number
  trades: Array<{
    entry_price: number
    exit_price: number
    profit_loss: number
    profit_loss_pct: number
    duration_bars: number
  }>
  equity_curve: Array<{ timestamp: string; equity: number }>
}

export default function BacktestingPage() {
  const [strategy, setStrategy] = useState('ema_crossover')
  const [timeframe, setTimeframe] = useState('15min')
  const [startDate, setStartDate] = useState('2026-01-01')
  const [endDate, setEndDate] = useState('2026-10-21')
  const [initialCapital, setInitialCapital] = useState(10000)
  const [riskPerTrade, setRiskPerTrade] = useState(1)

  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<BacktestResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runBacktest = async () => {
    setLoading(true)
    setError(null)

    try {
      // Mock backtest results for demo
      // In production, this would call the backend API
      await new Promise((resolve) => setTimeout(resolve, 2000))

      const mockResults: BacktestResult = {
        total_trades: 47,
        winning_trades: 28,
        losing_trades: 19,
        win_rate: 59.6,
        total_return: 28.5,
        max_drawdown: -12.3,
        sharpe_ratio: 1.45,
        trades: [
          {
            entry_price: 4120.50,
            exit_price: 4135.75,
            profit_loss: 152.5,
            profit_loss_pct: 0.37,
            duration_bars: 8,
          },
          {
            entry_price: 4118.25,
            exit_price: 4105.00,
            profit_loss: -132.75,
            profit_loss_pct: -0.32,
            duration_bars: 5,
          },
          {
            entry_price: 4125.00,
            exit_price: 4142.50,
            profit_loss: 175.0,
            profit_loss_pct: 0.42,
            duration_bars: 12,
          },
        ],
        equity_curve: [
          { timestamp: '2026-01-01', equity: 10000 },
          { timestamp: '2026-02-15', equity: 10850 },
          { timestamp: '2026-03-30', equity: 11240 },
          { timestamp: '2026-05-10', equity: 10950 },
          { timestamp: '2026-06-20', equity: 12150 },
          { timestamp: '2026-07-25', equity: 12450 },
          { timestamp: '2026-08-15', equity: 11920 },
          { timestamp: '2026-09-10', equity: 12850 },
          { timestamp: '2026-10-21', equity: 12850 },
        ],
      }

      setResults(mockResults)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Backtest failed')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setStrategy('ema_crossover')
    setTimeframe('15min')
    setStartDate('2026-01-01')
    setEndDate('2026-10-21')
    setInitialCapital(10000)
    setRiskPerTrade(1)
    setResults(null)
    setError(null)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gold-400 mb-2">اختبار الاستراتيجيات</h1>
          <p className="text-slate-400">اختبر استراتيجيات التداول على البيانات التاريخية</p>
        </div>

        {/* Warning */}
        <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-amber-300 mb-1">تنبيه</h3>
            <p className="text-amber-200 text-sm">
              النتائج التاريخية لا تضمن الأداء المستقبلي. هذا النظام لأغراض تعليمية فقط.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Configuration Panel */}
          <div className="lg:col-span-1">
            <div className="card sticky top-4">
              <div className="card-header border-b border-slate-700/50 pb-4">
                <h2 className="text-lg font-semibold text-gold-400">إعدادات الاختبار</h2>
              </div>
              <div className="card-body space-y-4">
                {/* Strategy */}
                <div>
                  <label className="block text-sm text-slate-400 mb-2">الاستراتيجية</label>
                  <select
                    value={strategy}
                    onChange={(e) => setStrategy(e.target.value)}
                    disabled={loading}
                    className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-100 text-sm disabled:opacity-50"
                  >
                    <option value="ema_crossover">EMA Crossover</option>
                    <option value="rsi_levels">RSI Levels</option>
                    <option value="adx_trend">ADX Trend Following</option>
                    <option value="combined">Combined Signal</option>
                  </select>
                </div>

                {/* Timeframe */}
                <div>
                  <label className="block text-sm text-slate-400 mb-2">الإطار الزمني</label>
                  <select
                    value={timeframe}
                    onChange={(e) => setTimeframe(e.target.value)}
                    disabled={loading}
                    className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-100 text-sm disabled:opacity-50"
                  >
                    <option value="5min">5 دقائق</option>
                    <option value="15min">15 دقيقة</option>
                    <option value="1h">ساعة واحدة</option>
                    <option value="4h">4 ساعات</option>
                  </select>
                </div>

                {/* Start Date */}
                <div>
                  <label className="block text-sm text-slate-400 mb-2">تاريخ البداية</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    disabled={loading}
                    className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-100 text-sm disabled:opacity-50"
                  />
                </div>

                {/* End Date */}
                <div>
                  <label className="block text-sm text-slate-400 mb-2">تاريخ النهاية</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    disabled={loading}
                    className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-100 text-sm disabled:opacity-50"
                  />
                </div>

                {/* Initial Capital */}
                <div>
                  <label className="block text-sm text-slate-400 mb-2">رأس المال الأولي ($)</label>
                  <input
                    type="number"
                    value={initialCapital}
                    onChange={(e) => setInitialCapital(Number(e.target.value))}
                    disabled={loading}
                    className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-100 text-sm disabled:opacity-50"
                  />
                </div>

                {/* Risk Per Trade */}
                <div>
                  <label className="block text-sm text-slate-400 mb-2">المخاطرة لكل صفقة (%)</label>
                  <input
                    type="number"
                    value={riskPerTrade}
                    onChange={(e) => setRiskPerTrade(Number(e.target.value))}
                    disabled={loading}
                    step="0.1"
                    className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-slate-100 text-sm disabled:opacity-50"
                  />
                </div>

                {/* Buttons */}
                <div className="space-y-2 pt-4">
                  <button
                    onClick={runBacktest}
                    disabled={loading}
                    className="w-full bg-gold-500/20 hover:bg-gold-500/30 border border-gold-500/50 text-gold-300 py-2 rounded font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    {loading ? 'جاري الاختبار...' : 'تشغيل الاختبار'}
                  </button>
                  <button
                    onClick={resetForm}
                    disabled={loading}
                    className="w-full bg-slate-700/50 hover:bg-slate-700 border border-slate-600 text-slate-300 py-2 rounded font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    <RotateCcw className="w-4 h-4" />
                    إعادة تعيين
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-3 space-y-6">
            {error && (
              <div className="card bg-red-900/20 border-red-700 p-4">
                <div className="flex items-start gap-3 text-red-400">
                  <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              </div>
            )}

            {results ? (
              <>
                {/* Performance Summary */}
                <div className="card">
                  <div className="card-header border-b border-slate-700/50 pb-4">
                    <h2 className="text-xl font-semibold text-gold-400">ملخص الأداء</h2>
                  </div>
                  <div className="card-body">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {/* Total Return */}
                      <div className="bg-slate-900/50 rounded p-4">
                        <div className="text-sm text-slate-400 mb-1">العائد الكلي</div>
                        <div className="text-2xl font-bold text-emerald-400">
                          {results.total_return.toFixed(2)}%
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          ${(initialCapital * (1 + results.total_return / 100)).toFixed(2)}
                        </div>
                      </div>

                      {/* Win Rate */}
                      <div className="bg-slate-900/50 rounded p-4">
                        <div className="text-sm text-slate-400 mb-1">نسبة الفوز</div>
                        <div className="text-2xl font-bold text-gold-400">{results.win_rate.toFixed(1)}%</div>
                        <div className="text-xs text-slate-500 mt-1">
                          {results.winning_trades}/{results.total_trades} صفقة
                        </div>
                      </div>

                      {/* Max Drawdown */}
                      <div className="bg-slate-900/50 rounded p-4">
                        <div className="text-sm text-slate-400 mb-1">أقصى خسارة</div>
                        <div className="text-2xl font-bold text-red-400">{results.max_drawdown.toFixed(2)}%</div>
                        <div className="text-xs text-slate-500 mt-1">الانخفاض الأقصى</div>
                      </div>

                      {/* Sharpe Ratio */}
                      <div className="bg-slate-900/50 rounded p-4">
                        <div className="text-sm text-slate-400 mb-1">نسبة شارب</div>
                        <div className="text-2xl font-bold text-blue-400">{results.sharpe_ratio.toFixed(2)}</div>
                        <div className="text-xs text-slate-500 mt-1">العائد المعدل بالمخاطرة</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Trade Statistics */}
                <div className="card">
                  <div className="card-header border-b border-slate-700/50 pb-4">
                    <h2 className="text-xl font-semibold text-gold-400">إحصائيات الصفقات</h2>
                  </div>
                  <div className="card-body">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded bg-emerald-900/30 flex items-center justify-center">
                          <TrendingUp className="w-5 h-5 text-emerald-400" />
                        </div>
                        <div>
                          <div className="text-sm text-slate-400">الصفقات الرابحة</div>
                          <div className="text-xl font-bold text-emerald-400">{results.winning_trades}</div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded bg-red-900/30 flex items-center justify-center">
                          <TrendingDown className="w-5 h-5 text-red-400" />
                        </div>
                        <div>
                          <div className="text-sm text-slate-400">الصفقات الخاسرة</div>
                          <div className="text-xl font-bold text-red-400">{results.losing_trades}</div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded bg-blue-900/30 flex items-center justify-center">
                          <span className="text-sm font-bold text-blue-400">∑</span>
                        </div>
                        <div>
                          <div className="text-sm text-slate-400">إجمالي الصفقات</div>
                          <div className="text-xl font-bold text-blue-400">{results.total_trades}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Recent Trades */}
                <div className="card">
                  <div className="card-header border-b border-slate-700/50 pb-4">
                    <h2 className="text-xl font-semibold text-gold-400">آخر الصفقات</h2>
                  </div>
                  <div className="card-body overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-700/50">
                          <th className="text-right py-2 px-2 text-slate-400">سعر الدخول</th>
                          <th className="text-right py-2 px-2 text-slate-400">سعر الخروج</th>
                          <th className="text-right py-2 px-2 text-slate-400">الربح/الخسارة</th>
                          <th className="text-right py-2 px-2 text-slate-400">النسبة المئوية</th>
                          <th className="text-right py-2 px-2 text-slate-400">المدة</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.trades.slice(0, 5).map((trade, idx) => (
                          <tr key={idx} className="border-b border-slate-700/20 hover:bg-slate-700/10">
                            <td className="py-3 px-2 text-slate-300">${trade.entry_price.toFixed(2)}</td>
                            <td className="py-3 px-2 text-slate-300">${trade.exit_price.toFixed(2)}</td>
                            <td
                              className={`py-3 px-2 font-semibold ${
                                trade.profit_loss >= 0 ? 'text-emerald-400' : 'text-red-400'
                              }`}
                            >
                              {trade.profit_loss >= 0 ? '+' : ''}${trade.profit_loss.toFixed(2)}
                            </td>
                            <td
                              className={`py-3 px-2 font-semibold ${
                                trade.profit_loss_pct >= 0 ? 'text-emerald-400' : 'text-red-400'
                              }`}
                            >
                              {trade.profit_loss_pct >= 0 ? '+' : ''}
                              {(trade.profit_loss_pct * 100).toFixed(2)}%
                            </td>
                            <td className="py-3 px-2 text-slate-400">{trade.duration_bars} شموع</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            ) : (
              <div className="card h-96 flex items-center justify-center">
                <div className="text-center">
                  <Play className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                  <p className="text-slate-400">اضغط على "تشغيل الاختبار" لبدء الاختبار</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
