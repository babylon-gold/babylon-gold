'use client'

import { useEffect, useState, useCallback } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react'
import { fetchCandlesWithIndicators } from '@/lib/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

interface EnhancedCandlestickChartProps {
  timeframe: string
}

export default function EnhancedCandlestickChart({ timeframe }: EnhancedCandlestickChartProps) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [visibleCandles, setVisibleCandles] = useState(50)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      const candles = await fetchCandlesWithIndicators(timeframe)

      console.log('Chart data received:', { isArray: Array.isArray(candles), length: candles?.length, type: typeof candles })

      // Response is already an array of CandleWithIndicators
      if (!Array.isArray(candles) || candles.length === 0) {
        throw new Error(`No candle data available. Got: ${typeof candles}, length: ${candles?.length}`)
      }

      const displayCandles = candles.slice(-visibleCandles)
      const labels = displayCandles.map((c: any) =>
        new Date(c.timestamp_utc).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      )

      const closeData = displayCandles.map((c: any) => c.close)
      const ema20Data = displayCandles.map((c: any) => c.ema20)
      const ema50Data = displayCandles.map((c: any) => c.ema50)
      const ema200Data = displayCandles.map((c: any) => c.ema200)

      setData({
        labels,
        datasets: [
          {
            label: 'Close Price',
            data: closeData,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.05)',
            fill: true,
            tension: 0.3,
            pointRadius: 2,
            borderWidth: 2,
          },
          {
            label: 'EMA 200',
            data: ema200Data,
            borderColor: '#8b5cf6',
            fill: false,
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 1.5,
            borderDashOffset: 5,
          },
          {
            label: 'EMA 50',
            data: ema50Data,
            borderColor: '#f59e0b',
            fill: false,
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 1.5,
          },
          {
            label: 'EMA 20',
            data: ema20Data,
            borderColor: '#f2b631',
            fill: false,
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 2,
          },
        ],
      })
      setError(null)
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        setError(err.message || 'Failed to load chart data')
      }
    } finally {
      setLoading(false)
    }
  }, [timeframe, visibleCandles])

  useEffect(() => {
    loadData()
    const interval = setInterval(() => loadData(), 60000)
    return () => {
      clearInterval(interval)
    }
  }, [loadData])

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        labels: { color: '#cbd5e1', font: { size: 11, family: "'Cairo', sans-serif" } },
      },
      tooltip: {
        backgroundColor: 'rgba(30, 41, 59, 0.95)',
        titleColor: '#f2b631',
        bodyColor: '#e2e8f0',
        borderColor: '#f2b631',
        borderWidth: 1,
        padding: 8,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: { color: 'rgba(71, 85, 105, 0.2)' },
        ticks: { color: '#94a3b8', font: { family: "'Cairo', sans-serif", size: 10 } },
      },
      x: {
        grid: { display: false },
        ticks: { color: '#94a3b8', font: { family: "'Cairo', sans-serif", size: 10 } },
      },
    },
  }

  if (loading) {
    return <div className="h-80 flex items-center justify-center text-slate-400">جاري تحميل البيانات...</div>
  }

  if (error) {
    return <div className="h-80 flex items-center justify-center text-red-400">خطأ: {error}</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button
          onClick={() => setVisibleCandles(Math.max(20, visibleCandles - 10))}
          className="p-2 hover:bg-slate-700/50 rounded text-sm text-gold-400"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setVisibleCandles(Math.min(150, visibleCandles + 10))}
          className="p-2 hover:bg-slate-700/50 rounded text-sm text-gold-400"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => setVisibleCandles(50)}
          className="p-2 hover:bg-slate-700/50 rounded text-sm text-gold-400"
          title="Reset"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <div className="text-sm text-slate-400 ml-auto">
          عرض {visibleCandles} شمعة / 150
        </div>
      </div>
      <div className="w-full h-72">
        {data && <Line data={data} options={options} />}
      </div>
    </div>
  )
}
