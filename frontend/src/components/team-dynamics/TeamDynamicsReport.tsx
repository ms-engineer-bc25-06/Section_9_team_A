'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  Download, 
  Share2, 
  TrendingUp, 
  TrendingDown,
  Users,
  MessageSquare,
  Target,
  BarChart3,
  PieChart,
  Activity,
  Lightbulb,
  AlertTriangle,
  CheckCircle,
  ArrowLeft
} from 'lucide-react';

interface TeamDynamicsReportProps {
  teamId: number;
  sessionId?: number;
  reportData: {
    interactions: any;
    compatibility: any;
    cohesion: any;
    recommendations: string[];
    trends: {
      improvement: boolean;
      areas: string[];
    };
  };
}

export default function TeamDynamicsReport({ 
  teamId, 
  sessionId, 
  reportData 
}: TeamDynamicsReportProps) {
  const [activeSection, setActiveSection] = useState<'summary' | 'details' | 'recommendations'>('summary');

  const generateReport = () => {
    // レポート生成ロジック（実際の実装ではPDF生成など）
    console.log('レポート生成中...');
  };

  const shareReport = () => {
    // レポート共有ロジック
    console.log('レポート共有中...');
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 0.8) return <CheckCircle className="w-5 h-5 text-green-600" />;
    if (score >= 0.6) return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
    return <AlertTriangle className="w-5 h-5 text-red-600" />;
  };

  return (
    <div className="space-y-6">
      {/* ダッシュボードに戻るリンク */}
      <div className="flex justify-start">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            ダッシュボードへ戻る
          </Button>
        </Link>
      </div>

      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">チームダイナミクス分析レポート</h1>
          <p className="text-gray-600">チームID: {teamId} | セッションID: {sessionId || 'N/A'}</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={generateReport} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            レポート出力
          </Button>
          <Button onClick={shareReport} variant="outline">
            <Share2 className="w-4 h-4 mr-2" />
            共有
          </Button>
        </div>
      </div>

      {/* ナビゲーション */}
      <div className="flex space-x-1 border-b">
        <button
          onClick={() => setActiveSection('summary')}
          className={`px-4 py-2 rounded-t-lg ${
            activeSection === 'summary'
              ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-700'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          サマリー
        </button>
        <button
          onClick={() => setActiveSection('details')}
          className={`px-4 py-2 rounded-t-lg ${
            activeSection === 'details'
              ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-700'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          詳細分析
        </button>
        <button
          onClick={() => setActiveSection('recommendations')}
          className={`px-4 py-2 rounded-t-lg ${
            activeSection === 'recommendations'
              ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-700'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          改善提案
        </button>
      </div>

      {/* サマリーセクション */}
      {activeSection === 'summary' && (
        <div className="space-y-6">
          {/* 主要メトリクス */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">相互作用スコア</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  {getScoreIcon(reportData.interactions.communication_efficiency)}
                  <div className={`text-2xl font-bold ${getScoreColor(reportData.interactions.communication_efficiency)}`}>
                    {(reportData.interactions.communication_efficiency * 100).toFixed(1)}%
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  総相互作用: {reportData.interactions.total_interactions}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">チーム相性スコア</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  {getScoreIcon(reportData.compatibility.average_compatibility)}
                  <div className={`text-2xl font-bold ${getScoreColor(reportData.compatibility.average_compatibility)}`}>
                    {(reportData.compatibility.average_compatibility * 100).toFixed(1)}%
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  メンバー数: {reportData.compatibility.total_members}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">チーム結束力スコア</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  {getScoreIcon(reportData.cohesion.cohesion_score)}
                  <div className={`text-2xl font-bold ${getScoreColor(reportData.cohesion.cohesion_score)}`}>
                    {(reportData.cohesion.cohesion_score * 100).toFixed(1)}%
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  共通トピック: {reportData.cohesion.common_topics.length}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* トレンド分析 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                トレンド分析
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2 mb-4">
                {reportData.trends.improvement ? (
                  <TrendingUp className="w-5 h-5 text-green-600" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-red-600" />
                )}
                <span className={`font-medium ${
                  reportData.trends.improvement ? 'text-green-600' : 'text-red-600'
                }`}>
                  {reportData.trends.improvement ? '改善傾向' : '改善が必要'}
                </span>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900">改善エリア:</h4>
                <div className="flex flex-wrap gap-2">
                  {reportData.trends.areas.map((area, index) => (
                    <Badge key={index} variant="outline" className="text-sm">
                      {area}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* クイックアクション */}
          <Card>
            <CardHeader>
              <CardTitle>クイックアクション</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button variant="outline" className="justify-start">
                  <Users className="w-4 h-4 mr-2" />
                  チームビルディング活動を計画
                </Button>
                <Button variant="outline" className="justify-start">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  コミュニケーション改善ワークショップ
                </Button>
                <Button variant="outline" className="justify-start">
                  <Target className="w-4 h-4 mr-2" />
                  目標設定セッション
                </Button>
                <Button variant="outline" className="justify-start">
                  <Activity className="w-4 h-4 mr-2" />
                  定期的な振り返りセッション
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 詳細分析セクション */}
      {activeSection === 'details' && (
        <div className="space-y-6">
          {/* 相互作用パターン詳細 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MessageSquare className="w-5 h-5 mr-2" />
                相互作用パターン詳細
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">相互作用タイプ分布</h4>
                  <div className="space-y-2">
                    {Object.entries(reportData.interactions.interaction_types_distribution).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between">
                        <span className="text-sm capitalize">{type}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${((count as number) / reportData.interactions.total_interactions) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">{count as number}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">沈黙メンバー分析</h4>
                  <div className="space-y-2">
                    {reportData.interactions.silent_members.map((member: any, index: number) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm">ユーザー {member.user_id}</span>
                        <Badge variant="secondary" className="text-xs">
                          {member.type === 'passive_listener' ? '受動的' : '完全沈黙'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 相性分析詳細 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="w-5 h-5 mr-2" />
                相性分析詳細
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">相性マトリックス</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse text-sm">
                      <thead>
                        <tr>
                          <th className="border p-2 bg-gray-50">メンバー</th>
                          {Object.keys(reportData.compatibility.compatibility_matrix).map((memberId) => (
                            <th key={memberId} className="border p-2 bg-gray-50">
                              {memberId}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(reportData.compatibility.compatibility_matrix).map(([memberId, compatibilities]) => (
                          <tr key={memberId}>
                            <td className="border p-2 bg-gray-50 font-medium">{memberId}</td>
                            {Object.entries(compatibilities as Record<string, number>).map(([otherId, score]) => (
                              <td key={otherId} className={`border p-2 text-center ${
                                memberId === otherId ? 'bg-gray-100' : ''
                              }`}>
                                {memberId === otherId ? '-' : `${((score as number) * 100).toFixed(0)}%`}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 結束力分析詳細 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="w-5 h-5 mr-2" />
                結束力分析詳細
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">詳細メトリクス</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">意見の一致度</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{ width: `${reportData.cohesion.opinion_alignment * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">
                          {(reportData.cohesion.opinion_alignment * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">文化的形成度</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${reportData.cohesion.cultural_formation * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">
                          {(reportData.cohesion.cultural_formation * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">共通トピック</h4>
                  <div className="flex flex-wrap gap-2">
                    {reportData.cohesion.common_topics.map((topic: string, index: number) => (
                      <Badge key={index} variant="outline" className="text-sm">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 改善提案セクション */}
      {activeSection === 'recommendations' && (
        <div className="space-y-6">
          {/* 主要な改善提案 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Lightbulb className="w-5 h-5 mr-2" />
                主要な改善提案
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {reportData.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                    <Lightbulb className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <p className="text-blue-800">{recommendation}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* アクションプラン */}
          <Card>
            <CardHeader>
              <CardTitle>アクションプラン</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">短期（1-2週間）</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• チームミーティングの改善</li>
                      <li>• コミュニケーションルールの確認</li>
                      <li>• フィードバックセッションの実施</li>
                    </ul>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">中期（1-2ヶ月）</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• チームビルディング活動</li>
                      <li>• スキル開発ワークショップ</li>
                      <li>• プロセス改善の実施</li>
                    </ul>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">長期（3-6ヶ月）</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• チーム文化の確立</li>
                      <li>• 継続的改善システム</li>
                      <li>• パフォーマンス評価の見直し</li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 成功指標 */}
          <Card>
            <CardHeader>
              <CardTitle>成功指標（KPI）</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">定量的指標</h4>
                  <ul className="space-y-2 text-sm">
                    <li>• 相互作用数: +20%</li>
                    <li>• コミュニケーション効率: +15%</li>
                    <li>• チーム相性スコア: +10%</li>
                    <li>• 結束力スコア: +15%</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">定性的指標</h4>
                  <ul className="space-y-2 text-sm">
                    <li>• チームメンバーの満足度向上</li>
                    <li>• コミュニケーションの質の改善</li>
                    <li>• チームワークの向上</li>
                    <li>• 問題解決能力の向上</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
