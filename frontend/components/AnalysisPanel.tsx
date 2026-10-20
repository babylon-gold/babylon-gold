'use client'

import { ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

interface AnalysisPanelProps {
  summary: string
}

export default function AnalysisPanel({ summary }: AnalysisPanelProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="mt-8">
      <div
        className="card cursor-pointer hover:border-gold-500/50 transition-all"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="card-header flex items-center justify-between">
          <h3 className="font-semibold text-lg">التحليل التفصيلي بالعربية</h3>
          {expanded ? (
            <ChevronUp className="w-5 h-5 text-gold-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gold-400" />
          )}
        </div>
        {expanded && (
          <div className="card-body">
            <div className="whitespace-pre-wrap text-sm text-slate-300 leading-relaxed font-mono bg-slate-900/50 p-4 rounded border border-slate-700">
              {summary}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
