"use client"

import { useState, useEffect, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/Select"
import { 
  Search, 
  Filter, 
  SortAsc, 
  SortDesc, 
  Calendar,
  Brain,
  MessageSquare,
  Activity,
  Star,
  Heart,
  TrendingUp,
  Download,
  Trash2,
  Eye
} from "lucide-react"
import { AnalysisResponse, AnalysisType } from "@/lib/api/analytics"
import { useAIAnalysis } from "@/hooks/useAIAnalysis"
import { useRealtimeAnalysis } from "@/hooks/useRealtimeAnalysis"

interface AnalysisHistoryProps {
  onSelectAnalysis?: (analysis: AnalysisResponse) => void
  onExportHistory?: () => void
  onDeleteAnalysis?: (analysisId: string) => void
}

type SortField = 'created_at' | 'title' | 'analysis_type' | 'confidence_score' | 'sentiment_score'
type SortOrder = 'asc' | 'desc'

export function AnalysisHistory({ 
  onSelectAnalysis, 
  onExportHistory, 
  onDeleteAnalysis 
}: AnalysisHistoryProps) {
  const { analyses, isLoading, error, refreshAnalyses, deleteAnalysis } = useAIAnalysis()
  const { isConnected, connectionStatus } = useRealtimeAnalysis()
  
  // フィルタリング・検索・並び替えの状態
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedType, setSelectedType] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")
  const [sortField, setSortField] = useState<SortField>('created_at')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const [selectedAnalyses, setSelectedAnalyses] = useState<Set<string>>(new Set())

  // 分析タイプのオプション
  const analysisTypeOptions = [
    { value: "all", label: "すべて" },
    { value: "personality", label: "個性分析" },
    { value: "communication", label: "コミュニケーション" },
    { value: "behavior", label: "行動特性" },
    { value: "sentiment", label: "感情分析" },
    { value: "topic", label: "トピック分析" },
    { value: "summary", label: "要約分析" }
  ]

  // ステータスのオプション
  const statusOptions = [
    { value: "all", label: "すべて" },
    { value: "processing", label: "処理中" },
    { value: "completed", label: "完了" },
    { value: "failed", label: "失敗" }
  ]

  // 並び替えフィールドのオプション
  const sortFieldOptions = [
    { value: "created_at", label: "作成日時" },
    { value: "title", label: "タイトル" },
    { value: "analysis_type", label: "分析タイプ" },
    { value: "confidence_score", label: "信頼度" },
    { value: "sentiment_score", label: "感情スコア" }
  ]

  // フィルタリング・検索・並び替えを適用した分析結果
  const filteredAnalyses = useMemo(() => {
    let filtered = analyses.filter(analysis => {
      // 検索クエリでフィルタリング
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        const matchesSearch = 
          analysis.title.toLowerCase().includes(query) ||
          analysis.summary.toLowerCase().includes(query) ||
          analysis.keywords.some(keyword => keyword.toLowerCase().includes(query)) ||
          analysis.topics.some(topic => topic.toLowerCase().includes(query))
        
        if (!matchesSearch) return false
      }

      // 分析タイプでフィルタリング
      if (selectedType !== "all" && analysis.analysis_type !== selectedType) {
        return false
      }

      // ステータスでフィルタリング
      if (selectedStatus !== "all" && analysis.status !== selectedStatus) {
        return false
      }

      return true
    })

    // 並び替え
    filtered.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortField) {
        case 'created_at':
          aValue = new Date(a.created_at).getTime()
          bValue = new Date(b.created_at).getTime()
          break
        case 'title':
          aValue = a.title.toLowerCase()
          bValue = b.title.toLowerCase()
          break
        case 'analysis_type':
          aValue = a.analysis_type.toLowerCase()
          bValue = b.analysis_type.toLowerCase()
          break
        case 'confidence_score':
          aValue = a.confidence_score || 0
          bValue = b.confidence_score || 0
          break
        case 'sentiment_score':
          aValue = a.sentiment_score || 0
          bValue = b.sentiment_score || 0
          break
        default:
          aValue = 0
          bValue = 0
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

    return filtered
  }, [analyses, searchQuery, selectedType, selectedStatus, sortField, sortOrder])

  // 分析タイプのアイコンを取得
  const getAnalysisTypeIcon = (type: string) => {
    switch (type) {
      case 'personality':
        return <Star className="h-4 w-4 text-yellow-500" />
      case 'communication':
        return <MessageSquare className="h-4 w-4 text-blue-500" />
      case 'behavior':
        return <Activity className="h-4 w-4 text-purple-500" />
      case 'sentiment':
        return <Heart className="h-4 w-4 text-red-500" />
      case 'topic':
        return <Brain className="h-4 w-4 text-green-500" />
      case 'summary':
        return <TrendingUp className="h-4 w-4 text-indigo-500" />
      default:
        return <Brain className="h-4 w-4 text-gray-500" />
    }
  }

  // 分析タイプのラベルを取得
  const getAnalysisTypeLabel = (type: string) => {
    const option = analysisTypeOptions.find(opt => opt.value === type)
    return option ? option.label : type
  }

  // ステータスのバッジを取得
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-100 text-green-800">完了</Badge>
      case 'processing':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">処理中</Badge>
      case 'failed':
        return <Badge variant="destructive" className="bg-red-100 text-red-800">失敗</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  // 感情スコアの色を取得
  const getSentimentColor = (score: number) => {
    if (score >= 0.7) return "text-green-600"
    if (score >= 0.4) return "text-yellow-600"
    return "text-red-600"
  }

  // 分析結果を選択
  const handleSelectAnalysis = (analysis: AnalysisResponse) => {
    if (onSelectAnalysis) {
      onSelectAnalysis(analysis)
    }
  }

  // 分析結果を削除
  const handleDeleteAnalysis = async (analysisId: string) => {
    if (onDeleteAnalysis) {
      onDeleteAnalysis(analysisId)
    } else {
      const success = await deleteAnalysis(analysisId)
      if (success) {
        setSelectedAnalyses(prev => {
          const newSet = new Set(prev)
          newSet.delete(analysisId)
          return newSet
        })
      }
    }
  }

  // 選択された分析結果を一括削除
  const handleBulkDelete = async () => {
    if (selectedAnalyses.size === 0) return

    const confirmed = confirm(`${selectedAnalyses.size}件の分析結果を削除しますか？`)
    if (!confirmed) return

    for (const analysisId of Array.from(selectedAnalyses)) {
      await handleDeleteAnalysis(analysisId)
    }
    setSelectedAnalyses(new Set())
  }

  // 選択状態を切り替え
  const toggleSelection = (analysisId: string) => {
    setSelectedAnalyses(prev => {
      const newSet = new Set(prev)
      if (newSet.has(analysisId)) {
        newSet.delete(analysisId)
      } else {
        newSet.add(analysisId)
      }
      return newSet
    })
  }

  // 全選択・全選択解除
  const toggleAllSelection = () => {
    if (selectedAnalyses.size === filteredAnalyses.length) {
      setSelectedAnalyses(new Set())
    } else {
      setSelectedAnalyses(new Set(filteredAnalyses.map(a => a.id)))
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>分析履歴</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>分析履歴</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-red-600">
            <p>エラーが発生しました: {error}</p>
            <Button onClick={refreshAnalyses} className="mt-4">
              再試行
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Brain className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <CardTitle className="text-2xl">分析履歴</CardTitle>
                <div className="flex items-center space-x-2 mt-1">
                  <Badge variant="outline">
                    {filteredAnalyses.length}件の分析結果
                  </Badge>
                  <Badge 
                    variant={isConnected ? "default" : "secondary"}
                    className="flex items-center space-x-1"
                  >
                    <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                    {isConnected ? 'リアルタイム接続中' : 'オフライン'}
                  </Badge>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" onClick={refreshAnalyses}>
                <TrendingUp className="h-4 w-4 mr-2" />
                更新
              </Button>
              {onExportHistory && (
                <Button variant="outline" onClick={onExportHistory}>
                  <Download className="h-4 w-4 mr-2" />
                  エクスポート
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* フィルター・検索・並び替え */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            {/* 検索 */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="検索..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* 分析タイプフィルター */}
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger>
                <SelectValue placeholder="分析タイプ" />
              </SelectTrigger>
              <SelectContent>
                {analysisTypeOptions.map(option => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* ステータスフィルター */}
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger>
                <SelectValue placeholder="ステータス" />
              </SelectTrigger>
              <SelectContent>
                {statusOptions.map(option => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* 並び替え */}
            <div className="flex space-x-2">
              <Select value={sortField} onValueChange={(value) => setSortField(value as SortField)}>
                <SelectTrigger>
                  <SelectValue placeholder="並び替え" />
                </SelectTrigger>
                <SelectContent>
                  {sortFieldOptions.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
              >
                {sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          {/* 一括操作 */}
          {selectedAnalyses.size > 0 && (
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
              <span className="text-sm text-blue-700">
                {selectedAnalyses.size}件が選択されています
              </span>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleAllSelection}
                >
                  {selectedAnalyses.size === filteredAnalyses.length ? '全選択解除' : '全選択'}
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleBulkDelete}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  一括削除
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 分析結果一覧 */}
      <div className="space-y-4">
        {filteredAnalyses.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8 text-gray-500">
              <Brain className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>分析結果が見つかりません</p>
              <p className="text-sm">検索条件を変更するか、新しい分析を実行してください</p>
            </CardContent>
          </Card>
        ) : (
          filteredAnalyses.map(analysis => (
            <Card key={analysis.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  {/* 選択チェックボックス */}
                  <input
                    type="checkbox"
                    checked={selectedAnalyses.has(analysis.id)}
                    onChange={() => toggleSelection(analysis.id)}
                    className="mt-1 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  />

                  {/* 分析タイプアイコン */}
                  <div className="p-2 bg-gray-100 rounded-lg">
                    {getAnalysisTypeIcon(analysis.analysis_type)}
                  </div>

                  {/* 分析内容 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-gray-900 truncate">
                          {analysis.title}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                          {analysis.summary}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        {getStatusBadge(analysis.status)}
                        <Badge variant="outline">
                          {getAnalysisTypeLabel(analysis.analysis_type)}
                        </Badge>
                      </div>
                    </div>

                    {/* メタデータ */}
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-4 w-4" />
                        <span>{new Date(analysis.created_at).toLocaleDateString('ja-JP')}</span>
                      </div>
                      {analysis.confidence_score && (
                        <span>信頼度: {((analysis.confidence_score) * 100).toFixed(1)}%</span>
                      )}
                      {analysis.sentiment_score && (
                        <span className={`${getSentimentColor(analysis.sentiment_score)}`}>
                          感情: {((analysis.sentiment_score) * 100).toFixed(0)}/100
                        </span>
                      )}
                    </div>

                    {/* キーワードとトピック */}
                    <div className="flex flex-wrap gap-2 mb-3">
                      {analysis.keywords?.slice(0, 3).map((keyword, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                      {analysis.keywords && analysis.keywords.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{analysis.keywords.length - 3}件
                        </Badge>
                      )}
                    </div>

                    {/* アクションボタン */}
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSelectAnalysis(analysis)}
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        詳細表示
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteAnalysis(analysis.id)}
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        削除
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
