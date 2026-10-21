'use client'

import { useEffect, useState } from 'react'
import { Line, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { fetchCandlesWithIndicators } from '@/lib/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend)

interface IndicatorChartsProps {
  timeframe: string
}

export default function IndicatorCharts({ timeframe }: IndicatorChartsProps) {
  const [rsiData, setRsiData] = useState<any>(null)
  const [adxData, setAdxData] = useState<any>(null)
  const [atrData, setAtrData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const candles = await fetchCandlesWithIndicators(timeframe, 100)

        // Response is already an array of CandleWithIndicators
        if (!Array.isArray(candles) || candles.length === 0) {
          throw new Error('No candle data available')
        }
        const labels = candles.map((c: any) =>
          new Date(c.timestamp_utc).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
        )

        // RSI Chart
        setRsiData({
          labels,
          datasets: [
            {
              label: 'RSI(14)',
              data: candles.map((c: any) => c.rsi14),
              borderColor: '#f59e0b',
              backgroundColor: 'rgba(245, 158, 11, 0.05)',
              fill: true,
              tension: 0.3,
              pointRadius: 1,
              borderWidth: 2,
            },
          ],
        })

        // ADX Chart
        setAdxData({
          labels,
          datasets: [
            {
              label: 'ADX(14)',
              data: candles.map((c: any) => c.adx14),
              borderColor: '#8b5cf6',
              backgroundColor: 'rgba(139, 92, 246, 0.05)',
              fill: true,
              tension: 0.3,
              pointRadius: 1,
              borderWidth: 2,
            },
          ],
        })

        // ATR Chart
        setAtrData({
          labels,
          datasets: [
            {
              label: 'ATR(14)',
              data: candles.map((c: any) => c.atr14),
              backgroundColor: '#f2b631',
              borderColor: '#d97706',
              borderWidth: 0,
            },
          ],
        })

        setLoading(false)
      } catch (err) {
        console.error('Failed to load indicator data:', err)
        setLoading(false)
      }
    }

    loadData()
    const interval = setInterval(loadData, 60000)
    return () => clearInterval(interval)
  }, [timeframe])

  const chartOptions = {
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
      },
    },
    scales: {
      y: {
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
    return <div className="text-slate-400 text-center py-8">جاري تحميل المؤشرات...</div>
  }

  return (
    <div className="space-y-6">
      {/* RSI */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold">RSI(14) - مؤشر القوة النسبية</h3>
        </div>
        <div className="card-body h-40">
          {rsiData && <Line data={rsiData} options={chartOptions} />}
        </div>
      </div>

      {/* ADX */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold">ADX(14) - مؤشر الاتجاه المتوسط</h3>
        </div>
        <div className="card-body h-40">
          {adxData && <Line data={adxData} options={chartOptions} />}
        </div>
      </div>

      {/* ATR */}
      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold">ATR(14) - متوسط نطاق التذبذب</h3>
        </div>
        <div className="card-body h-40">
          {atrData && <Bar data={atrData} options={chartOptions} />}
        </div>
      </div>

      {/* Legend */}
      <div className="card bg-slate-900/50 text-sm text-slate-400 space-y-2">
        <div>
          <strong className="text-slate-300">📊 RSI:</strong> فوق 70 مرتفع جداً (بيع), تحت 30 منخفض جداً (شراء)
        </div>
        <div>
          <strong className="text-slate-300">📈 ADX:</strong> فوق 40 اتجاه قوي جداً, تحت 25 اتجاه ضعيف
        </div>
        <div>
          <strong className="text-slate-300">📉 ATR:</strong> قياس التقلبات - أعلى = تقلبات أكثر
        </div>
      </div>
    </div>
  )
}
