"use client"

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Switch } from '@/components/ui/Switch'
import { Slider } from '@/components/ui/Slider'
import { Settings, Mic, Volume2, Zap, Shield } from 'lucide-react'

interface AudioStreamingConfig {
  sampleRate: number
  channels: number
  bitDepth: number
  echoCancellation: boolean
  noiseSuppression: boolean
  autoGainControl: boolean
  highPassFilter: boolean
}

interface AudioQualitySettingsProps {
  config: AudioStreamingConfig
  onConfigChange: (newConfig: Partial<AudioStreamingConfig>) => void
  isStreaming: boolean
}

export const AudioQualitySettings: React.FC<AudioQualitySettingsProps> = ({
  config,
  onConfigChange,
  isStreaming,
}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  // サンプルレートの選択肢
  const sampleRateOptions = [
    { value: 8000, label: '8kHz (電話品質)' },
    { value: 16000, label: '16kHz (低品質)' },
    { value: 22050, label: '22.05kHz (中品質)' },
    { value: 44100, label: '44.1kHz (CD品質)' },
    { value: 48000, label: '48kHz (高品質)' },
  ]

  // ビット深度の選択肢
  const bitDepthOptions = [
    { value: 8, label: '8bit' },
    { value: 16, label: '16bit (標準)' },
    { value: 24, label: '24bit (高品質)' },
  ]

  // 設定の更新
  const handleConfigChange = (key: keyof AudioStreamingConfig, value: any) => {
    onConfigChange({ [key]: value })
  }

  // プリセット設定の適用
  const applyPreset = (preset: 'voice' | 'music' | 'conference' | 'custom') => {
    switch (preset) {
      case 'voice':
        onConfigChange({
          sampleRate: 16000,
          channels: 1,
          bitDepth: 16,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          highPassFilter: true,
        })
        break
      case 'music':
        onConfigChange({
          sampleRate: 48000,
          channels: 2,
          bitDepth: 24,
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: true,
          highPassFilter: false,
        })
        break
      case 'conference':
        onConfigChange({
          sampleRate: 22050,
          channels: 1,
          bitDepth: 16,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          highPassFilter: true,
        })
        break
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Settings className="h-5 w-5 text-blue-500" />
            <span>音声品質設定</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? '折りたたむ' : '展開'}
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* プリセット設定 */}
        <div className="space-y-3">
          <div className="text-sm font-medium text-gray-700">プリセット設定</div>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => applyPreset('voice')}
              disabled={isStreaming}
            >
              <Mic className="h-4 w-4 mr-1" />
              音声通話
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => applyPreset('music')}
              disabled={isStreaming}
            >
              <Volume2 className="h-4 w-4 mr-1" />
              音楽
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => applyPreset('conference')}
              disabled={isStreaming}
            >
              <Zap className="h-4 w-4 mr-1" />
              会議
            </Button>
          </div>
        </div>

        {/* 基本設定 */}
        <div className="space-y-4">
          <div className="text-sm font-medium text-gray-700">基本設定</div>
          
          {/* サンプルレート */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-600">
                サンプルレート
              </label>
              <Badge variant="secondary">
                {config.sampleRate}Hz
              </Badge>
            </div>
            <select
              value={config.sampleRate}
              onChange={(e) => handleConfigChange('sampleRate', parseInt(e.target.value))}
              disabled={isStreaming}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              {sampleRateOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* ビット深度 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-600">
                ビット深度
              </label>
              <Badge variant="secondary">
                {config.bitDepth}bit
              </Badge>
            </div>
            <select
              value={config.bitDepth}
              onChange={(e) => handleConfigChange('bitDepth', parseInt(e.target.value))}
              disabled={isStreaming}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              {bitDepthOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* チャンネル数 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-600">
                チャンネル数
              </label>
              <Badge variant="secondary">
                {config.channels}ch
              </Badge>
            </div>
            <div className="flex space-x-2">
              <Button
                variant={config.channels === 1 ? "default" : "outline"}
                size="sm"
                onClick={() => handleConfigChange('channels', 1)}
                disabled={isStreaming}
              >
                モノラル
              </Button>
              <Button
                variant={config.channels === 2 ? "default" : "outline"}
                size="sm"
                onClick={() => handleConfigChange('channels', 2)}
                disabled={isStreaming}
              >
                ステレオ
              </Button>
            </div>
          </div>
        </div>

        {/* 詳細設定（展開時のみ表示） */}
        {isExpanded && (
          <div className="space-y-4 pt-4 border-t">
            <div className="text-sm font-medium text-gray-700">詳細設定</div>
            
            {/* エコーキャンセル */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4 text-gray-500" />
                <div>
                  <div className="text-sm font-medium text-gray-600">エコーキャンセル</div>
                  <div className="text-xs text-gray-500">
                    自分の音声がエコーするのを防ぎます
                  </div>
                </div>
              </div>
              <Switch
                checked={config.echoCancellation}
                onCheckedChange={(checked) => handleConfigChange('echoCancellation', checked)}
                disabled={isStreaming}
              />
            </div>

            {/* ノイズ除去 */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Mic className="h-4 w-4 text-gray-500" />
                <div>
                  <div className="text-sm font-medium text-gray-600">ノイズ除去</div>
                  <div className="text-xs text-gray-500">
                    背景ノイズを除去して音声をクリアにします
                  </div>
                </div>
              </div>
              <Switch
                checked={config.noiseSuppression}
                onCheckedChange={(checked) => handleConfigChange('noiseSuppression', checked)}
                disabled={isStreaming}
              />
            </div>

            {/* 自動ゲイン制御 */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Volume2 className="h-4 w-4 text-gray-500" />
                <div>
                  <div className="text-sm font-medium text-gray-600">自動ゲイン制御</div>
                  <div className="text-xs text-gray-500">
                    音量を自動的に調整して一定に保ちます
                  </div>
                </div>
              </div>
              <Switch
                checked={config.autoGainControl}
                onCheckedChange={(checked) => handleConfigChange('autoGainControl', checked)}
                disabled={isStreaming}
              />
            </div>

            {/* ハイパスフィルター */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Zap className="h-4 w-4 text-gray-500" />
                <div>
                  <div className="text-sm font-medium text-gray-600">ハイパスフィルター</div>
                  <div className="text-xs text-gray-500">
                    低周波ノイズ（風の音など）を除去します
                  </div>
                </div>
              </div>
              <Switch
                checked={config.highPassFilter}
                onCheckedChange={(checked) => handleConfigChange('highPassFilter', checked)}
                disabled={isStreaming}
              />
            </div>
          </div>
        )}

        {/* 現在の設定サマリー */}
        <div className="pt-4 border-t">
          <div className="text-sm font-medium text-gray-700 mb-2">現在の設定</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-500">サンプルレート:</span>
              <span className="font-medium">{config.sampleRate}Hz</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">ビット深度:</span>
              <span className="font-medium">{config.bitDepth}bit</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">チャンネル:</span>
              <span className="font-medium">{config.channels}ch</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">品質:</span>
              <span className="font-medium">
                {config.sampleRate >= 48000 && config.bitDepth >= 24 ? '高品質' :
                 config.sampleRate >= 44100 && config.bitDepth >= 16 ? '標準品質' : '低品質'}
              </span>
            </div>
          </div>
        </div>

        {/* 注意事項 */}
        {isStreaming && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="text-sm text-yellow-800">
              <strong>注意:</strong> ストリーミング中は設定を変更できません。設定を変更するには一度ストリーミングを停止してください。
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
