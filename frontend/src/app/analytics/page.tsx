"use client"

import { AnalyticsCard, AnalyticsDashboard } from "@/components/analytics"
import { useAIAnalysis } from "@/hooks/useAIAnalysis"
import { useAuth } from "@/components/auth/AuthProvider"
import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/Select"
import { 
  Brain, 
  MessageSquare, 
  TrendingUp, 
  Activity, 
  Star,
  Plus,
  Filter,
  BarChart3,
  LogIn
} from "lucide-react"
import Link from "next/link"

export default function AnalyticsPage() {
  const { analyses, isLoading, error, deleteAnalysis } = useAIAnalysis()
  const { backendToken, user, isLoading: authLoading } = useAuth()
  const [selectedType, setSelectedType] = useState<string>("all")
  const [sortBy, setSortBy] = useState<string>("date")
  const [viewMode, setViewMode] = useState<'list' | 'dashboard'>('dashboard')
  const [isRetrying, setIsRetrying] = useState(false)

  // 認証状態の読み込み中
  if (authLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">認証状態を確認中...</p>
        </div>
      </div>
    )
  }

  // 認証が必要な場合の表示
  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="mb-6">
            <LogIn className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">認証が必要です</h1>
            <p className="text-gray-600 mb-4">
              AI分析結果を表示するには、ログインが必要です。
            </p>
            <Link href="/analytics/login">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <LogIn className="h-4 w-4 mr-2" />
                AI分析にログイン
              </Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // Firebase認証済みだがバックエンド連携が未完了の場合
  if (!backendToken) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="mb-6">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 max-w-md mx-auto">
              <div className="mb-4">
                <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">⚠️</span>
                </div>
                <h2 className="text-xl font-semibold text-yellow-800 mb-2">
                  Firebase認証済み: {user.email}
                </h2>
                <p className="text-sm text-yellow-700 mb-4">
                  バックエンドとの連携が完了していません。
                </p>
              </div>
              
              <div className="space-y-3">
                <Button 
                  onClick={() => window.location.reload()} 
                  className="w-full bg-yellow-600 hover:bg-yellow-700"
                  disabled={isRetrying}
                >
                  {isRetrying ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      連携中...
                    </>
                  ) : (
                    <>
                      <LogIn className="h-4 w-4 mr-2" />
                      再読み込み
                    </>
                  )}
                </Button>
                
                <Link href="/analytics/login">
                  <Button variant="outline" className="w-full">
                    ログインページに戻る
                  </Button>
                </Link>
              </div>
              
              <div className="mt-4 text-xs text-yellow-600 bg-yellow-100 p-2 rounded">
                <p>Debug: backendToken = {backendToken ? '存在' : 'null'}</p>
                <p>Debug: user.uid = {user.uid}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const filteredAnalyses = analyses.filter(analysis => 
    selectedType === "all" || analysis.analysis_type === selectedType
  )

  const sortedAnalyses = [...filteredAnalyses].sort((a, b) => {
    switch (sortBy) {
      case "date":
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case "confidence":
        return b.confidence_score - a.confidence_score
      case "type":
        return a.analysis_type.localeCompare(b.analysis_type)
      default:
        return 0
    }
  })

  const getAnalysisTypeStats = () => {
    const stats = { personality: 0, communication: 0, behavior: 0, total: analyses.length }
    analyses.forEach(analysis => {
      if (analysis.analysis_type in stats) {
        stats[analysis.analysis_type as keyof typeof stats]++
      }
    })
    return stats
  }

  const stats = getAnalysisTypeStats()

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">エラーが発生しました</h1>
          <p className="text-gray-600">{error}</p>
          <div className="mt-4">
            <Button onClick={() => window.location.reload()}>
              再読み込み
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* ヘッダー */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              AI分析結果
            </h1>
            <p className="text-gray-600">
              音声チャットのAI分析結果を確認・管理できます
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button
              onClick={() => setViewMode(viewMode === 'dashboard' ? 'list' : 'dashboard')}
              variant="outline"
              className="flex items-center space-x-2"
            >
              {viewMode === 'dashboard' ? (
                <>
                  <BarChart3 className="h-4 w-4" />
                  <span>リスト表示</span>
                </>
              ) : (
                <>
                  <TrendingUp className="h-4 w-4" />
                  <span>ダッシュボード</span>
                </>
              )}
            </Button>
            
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="h-4 w-4 mr-2" />
              新規分析
            </Button>
          </div>
        </div>

        {/* 統計情報 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center space-x-2">
              <Brain className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-gray-600">総分析数</p>
                <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center space-x-2">
              <Star className="h-5 w-5 text-yellow-500" />
              <div>
                <p className="text-sm text-gray-600">個性分析</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.personality}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm text-gray-600">コミュニケーション</p>
                <p className="text-2xl font-bold text-green-600">{stats.communication}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-purple-500" />
              <div>
                <p className="text-sm text-gray-600">行動特性</p>
                <p className="text-2xl font-bold text-purple-600">{stats.behavior}</p>
              </div>
            </div>
          </div>
        </div>

        {/* フィルター・ソート */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">フィルター:</span>
            </div>
            
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">すべての分析</SelectItem>
                <SelectItem value="personality">個性分析</SelectItem>
                <SelectItem value="communication">コミュニケーション</SelectItem>
                <SelectItem value="behavior">行動特性</SelectItem>
                <SelectItem value="sentiment">感情分析</SelectItem>
                <SelectItem value="topic">トピック分析</SelectItem>
                <SelectItem value="summary">要約</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">ソート:</span>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="date">日付順</SelectItem>
                <SelectItem value="confidence">信頼度順</SelectItem>
                <SelectItem value="type">タイプ順</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      {viewMode === 'dashboard' ? (
        <AnalyticsDashboard analyses={analyses} isLoading={isLoading} />
      ) : (
        <div className="space-y-6">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">分析結果を読み込み中...</p>
            </div>
          ) : sortedAnalyses.length === 0 ? (
            <div className="text-center py-8">
              <Brain className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">分析結果がありません</h3>
              <p className="text-gray-600">音声チャットに参加してAI分析を開始してください</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {sortedAnalyses.map((analysis) => (
                <AnalyticsCard
                  key={analysis.id}
                  analysis={analysis}
                  onDelete={deleteAnalysis}
                  showActions={true}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}