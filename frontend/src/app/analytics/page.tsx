"use client"

import { useState } from "react"
import { AnalyticsCard } from "@/components/analytics/AnalyticsCard"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { useAIAnalysis } from "@/hooks/useAIAnalysis"
import { ArrowLeft, BarChart3, Filter, Download, Calendar, TrendingUp, Brain, MessageSquare, Activity } from "lucide-react"
import Link from "next/link"

export default function AnalyticsPage() {
  const { analyses, isLoading, error } = useAIAnalysis()
  const [selectedType, setSelectedType] = useState<string>("all")
  const [sortBy, setSortBy] = useState<"date" | "confidence" | "type">("date")

  const analysisTypes = [
    { id: "all", label: "すべて", icon: <Brain className="h-4 w-4" /> },
    { id: "personality", label: "個性分析", icon: <Brain className="h-4 w-4 text-yellow-500" /> },
    { id: "communication", label: "コミュニケーション", icon: <MessageSquare className="h-4 w-4 text-blue-500" /> },
    { id: "behavior", label: "行動特性", icon: <Activity className="h-4 w-4 text-purple-500" /> }
  ]

  const filteredAnalyses = analyses.filter(analysis => 
    selectedType === "all" || analysis.analysisType === selectedType
  )

  const sortedAnalyses = [...filteredAnalyses].sort((a, b) => {
    switch (sortBy) {
      case "date":
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      case "confidence":
        return b.confidenceScore - a.confidenceScore
      case "type":
        return a.analysisType.localeCompare(b.analysisType)
      default:
        return 0
    }
  })

  const getAnalysisTypeStats = () => {
    const stats = { personality: 0, communication: 0, behavior: 0, total: analyses.length }
    analyses.forEach(analysis => {
      if (analysis.analysisType in stats) {
        stats[analysis.analysisType as keyof typeof stats]++
      }
    })
    return stats
  }

  const stats = getAnalysisTypeStats()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">分析結果を読み込み中...</p>
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
              <Link href="/profile">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  プロフィールへ戻る
                </Button>
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">AI分析結果</h1>
            </div>
            <div className="flex items-center space-x-2">
              <Link href="/analytics/reports">
                <Button variant="outline">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  詳細レポート
                </Button>
              </Link>
              <Button>
                <Download className="h-4 w-4 mr-2" />
                エクスポート
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* 統計サマリー */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">総分析数</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">個性分析</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats.personality}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">コミュニケーション</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.communication}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">行動特性</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{stats.behavior}</div>
            </CardContent>
          </Card>
        </div>

        {/* フィルターとソート */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">分析タイプ:</span>
              </div>
              <div className="flex space-x-2">
                {analysisTypes.map((type) => (
                  <Button
                    key={type.id}
                    variant={selectedType === type.id ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedType(type.id)}
                    className="flex items-center space-x-2"
                  >
                    {type.icon}
                    <span>{type.label}</span>
                  </Button>
                ))}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-700">並び順:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as "date" | "confidence" | "type")}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="date">日付順</option>
                <option value="confidence">信頼度順</option>
                <option value="type">タイプ順</option>
              </select>
            </div>
          </div>
        </div>

        {/* 分析結果一覧 */}
        {sortedAnalyses.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">分析結果がありません</h3>
              <p className="text-gray-600 mb-4">
                まだAI分析が実行されていないか、選択された条件に一致する結果がありません。
              </p>
              <Link href="/profile">
                <Button>
                  プロフィールで分析を実行
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {sortedAnalyses.map((analysis) => (
              <AnalyticsCard
                key={analysis.id}
                analysis={analysis}
                onViewDetails={(analysis) => {
                  // 詳細表示の処理（必要に応じて実装）
                  console.log("詳細表示:", analysis)
                }}
                onDelete={(analysisId) => {
                  // 削除処理（必要に応じて実装）
                  console.log("削除:", analysisId)
                }}
              />
            ))}
          </div>
        )}

        {/* ページネーション（必要に応じて） */}
        {sortedAnalyses.length > 10 && (
          <div className="mt-8 flex justify-center">
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">前へ</Button>
              <Button variant="outline" size="sm">1</Button>
              <Button variant="outline" size="sm">2</Button>
              <Button variant="outline" size="sm">3</Button>
              <Button variant="outline" size="sm">次へ</Button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}