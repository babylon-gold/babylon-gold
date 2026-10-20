'use client'

import { Loader2 } from 'lucide-react'

export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-96">
      <div className="text-center">
        <Loader2 className="w-12 h-12 text-gold-400 animate-spin mx-auto mb-4" />
        <p className="text-slate-400">جاري تحميل البيانات...</p>
      </div>
    </div>
  )
}
