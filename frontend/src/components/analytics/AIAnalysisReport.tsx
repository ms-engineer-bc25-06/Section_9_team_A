"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Separator } from "@/components/ui/Separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs"
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
  Heart,
  Download,
  Share2,
  RefreshCw
} from "lucide-react"
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from "recharts"
import { AnalysisResponse } from "@/lib/api/analytics"

interface AIAnalysisReportProps {
  analysis: AnalysisResponse
  onRefresh?: () => void
  onExport?: () => void
  onShare?: () => void
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

export function AIAnalysisReport({ 
  analysis, 
  onRefresh, 
  onExport, 
  onShare 
}: AIAnalysisReportProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({})
  const [activeTab, setActiveTab] = useState("overview")

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

  // 感情分析の時系列データ（サンプル）
  const sentimentTimelineData = [
    { time: "開始", score: 0.3 },
    { time: "5分", score: 0.6 },
    { time: "10分", score: 0.8 },
    { time: "15分", score: 0.7 },
    { time: "20分", score: 0.9 },
    { time: "終了", score: 0.8 }
  ]

  // 個性特性のレーダーチャートデータ
  const personalityRadarData = analysis.personality_traits?.map(trait => ({
    subject: trait.trait,
    A: trait.score,
    fullMark: 10
  })) || []

  // コミュニケーションパターンの棒グラフデータ
  const communicationBarData = analysis.communication_patterns?.map(pattern => ({
    name: pattern.pattern,
    frequency: pattern.frequency,
    effectiveness: pattern.frequency * 10 // 仮の効果性スコア
  })) || []

  // 行動特性の円グラフデータ
  const behaviorPieData = analysis.behavior_scores?.map(score => ({
    name: score.category,
    value: score.score
  })) || []

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
                <CardTitle className="text-2xl">{analysis.title}</CardTitle>
                <div className="flex items-center space-x-2 mt-1">
                  <Badge variant="outline">{analysis.analysis_type}</Badge>
                  <Badge variant="secondary">
                    {new Date(analysis.created_at).toLocaleDateString('ja-JP')}
                  </Badge>
                  <Badge 
                    variant={analysis.status === 'completed' ? 'default' : 'secondary'}
                  >
                    {analysis.status === 'completed' ? '完了' : '処理中'}
                  </Badge>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {onRefresh && (
                <Button variant="outline" size="sm" onClick={onRefresh}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  更新
                </Button>
              )}
              {onExport && (
                <Button variant="outline" size="sm" onClick={onExport}>
                  <Download className="h-4 w-4 mr-2" />
                  エクスポート
                </Button>
              )}
              {onShare && (
                <Button variant="outline" size="sm" onClick={onShare}>
                  <Share2 className="h-4 w-4 mr-2" />
                  共有
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 text-lg">{analysis.summary}</p>
          
          {/* キーワードとトピック */}
          <div className="flex flex-wrap gap-2 mt-4">
            {analysis.keywords?.map((keyword, index) => (
              <Badge key={index} variant="secondary">
                {keyword}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* タブ付き詳細表示 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">概要</TabsTrigger>
          <TabsTrigger value="personality">個性分析</TabsTrigger>
          <TabsTrigger value="communication">コミュニケーション</TabsTrigger>
          <TabsTrigger value="behavior">行動特性</TabsTrigger>
          <TabsTrigger value="insights">インサイト</TabsTrigger>
        </TabsList>

        {/* 概要タブ */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* 基本統計 */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5 text-blue-500" />
                  <span>基本統計</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">単語数</span>
                  <span className="font-semibold">{analysis.word_count || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">文数</span>
                  <span className="font-semibold">{analysis.sentence_count || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">信頼度</span>
                  <span className="font-semibold">
                    {((analysis.confidence_score || 0) * 100).toFixed(1)}%
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* 感情分析 */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center space-x-2">
                  <Heart className="h-5 w-5 text-red-500" />
                  <span>感情分析</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-center">
                  <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(analysis.sentiment_score || 0)}`}>
                    {getSentimentLabel(analysis.sentiment_score || 0)}
                  </div>
                </div>
                <div className="text-center">
                  <span className="text-2xl font-bold">
                    {((analysis.sentiment_score || 0) * 100).toFixed(0)}
                  </span>
                  <span className="text-gray-500 text-sm">/100</span>
                </div>
              </CardContent>
            </Card>

            {/* 処理時間 */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center space-x-2">
                  <Activity className="h-5 w-5 text-green-500" />
                  <span>処理情報</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">処理時間</span>
                  <span className="font-semibold">2.3秒</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">モデル</span>
                  <span className="font-semibold">GPT-4</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 感情の時系列変化 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-green-500" />
                <span>感情の時系列変化</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={sentimentTimelineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis domain={[-1, 1]} />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#8884d8" 
                    strokeWidth={3}
                    dot={{ fill: '#8884d8', strokeWidth: 2, r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 個性分析タブ */}
        <TabsContent value="personality" className="space-y-6">
          {analysis.personality_traits && analysis.personality_traits.length > 0 ? (
            <>
              {/* レーダーチャート */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Star className="h-5 w-5 text-yellow-500" />
                    <span>個性特性レーダーチャート</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <RadarChart data={personalityRadarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="subject" />
                      <PolarRadiusAxis domain={[0, 10]} />
                      <Radar 
                        name="個性特性" 
                        dataKey="A" 
                        stroke="#8884d8" 
                        fill="#8884d8" 
                        fillOpacity={0.6} 
                      />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* 詳細リスト */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Star className="h-5 w-5 text-yellow-500" />
                    <span>個性特性詳細</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {analysis.personality_traits.map((trait, index) => (
                      <div key={index} className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-yellow-800">{trait.trait}</span>
                          <Badge variant="outline" className="bg-yellow-100">
                            {trait.score}/10
                          </Badge>
                        </div>
                        <p className="text-sm text-yellow-700">{trait.description}</p>
                        <div className="w-full bg-yellow-200 rounded-full h-2 mt-2">
                          <div 
                            className="bg-yellow-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${(trait.score / 10) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-8 text-gray-500">
                <Star className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>個性分析データがありません</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* コミュニケーションタブ */}
        <TabsContent value="communication" className="space-y-6">
          {analysis.communication_patterns && analysis.communication_patterns.length > 0 ? (
            <>
              {/* 棒グラフ */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <MessageSquare className="h-5 w-5 text-blue-500" />
                    <span>コミュニケーションパターン</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={communicationBarData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="frequency" fill="#8884d8" name="頻度" />
                      <Bar dataKey="effectiveness" fill="#82ca9d" name="効果性" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* 詳細リスト */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <MessageSquare className="h-5 w-5 text-blue-500" />
                    <span>パターン詳細</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {analysis.communication_patterns.map((pattern, index) => (
                      <div key={index} className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <div className="flex items-center justify-between mb-3">
                          <span className="font-medium text-blue-800">{pattern.pattern}</span>
                          <Badge variant="outline" className="bg-blue-100">
                            頻度: {pattern.frequency}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-medium text-blue-700 mb-1">強み</p>
                            <p className="text-sm text-blue-600">{pattern.strength}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-blue-700 mb-1">改善点</p>
                            <p className="text-sm text-blue-600">{pattern.improvement}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-8 text-gray-500">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>コミュニケーション分析データがありません</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 行動特性タブ */}
        <TabsContent value="behavior" className="space-y-6">
          {analysis.behavior_scores && analysis.behavior_scores.length > 0 ? (
            <>
              {/* 円グラフ */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Activity className="h-5 w-5 text-purple-500" />
                    <span>行動特性分布</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                      <Pie
                        data={behaviorPieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {behaviorPieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* 詳細リスト */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Activity className="h-5 w-5 text-purple-500" />
                    <span>スコア詳細</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {analysis.behavior_scores.map((score, index) => (
                      <div key={index} className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                        <div className="flex items-center justify-between mb-3">
                          <span className="font-medium text-purple-800">{score.category}</span>
                          <div className="flex items-center space-x-2">
                            {score.trend === 'up' && <TrendingUp className="h-4 w-4 text-green-500" />}
                            {score.trend === 'down' && <TrendingUp className="h-4 w-4 text-red-500 rotate-180" />}
                            {score.trend === 'stable' && <BarChart3 className="h-4 w-4 text-gray-500" />}
                            <span className="text-sm font-medium text-purple-700">
                              {score.score}/{score.max_score}
                            </span>
                          </div>
                        </div>
                        <div className="w-full bg-purple-200 rounded-full h-2 mb-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${(score.score / score.max_score) * 100}%` }}
                          ></div>
                        </div>
                        <p className="text-xs text-purple-600">
                          傾向: {score.trend === 'up' ? '向上' : score.trend === 'down' ? '低下' : '安定'}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-8 text-gray-500">
                <Activity className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>行動特性分析データがありません</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* インサイトタブ */}
        <TabsContent value="insights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Lightbulb className="h-5 w-5 text-yellow-500" />
                <span>AIインサイト</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* 成長ポイント */}
                <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg border border-green-200">
                  <h4 className="font-semibold text-green-800 mb-3 flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5" />
                    <span>成長ポイント</span>
                  </h4>
                  <ul className="space-y-2 text-green-700">
                    <li className="flex items-start space-x-2">
                      <span className="text-green-500 mt-1">•</span>
                      <span>コミュニケーション能力が前回比+15%向上</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-green-500 mt-1">•</span>
                      <span>チーム貢献度が継続的に向上</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-green-500 mt-1">•</span>
                      <span>新しいアイデアの提案頻度が増加</span>
                    </li>
                  </ul>
                </div>

                {/* 改善提案 */}
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border border-blue-200">
                  <h4 className="font-semibold text-blue-800 mb-3 flex items-center space-x-2">
                    <Target className="h-5 w-5" />
                    <span>改善提案</span>
                  </h4>
                  <ul className="space-y-2 text-blue-700">
                    <li className="flex items-start space-x-2">
                      <span className="text-blue-500 mt-1">•</span>
                      <span>感情表現の多様化を意識する</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-blue-500 mt-1">•</span>
                      <span>チームメンバーへの積極的なサポート</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-blue-500 mt-1">•</span>
                      <span>新しい視点からの問題解決アプローチ</span>
                    </li>
                  </ul>
                </div>

                {/* 今後の目標 */}
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-lg border border-purple-200">
                  <h4 className="font-semibold text-purple-800 mb-3 flex items-center space-x-2">
                    <Star className="h-5 w-5" />
                    <span>今後の目標</span>
                  </h4>
                  <ul className="space-y-2 text-purple-700">
                    <li className="flex items-start space-x-2">
                      <span className="text-purple-500 mt-1">•</span>
                      <span>リーダーシップスキルの向上</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-purple-500 mt-1">•</span>
                      <span>クロスファンクショナルな協力の促進</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <span className="text-purple-500 mt-1">•</span>
                      <span>イノベーション思考の強化</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
