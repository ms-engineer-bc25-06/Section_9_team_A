"use client"

import { useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Mic, Volume2, Activity, Wifi, AlertTriangle } from 'lucide-react'

interface AudioQualityMetrics {
  volume: number
  clarity: number
  latency: number
  packetLoss: number
  jitter: number
}

interface AudioQualityMonitorProps {
  metrics: AudioQualityMetrics
  isStreaming: boolean
  error?: string | null
}

export const AudioQualityMonitor: React.FC<AudioQualityMonitorProps> = ({
  metrics,
  isStreaming,
  error,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationFrameRef = useRef<number>()

  // 音声波形の描画
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !isStreaming) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const drawWaveform = () => {
      const { width, height } = canvas
      ctx.clearRect(0, 0, width, height)

      // 背景
      ctx.fillStyle = '#f8fafc'
      ctx.fillRect(0, 0, width, height)

      // 波形の描画
      ctx.strokeStyle = '#3b82f6'
      ctx.lineWidth = 2
      ctx.beginPath()

      const centerY = height / 2
      const barWidth = width / 50
      
      for (let i = 0; i < 50; i++) {
        const x = i * barWidth
        const barHeight = (Math.random() * 0.5 + 0.1) * height * (metrics.volume / 100)
        const y1 = centerY - barHeight / 2
        const y2 = centerY + barHeight / 2
        
        ctx.moveTo(x, y1)
        ctx.lineTo(x, y2)
      }
      
      ctx.stroke()

      // アニメーション継続
      animationFrameRef.current = requestAnimationFrame(drawWaveform)
    }

    drawWaveform()

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [isStreaming, metrics.volume])

  // 品質レベルの判定
  const getQualityLevel = (value: number, thresholds: { good: number; warning: number }) => {
    if (value >= thresholds.good) return 'good'
    if (value >= thresholds.warning) return 'warning'
    return 'poor'
  }

  // 品質レベルの色
  const getQualityColor = (level: string) => {
    switch (level) {
      case 'good': return 'text-green-600 bg-green-100'
      case 'warning': return 'text-yellow-600 bg-yellow-100'
      case 'poor': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  // 音量レベルの判定
  const volumeLevel = getQualityLevel(metrics.volume, { good: 70, warning: 40 })
  const clarityLevel = getQualityLevel(metrics.clarity, { good: 80, warning: 60 })
  const latencyLevel = getQualityLevel(100 - metrics.latency, { good: 80, warning: 60 })

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-blue-500" />
          <span>音声品質監視</span>
          {isStreaming && (
            <Badge variant="default" className="bg-green-100 text-green-800">
              ストリーミング中
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* エラー表示 */}
        {error && (
          <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <AlertTriangle className="h-4 w-4 text-red-500" />
            <span className="text-red-700 text-sm">{error}</span>
          </div>
        )}

        {/* 音声波形表示 */}
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <Mic className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium">音声波形</span>
          </div>
          <canvas
            ref={canvasRef}
            width={400}
            height={80}
            className="border rounded-lg bg-gray-50"
          />
        </div>

        {/* 品質メトリクス */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 音量レベル */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">音量レベル</span>
              <Badge className={getQualityColor(volumeLevel)}>
                {metrics.volume.toFixed(1)}%
              </Badge>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  volumeLevel === 'good' ? 'bg-green-500' :
                  volumeLevel === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${metrics.volume}%` }}
              />
            </div>
          </div>

          {/* 音声明瞭度 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">音声明瞭度</span>
              <Badge className={getQualityColor(clarityLevel)}>
                {metrics.clarity.toFixed(1)}%
              </Badge>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  clarityLevel === 'good' ? 'bg-green-500' :
                  clarityLevel === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${metrics.clarity}%` }}
              />
            </div>
          </div>

          {/* レイテンシー */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">レイテンシー</span>
              <Badge className={getQualityColor(latencyLevel)}>
                {metrics.latency.toFixed(1)}ms
              </Badge>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  latencyLevel === 'good' ? 'bg-green-500' :
                  latencyLevel === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${100 - metrics.latency}%` }}
              />
            </div>
          </div>
        </div>

        {/* 詳細メトリクス */}
        <div className="grid grid-cols-2 gap-4 pt-2 border-t">
          <div className="flex items-center space-x-2">
            <Wifi className="h-4 w-4 text-gray-400" />
            <div>
              <div className="text-xs text-gray-500">パケット損失</div>
              <div className="text-sm font-medium">{metrics.packetLoss.toFixed(2)}%</div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Volume2 className="h-4 w-4 text-gray-400" />
            <div>
              <div className="text-xs text-gray-500">ジッター</div>
              <div className="text-sm font-medium">{metrics.jitter.toFixed(2)}ms</div>
            </div>
          </div>
        </div>

        {/* 品質改善のヒント */}
        {volumeLevel === 'poor' && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-sm text-blue-800">
              <strong>音量が低い場合:</strong> マイクの音量を上げるか、マイクに近づいてください。
            </div>
          </div>
        )}

        {clarityLevel === 'poor' && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-sm text-blue-800">
              <strong>音声が不明瞭な場合:</strong> 静かな環境で話すか、マイクの品質を確認してください。
            </div>
          </div>
        )}

        {latencyLevel === 'poor' && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-sm text-blue-800">
              <strong>レイテンシーが高い場合:</strong> インターネット接続を確認してください。
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
