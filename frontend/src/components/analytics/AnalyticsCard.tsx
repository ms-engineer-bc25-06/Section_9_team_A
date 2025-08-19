"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { 
  Brain, 
  MessageSquare, 
  TrendingUp, 
  Star, 
  Activity,
  ChevronDown,
  ChevronUp,
  BarChart3,
  Calendar,
  Eye,
  Trash2,
  ExternalLink
} from "lucide-react"
import { AnalysisResponse } from "@/lib/api/analytics"

interface AnalyticsCardProps {
  analysis: AnalysisResponse
  onViewDetails?: (analysis: AnalysisResponse) => void
  onDelete?: (analysisId: string) => void
  showActions?: boolean
}

export function AnalyticsCard({ 
  analysis, 
  onViewDetails, 
  onDelete, 
  showActions = true 
}: AnalyticsCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const getAnalysisTypeIcon = (type: string) => {
    switch (type) {
      case "personality": return <Star className="h-4 w-4 text-yellow-500" />
      case "communication": return <MessageSquare className="h-4 w-4 text-blue-500" />
      case "behavior": return <Activity className="h-4 w-4 text-purple-500" />
      case "sentiment": return <BarChart3 className="h-4 w-4 text-green-500" />
      case "topic": return <Brain className="h-4 w-4 text-indigo-500" />
      case "summary": return <Brain className="h-4 w-4 text-gray-500" />
      default: return <Brain className="h-4 w-4 text-gray-500" />
    }
  }

  const getAnalysisTypeLabel = (type: string) => {
    switch (type) {
      case "personality": return "個性分析"
      case "communication": return "コミュニケーション"
      case "behavior": return "行動特性"
      case "sentiment": return "感情分析"
      case "topic": return "トピック分析"
      case "summary": return "要約"
      default: return "分析"
    }
  }

  const getAnalysisTypeColor = (type: string) => {
    switch (type) {
      case "personality": return "bg-yellow-100 text-yellow-800"
      case "communication": return "bg-blue-100 text-blue-800"
      case "behavior": return "bg-purple-100 text-purple-800"
      case "sentiment": return "bg-green-100 text-green-800"
      case "topic": return "bg-indigo-100 text-indigo-800"
      case "summary": return "bg-gray-100 text-gray-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

  const getSentimentColor = (score: number) => {
    if (score >= 0.7) return "text-green-600 bg-green-100"
    if (score >= 0.4) return "text-yellow-600 bg-yellow-100"
    return "text-red-600 bg-red-100"
  }

  const getSentimentLabel = (score: number) => {
    if (score >= 0.7) return "ポジティブ"
    if (score >= 0.4) return "ニュートラル"
    return "ネガティブ"
  }

  const getTrendIcon = (trend: "up" | "down" | "stable") => {
    switch (trend) {
      case "up": return <TrendingUp className="h-4 w-4 text-green-500" />
      case "down": return <TrendingUp className="h-4 w-4 text-red-500 rotate-180" />
      default: return <BarChart3 className="h-4 w-4 text-gray-500" />
    }
  }

  const getTrendColor = (trend: "up" | "down" | "stable") => {
    switch (trend) {
      case "up": return "text-green-600"
      case "down": return "text-red-600"
      default: return "text-gray-600"
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const renderAnalysisContent = () => {
    switch (analysis.analysis_type) {
      case "personality":
        return (
          <div className="space-y-3">
            <p className="text-gray-600 text-sm">{analysis.summary}</p>
            {analysis.personality_traits && (
              <div className="space-y-2">
                <h5 className="font-medium text-sm text-gray-700">性格特性</h5>
                <div className="grid grid-cols-1 gap-2">
                  {analysis.personality_traits.slice(0, 3).map((trait, index) => (
                    <div key={index} className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">{trait.trait}</span>
                      <Badge variant="outline" className="text-xs">
                        {trait.score}/10
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      case "communication":
        return (
          <div className="space-y-3">
            <p className="text-gray-600 text-sm">{analysis.summary}</p>
            {analysis.communication_patterns && (
              <div className="space-y-2">
                <h5 className="font-medium text-sm text-gray-700">パターン</h5>
                <div className="space-y-1">
                  {analysis.communication_patterns.slice(0, 2).map((pattern, index) => (
                    <div key={index} className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">{pattern.pattern}</span>
                      <Badge variant="outline" className="text-xs">
                        頻度: {pattern.frequency}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      case "behavior":
        return (
          <div className="space-y-3">
            <p className="text-gray-600 text-sm">{analysis.summary}</p>
            {analysis.behavior_scores && (
              <div className="space-y-2">
                <h5 className="font-medium text-sm text-gray-700">スコア</h5>
                <div className="space-y-1">
                  {analysis.behavior_scores.slice(0, 2).map((score, index) => (
                    <div key={index} className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">{score.category}</span>
                      <div className="flex items-center space-x-1">
                        {getTrendIcon(score.trend)}
                        <span className={`font-medium ${getTrendColor(score.trend)}`}>
                          {score.score}/{score.max_score}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      default:
        return (
          <div className="space-y-3">
            <p className="text-gray-600 text-sm">{analysis.summary}</p>
            {analysis.keywords && analysis.keywords.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {analysis.keywords.slice(0, 3).map((keyword, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {keyword}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        )
    }
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-2">
            {getAnalysisTypeIcon(analysis.analysis_type)}
            <div>
              <CardTitle className="text-base font-medium line-clamp-2">
                {analysis.title}
              </CardTitle>
              <div className="flex items-center space-x-2 mt-1">
                <Badge className={getAnalysisTypeColor(analysis.analysis_type)}>
                  {getAnalysisTypeLabel(analysis.analysis_type)}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {Math.round(analysis.confidence_score * 100)}%
                </Badge>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-6 w-6 p-0"
            >
              {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* 基本情報 */}
        <div className="space-y-3">
          {renderAnalysisContent()}
          
          {/* 感情分析スコア */}
          {analysis.sentiment_score !== undefined && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500">感情傾向:</span>
              <Badge className={getSentimentColor(analysis.sentiment_score)}>
                {getSentimentLabel(analysis.sentiment_score)}
              </Badge>
            </div>
          )}

          {/* 作成日時 */}
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <Calendar className="h-3 w-3" />
            <span>{formatDate(analysis.created_at)}</span>
          </div>
        </div>

        {/* 展開された詳細情報 */}
        {isExpanded && (
          <div className="mt-4 pt-3 border-t border-gray-100">
            <div className="space-y-3">
              {/* キーワード */}
              {analysis.keywords && analysis.keywords.length > 0 && (
                <div>
                  <h6 className="font-medium text-sm text-gray-700 mb-2">キーワード</h6>
                  <div className="flex flex-wrap gap-1">
                    {analysis.keywords.map((keyword, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* トピック */}
              {analysis.topics && analysis.topics.length > 0 && (
                <div>
                  <h6 className="font-medium text-sm text-gray-700 mb-2">トピック</h6>
                  <div className="flex flex-wrap gap-1">
                    {analysis.topics.map((topic, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* 詳細な分析結果 */}
              {analysis.analysis_type === "personality" && analysis.personality_traits && (
                <div>
                  <h6 className="font-medium text-sm text-gray-700 mb-2">詳細な性格特性</h6>
                  <div className="space-y-2">
                    {analysis.personality_traits.map((trait, index) => (
                      <div key={index} className="bg-gray-50 p-2 rounded text-xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">{trait.trait}</span>
                          <Badge variant="outline">{trait.score}/10</Badge>
                        </div>
                        <p className="text-gray-600">{trait.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {analysis.analysis_type === "communication" && analysis.communication_patterns && (
                <div>
                  <h6 className="font-medium text-sm text-gray-700 mb-2">詳細なパターン</h6>
                  <div className="space-y-2">
                    {analysis.communication_patterns.map((pattern, index) => (
                      <div key={index} className="bg-blue-50 p-2 rounded text-xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">{pattern.pattern}</span>
                          <Badge variant="outline">頻度: {pattern.frequency}</Badge>
                        </div>
                        <div className="space-y-1">
                          <p><strong>強み:</strong> {pattern.strength}</p>
                          <p><strong>改善点:</strong> {pattern.improvement}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {analysis.analysis_type === "behavior" && analysis.behavior_scores && (
                <div>
                  <h6 className="font-medium text-sm text-gray-700 mb-2">詳細なスコア</h6>
                  <div className="space-y-2">
                    {analysis.behavior_scores.map((score, index) => (
                      <div key={index} className="bg-purple-50 p-2 rounded text-xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">{score.category}</span>
                          <div className="flex items-center space-x-1">
                            {getTrendIcon(score.trend)}
                            <span className={`font-medium ${getTrendColor(score.trend)}`}>
                              {score.score}/{score.max_score}
                            </span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                          <div 
                            className="bg-purple-600 h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${(score.score / score.max_score) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* アクションボタン */}
        {showActions && (
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                onClick={() => onViewDetails?.(analysis)}
                className="h-8 px-3 text-xs"
              >
                <Eye className="h-3 w-3 mr-1" />
                詳細
              </Button>
              <Button
                variant="outline"
                className="h-8 px-3 text-xs"
              >
                <ExternalLink className="h-3 w-3 mr-1" />
                共有
              </Button>
            </div>
            
            {onDelete && (
              <Button
                variant="outline"
                onClick={() => onDelete(analysis.id)}
                className="h-8 px-3 text-xs text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <Trash2 className="h-3 w-3 mr-1" />
                削除
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

