'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { BarChart3, TrendingUp, LineChart, Settings, Bell, CandlestickChart, Zap, User } from 'lucide-react'

export default function Navigation() {
  const pathname = usePathname()

  const isActive = (href: string) => pathname === href

  return (
    <nav className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur border-b border-slate-700/50">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        {/* Logo/Brand */}
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center">
            <span className="text-slate-900 font-bold text-sm">B</span>
          </div>
          <span className="text-gold-400 font-bold hidden sm:inline">Babylon AI</span>
        </Link>

        {/* Links */}
        <div className="flex items-center gap-1">
          <Link
            href="/"
            className={`flex items-center gap-2 px-4 py-2 rounded transition text-sm ${
              isActive('/')
                ? 'bg-gold-500/20 text-gold-300 border border-gold-500/50'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span className="hidden sm:inline">لوحة التحكم</span>
          </Link>

          <Link
            href="/account"
            className={`flex items-center gap-2 px-4 py-2 rounded transition text-sm ${
              isActive('/account')
                ? 'bg-gold-500/20 text-gold-300 border border-gold-500/50'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <User className="w-4 h-4" />
            <span className="hidden sm:inline">حسابي</span>
          </Link>

          <Link
            href="/signals"
            className={`flex items-center gap-2 px-4 py-2 rounded transition text-sm ${
              isActive('/signals')
                ? 'bg-gold-500/20 text-gold-300 border border-gold-500/50'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            <span className="hidden sm:inline">الإشارات</span>
          </Link>

          <Link
            href="/charts"
            className={`flex items-center gap-2 px-4 py-2 rounded transition text-sm ${
              isActive('/charts')
                ? 'bg-gold-500/20 text-gold-300 border border-gold-500/50'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <CandlestickChart className="w-4 h-4" />
            <span className="hidden sm:inline">الرسوم البيانية</span>
          </Link>

          <Link
            href="/backtesting"
            className={`flex items-center gap-2 px-4 py-2 rounded transition text-sm ${
              isActive('/backtesting')
                ? 'bg-gold-500/20 text-gold-300 border border-gold-500/50'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Zap className="w-4 h-4" />
            <span className="hidden sm:inline">الاختبار</span>
          </Link>

          <Link
            href="/performance"
            className={`flex items-center gap-2 px-4 py-2 rounded transition text-sm ${
              isActive('/performance')
                ? 'bg-gold-500/20 text-gold-300 border border-gold-500/50'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <LineChart className="w-4 h-4" />
            <span className="hidden sm:inline">الأداء</span>
          </Link>

          <Link
            href="/admin"
            className={`flex items-center gap-2 px-4 py-2 rounded transition text-sm ${
              isActive('/admin')
                ? 'bg-gold-500/20 text-gold-300 border border-gold-500/50'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Settings className="w-4 h-4" />
            <span className="hidden sm:inline">الإدارة</span>
          </Link>

          <Link
            href="/notifications"
            className={`flex items-center gap-2 px-4 py-2 rounded transition text-sm ${
              isActive('/notifications')
                ? 'bg-gold-500/20 text-gold-300 border border-gold-500/50'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Bell className="w-4 h-4" />
            <span className="hidden sm:inline">الإشعارات</span>
          </Link>
        </div>

        {/* Status Indicator */}
        <div className="text-xs text-slate-500">
          <span className="inline-block w-2 h-2 bg-emerald-500 rounded-full mr-2 animate-pulse"></span>
          تاريخية
        </div>
      </div>
    </nav>
  )
}
