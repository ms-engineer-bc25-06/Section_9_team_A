"use client"

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Switch } from '@/components/ui/Switch'
import { Slider } from '@/components/ui/Slider'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Separator } from '@/components/ui/Separator'
import { 
  Settings, 
  Mic, 
  Volume2, 
  Zap, 
  ChevronDown, 
  ChevronUp,
  Play,
  Pause,
  RotateCcw,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

interface AdvancedAudioQualitySettingsProps {
  config: {
    echoCancellation: any
    noiseReduction: any
    audioCompression: any
    [key: string]: any // インデックスシグネチャを追加
  }
  onConfigChange: (newConfig: any) => void
  isEnabled: boolean
  onToggle: (enabled: boolean) => void
  onReset: () => void
  isProcessing: boolean
}

export const AdvancedAudioQualitySettings: React.FC<AdvancedAudioQualitySettingsProps> = ({
  config,
  onConfigChange,
  isEnabled,
  onToggle,
  onReset,
  isProcessing,
}) => {
  const [expandedSections, setExpandedSections] = useState({
    echoCancellation: true,
    noiseReduction: true,
    audioCompression: true,
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const updateConfig = (section: string, key: string, value: any) => {
    onConfigChange({
      [section]: {
        ...config[section],
        [key]: value,
      },
    })
  }

  const updateNestedConfig = (section: string, subsection: string, key: string, value: any) => {
    onConfigChange({
      [section]: {
        ...config[section],
        [subsection]: {
          ...config[section][subsection],
          [key]: value,
        },
      },
    })
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          高度な音声品質設定
        </CardTitle>
        <div className="flex items-center gap-2">
          <Switch
            checked={isEnabled}
            onCheckedChange={onToggle}
            disabled={isProcessing}
          />
          <Badge variant={isEnabled ? "default" : "secondary"}>
            {isEnabled ? "有効" : "無効"}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* エコーキャンセル設定 */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Mic className="h-4 w-4" />
              エコーキャンセル
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleSection('echoCancellation')}
            >
              {expandedSections.echoCancellation ? <ChevronUp /> : <ChevronDown />}
            </Button>
          </div>

          {expandedSections.echoCancellation && (
            <div className="space-y-4 pl-4 border-l-2 border-gray-200">
              <div className="flex items-center justify-between">
                <span>有効</span>
                <Switch
                  checked={config.echoCancellation.enabled}
                  onCheckedChange={(checked) => updateConfig('echoCancellation', 'enabled', checked)}
                  disabled={!isEnabled || isProcessing}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">遅延補償 (ms)</label>
                <Slider
                  value={[config.echoCancellation.delayCompensation]}
                  onValueChange={([value]: [number]) => updateConfig('echoCancellation', 'delayCompensation', value)}
                  min={0}
                  max={200}
                  step={1}
                  disabled={!isEnabled || isProcessing}
                />
                <span className="text-xs text-gray-500">{config.echoCancellation.delayCompensation}ms</span>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">フィルタ長</label>
                <Select
                  value={config.echoCancellation.filterLength.toString()}
                  onValueChange={(value) => updateConfig('echoCancellation', 'filterLength', parseInt(value))}
                  disabled={!isEnabled || isProcessing}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1024">1024</SelectItem>
                    <SelectItem value="2048">2048</SelectItem>
                    <SelectItem value="4096">4096</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">適応率</label>
                <Slider
                  value={[config.echoCancellation.adaptationRate]}
                  onValueChange={([value]: [number]) => updateConfig('echoCancellation', 'adaptationRate', value)}
                  min={0.001}
                  max={0.1}
                  step={0.001}
                  disabled={!isEnabled || isProcessing}
                />
                <span className="text-xs text-gray-500">{config.echoCancellation.adaptationRate.toFixed(3)}</span>
              </div>

              <div className="flex items-center justify-between">
                <span>二重通話検出</span>
                <Switch
                  checked={config.echoCancellation.doubleTalkDetection}
                  onCheckedChange={(checked) => updateConfig('echoCancellation', 'doubleTalkDetection', checked)}
                  disabled={!isEnabled || isProcessing}
                />
              </div>

              <div className="flex items-center justify-between">
                <span>非線形処理</span>
                <Switch
                  checked={config.echoCancellation.nonlinearProcessing}
                  onCheckedChange={(checked) => updateConfig('echoCancellation', 'nonlinearProcessing', checked)}
                  disabled={!isEnabled || isProcessing}
                />
              </div>
            </div>
          )}
        </div>

        <Separator />

        {/* ノイズ除去設定 */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Volume2 className="h-4 w-4" />
              ノイズ除去
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleSection('noiseReduction')}
            >
              {expandedSections.noiseReduction ? <ChevronUp /> : <ChevronDown />}
            </Button>
          </div>

          {expandedSections.noiseReduction && (
            <div className="space-y-4 pl-4 border-l-2 border-gray-200">
              <div className="flex items-center justify-between">
                <span>有効</span>
                <Switch
                  checked={config.noiseReduction.enabled}
                  onCheckedChange={(checked) => updateConfig('noiseReduction', 'enabled', checked)}
                  disabled={!isEnabled || isProcessing}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">アルゴリズム</label>
                <Select
                  value={config.noiseReduction.algorithm}
                  onValueChange={(value) => updateConfig('noiseReduction', 'algorithm', value)}
                  disabled={!isEnabled || isProcessing}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="spectral-subtraction">スペクトル減算</SelectItem>
                    <SelectItem value="wiener-filter">ウィーナーフィルタ</SelectItem>
                    <SelectItem value="kalman-filter">カルマンフィルタ</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">VAD閾値</label>
                <Slider
                  value={[config.noiseReduction.voiceActivityDetection.threshold]}
                  onValueChange={([value]: [number]) => updateNestedConfig('noiseReduction', 'voiceActivityDetection', 'threshold', value)}
                  min={0.05}
                  max={0.5}
                  step={0.01}
                  disabled={!isEnabled || isProcessing}
                />
                <span className="text-xs text-gray-500">{config.noiseReduction.voiceActivityDetection.threshold.toFixed(2)}</span>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">ノイズフロア (dB)</label>
                <Slider
                  value={[Math.abs(config.noiseReduction.voiceActivityDetection.noiseFloor)]}
                  onValueChange={([value]: [number]) => updateNestedConfig('noiseReduction', 'voiceActivityDetection', 'noiseFloor', -value)}
                  min={20}
                  max={80}
                  step={1}
                  disabled={!isEnabled || isProcessing}
                />
                <span className="text-xs text-gray-500">{config.noiseReduction.voiceActivityDetection.noiseFloor}dB</span>
              </div>

              <div className="flex items-center justify-between">
                <span>適応処理</span>
                <Switch
                  checked={config.noiseReduction.adaptiveProcessing.enabled}
                  onCheckedChange={(checked) => updateNestedConfig('noiseReduction', 'adaptiveProcessing', 'enabled', checked)}
                  disabled={!isEnabled || isProcessing}
                />
              </div>
            </div>
          )}
        </div>

        <Separator />

        {/* 音声圧縮設定 */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Zap className="h-4 w-4" />
              音声圧縮
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleSection('audioCompression')}
            >
              {expandedSections.audioCompression ? <ChevronUp /> : <ChevronDown />}
            </Button>
          </div>

          {expandedSections.audioCompression && (
            <div className="space-y-4 pl-4 border-l-2 border-gray-200">
              <div className="flex items-center justify-between">
                <span>有効</span>
                <Switch
                  checked={config.audioCompression.enabled}
                  onCheckedChange={(checked) => updateConfig('audioCompression', 'enabled', checked)}
                  disabled={!isEnabled || isProcessing}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">アルゴリズム</label>
                <Select
                  value={config.audioCompression.algorithm}
                  onValueChange={(value) => updateConfig('audioCompression', 'algorithm', value)}
                  disabled={!isEnabled || isProcessing}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="opus">Opus</SelectItem>
                    <SelectItem value="aac">AAC</SelectItem>
                    <SelectItem value="mp3">MP3</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">品質</label>
                <Select
                  value={config.audioCompression.quality}
                  onValueChange={(value) => updateConfig('audioCompression', 'quality', value)}
                  disabled={!isEnabled || isProcessing}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">低</SelectItem>
                    <SelectItem value="medium">中</SelectItem>
                    <SelectItem value="high">高</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">ビットレート (kbps)</label>
                <Slider
                  value={[config.audioCompression.bitrate]}
                  onValueChange={([value]: [number]) => updateConfig('audioCompression', 'bitrate', value)}
                  min={16}
                  max={128}
                  step={8}
                  disabled={!isEnabled || isProcessing}
                />
                <span className="text-xs text-gray-500">{config.audioCompression.bitrate}kbps</span>
              </div>

              <div className="flex items-center justify-between">
                <span>可変ビットレート</span>
                <Switch
                  checked={config.audioCompression.variableBitrate}
                  onCheckedChange={(checked) => updateConfig('audioCompression', 'variableBitrate', checked)}
                  disabled={!isEnabled || isProcessing}
                />
              </div>

              <div className="flex items-center justify-between">
                <span>適応圧縮</span>
                <Switch
                  checked={config.audioCompression.adaptiveCompression.enabled}
                  onCheckedChange={(checked) => updateNestedConfig('audioCompression', 'adaptiveCompression', 'enabled', checked)}
                  disabled={!isEnabled || isProcessing}
                />
              </div>
            </div>
          )}
        </div>

        {/* 制御ボタン */}
        <div className="flex items-center justify-between pt-4 border-t">
          <Button
            variant="outline"
            onClick={onReset}
            disabled={!isEnabled || isProcessing}
            className="flex items-center gap-2"
          >
            <RotateCcw className="h-4 w-4" />
            リセット
          </Button>

          <div className="flex items-center gap-2">
            {isProcessing && (
              <Badge variant="secondary" className="flex items-center gap-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                処理中
              </Badge>
            )}
            <Badge variant={isEnabled ? "default" : "secondary"}>
              {isEnabled ? "最適化有効" : "最適化無効"}
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
