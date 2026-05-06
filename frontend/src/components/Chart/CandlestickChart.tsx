import { useEffect, useRef } from 'react'
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time } from 'lightweight-charts'
import type { OHLCVData } from '../../types'

interface CandlestickChartProps {
  data: OHLCVData[]
  onVisibleTimeRangeChange?: (from: Date, to: Date) => void
  onCrosshairMove?: (data: OHLCVData | null) => void
  className?: string
}

export function CandlestickChart({
  data,
  onVisibleTimeRangeChange,
  onCrosshairMove,
  className = '',
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return

    // Create chart
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
        mode: 1, // CrosshairMode.Magnet
        vertLine: {
          color: '#758696',
          labelBackgroundColor: '#758696',
        },
        horzLine: {
          color: '#758696',
          labelBackgroundColor: '#758696',
        },
      },
      rightPriceScale: {
        borderColor: '#2B2B43',
      },
      timeScale: {
        borderColor: '#2B2B43',
        timeVisible: true,
      },
      handleScroll: {
        vertTouchDrag: false,
      },
    })

    // Create candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',      // Green for up
      downColor: '#ef4444',    // Red for down
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    })

    // Handle crosshair move
    chart.subscribeCrosshairMove((param) => {
      if (!param.time || !onCrosshairMove) {
        onCrosshairMove?.(null)
        return
      }

      const dataPoint = data.find(
        (d) => new Date(d.date).getTime() / 1000 === param.time
      )
      onCrosshairMove(dataPoint || null)
    })

    // Handle visible range change
    if (onVisibleTimeRangeChange) {
      chart.timeScale().subscribeVisibleTimeRangeChange(() => {
        const range = chart.timeScale().getVisibleLogicalRange()
        if (range) {
          const from = Math.floor(range.from)
          const to = Math.ceil(range.to)
          if (data[from] && data[to]) {
            onVisibleTimeRangeChange(
              new Date(data[from].date),
              new Date(data[to].date)
            )
          }
        }
      })
    }

    chartRef.current = chart
    candlestickSeriesRef.current = candlestickSeries

    // Handle resize
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
  }, [data, onCrosshairMove, onVisibleTimeRangeChange])

  // Update chart data
  useEffect(() => {
    if (!candlestickSeriesRef.current || data.length === 0) return

    const chartData: CandlestickData[] = data.map((item) => ({
      time: (new Date(item.date).getTime() / 1000) as Time,
      open: parseFloat(item.open),
      high: parseFloat(item.high),
      low: parseFloat(item.low),
      close: parseFloat(item.close),
    }))

    candlestickSeriesRef.current.setData(chartData)

    // Fit content after data update
    chartRef.current?.timeScale().fitContent()
  }, [data])

  return (
    <div
      ref={chartContainerRef}
      className={`w-full h-full ${className}`}
      style={{ minHeight: '400px' }}
    />
  )
}
