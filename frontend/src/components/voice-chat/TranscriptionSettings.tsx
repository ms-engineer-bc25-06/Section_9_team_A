"use client"

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Switch } from '@/components/ui/Switch'
import { Settings, Languages, FileText, Zap, Shield } from 'lucide-react'
import { WhisperTranscriptionOptions } from '@/lib/openai-whisper'

interface TranscriptionSettingsProps {
  options: WhisperTranscriptionOptions
  onOptionsChange: (options: Partial<WhisperTranscriptionOptions>) => void
  isTranscribing: boolean
}

export const TranscriptionSettings: React.FC<TranscriptionSettingsProps> = ({
  options,
  onOptionsChange,
  isTranscribing,
}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  // 言語オプション
  const languageOptions = [
    { value: 'ja', label: '日本語', flag: '🇯🇵' },
    { value: 'en', label: '英語', flag: '🇺🇸' },
    { value: 'zh', label: '中国語', flag: '🇨🇳' },
    { value: 'ko', label: '韓国語', flag: '🇰🇷' },
    { value: 'fr', label: 'フランス語', flag: '🇫🇷' },
    { value: 'de', label: 'ドイツ語', flag: '🇩🇪' },
    { value: 'es', label: 'スペイン語', flag: '🇪🇸' },
    { value: 'auto', label: '自動検出', flag: '🌐' },
  ]

  // レスポンス形式オプション
  const responseFormatOptions = [
    { value: 'json', label: 'JSON (詳細)', description: 'セグメント情報を含む詳細な結果' },
    { value: 'text', label: 'テキスト', description: 'シンプルなテキストのみ' },
    { value: 'srt', label: 'SRT', description: '字幕形式' },
    { value: 'vtt', label: 'VTT', description: 'WebVTT形式' },
  ]

  // 設定の更新
  const handleOptionChange = (key: keyof WhisperTranscriptionOptions, value: any) => {
    onOptionsChange({ [key]: value })
  }

  // プリセット設定の適用
  const applyPreset = (preset: 'conversation' | 'presentation' | 'interview' | 'custom') => {
    switch (preset) {
      case 'conversation':
        onOptionsChange({
          language: 'ja',
          response_format: 'json',
          temperature: 0.3,
        })
        break
      case 'presentation':
        onOptionsChange({
          language: 'ja',
          response_format: 'srt',
          temperature: 0.1,
        })
        break
      case 'interview':
        onOptionsChange({
          language: 'auto',
          response_format: 'json',
          temperature: 0.2,
        })
        break
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Settings className="h-5 w-5 text-green-500" />
            <span>文字起こし設定</span>
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
              onClick={() => applyPreset('conversation')}
              disabled={isTranscribing}
            >
              <FileText className="h-4 w-4 mr-1" />
              会話
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => applyPreset('presentation')}
              disabled={isTranscribing}
            >
              <Zap className="h-4 w-4 mr-1" />
              プレゼンテーション
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => applyPreset('interview')}
              disabled={isTranscribing}
            >
              <Shield className="h-4 w-4 mr-1" />
              インタビュー
            </Button>
          </div>
        </div>

        {/* 基本設定 */}
        <div className="space-y-4">
          <div className="text-sm font-medium text-gray-700">基本設定</div>
          
          {/* 言語設定 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-600">
                言語設定
              </label>
              <Badge variant="secondary">
                {languageOptions.find(lang => lang.value === options.language)?.flag || '🌐'}
                {languageOptions.find(lang => lang.value === options.language)?.label || '自動検出'}
              </Badge>
            </div>
            <select
              value={options.language || 'auto'}
              onChange={(e) => handleOptionChange('language', e.target.value)}
              disabled={isTranscribing}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-100"
            >
              {languageOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.flag} {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* レスポンス形式 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-600">
                出力形式
              </label>
              <Badge variant="secondary">
                {responseFormatOptions.find(format => format.value === options.response_format)?.label || 'JSON'}
              </Badge>
            </div>
            <select
              value={options.response_format || 'json'}
              onChange={(e) => handleOptionChange('response_format', e.target.value)}
              disabled={isTranscribing}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-100"
            >
              {responseFormatOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500">
              {responseFormatOptions.find(format => format.value === options.response_format)?.description}
            </p>
          </div>

          {/* 温度設定 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-600">
                創造性レベル
              </label>
              <Badge variant="secondary">
                {options.temperature || 0.3}
              </Badge>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={options.temperature || 0.3}
              onChange={(e) => handleOptionChange('temperature', parseFloat(e.target.value))}
              disabled={isTranscribing}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>正確性重視 (0.0)</span>
              <span>バランス (0.5)</span>
              <span>創造性重視 (1.0)</span>
            </div>
          </div>
        </div>

        {/* 詳細設定（展開時のみ表示） */}
        {isExpanded && (
          <div className="space-y-4 pt-4 border-t">
            <div className="text-sm font-medium text-gray-700">詳細設定</div>
            
            {/* プロンプト設定 */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-600">
                プロンプト（文脈のヒント）
              </label>
              <textarea
                value={options.prompt || ''}
                onChange={(e) => handleOptionChange('prompt', e.target.value)}
                disabled={isTranscribing}
                placeholder="例: これは技術的な会議の音声です。専門用語が多く含まれています。"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-100 resize-none"
                rows={3}
              />
              <p className="text-xs text-gray-500">
                音声の内容や文脈に関する情報を入力すると、文字起こしの精度が向上します
              </p>
            </div>

            {/* モデル設定 */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-600">
                  使用モデル
                </label>
                <Badge variant="secondary">
                  {options.model || 'whisper-1'}
                </Badge>
              </div>
              <select
                value={options.model || 'whisper-1'}
                onChange={(e) => handleOptionChange('model', e.target.value)}
                disabled={isTranscribing}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-100"
              >
                <option value="whisper-1">Whisper v1 (最新)</option>
              </select>
            </div>
          </div>
        )}

        {/* 現在の設定サマリー */}
        <div className="pt-4 border-t">
          <div className="text-sm font-medium text-gray-700 mb-2">現在の設定</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-500">言語:</span>
              <span className="font-medium">
                {languageOptions.find(lang => lang.value === options.language)?.label || '自動検出'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">出力形式:</span>
              <span className="font-medium">
                {responseFormatOptions.find(format => format.value === options.response_format)?.label || 'JSON'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">創造性:</span>
              <span className="font-medium">
                {options.temperature || 0.3}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">モデル:</span>
              <span className="font-medium">
                {options.model || 'whisper-1'}
              </span>
            </div>
          </div>
        </div>

        {/* 注意事項 */}
        {isTranscribing && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="text-sm text-yellow-800">
              <strong>注意:</strong> 文字起こし中は設定を変更できません。設定を変更するには一度文字起こしを停止してください。
            </div>
          </div>
        )}

        {/* 設定のヒント */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="text-sm text-blue-800">
            <strong>設定のヒント:</strong>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>言語を指定すると精度が向上します</li>
              <li>温度を低くすると一貫性のある結果になります</li>
              <li>プロンプトで文脈を指定すると専門用語の認識が改善されます</li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
