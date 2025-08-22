"use client"

import { useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Progress } from '@/components/ui/Progress'
import { 
  Activity, 
  Mic, 
  Volume2, 
  Zap, 
  TrendingUp, 
  TrendingDown,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react'

interface AdvancedAudioQualityMonitorProps {
  stats: {
    echoCancellation: any
    noiseReduction: any
    audioCompression: any
    overallQuality: number
    processingLatency: number
    cpuUsage: number
    memoryUsage: number
  }
  isEnabled: boolean
  isProcessing: boolean
}

export const AdvancedAudioQualityMonitor: React.FC<AdvancedAudioQualityMonitorProps> = ({
  stats,
  isEnabled,
  isProcessing,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()

  // 波形描画
  useEffect(() => {
    if (!canvasRef.current || !isProcessing) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const drawWaveform = () => {
      const { width, height } = canvas
      ctx.clearRect(0, 0, width, height)

      // 背景
      ctx.fillStyle = '#f8fafc'
      ctx.fillRect(0, 0, width, height)

      // グリッド
      ctx.strokeStyle = '#e2e8f0'
      ctx.lineWidth = 1
      for (let i = 0; i < width; i += 20) {
        ctx.beginPath()
        ctx.moveTo(i, 0)
        ctx.lineTo(i, height)
        ctx.stroke()
      }
      for (let i = 0; i < height; i += 20) {
        ctx.beginPath()
        ctx.moveTo(0, i)
        ctx.lineTo(width, i)
        ctx.stroke()
      }

      // 波形描画（シミュレーション）
      ctx.strokeStyle = '#3b82f6'
      ctx.lineWidth = 2
      ctx.beginPath()
      
      for (let x = 0; x < width; x++) {
        const time = Date.now() * 0.001 + x * 0.01
        const amplitude = Math.sin(time) * 0.3 + Math.sin(time * 2) * 0.2
        const y = height / 2 + amplitude * height / 2
        
        if (x === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      }
      
      ctx.stroke()

      // 品質インジケーター
      const qualityColor = stats.overallQuality > 0.7 ? '#10b981' : 
                          stats.overallQuality > 0.4 ? '#f59e0b' : '#ef4444'
      
      ctx.fillStyle = qualityColor
      ctx.fillRect(width - 10, 10, 8, 8)

      animationRef.current = requestAnimationFrame(drawWaveform)
    }

    drawWaveform()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isProcessing, stats.overallQuality])

  // 品質レベルの判定
  const getQualityLevel = (quality: number) => {
    if (quality >= 0.8) return { level: '優秀', color: 'bg-green-500', icon: CheckCircle }
    if (quality >= 0.6) return { level: '良好', color: 'bg-blue-500', icon: CheckCircle }
    if (quality >= 0.4) return { level: '普通', color: 'bg-yellow-500', icon: AlertCircle }
    return { level: '要改善', color: 'bg-red-500', icon: AlertCircle }
  }

  const overallQuality = getQualityLevel(stats.overallQuality)

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          高度な音声品質モニター
        </CardTitle>
        <div className="flex items-center gap-2">
          <Badge variant={isEnabled ? "default" : "secondary"}>
            {isEnabled ? "有効" : "無効"}
          </Badge>
          {isProcessing && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              処理中
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* 全体的な品質 */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">全体的な品質</h3>
            <Badge className={overallQuality.color}>
              {overallQuality.level}
            </Badge>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>品質スコア</span>
              <span className="font-mono">{(stats.overallQuality * 100).toFixed(1)}%</span>
            </div>
            <Progress value={stats.overallQuality * 100} className="h-2" />
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span>処理遅延: {stats.processingLatency.toFixed(1)}ms</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-blue-500" />
              <span>CPU使用率: {(stats.cpuUsage * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* 波形表示 */}
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">リアルタイム波形</h3>
          <canvas
            ref={canvasRef}
            width={400}
            height={120}
            className="w-full h-32 border rounded-lg bg-gray-50"
          />
        </div>

        {/* エコーキャンセル統計 */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Mic className="h-4 w-4" />
            エコーキャンセル
          </h3>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>フィルタ収束</span>
                <span className="font-mono">{(stats.echoCancellation.filterConvergence * 100).toFixed(1)}%</span>
              </div>
              <Progress value={stats.echoCancellation.filterConvergence * 100} className="h-2" />
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>エコー抑制</span>
                <span className="font-mono">{(stats.echoCancellation.echoSuppression * 100).toFixed(1)}%</span>
              </div>
              <Progress value={stats.echoCancellation.echoSuppression * 100} className="h-2" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
            <div>残存エコー: {stats.echoCancellation.residualEcho.toFixed(3)}</div>
            <div>信号品質: {(stats.echoCancellation.signalQuality * 100).toFixed(1)}%</div>
            <div>適応率: {stats.echoCancellation.adaptationRate.toFixed(3)}</div>
            <div>収束時間: {stats.echoCancellation.convergenceTime}ms</div>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant={stats.echoCancellation.adaptationActive ? "default" : "secondary"}>
              {stats.echoCancellation.adaptationActive ? "適応中" : "安定"}
            </Badge>
            <span className="text-xs text-gray-500">
              処理サンプル数: {stats.echoCancellation.totalSamples.toLocaleString()}
            </span>
          </div>
        </div>

        {/* ノイズ除去統計 */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Volume2 className="h-4 w-4" />
            ノイズ除去
          </h3>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>ノイズ除去率</span>
                <span className="font-mono">{(stats.noiseReduction.noiseReduction * 100).toFixed(1)}%</span>
              </div>
              <Progress value={stats.noiseReduction.noiseReduction * 100} className="h-2" />
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>SNR改善</span>
                <span className="font-mono">{stats.noiseReduction.snrImprovement.toFixed(1)}dB</span>
              </div>
              <Progress value={Math.min(100, Math.max(0, stats.noiseReduction.snrImprovement + 20))} className="h-2" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
            <div>信号歪み: {stats.noiseReduction.signalDistortion.toFixed(3)}</div>
            <div>音声保持: {(stats.noiseReduction.speechPreservation * 100).toFixed(1)}%</div>
            <div>ノイズレベル: {stats.noiseReduction.noiseLevel.toFixed(1)}dB</div>
            <div>全体品質: {(stats.noiseReduction.overallQuality * 100).toFixed(1)}%</div>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant={stats.noiseReduction.adaptationActive ? "default" : "secondary"}>
              {stats.noiseReduction.adaptationActive ? "適応中" : "安定"}
            </Badge>
            <span className="text-xs text-gray-500">
              フレーム数: {stats.noiseReduction.totalFrames} (音声: {stats.noiseReduction.voiceFrames}, ノイズ: {stats.noiseReduction.noiseFrames})
            </span>
          </div>
        </div>

        {/* 音声圧縮統計 */}
        <div className="space-y-3">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Zap className="h-4 w-4" />
            音声圧縮
          </h3>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>圧縮比</span>
                <span className="font-mono">{stats.audioCompression.compressionRatio.toFixed(2)}:1</span>
              </div>
              <Progress value={Math.min(100, stats.audioCompression.compressionRatio * 10)} className="h-2" />
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>品質スコア</span>
                <span className="font-mono">{(stats.audioCompression.qualityScore * 100).toFixed(1)}%</span>
              </div>
              <Progress value={stats.audioCompression.qualityScore * 100} className="h-2" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
            <div>ビットレート: {stats.audioCompression.bitrate}kbps</div>
            <div>エンコード時間: {stats.audioCompression.encodingTime.toFixed(1)}ms</div>
            <div>知覚品質: {(stats.audioCompression.perceptualQuality * 100).toFixed(1)}%</div>
            <div>スペクトル歪み: {stats.audioCompression.spectralDistortion.toFixed(3)}</div>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="outline">
              効率: {(stats.audioCompression.efficiency * 100).toFixed(1)}%
            </Badge>
            <span className="text-xs text-gray-500">
              フレーム数: {stats.audioCompression.frameCount} | 
              平均フレームサイズ: {stats.audioCompression.averageFrameSize.toFixed(1)}バイト
            </span>
          </div>
        </div>

        {/* システムリソース */}
        <div className="space-y-3 pt-4 border-t">
          <h3 className="text-lg font-semibold">システムリソース</h3>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>CPU使用率</span>
                <span className="font-mono">{(stats.cpuUsage * 100).toFixed(1)}%</span>
              </div>
              <Progress value={stats.cpuUsage * 100} className="h-2" />
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>メモリ使用量</span>
                <span className="font-mono">{stats.memoryUsage.toFixed(1)}MB</span>
              </div>
              <Progress value={Math.min(100, stats.memoryUsage / 10)} className="h-2" />
            </div>
          </div>

          <div className="text-xs text-gray-500 text-center">
            処理遅延: {stats.processingLatency.toFixed(1)}ms | 
            全体的な品質: {(stats.overallQuality * 100).toFixed(1)}%
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
