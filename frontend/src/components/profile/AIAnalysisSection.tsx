"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Separator } from "@/components/ui/Separator"
import { 
  Brain, 
  MessageSquare, 
  TrendingUp, 
  Target, 
  Star, 
  Activity,
  ChevronDown,
  ChevronUp,
  BarChart3,
  Lightbulb,
  Users,
  Heart
} from "lucide-react"
import { AnalysisResponse } from "@/lib/api/analytics"

interface AIAnalysisSectionProps {
  analyses: AnalysisResponse[]
  isLoading?: boolean
}

export function AIAnalysisSection({ analyses, isLoading = false }: AIAnalysisSectionProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({})
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResponse | null>(null)

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }))
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

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>AI分析結果</span>
          </CardTitle>
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

  if (!analyses || analyses.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>AI分析結果</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <Brain className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>まだAI分析が実行されていません</p>
            <p className="text-sm">音声チャットに参加して分析を開始してください</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // 最新の分析結果を取得
  const latestAnalysis = analyses[0]
  const personalityAnalysis = analyses.find(a => a.analysis_type === "personality")
  const communicationAnalysis = analyses.find(a => a.analysis_type === "communication")
  const behaviorAnalysis = analyses.find(a => a.analysis_type === "behavior")

  return (
    <div className="space-y-6">
      {/* 分析概要 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>AI分析結果</span>
            <Badge variant="secondary" className="ml-2">
              {analyses.length}件の分析
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <Brain className="h-8 w-8 mx-auto mb-2 text-blue-600" />
              <p className="text-sm text-gray-600">個性分析</p>
              <p className="text-2xl font-bold text-blue-600">
                {personalityAnalysis ? "完了" : "未実行"}
              </p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <MessageSquare className="h-8 w-8 mx-auto mb-2 text-green-600" />
              <p className="text-sm text-gray-600">コミュニケーション</p>
              <p className="text-2xl font-bold text-green-600">
                {communicationAnalysis ? "完了" : "未実行"}
              </p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <Activity className="h-8 w-8 mx-auto mb-2 text-purple-600" />
              <p className="text-sm text-gray-600">行動特性</p>
              <p className="text-2xl font-bold text-purple-600">
                {behaviorAnalysis ? "完了" : "未実行"}
              </p>
            </div>
          </div>

          {latestAnalysis && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">最新の分析: {latestAnalysis.title}</h4>
                <Badge variant="outline">
                  {new Date(latestAnalysis.created_at).toLocaleDateString('ja-JP')}
                </Badge>
              </div>
              <p className="text-sm text-gray-600">{latestAnalysis.summary}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 個性分析 */}
      {personalityAnalysis && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <Star className="h-5 w-5 text-yellow-500" />
                <span>個性分析</span>
              </CardTitle>
                             <Button
                 variant="ghost"
                 onClick={() => toggleSection('personality')}
               >
                {expandedSections['personality'] ? <ChevronUp /> : <ChevronDown />}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-gray-600">{personalityAnalysis.summary}</p>
              
              {expandedSections['personality'] && personalityAnalysis.personality_traits && (
                <div className="space-y-3">
                  <Separator />
                  <h5 className="font-medium">性格特性</h5>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {personalityAnalysis.personality_traits.map((trait, index) => (
                      <div key={index} className="bg-gray-50 p-3 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{trait.trait}</span>
                          <Badge variant="outline">{trait.score}/10</Badge>
                        </div>
                        <p className="text-sm text-gray-600">{trait.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* コミュニケーションパターン */}
      {communicationAnalysis && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <MessageSquare className="h-5 w-5 text-blue-500" />
                <span>コミュニケーションパターン</span>
              </CardTitle>
                             <Button
                 variant="ghost"
                 onClick={() => toggleSection('communication')}
               >
                {expandedSections['communication'] ? <ChevronUp /> : <ChevronDown />}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-gray-600">{communicationAnalysis.summary}</p>
              
              {expandedSections['communication'] && communicationAnalysis.communication_patterns && (
                <div className="space-y-3">
                  <Separator />
                  <h5 className="font-medium">パターン詳細</h5>
                  <div className="space-y-3">
                    {communicationAnalysis.communication_patterns.map((pattern, index) => (
                      <div key={index} className="bg-blue-50 p-3 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{pattern.pattern}</span>
                          <Badge variant="outline">頻度: {pattern.frequency}</Badge>
                        </div>
                        <div className="space-y-2">
                          <p className="text-sm"><strong>強み:</strong> {pattern.strength}</p>
                          <p className="text-sm"><strong>改善点:</strong> {pattern.improvement}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 行動特性スコア */}
      {behaviorAnalysis && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-purple-500" />
                <span>行動特性スコア</span>
              </CardTitle>
                             <Button
                 variant="ghost"
                 onClick={() => toggleSection('behavior')}
               >
                {expandedSections['behavior'] ? <ChevronUp /> : <ChevronDown />}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-gray-600">{behaviorAnalysis.summary}</p>
              
              {expandedSections['behavior'] && behaviorAnalysis.behavior_scores && (
                <div className="space-y-3">
                  <Separator />
                  <h5 className="font-medium">スコア詳細</h5>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {behaviorAnalysis.behavior_scores.map((score, index) => (
                      <div key={index} className="bg-purple-50 p-3 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{score.category}</span>
                          <div className="flex items-center space-x-2">
                            {getTrendIcon(score.trend)}
                            <span className={`text-sm font-medium ${getTrendColor(score.trend)}`}>
                              {score.score}/{score.max_score}
                            </span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${(score.score / score.max_score) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 成長・変化の可視化 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-green-500" />
            <span>成長・変化の可視化</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <TrendingUp className="h-8 w-8 mx-auto mb-2 text-green-600" />
                <p className="text-sm text-gray-600">コミュニケーション能力</p>
                <p className="text-2xl font-bold text-green-600">+15%</p>
                <p className="text-xs text-gray-500">過去30日間</p>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Users className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                <p className="text-sm text-gray-600">チーム貢献度</p>
                <p className="text-2xl font-bold text-blue-600">+8%</p>
                <p className="text-xs text-gray-500">過去30日間</p>
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg">
              <h5 className="font-medium mb-2 flex items-center space-x-2">
                <Lightbulb className="h-4 w-4 text-yellow-500" />
                <span>今月の成長ポイント</span>
              </h5>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 積極的な発言が増加（前月比+20%）</li>
                <li>• チームメンバーへのサポート頻度向上</li>
                <li>• 新しいアイデアの提案が増加</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
