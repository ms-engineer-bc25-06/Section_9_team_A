"use client"

import { useState } from "react"
import { useAIAnalysis } from "@/hooks/useAIAnalysis"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { ArrowLeft, BarChart3, TrendingUp, Calendar, Download, Filter, Brain, MessageSquare, Activity, Star, Users, Target } from "lucide-react"
import Link from "next/link"

export default function ReportsPage() {
  const { analyses, isLoading, error } = useAIAnalysis()
  const [selectedPeriod, setSelectedPeriod] = useState<string>("month")
  const [selectedType, setSelectedType] = useState<string>("all")

  const periods = [
    { id: "week", label: "1週間", days: 7 },
    { id: "month", label: "1ヶ月", days: 30 },
    { id: "quarter", label: "3ヶ月", days: 90 },
    { id: "year", label: "1年", days: 365 }
  ]

  const analysisTypes = [
    { id: "all", label: "すべて", icon: <Brain className="h-4 w-4" /> },
    { id: "personality", label: "個性分析", icon: <Brain className="h-4 w-4 text-yellow-500" /> },
    { id: "communication", label: "コミュニケーション", icon: <MessageSquare className="h-4 w-4 text-blue-500" /> },
    { id: "behavior", label: "行動特性", icon: <Activity className="h-4 w-4 text-purple-500" /> }
  ]

  const getFilteredAnalyses = () => {
    const now = new Date()
    const periodDays = periods.find(p => p.id === selectedPeriod)?.days || 30
    const cutoffDate = new Date(now.getTime() - periodDays * 24 * 60 * 60 * 1000)

    return analyses.filter(analysis => {
      const analysisDate = new Date(analysis.createdAt)
      const dateMatch = analysisDate >= cutoffDate
      const typeMatch = selectedType === "all" || analysis.analysisType === selectedType
      return dateMatch && typeMatch
    })
  }

  const filteredAnalyses = getFilteredAnalyses()

  const getAnalysisStats = () => {
    const stats = {
      total: filteredAnalyses.length,
      personality: filteredAnalyses.filter(a => a.analysisType === "personality").length,
      communication: filteredAnalyses.filter(a => a.analysisType === "communication").length,
      behavior: filteredAnalyses.filter(a => a.analysisType === "behavior").length,
      avgConfidence: filteredAnalyses.length > 0 
        ? filteredAnalyses.reduce((sum, a) => sum + a.confidenceScore, 0) / filteredAnalyses.length 
        : 0,
      avgSentiment: filteredAnalyses.length > 0 
        ? filteredAnalyses.reduce((sum, a) => sum + (a.sentimentScore || 0), 0) / filteredAnalyses.length 
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
        a.createdAt.startsWith(dateStr)
      )
      
      trendData.push({
        date: dateStr,
        count: dayAnalyses.length,
        avgConfidence: dayAnalyses.length > 0 
          ? dayAnalyses.reduce((sum, a) => sum + a.confidenceScore, 0) / dayAnalyses.length 
          : 0
      })
    }
    
    return trendData
  }

  const getTopKeywords = () => {
    const keywordCounts: Record<string, number> = {}
    
    filteredAnalyses.forEach(analysis => {
      analysis.keywords?.forEach(keyword => {
        keywordCounts[keyword] = (keywordCounts[keyword] || 0) + 1
      })
    })
    
    return Object.entries(keywordCounts)
      .sort(([,a], [,b]) => b - a)
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

  const stats = getAnalysisStats()
  const trendData = getTrendData()
  const topKeywords = getTopKeywords()
  const topTopics = getTopTopics()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">レポートを読み込み中...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              エラーが発生しました: {error}
            </div>
            <Button onClick={() => window.location.reload()}>
              再読み込み
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/analytics">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  分析結果一覧へ戻る
                </Button>
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">詳細レポート</h1>
            </div>
            <div className="flex items-center space-x-2">
              <Button>
                <Download className="h-4 w-4 mr-2" />
                PDF出力
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* フィルター */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-6">
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">期間:</span>
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                {periods.map((period) => (
                  <option key={period.id} value={period.id}>
                    {period.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">分析タイプ:</span>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                {analysisTypes.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 統計サマリー */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                <BarChart3 className="h-4 w-4 mr-2" />
                総分析数
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
              <p className="text-sm text-gray-500 mt-1">
                選択期間内の分析結果
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                <Star className="h-4 w-4 mr-2 text-yellow-500" />
                平均信頼度
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {Math.round(stats.avgConfidence * 100)}%
              </div>
              <p className="text-sm text-gray-500 mt-1">
                AI分析の精度
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                <TrendingUp className="h-4 w-4 mr-2 text-green-500" />
                平均感情スコア
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {Math.round(stats.avgSentiment * 100)}%
              </div>
              <p className="text-sm text-gray-500 mt-1">
                ポジティブ度
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 分析タイプ別統計 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                <Brain className="h-4 w-4 mr-2 text-yellow-500" />
                個性分析
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats.personality}</div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${stats.total > 0 ? (stats.personality / stats.total) * 100 : 0}%` }}
                ></div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                <MessageSquare className="h-4 w-4 mr-2 text-blue-500" />
                コミュニケーション
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.communication}</div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${stats.total > 0 ? (stats.communication / stats.total) * 100 : 0}%` }}
                ></div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                <Activity className="h-4 w-4 mr-2 text-purple-500" />
                行動特性
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{stats.behavior}</div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${stats.total > 0 ? (stats.behavior / stats.total) * 100 : 0}%` }}
                ></div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* トレンド分析 */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-green-500" />
              分析頻度の推移
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end space-x-1">
              {trendData.map((data, index) => (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div 
                    className="w-full bg-blue-500 rounded-t transition-all duration-300"
                    style={{ 
                      height: `${Math.max(data.count * 20, 4)}px`,
                      opacity: data.count > 0 ? 0.8 : 0.3
                    }}
                  ></div>
                  <span className="text-xs text-gray-500 mt-1">
                    {new Date(data.date).getDate()}
                  </span>
                </div>
              ))}
            </div>
            <div className="text-center text-sm text-gray-500 mt-2">
              日別の分析実行回数
            </div>
          </CardContent>
        </Card>

        {/* キーワードとトピック */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2 text-indigo-500" />
                頻出キーワード
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {topKeywords.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{item.keyword}</span>
                    <Badge variant="outline">{item.count}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2 text-green-500" />
                主要トピック
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {topTopics.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{item.topic}</span>
                    <Badge variant="outline">{item.count}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 分析結果がない場合 */}
        {filteredAnalyses.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">レポートデータがありません</h3>
              <p className="text-gray-600 mb-4">
                選択された期間と条件に一致する分析結果がありません。
              </p>
              <Link href="/profile">
                <Button>
                  プロフィールで分析を実行
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}