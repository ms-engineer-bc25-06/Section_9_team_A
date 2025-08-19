"use client"

import { useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { ScrollArea } from '@/components/ui/ScrollArea'
import { 
  Mic, 
  MicOff, 
  Pause, 
  Play, 
  Trash2, 
  Download, 
  FileText, 
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'

interface TranscriptionSegment {
  id: string
  text: string
  startTime: number
  endTime: number
  confidence: number
  isComplete: boolean
  timestamp: Date
}

interface RealTimeTranscriptionProps {
  isTranscribing: boolean
  isPaused: boolean
  currentText: string
  segments: TranscriptionSegment[]
  onStart: () => Promise<void>
  onStop: () => void
  onPause: () => void
  onResume: () => void
  onClear: () => void
  error?: string | null
  onClearError?: () => void
}

export const RealTimeTranscription: React.FC<RealTimeTranscriptionProps> = ({
  isTranscribing,
  isPaused,
  currentText,
  segments,
  onStart,
  onStop,
  onPause,
  onResume,
  onClear,
  error,
  onClearError,
}) => {
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const currentTextRef = useRef<HTMLDivElement>(null)

  // 自動スクロール
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [segments])

  // 現在のテキストの自動スクロール
  useEffect(() => {
    if (currentTextRef.current) {
      currentTextRef.current.scrollLeft = currentTextRef.current.scrollWidth
    }
  }, [currentText])

  // 時間のフォーマット
  const formatTime = (milliseconds: number): string => {
    const seconds = Math.floor(milliseconds / 1000)
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  // 信頼度の色を取得
  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100'
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  // 信頼度のレベルを取得
  const getConfidenceLevel = (confidence: number): string => {
    if (confidence >= 0.8) return '高'
    if (confidence >= 0.6) return '中'
    return '低'
  }

  // テキストをエクスポート
  const exportTranscription = () => {
    if (segments.length === 0) return

    const text = segments
      .filter(seg => seg.isComplete)
      .map(seg => `[${formatTime(seg.startTime)}] ${seg.text}`)
      .join('\n')

    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transcription-${new Date().toISOString().slice(0, 19)}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // 統計情報の計算
  const totalWords = segments.reduce((sum, seg) => {
    return sum + seg.text.split(/\s+/).filter(word => word.length > 0).length
  }, 0)

  const averageConfidence = segments.length > 0 
    ? segments.reduce((sum, seg) => sum + seg.confidence, 0) / segments.length 
    : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-blue-500" />
            <span>リアルタイム文字起こし</span>
            {isTranscribing && (
              <Badge variant="default" className="bg-green-100 text-green-800">
                <Activity className="h-3 w-3 mr-1 animate-pulse" />
                処理中
              </Badge>
            )}
            {isPaused && (
              <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                <Pause className="h-3 w-3 mr-1" />
                一時停止
              </Badge>
            )}
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={exportTranscription}
              disabled={segments.length === 0}
            >
              <Download className="h-4 w-4 mr-1" />
              エクスポート
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onClear}
              disabled={segments.length === 0}
            >
              <Trash2 className="h-4 w-4 mr-1" />
              クリア
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* エラー表示 */}
        {error && (
          <div className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-4 w-4 text-red-500" />
              <span className="text-red-700 text-sm">{error}</span>
            </div>
            {onClearError && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClearError}
                className="text-red-600 hover:text-red-700"
              >
                閉じる
              </Button>
            )}
          </div>
        )}

        {/* 制御ボタン */}
        <div className="flex flex-wrap gap-2">
          {!isTranscribing ? (
            <Button onClick={onStart} disabled={!isTranscribing}>
              <Mic className="h-4 w-4 mr-2" />
              文字起こし開始
            </Button>
          ) : (
            <>
              <Button onClick={onStop} variant="destructive">
                <MicOff className="h-4 w-4 mr-2" />
                停止
              </Button>
              {isPaused ? (
                <Button onClick={onResume} variant="outline">
                  <Play className="h-4 w-4 mr-2" />
                  再開
                </Button>
              ) : (
                <Button onClick={onPause} variant="outline">
                  <Pause className="h-4 w-4 mr-2" />
                  一時停止
                </Button>
              )}
            </>
          )}
        </div>

        {/* 統計情報 */}
        {segments.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-3 bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{segments.length}</div>
              <div className="text-xs text-gray-600">セグメント数</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{totalWords}</div>
              <div className="text-xs text-gray-600">総単語数</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(averageConfidence * 100)}%
              </div>
              <div className="text-xs text-gray-600">平均信頼度</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {segments.length > 0 ? formatTime(Math.max(...segments.map(s => s.endTime))) : '0:00'}
              </div>
              <div className="text-xs text-gray-600">総時間</div>
            </div>
          </div>
        )}

        {/* 現在のテキスト */}
        {currentText && (
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">現在のテキスト</span>
            </div>
            <div
              ref={currentTextRef}
              className="p-3 bg-blue-50 border border-blue-200 rounded-lg max-h-32 overflow-x-auto"
            >
              <p className="text-blue-800 whitespace-nowrap">
                {currentText}
                {isTranscribing && !isPaused && (
                  <span className="inline-block w-2 h-4 bg-blue-500 ml-1 animate-pulse" />
                )}
              </p>
            </div>
          </div>
        )}

        {/* 文字起こしセグメント */}
        {segments.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">文字起こし履歴</span>
              <Badge variant="outline">
                {segments.filter(s => s.isComplete).length} / {segments.length} 完了
              </Badge>
            </div>
            <ScrollArea className="h-64 w-full border rounded-lg p-2">
              <div ref={scrollAreaRef} className="space-y-2">
                {segments.map((segment) => (
                  <div
                    key={segment.id}
                    className={`p-3 rounded-lg border ${
                      segment.isComplete ? 'bg-white' : 'bg-yellow-50'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="text-xs">
                          {formatTime(segment.startTime)}
                        </Badge>
                        {segment.isComplete ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <Activity className="h-4 w-4 text-yellow-500 animate-pulse" />
                        )}
                      </div>
                      <Badge className={`text-xs ${getConfidenceColor(segment.confidence)}`}>
                        信頼度: {getConfidenceLevel(segment.confidence)} ({Math.round(segment.confidence * 100)}%)
                      </Badge>
                    </div>
                    <p className="text-gray-800 text-sm leading-relaxed">
                      {segment.text}
                    </p>
                    <div className="text-xs text-gray-500 mt-2">
                      {segment.timestamp.toLocaleTimeString('ja-JP')}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        )}

        {/* 開始前のメッセージ */}
        {!isTranscribing && segments.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium mb-2">文字起こしを開始してください</p>
            <p className="text-sm">
              音声チャット中にリアルタイムで文字起こしが行われます
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
