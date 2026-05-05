import { useEffect, useRef } from 'react'
import { createChart, IChartApi, ISeriesApi, LineData, Time } from 'lightweight-charts'

interface EquityCurveChartProps {
  data: { date: string; equity: number | string }[]
  className?: string
}

export function EquityCurveChart({ data, className = '' }: EquityCurveChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const lineSeriesRef = useRef<ISeriesApi<'Line'> | null>(null)

  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#2B2B43',
      },
      timeScale: {
        borderColor: '#2B2B43',
        timeVisible: true,
      },
    })

    const lineSeries = chart.addLineSeries({
      color: '#2563eb',
      lineWidth: 2,
    })

    chartRef.current = chart
    lineSeriesRef.current = lineSeries

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        const { width, height } = chartContainerRef.current.getBoundingClientRect()
        chartRef.current.applyOptions({ width, height })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  useEffect(() => {
    if (!lineSeriesRef.current || data.length === 0) return

    const chartData: LineData[] = data.map((item) => ({
      time: (new Date(item.date).getTime() / 1000) as Time,
      value: typeof item.equity === 'string' ? parseFloat(item.equity) : item.equity,
    }))

    lineSeriesRef.current.setData(chartData)
    chartRef.current?.timeScale().fitContent()
  }, [data])

  return (
    <div
      ref={chartContainerRef}
      className={`w-full h-full ${className}`}
      style={{ minHeight: '300px' }}
    />
  )
}
