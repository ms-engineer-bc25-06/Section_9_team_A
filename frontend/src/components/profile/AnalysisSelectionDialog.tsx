"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Search, FileText, Calendar, User, Eye, EyeOff } from 'lucide-react'

// 分析結果の型定義（実際のAPIレスポンスに合わせて調整）
interface Analysis {
  id: number
  title: string
  analysis_type: string
  created_at: string
  is_public: boolean
  visibility_level: string
  user_id: number
  user_name: string
}

interface AnalysisSelectionDialogProps {
  isOpen: boolean
  onClose: () => void
  onSelect: (analysis: Analysis) => void
}

export function AnalysisSelectionDialog({ isOpen, onClose, onSelect }: AnalysisSelectionDialogProps) {
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [filteredAnalyses, setFilteredAnalyses] = useState<Analysis[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedAnalysis, setSelectedAnalysis] = useState<Analysis | null>(null)

  // モックデータ（実際の実装ではAPIから取得）
  useEffect(() => {
    if (isOpen) {
      setLoading(true)
      // シミュレーション用の遅延
      setTimeout(() => {
        const mockAnalyses: Analysis[] = [
          {
            id: 1,
            title: "コミュニケーションスタイル分析",
            analysis_type: "communication",
            created_at: "2024-01-15T10:30:00Z",
            is_public: false,
            visibility_level: "private",
            user_id: 1,
            user_name: "田中太郎"
          },
          {
            id: 2,
            title: "チーム内での役割分析",
            analysis_type: "team_role",
            created_at: "2024-01-14T15:45:00Z",
            is_public: false,
            visibility_level: "private",
            user_id: 1,
            user_name: "田中太郎"
          },
          {
            id: 3,
            title: "リーダーシップ傾向分析",
            analysis_type: "leadership",
            created_at: "2024-01-13T09:20:00Z",
            is_public: false,
            visibility_level: "private",
            user_id: 1,
            user_name: "田中太郎"
          },
          {
            id: 4,
            title: "ストレス耐性分析",
            analysis_type: "stress_tolerance",
            created_at: "2024-01-12T14:15:00Z",
            is_public: false,
            visibility_level: "private",
            user_id: 1,
            user_name: "田中太郎"
          }
        ]
        setAnalyses(mockAnalyses)
        setFilteredAnalyses(mockAnalyses)
        setLoading(false)
      }, 500)
    }
  }, [isOpen])

  // 検索フィルタリング
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredAnalyses(analyses)
    } else {
      const filtered = analyses.filter(analysis =>
        analysis.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        analysis.analysis_type.toLowerCase().includes(searchTerm.toLowerCase())
      )
      setFilteredAnalyses(filtered)
    }
  }, [searchTerm, analyses])

  // 分析結果の選択
  const handleAnalysisSelect = (analysis: Analysis) => {
    setSelectedAnalysis(analysis)
  }

  // 承認リクエスト作成の開始
  const handleStartApproval = () => {
    if (selectedAnalysis) {
      onSelect(selectedAnalysis)
      onClose()
    }
  }

  // 分析タイプの日本語表示
  const getAnalysisTypeLabel = (type: string) => {
    const typeLabels: Record<string, string> = {
      'communication': 'コミュニケーション',
      'team_role': 'チーム役割',
      'leadership': 'リーダーシップ',
      'stress_tolerance': 'ストレス耐性',
      'personality': '性格分析',
      'work_style': '仕事スタイル'
    }
    return typeLabels[type] || type
  }

  // 可視性レベルの日本語表示
  const getVisibilityLabel = (level: string) => {
    const levelLabels: Record<string, string> = {
      'private': '本人のみ',
      'team': 'チーム内',
      'organization': '組織内',
      'public': '公開'
    }
    return levelLabels[level] || level
  }

  // 日付のフォーマット
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">分析結果を選択</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            ✕
          </Button>
        </div>

        <div className="p-6">
          {/* 検索バー */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="分析結果を検索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* 分析結果一覧 */}
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">読み込み中...</p>
            </div>
          ) : filteredAnalyses.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">分析結果が見つかりません</p>
              <p className="text-sm text-gray-500 mt-1">
                {searchTerm ? '検索条件を変更してください' : '分析結果がありません'}
              </p>
            </div>
          ) : (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {filteredAnalyses.map((analysis) => (
                <Card
                  key={analysis.id}
                  className={`cursor-pointer transition-all ${
                    selectedAnalysis?.id === analysis.id
                      ? 'ring-2 ring-blue-500 bg-blue-50'
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleAnalysisSelect(analysis)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-medium text-gray-900">{analysis.title}</h3>
                          <Badge variant="secondary">
                            {getAnalysisTypeLabel(analysis.analysis_type)}
                          </Badge>
                          {analysis.is_public ? (
                            <Badge className="bg-green-100 text-green-800">
                              <Eye className="h-3 w-3 mr-1" />
                              公開中
                            </Badge>
                          ) : (
                            <Badge variant="outline">
                              <EyeOff className="h-3 w-3 mr-1" />
                              {getVisibilityLabel(analysis.visibility_level)}
                            </Badge>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span className="flex items-center">
                            <Calendar className="h-3 w-3 mr-1" />
                            {formatDate(analysis.created_at)}
                          </span>
                          <span className="flex items-center">
                            <User className="h-3 w-3 mr-1" />
                            {analysis.user_name}
                          </span>
                        </div>
                      </div>
                      
                      <div className="ml-4">
                        <Button
                          variant={selectedAnalysis?.id === analysis.id ? "default" : "outline"}
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleAnalysisSelect(analysis)
                          }}
                        >
                          {selectedAnalysis?.id === analysis.id ? '選択済み' : '選択'}
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* アクションボタン */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t bg-gray-50">
          <Button variant="outline" onClick={onClose}>
            キャンセル
          </Button>
          <Button
            onClick={handleStartApproval}
            disabled={!selectedAnalysis}
          >
            承認リクエストを作成
          </Button>
        </div>
      </div>
    </div>
  )
}
