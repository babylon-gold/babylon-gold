'use client'

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
import { Analysis } from '@/lib/api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface CandlestickChartProps {
  analysis: Analysis
}

export default function CandlestickChart({ analysis }: CandlestickChartProps) {
  // For now, show a simplified price visualization with EMAs
  const currentPrice = analysis.current_price
  const support = analysis.indicators.support_level || currentPrice * 0.95
  const resistance = analysis.indicators.resistance_level || currentPrice * 1.05

  const data = {
    labels: ['الدعم', 'EMA200', 'EMA50', 'EMA20', 'السعر', 'المقاومة'],
    datasets: [
      {
        label: 'السعر الحالي',
        data: [
          support,
          analysis.indicators.ema_200 || currentPrice,
          analysis.indicators.ema_50 || currentPrice,
          analysis.indicators.ema_20 || currentPrice,
          currentPrice,
          resistance,
        ],
        borderColor: '#f2b631',
        backgroundColor: 'rgba(242, 182, 49, 0.1)',
        fill: false,
        tension: 0.4,
        pointRadius: 6,
        pointBackgroundColor: '#f2b631',
        pointBorderColor: '#1e293b',
        pointBorderWidth: 2,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        labels: {
          color: '#cbd5e1',
          font: {
            family: "'Cairo', sans-serif",
            size: 12,
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(30, 41, 59, 0.9)',
        titleColor: '#f2b631',
        bodyColor: '#e2e8f0',
        borderColor: '#f2b631',
        borderWidth: 1,
        padding: 12,
        titleFont: {
          family: "'Cairo', sans-serif",
        },
        bodyFont: {
          family: "'Cairo', sans-serif",
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(71, 85, 105, 0.2)',
          drawBorder: false,
        },
        ticks: {
          color: '#94a3b8',
          font: {
            family: "'Cairo', sans-serif",
          },
          callback: function (value: any) {
            return '$' + value.toFixed(0)
          },
        },
      },
      x: {
        grid: {
          display: false,
          drawBorder: false,
        },
        ticks: {
          color: '#94a3b8',
          font: {
            family: "'Cairo', sans-serif",
          },
        },
      },
    },
  }

  return (
    <div className="w-full h-64">
      <Line data={data} options={options} />
    </div>
  )
}
