'use client'

import { useEffect, useState } from 'react'
import { User, Settings, LogOut, TrendingUp, TrendingDown, DollarSign, BarChart3, Eye, EyeOff, Edit2 } from 'lucide-react'

interface UserAccount {
  id: string
  name: string
  email: string
  country: string
  account_type: string
  account_created: string
  profile_image?: string
}

interface AccountStats {
  total_balance: number
  equity: number
  available_balance: number
  used_margin: number
  margin_level: number
  total_trades: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  total_profit_loss: number
  profit_loss_pct: number
  max_drawdown: number
  best_trade: number
  worst_trade: number
  avg_win: number
  avg_loss: number
}

interface RecentTrade {
  id: string
  symbol: string
  type: string
  entry_time: string
  exit_time?: string
  entry_price: number
  exit_price?: number
  size: number
  profit_loss: number
  profit_loss_pct: number
  status: string
}

export default function AccountPage() {
  const [user, setUser] = useState<UserAccount | null>(null)
  const [stats, setStats] = useState<AccountStats | null>(null)
  const [recentTrades, setRecentTrades] = useState<RecentTrade[]>([])
  const [loading, setLoading] = useState(true)
  const [showBalance, setShowBalance] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    // Simulate loading user data
    setTimeout(() => {
      setUser({
        id: 'user_001',
        name: 'أحمد محمود',
        email: 'thairaljaabi1980@gmail.com',
        country: 'العراق',
        account_type: 'Pro Trader',
        account_created: '2026-01-15',
        profile_image: ''
      })

      setStats({
        total_balance: 25000,
        equity: 24850,
        available_balance: 24850,
        used_margin: 0,
        margin_level: 999,
        total_trades: 127,
        winning_trades: 78,
        losing_trades: 49,
        win_rate: 61.4,
        total_profit_loss: 4850,
        profit_loss_pct: 19.4,
        max_drawdown: -8.5,
        best_trade: 450,
        worst_trade: -320,
        avg_win: 125.5,
        avg_loss: -95.3
      })

      setRecentTrades([
        {
          id: 'trade_001',
          symbol: 'XAU/USD',
          type: 'BUY',
          entry_time: '2026-10-21 14:30',
          exit_time: '2026-10-21 15:45',
          entry_price: 4120.50,
          exit_price: 4135.20,
          size: 1.5,
          profit_loss: 220.5,
          profit_loss_pct: 0.36,
          status: 'مغلقة'
        },
        {
          id: 'trade_002',
          symbol: 'XAU/USD',
          type: 'SELL',
          entry_time: '2026-10-21 13:15',
          exit_time: '2026-10-21 14:00',
          entry_price: 4118.00,
          exit_price: 4125.50,
          size: 1.0,
          profit_loss: -75.0,
          profit_loss_pct: -0.18,
          status: 'مغلقة'
        },
        {
          id: 'trade_003',
          symbol: 'XAU/USD',
          type: 'BUY',
          entry_time: '2026-10-21 11:45',
          entry_price: 4115.00,
          size: 2.0,
          profit_loss: 185.0,
          profit_loss_pct: 0.22,
          status: 'مفتوحة'
        },
        {
          id: 'trade_004',
          symbol: 'XAU/USD',
          type: 'BUY',
          entry_time: '2026-10-20 16:30',
          exit_time: '2026-10-21 09:00',
          entry_price: 4110.50,
          exit_price: 4140.00,
          size: 1.2,
          profit_loss: 354.0,
          profit_loss_pct: 0.71,
          status: 'مغلقة'
        },
        {
          id: 'trade_005',
          symbol: 'XAU/USD',
          type: 'SELL',
          entry_time: '2026-10-20 14:00',
          exit_time: '2026-10-20 15:30',
          entry_price: 4130.00,
          exit_price: 4118.50,
          size: 0.8,
          profit_loss: 92.0,
          profit_loss_pct: 0.28,
          status: 'مغلقة'
        }
      ])

      setLoading(false)
    }, 800)
  }, [])

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin inline-block w-8 h-8 border-2 border-gold-400 border-t-transparent rounded-full"></div>
            <p className="text-slate-400 ml-4">جاري تحميل البيانات...</p>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* User Profile Header */}
        <div className="card p-6 border border-slate-700/50">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-start gap-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center">
                <User className="w-10 h-10 text-slate-900" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gold-400 mb-1">{user?.name}</h1>
                <p className="text-slate-400 mb-2">{user?.email}</p>
                <div className="flex gap-4 text-sm">
                  <span className="text-slate-400">
                    <strong>البلد:</strong> {user?.country}
                  </span>
                  <span className="text-slate-400">
                    <strong>نوع الحساب:</strong> {user?.account_type}
                  </span>
                  <span className="text-slate-400">
                    <strong>تاريخ الإنشاء:</strong> {user?.account_created}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <button className="p-2 hover:bg-slate-700/50 rounded-lg transition text-slate-400 hover:text-gold-400">
                <Edit2 className="w-5 h-5" />
              </button>
              <button className="p-2 hover:bg-slate-700/50 rounded-lg transition text-slate-400 hover:text-gold-400">
                <Settings className="w-5 h-5" />
              </button>
              <button className="p-2 hover:bg-red-900/20 rounded-lg transition text-red-400">
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Account Balance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card p-4 border border-gold-500/30 bg-slate-900/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm">الرصيد الإجمالي</span>
              <DollarSign className="w-4 h-4 text-gold-400" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gold-400">
                {showBalance ? `$${stats?.total_balance.toLocaleString()}` : '••••••'}
              </span>
              <button onClick={() => setShowBalance(!showBalance)} className="text-slate-500 hover:text-slate-400">
                {showBalance ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="card p-4 border border-emerald-500/30 bg-slate-900/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm">حقوق الملكية</span>
              <TrendingUp className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400">
              ${stats?.equity.toLocaleString()}
            </div>
            <div className="text-xs text-emerald-400 mt-1">متاح</div>
          </div>

          <div className="card p-4 border border-amber-500/30 bg-slate-900/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm">معدل الفوز</span>
              <BarChart3 className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-amber-400">
              {stats?.win_rate.toFixed(1)}%
            </div>
            <div className="text-xs text-slate-500 mt-1">{stats?.winning_trades}/{stats?.total_trades}</div>
          </div>

          <div className={`card p-4 border-b-2 bg-slate-900/50 ${(stats?.total_profit_loss || 0) >= 0 ? 'border-emerald-500/30' : 'border-red-500/30'}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm">الربح/الخسارة</span>
              {(stats?.total_profit_loss || 0) >= 0 ? (
                <TrendingUp className="w-4 h-4 text-emerald-400" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-400" />
              )}
            </div>
            <div className={`text-2xl font-bold ${(stats?.total_profit_loss || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              ${stats?.total_profit_loss.toLocaleString()}
            </div>
            <div className={`text-xs mt-1 ${(stats?.total_profit_loss || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {(stats?.profit_loss_pct || 0) >= 0 ? '+' : ''}{stats?.profit_loss_pct.toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-slate-700/50 mb-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 font-semibold border-b-2 transition ${
              activeTab === 'overview'
                ? 'text-gold-400 border-gold-400'
                : 'text-slate-400 border-transparent hover:text-slate-300'
            }`}
          >
            النظرة العامة
          </button>
          <button
            onClick={() => setActiveTab('trades')}
            className={`px-4 py-2 font-semibold border-b-2 transition ${
              activeTab === 'trades'
                ? 'text-gold-400 border-gold-400'
                : 'text-slate-400 border-transparent hover:text-slate-300'
            }`}
          >
            الصفقات الأخيرة
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 font-semibold border-b-2 transition ${
              activeTab === 'settings'
                ? 'text-gold-400 border-gold-400'
                : 'text-slate-400 border-transparent hover:text-slate-300'
            }`}
          >
            الإعدادات
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Performance Stats */}
            <div className="card p-6">
              <h3 className="text-xl font-semibold text-gold-400 mb-4">إحصائيات الأداء</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center pb-2 border-b border-slate-700/30">
                  <span className="text-slate-400">إجمالي الصفقات</span>
                  <span className="font-semibold text-slate-200">{stats?.total_trades}</span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b border-slate-700/30">
                  <span className="text-slate-400">صفقات رابحة</span>
                  <span className="font-semibold text-emerald-400">{stats?.winning_trades}</span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b border-slate-700/30">
                  <span className="text-slate-400">صفقات خاسرة</span>
                  <span className="font-semibold text-red-400">{stats?.losing_trades}</span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b border-slate-700/30">
                  <span className="text-slate-400">أفضل صفقة</span>
                  <span className="font-semibold text-emerald-400">+${stats?.best_trade.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b border-slate-700/30">
                  <span className="text-slate-400">أسوأ صفقة</span>
                  <span className="font-semibold text-red-400">${stats?.worst_trade.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b border-slate-700/30">
                  <span className="text-slate-400">متوسط الربح</span>
                  <span className="font-semibold text-emerald-400">+${stats?.avg_win.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">متوسط الخسارة</span>
                  <span className="font-semibold text-red-400">${stats?.avg_loss.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Risk Metrics */}
            <div className="card p-6">
              <h3 className="text-xl font-semibold text-gold-400 mb-4">مؤشرات المخاطر</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-slate-400 text-sm">الهامش المستخدم</span>
                    <span className="text-slate-200 font-semibold">{stats?.used_margin}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-700/50 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400"
                      style={{ width: `${(stats?.used_margin || 0) / 100 * 100}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-slate-400 text-sm">مستوى الهامش</span>
                    <span className="text-slate-200 font-semibold">{stats?.margin_level}</span>
                  </div>
                  <div className="w-full h-2 bg-slate-700/50 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-gold-500 to-gold-400"
                      style={{ width: `${Math.min(((stats?.margin_level || 100) / 200) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>

                <div className="pt-2 space-y-2 mt-4">
                  <div className="flex justify-between items-center p-2 bg-slate-900/50 rounded">
                    <span className="text-slate-400">أقصى خسارة</span>
                    <span className="text-red-400 font-semibold">{stats?.max_drawdown.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-slate-900/50 rounded">
                    <span className="text-slate-400">الرصيد المتاح</span>
                    <span className="text-emerald-400 font-semibold">${stats?.available_balance.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Trades Tab */}
        {activeTab === 'trades' && (
          <div className="card p-6">
            <h3 className="text-xl font-semibold text-gold-400 mb-4">الصفقات الأخيرة</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50">
                    <th className="text-right py-3 px-4 text-slate-400">الرمز</th>
                    <th className="text-right py-3 px-4 text-slate-400">النوع</th>
                    <th className="text-right py-3 px-4 text-slate-400">وقت الدخول</th>
                    <th className="text-right py-3 px-4 text-slate-400">سعر الدخول</th>
                    <th className="text-right py-3 px-4 text-slate-400">الحجم</th>
                    <th className="text-right py-3 px-4 text-slate-400">الربح/الخسارة</th>
                    <th className="text-right py-3 px-4 text-slate-400">الحالة</th>
                  </tr>
                </thead>
                <tbody>
                  {recentTrades.map((trade) => (
                    <tr key={trade.id} className="border-b border-slate-700/30 hover:bg-slate-800/30 transition">
                      <td className="py-3 px-4 text-slate-200">{trade.symbol}</td>
                      <td className="py-3 px-4">
                        <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                          trade.type === 'BUY'
                            ? 'bg-emerald-500/20 text-emerald-400'
                            : 'bg-red-500/20 text-red-400'
                        }`}>
                          {trade.type === 'BUY' ? '🔺 شراء' : '🔻 بيع'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400">{trade.entry_time}</td>
                      <td className="py-3 px-4 text-slate-200">${trade.entry_price.toFixed(2)}</td>
                      <td className="py-3 px-4 text-slate-200">{trade.size}</td>
                      <td className={`py-3 px-4 font-semibold ${
                        trade.profit_loss >= 0 ? 'text-emerald-400' : 'text-red-400'
                      }`}>
                        {trade.profit_loss >= 0 ? '+' : ''}${trade.profit_loss.toFixed(2)} ({trade.profit_loss_pct >= 0 ? '+' : ''}{trade.profit_loss_pct.toFixed(2)}%)
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                          trade.status === 'مفتوحة'
                            ? 'bg-blue-500/20 text-blue-400'
                            : 'bg-slate-700/30 text-slate-400'
                        }`}>
                          {trade.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="card p-6">
              <h3 className="text-xl font-semibold text-gold-400 mb-4">إعدادات الحساب</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-slate-400 text-sm mb-2">البريد الإلكتروني</label>
                  <input type="email" value={user?.email} disabled className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded text-slate-300 disabled:opacity-50" />
                </div>
                <div>
                  <label className="block text-slate-400 text-sm mb-2">الاسم الكامل</label>
                  <input type="text" value={user?.name} disabled className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded text-slate-300 disabled:opacity-50" />
                </div>
                <div>
                  <label className="block text-slate-400 text-sm mb-2">البلد</label>
                  <input type="text" value={user?.country} disabled className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded text-slate-300 disabled:opacity-50" />
                </div>
              </div>
            </div>

            <div className="card p-6">
              <h3 className="text-xl font-semibold text-gold-400 mb-4">تفضيلات التداول</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded border border-slate-700/30">
                  <span className="text-slate-400">تفعيل الإشعارات</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5 rounded cursor-pointer" />
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded border border-slate-700/30">
                  <span className="text-slate-400">إظهار السعر الكامل</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5 rounded cursor-pointer" />
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded border border-slate-700/30">
                  <span className="text-slate-400">الوضع الداكن</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5 rounded cursor-pointer" />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
