"use client"

import { AnalyticsChart } from "@/components/analytics"
import { useAIAnalysis } from "@/hooks/useAIAnalysis"
import { useAuth } from "@/components/auth/AuthProvider"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/Select"
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  Star, 
  MessageSquare,
  Calendar,
  Filter,
  Download,
  Eye,
  LogIn
} from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/Button"

export default function ReportsPage() {
  const { analyses, isLoading, error } = useAIAnalysis()
  const { backendToken, user } = useAuth()
  const [selectedPeriod, setSelectedPeriod] = useState<string>("30")
  const [selectedType, setSelectedType] = useState<string>("all")

  const periods = [
    { id: "7", label: "過去7日", days: 7 },
    { id: "30", label: "過去30日", days: 30 },
    { id: "90", label: "過去90日", days: 90 },
    { id: "all", label: "すべて", days: 0 }
  ]

  const analysisTypes = [
    { id: "all", label: "すべての分析" },
    { id: "personality", label: "個性分析" },
    { id: "communication", label: "コミュニケーション" },
    { id: "behavior", label: "行動特性" },
    { id: "sentiment", label: "感情分析" },
    { id: "topic", label: "トピック分析" },
    { id: "summary", label: "要約" }
  ]

  const getFilteredAnalyses = () => {
    const now = new Date()
    const periodDays = periods.find(p => p.id === selectedPeriod)?.days || 30
    const cutoffDate = new Date(now.getTime() - periodDays * 24 * 60 * 60 * 1000)

    return analyses.filter(analysis => {
      const analysisDate = new Date(analysis.created_at)
      const dateMatch = analysisDate >= cutoffDate
      const typeMatch = selectedType === "all" || analysis.analysis_type === selectedType
      return dateMatch && typeMatch
    })
  }

  const filteredAnalyses = getFilteredAnalyses()

  const getAnalysisStats = () => {
    const stats = {
      total: filteredAnalyses.length,
      personality: filteredAnalyses.filter(a => a.analysis_type === "personality").length,
      communication: filteredAnalyses.filter(a => a.analysis_type === "communication").length,
      behavior: filteredAnalyses.filter(a => a.analysis_type === "behavior").length,
      avgConfidence: filteredAnalyses.length > 0 
        ? filteredAnalyses.reduce((sum, a) => sum + a.confidence_score, 0) / filteredAnalyses.length 
        : 0,
      avgSentiment: filteredAnalyses.length > 0 
        ? filteredAnalyses.reduce((sum, a) => sum + (a.sentiment_score || 0), 0) / filteredAnalyses.length 
        : 0
    }
    return stats
  }

  const getTrendData = () => {
    const trendData = []
    const periodDays = periods.find(p => p.id === selectedPeriod)?.days || 30
    
    for (let i = periodDays - 1; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      const dateStr = date.toISOString().split('T')[0]
      
      const dayAnalyses = filteredAnalyses.filter(a => 
        a.created_at.startsWith(dateStr)
      )
      
      trendData.push({
        date: dateStr,
        count: dayAnalyses.length,
        avgConfidence: dayAnalyses.length > 0 
          ? dayAnalyses.reduce((sum, a) => sum + a.confidence_score, 0) / dayAnalyses.length 
          : 0
      })
    }
    
    return trendData
  }

  const getTopKeywords = () => {
    const keywordCount: Record<string, number> = {}
    
    filteredAnalyses.forEach(analysis => {
      analysis.keywords?.forEach(keyword => {
        keywordCount[keyword] = (keywordCount[keyword] || 0) + 1
      })
    })
    
    return Object.entries(keywordCount)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([keyword, count]) => ({ keyword, count }))
  }

  const getTopTopics = () => {
    const topicCounts: Record<string, number> = {}
    
    filteredAnalyses.forEach(analysis => {
      analysis.topics?.forEach(topic => {
        topicCounts[topic] = (topicCounts[topic] || 0) + 1
      })
    })
    
    return Object.entries(topicCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 8)
      .map(([topic, count]) => ({ topic, count }))
  }

  // 認証が必要な場合の表示
  if (!backendToken) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="mb-6">
            <LogIn className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">認証が必要です</h1>
            <p className="text-gray-600 mb-4">
              分析レポートを表示するには、ログインが必要です。
            </p>
            <Link href="/auth/login">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <LogIn className="h-4 w-4 mr-2" />
                ログイン
              </Button>
            </Link>
          </div>
          
          {user && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 max-w-md mx-auto">
              <p className="text-sm text-yellow-800">
                <strong>Firebase認証済み:</strong> {user.email}
              </p>
              <p className="text-sm text-yellow-700 mt-1">
                バックエンドとの連携が完了していません。ページを再読み込みしてください。
              </p>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600 mb-4">エラーが発生しました</h1>
            <p className="text-gray-600">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  const stats = getAnalysisStats()
  const trendData = getTrendData()
  const topKeywords = getTopKeywords()
  const topTopics = getTopTopics()

  return (
    <div className="container mx-auto px-4 py-8">
      {/* ヘッダー */}
      <div className="mb-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            分析レポート
          </h1>
          <p className="text-gray-600">
            期間別・タイプ別の詳細な分析レポートとトレンド分析
          </p>
        </div>

        {/* フィルター */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">期間:</span>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {periods.map(period => (
                    <SelectItem key={period.id} value={period.id}>
                      {period.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">分析タイプ:</span>
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {analysisTypes.map(type => (
                  <SelectItem key={type.id} value={type.id}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* 統計サマリー */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
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
              <Star className="h-5 w-5 text-yellow-500" />
              <div>
                <p className="text-sm text-gray-600">個性分析</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.personality}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm text-gray-600">コミュニケーション</p>
                <p className="text-2xl font-bold text-green-600">{stats.communication}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-purple-500" />
              <div>
                <p className="text-sm text-gray-600">行動特性</p>
                <p className="text-2xl font-bold text-purple-600">{stats.behavior}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-indigo-500" />
              <div>
                <p className="text-sm text-gray-600">平均信頼度</p>
                <p className="text-2xl font-bold text-indigo-600">
                  {Math.round(stats.avgConfidence * 100)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* メインコンテンツ */}
      {isLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">レポートを読み込み中...</p>
        </div>
      ) : filteredAnalyses.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">データがありません</h3>
            <p className="text-gray-600">選択された条件に一致する分析データがありません</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-8">
          {/* トレンド分析 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-green-500" />
                  <span>分析件数の推移</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <AnalyticsChart
                  analyses={filteredAnalyses}
                  chartType="line"
                  dataType="confidence"
                  title=""
                  className="h-64"
                />
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5 text-blue-500" />
                  <span>信頼度の推移</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <AnalyticsChart
                  analyses={filteredAnalyses}
                  chartType="area"
                  dataType="confidence"
                  title=""
                  className="h-64"
                />
              </CardContent>
            </Card>
          </div>

          {/* 詳細分析 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {stats.personality > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Star className="h-5 w-5 text-yellow-500" />
                    <span>性格特性分析</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <AnalyticsChart
                    analyses={filteredAnalyses}
                    chartType="radar"
                    dataType="personality"
                    title=""
                    className="h-64"
                  />
                </CardContent>
              </Card>
            )}
            
            {stats.communication > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <MessageSquare className="h-5 w-5 text-green-500" />
                    <span>コミュニケーションパターン</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <AnalyticsChart
                    analyses={filteredAnalyses}
                    chartType="pie"
                    dataType="communication"
                    title=""
                    className="h-64"
                  />
                </CardContent>
              </Card>
            )}
          </div>

          {/* キーワード分析 */}
          {topKeywords.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Eye className="h-5 w-5 text-purple-500" />
                  <span>トップキーワード</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {topKeywords.map(({ keyword, count }, index) => (
                    <div key={index} className="text-center p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm font-medium text-gray-900">{keyword}</p>
                      <Badge variant="secondary" className="mt-1">
                        {count}回
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

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
      )}
    </div>
  )
}