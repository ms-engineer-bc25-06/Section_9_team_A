"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs"
import { 
  Brain, 
  BarChart3, 
  TrendingUp, 
  Users, 
  Activity,
  Plus,
  Download,
  Share2,
  Settings
} from "lucide-react"
import { AnalysisHistory } from "@/components/analytics/AnalysisHistory"
import { AIAnalysisReport } from "@/components/analytics/AIAnalysisReport"
import { useAIAnalysis } from "@/hooks/useAIAnalysis"
import { useRealtimeAnalysis } from "@/hooks/useRealtimeAnalysis"
import { AnalysisResponse } from "@/lib/api/analytics"

export default function AnalyticsPage() {
  const { analyses, isLoading, error, createAnalysis } = useAIAnalysis()
  const { isConnected, connectionStatus } = useRealtimeAnalysis()
  
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResponse | null>(null)
  const [activeTab, setActiveTab] = useState("overview")
  const [showCreateForm, setShowCreateForm] = useState(false)

  // 統計データの計算
  const stats = {
    totalAnalyses: analyses.length,
    completedAnalyses: analyses.filter(a => a.status === 'completed').length,
    processingAnalyses: analyses.filter(a => a.status === 'processing').length,
    failedAnalyses: analyses.filter(a => a.status === 'failed').length,
    averageConfidence: analyses.length > 0 
      ? analyses.reduce((sum, a) => sum + (a.confidence_score || 0), 0) / analyses.length 
      : 0,
    averageSentiment: analyses.length > 0 
      ? analyses.reduce((sum, a) => sum + (a.sentiment_score || 0), 0) / analyses.length 
      : 0
  }

  // 分析タイプ別の統計
  const typeStats = {
    personality: analyses.filter(a => a.analysis_type === 'personality').length,
    communication: analyses.filter(a => a.analysis_type === 'communication').length,
    behavior: analyses.filter(a => a.analysis_type === 'behavior').length,
    sentiment: analyses.filter(a => a.analysis_type === 'sentiment').length,
    topic: analyses.filter(a => a.analysis_type === 'topic').length,
    summary: analyses.filter(a => a.analysis_type === 'summary').length
  }

  // 分析結果を選択
  const handleSelectAnalysis = (analysis: AnalysisResponse) => {
    setSelectedAnalysis(analysis)
    setActiveTab("report")
  }

  // 履歴をエクスポート
  const handleExportHistory = () => {
    // CSVエクスポートの実装
    const csvContent = generateCSV(analyses)
    downloadCSV(csvContent, 'ai_analysis_history.csv')
  }

  // 分析履歴を削除
  const handleDeleteAnalysis = async (analysisId: string) => {
    // 削除処理はuseAIAnalysisフックで処理される
    if (selectedAnalysis?.id === analysisId) {
      setSelectedAnalysis(null)
      setActiveTab("overview")
    }
  }

  // CSV生成
  const generateCSV = (data: AnalysisResponse[]) => {
    const headers = ['ID', 'タイトル', '分析タイプ', 'ステータス', '信頼度', '感情スコア', '作成日時', '要約']
    const rows = data.map(analysis => [
      analysis.id,
      analysis.title,
      analysis.analysis_type,
      analysis.status,
      analysis.confidence_score,
      analysis.sentiment_score,
      analysis.created_at,
      analysis.summary
    ])
    
    return [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n')
  }

  // CSVダウンロード
  const downloadCSV = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // 新しい分析を作成
  const handleCreateAnalysis = async (text: string, analysisTypes: string[]) => {
    try {
      await createAnalysis(text, analysisTypes)
      setShowCreateForm(false)
    } catch (error) {
      console.error('分析の作成に失敗:', error)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-8">
        {/* ページヘッダー */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI分析ダッシュボード</h1>
            <p className="text-gray-600 mt-2">
              コミュニケーション分析結果の詳細な洞察と成長の可視化
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              onClick={() => setShowCreateForm(true)}
            >
              <Plus className="h-4 w-4 mr-2" />
              新規分析
            </Button>
            <Button
              variant="outline"
              onClick={handleExportHistory}
            >
              <Download className="h-4 w-4 mr-2" />
              エクスポート
            </Button>
            <Button variant="outline">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* 接続状態表示 */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-gray-400'
                }`}></div>
                <span className="text-sm text-gray-600">
                  {isConnected ? 'リアルタイム接続中' : 'オフライン'}
                </span>
              </div>
              <div className="text-sm text-gray-500">
                最終更新: {new Date().toLocaleTimeString('ja-JP')}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 統計サマリー */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center space-x-2">
                <Brain className="h-5 w-5 text-blue-500" />
                <span>総分析数</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">{stats.totalAnalyses}</div>
              <p className="text-sm text-gray-600 mt-1">累計分析結果</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-green-500" />
                <span>完了率</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {stats.totalAnalyses > 0 
                  ? Math.round((stats.completedAnalyses / stats.totalAnalyses) * 100)
                  : 0}%
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {stats.completedAnalyses}/{stats.totalAnalyses}件完了
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-purple-500" />
                <span>平均信頼度</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">
                {(stats.averageConfidence * 100).toFixed(1)}%
              </div>
              <p className="text-sm text-gray-600 mt-1">分析精度の指標</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center space-x-2">
                <Activity className="h-5 w-5 text-orange-500" />
                <span>感情傾向</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600">
                {stats.averageSentiment > 0.3 ? 'ポジティブ' : 
                 stats.averageSentiment < -0.3 ? 'ネガティブ' : 'ニュートラル'}
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {(stats.averageSentiment * 100).toFixed(0)}/100
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 分析タイプ別統計 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>分析タイプ別統計</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(typeStats).map(([type, count]) => (
                <div key={type} className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-700">{count}</div>
                  <div className="text-sm text-gray-600 capitalize">{type}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* メインコンテンツ */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">概要</TabsTrigger>
            <TabsTrigger value="history">分析履歴</TabsTrigger>
            <TabsTrigger value="report" disabled={!selectedAnalysis}>
              詳細レポート
            </TabsTrigger>
          </TabsList>

          {/* 概要タブ */}
          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-blue-500" />
                  <span>最近の分析結果</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {analyses.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Brain className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>まだ分析結果がありません</p>
                    <p className="text-sm">音声チャットに参加して分析を開始してください</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {analyses.slice(0, 5).map(analysis => (
                      <div 
                        key={analysis.id}
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                        onClick={() => handleSelectAnalysis(analysis)}
                      >
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-blue-100 rounded-lg">
                            <Brain className="h-4 w-4 text-blue-600" />
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900">{analysis.title}</h4>
                            <p className="text-sm text-gray-600">{analysis.summary}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">
                            {new Date(analysis.created_at).toLocaleDateString('ja-JP')}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            analysis.status === 'completed' 
                              ? 'bg-green-100 text-green-800' 
                              : analysis.status === 'processing'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {analysis.status === 'completed' ? '完了' : 
                             analysis.status === 'processing' ? '処理中' : '失敗'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 成長の可視化 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-green-500" />
                  <span>成長の可視化</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="text-center p-6 bg-green-50 rounded-lg border border-green-200">
                    <TrendingUp className="h-12 w-12 mx-auto mb-4 text-green-600" />
                    <h4 className="text-lg font-semibold text-green-800 mb-2">コミュニケーション能力</h4>
                    <p className="text-3xl font-bold text-green-600">+15%</p>
                    <p className="text-sm text-green-700 mt-1">過去30日間の向上</p>
                  </div>
                  <div className="text-center p-6 bg-blue-50 rounded-lg border border-blue-200">
                    <Users className="h-12 w-12 mx-auto mb-4 text-blue-600" />
                    <h4 className="text-lg font-semibold text-blue-800 mb-2">チーム貢献度</h4>
                    <p className="text-3xl font-bold text-blue-600">+8%</p>
                    <p className="text-sm text-blue-700 mt-1">過去30日間の向上</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 分析履歴タブ */}
          <TabsContent value="history" className="space-y-6">
            <AnalysisHistory
              onSelectAnalysis={handleSelectAnalysis}
              onExportHistory={handleExportHistory}
              onDeleteAnalysis={handleDeleteAnalysis}
            />
          </TabsContent>

          {/* 詳細レポートタブ */}
          <TabsContent value="report" className="space-y-6">
            {selectedAnalysis ? (
              <AIAnalysisReport
                analysis={selectedAnalysis}
                onRefresh={() => {
                  // 分析結果を再取得
                }}
                onExport={() => {
                  // 個別レポートのエクスポート
                  const csvContent = generateCSV([selectedAnalysis])
                  downloadCSV(csvContent, `analysis_${selectedAnalysis.id}.csv`)
                }}
                onShare={() => {
                  // 共有機能の実装
                  console.log('共有機能:', selectedAnalysis.id)
                }}
              />
            ) : (
              <Card>
                <CardContent className="text-center py-8 text-gray-500">
                  <Brain className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>分析結果が選択されていません</p>
                  <p className="text-sm">分析履歴から詳細を表示したい分析結果を選択してください</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}