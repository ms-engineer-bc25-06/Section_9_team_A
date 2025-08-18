'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select'
import { AnalyticsChart } from './AnalyticsChart'
import { AnalysisResponse } from '@/lib/api/analytics'
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  Star, 
  MessageSquare,
  Calendar,
  Filter
} from 'lucide-react'

interface AnalyticsDashboardProps {
  analyses: AnalysisResponse[]
  isLoading?: boolean
}

type ChartType = 'line' | 'area' | 'bar' | 'pie' | 'radar'
type DataType = 'sentiment' | 'confidence' | 'personality' | 'communication' | 'behavior'

interface ChartConfig {
  id: string
  title: string
  chartType: ChartType
  dataType: DataType
  description: string
  icon: React.ReactNode
}

const CHART_CONFIGS: ChartConfig[] = [
  {
    id: 'sentiment-trend',
    title: '感情傾向の推移',
    chartType: 'line',
    dataType: 'sentiment',
    description: '時間経過による感情スコアの変化',
    icon: <TrendingUp className="h-5 w-5 text-green-500" />
  },
  {
    id: 'confidence-analysis',
    title: '分析信頼度',
    chartType: 'bar',
    dataType: 'confidence',
    description: '各分析の信頼度スコア',
    icon: <BarChart3 className="h-5 w-5 text-blue-500" />
  },
  {
    id: 'personality-radar',
    title: '性格特性レーダーチャート',
    chartType: 'radar',
    dataType: 'personality',
    description: '性格特性の多角的な分析',
    icon: <Star className="h-5 w-5 text-yellow-500" />
  },
  {
    id: 'communication-patterns',
    title: 'コミュニケーションパターン',
    chartType: 'pie',
    dataType: 'communication',
    description: 'コミュニケーションスタイルの分布',
    icon: <MessageSquare className="h-5 w-5 text-indigo-500" />
  },
  {
    id: 'behavior-scores',
    title: '行動特性スコア',
    chartType: 'bar',
    dataType: 'behavior',
    description: '行動特性の各カテゴリ別スコア',
    icon: <Activity className="h-5 w-5 text-purple-500" />
  }
]

export function AnalyticsDashboard({ analyses, isLoading = false }: AnalyticsDashboardProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<string>('30')
  const [selectedChartType, setSelectedChartType] = useState<ChartType>('line')
  const [expandedCharts, setExpandedCharts] = useState<Record<string, boolean>>({})

  // 期間フィルタリング
  const getFilteredAnalyses = () => {
    if (selectedPeriod === 'all') return analyses
    
    const days = parseInt(selectedPeriod)
    const cutoffDate = new Date()
    cutoffDate.setDate(cutoffDate.getDate() - days)
    
    return analyses.filter(analysis => 
      new Date(analysis.created_at) >= cutoffDate
    )
  }

  const filteredAnalyses = getFilteredAnalyses()

  // 統計情報の計算
  const getStats = () => {
    const total = filteredAnalyses.length
    const avgConfidence = total > 0 
      ? filteredAnalyses.reduce((sum, a) => sum + a.confidence_score, 0) / total 
      : 0
    const avgSentiment = total > 0 
      ? filteredAnalyses.filter(a => a.sentiment_score !== undefined)
          .reduce((sum, a) => sum + (a.sentiment_score || 0), 0) / 
          filteredAnalyses.filter(a => a.sentiment_score !== undefined).length
      : 0

    return { total, avgConfidence, avgSentiment }
  }

  const stats = getStats()

  // チャートの展開/折りたたみ
  const toggleChart = (chartId: string) => {
    setExpandedCharts(prev => ({
      ...prev,
      [chartId]: !prev[chartId]
    }))
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (analyses.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">分析データがありません</h3>
          <p className="text-gray-600">AI分析を実行して、データを表示してください</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">分析ダッシュボード</h2>
          <p className="text-gray-600">AI分析結果の包括的な可視化</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">過去7日</SelectItem>
              <SelectItem value="30">過去30日</SelectItem>
              <SelectItem value="90">過去90日</SelectItem>
              <SelectItem value="all">すべて</SelectItem>
            </SelectContent>
          </Select>
          
          <Select value={selectedChartType} onValueChange={(value: ChartType) => setSelectedChartType(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="line">ライン</SelectItem>
              <SelectItem value="area">エリア</SelectItem>
              <SelectItem value="bar">バー</SelectItem>
              <SelectItem value="pie">パイ</SelectItem>
              <SelectItem value="radar">レーダー</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* 統計サマリー */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-gray-600">総分析数</p>
                <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm text-gray-600">平均信頼度</p>
                <p className="text-2xl font-bold text-green-600">
                  {Math.round(stats.avgConfidence * 100)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-purple-500" />
              <div>
                <p className="text-sm text-gray-600">平均感情スコア</p>
                <p className="text-2xl font-bold text-purple-600">
                  {stats.avgSentiment > 0 ? '+' : ''}{Math.round(stats.avgSentiment * 100)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* チャートグリッド */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {CHART_CONFIGS.map((config) => (
          <Card key={config.id} className="overflow-hidden">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {config.icon}
                  <div>
                    <CardTitle className="text-lg">{config.title}</CardTitle>
                    <p className="text-sm text-gray-600">{config.description}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleChart(config.id)}
                >
                  {expandedCharts[config.id] ? '折りたたむ' : '展開'}
                </Button>
              </div>
            </CardHeader>
            
            <CardContent className="pt-0">
              <div className={expandedCharts[config.id] ? 'h-96' : 'h-64'}>
                <AnalyticsChart
                  analyses={filteredAnalyses}
                  chartType={config.chartType}
                  dataType={config.dataType}
                  title=""
                  className="h-full"
                />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* データ更新情報 */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4" />
              <span>最終更新: {new Date().toLocaleString('ja-JP')}</span>
            </div>
            <Badge variant="outline">
              {filteredAnalyses.length}件のデータ
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
