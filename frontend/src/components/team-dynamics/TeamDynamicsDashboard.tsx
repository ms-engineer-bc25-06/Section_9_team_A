'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import Spinner from '@/components/ui/Spinner';
import { 
  Users, 
  MessageSquare, 
  TrendingUp, 
  Target,
  Activity,
  BarChart3,
  PieChart,
  Lightbulb
} from 'lucide-react';

interface TeamDynamicsData {
  team_id: number;
  session_id: number;
  total_interactions: number;
  interaction_matrix: Record<number, Record<number, any>>;
  silent_members: Array<{
    user_id: number;
    listening_count: number;
    type: string;
  }>;
  communication_efficiency: number;
  interaction_types_distribution: Record<string, number>;
  cohesion_score: number;
  common_topics: string[];
  opinion_alignment: number;
  cultural_formation: number;
  improvement_suggestions: string;
  average_compatibility: number;
  compatibility_matrix: Record<number, Record<number, number>>;
}

interface TeamDynamicsDashboardProps {
  teamId: number;
  sessionId?: number;
}

export default function TeamDynamicsDashboard({ 
  teamId, 
  sessionId 
}: TeamDynamicsDashboardProps) {
  const [dynamicsData, setDynamicsData] = useState<TeamDynamicsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'interactions' | 'compatibility' | 'cohesion'>('interactions');

  useEffect(() => {
    if (teamId) {
      fetchTeamDynamics();
    }
  }, [teamId, sessionId]);

  const fetchTeamDynamics = async () => {
    setLoading(true);
    try {
      // 実際のAPIエンドポイントに置き換える
      const response = await fetch(`/api/teams/${teamId}/dynamics/summary`);
      if (response.ok) {
        const data = await response.json();
        setDynamicsData(data);
      }
    } catch (error) {
      console.error('チームダイナミクスデータの取得に失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeInteractions = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/teams/${teamId}/interactions/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      if (response.ok) {
        await fetchTeamDynamics();
      }
    } catch (error) {
      console.error('相互作用分析の実行に失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateCompatibility = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/teams/${teamId}/compatibility/calculate`, {
        method: 'POST'
      });
      if (response.ok) {
        await fetchTeamDynamics();
      }
    } catch (error) {
      console.error('相性計算の実行に失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeCohesion = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/teams/${teamId}/cohesion/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      if (response.ok) {
        await fetchTeamDynamics();
      }
    } catch (error) {
      console.error('結束力分析の実行に失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const getEfficiencyColor = (efficiency: number) => {
    if (efficiency >= 0.8) return 'text-green-600';
    if (efficiency >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Spinner className="w-8 h-8" />
        <span className="ml-2">分析中...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">チームダイナミクス分析</h1>
          <p className="text-gray-600">チームの相互作用、相性、結束力を分析します</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={analyzeInteractions} disabled={loading}>
            <Activity className="w-4 h-4 mr-2" />
            相互作用分析
          </Button>
          <Button onClick={calculateCompatibility} disabled={loading}>
            <Users className="w-4 h-4 mr-2" />
            相性計算
          </Button>
          <Button onClick={analyzeCohesion} disabled={loading}>
            <Target className="w-4 h-4 mr-2" />
            結束力分析
          </Button>
        </div>
      </div>

      {/* タブナビゲーション */}
      <div className="flex space-x-1 border-b">
        <button
          onClick={() => setActiveTab('interactions')}
          className={`px-4 py-2 rounded-t-lg ${
            activeTab === 'interactions'
              ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-700'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          <MessageSquare className="w-4 h-4 inline mr-2" />
          相互作用パターン
        </button>
        <button
          onClick={() => setActiveTab('compatibility')}
          className={`px-4 py-2 rounded-t-lg ${
            activeTab === 'compatibility'
              ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-700'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          <Users className="w-4 h-4 inline mr-2" />
          チーム相性
        </button>
        <button
          onClick={() => setActiveTab('cohesion')}
          className={`px-4 py-2 rounded-t-lg ${
            activeTab === 'cohesion'
              ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-700'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          <Target className="w-4 h-4 inline mr-2" />
          チーム結束力
        </button>
      </div>

      {/* 相互作用パターンタブ */}
      {activeTab === 'interactions' && dynamicsData && (
        <div className="space-y-6">
          {/* 概要カード */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">総相互作用数</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dynamicsData.total_interactions}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">コミュニケーション効率</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getEfficiencyColor(dynamicsData.communication_efficiency)}`}>
                  {(dynamicsData.communication_efficiency * 100).toFixed(1)}%
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">沈黙メンバー数</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dynamicsData.silent_members.length}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">相互作用タイプ</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{Object.keys(dynamicsData.interaction_types_distribution).length}</div>
              </CardContent>
            </Card>
          </div>

          {/* 相互作用タイプ分布 */}
          <Card>
            <CardHeader>
              <CardTitle>相互作用タイプ分布</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(dynamicsData.interaction_types_distribution).map(([type, count]) => (
                  <div key={type} className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{count}</div>
                    <div className="text-sm text-gray-600 capitalize">{type}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 沈黙メンバー詳細 */}
          {dynamicsData.silent_members.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>沈黙メンバー詳細</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {dynamicsData.silent_members.map((member) => (
                    <div key={member.user_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <span className="font-medium">ユーザーID: {member.user_id}</span>
                        <Badge variant="secondary" className="ml-2">
                          {member.type === 'passive_listener' ? '受動的リスナー' : '完全沈黙'}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600">
                        受信回数: {member.listening_count}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* チーム相性タブ */}
      {activeTab === 'compatibility' && dynamicsData && (
        <div className="space-y-6">
          {/* 相性スコア概要 */}
          <Card>
            <CardHeader>
              <CardTitle>チーム相性スコア</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <div className={`text-4xl font-bold ${getScoreColor(dynamicsData.average_compatibility)}`}>
                  {(dynamicsData.average_compatibility * 100).toFixed(1)}%
                </div>
                <p className="text-gray-600 mt-2">平均相性スコア</p>
              </div>
            </CardContent>
          </Card>

          {/* 相性マトリックス */}
          <Card>
            <CardHeader>
              <CardTitle>相性マトリックス</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr>
                      <th className="border p-2 bg-gray-50">メンバー</th>
                      {Object.keys(dynamicsData.compatibility_matrix).map((memberId) => (
                        <th key={memberId} className="border p-2 bg-gray-50">
                          {memberId}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(dynamicsData.compatibility_matrix).map(([memberId, compatibilities]) => (
                      <tr key={memberId}>
                        <td className="border p-2 bg-gray-50 font-medium">{memberId}</td>
                        {Object.entries(compatibilities).map(([otherId, score]) => (
                          <td key={otherId} className={`border p-2 text-center ${
                            memberId === otherId ? 'bg-gray-100' : ''
                          }`}>
                            {memberId === otherId ? '-' : `${(score * 100).toFixed(0)}%`}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* チーム結束力タブ */}
      {activeTab === 'cohesion' && dynamicsData && (
        <div className="space-y-6">
          {/* 結束力スコア */}
          <Card>
            <CardHeader>
              <CardTitle>チーム結束力スコア</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <div className={`text-4xl font-bold ${getScoreColor(dynamicsData.cohesion_score)}`}>
                  {(dynamicsData.cohesion_score * 100).toFixed(1)}%
                </div>
                <p className="text-gray-600 mt-2">結束力スコア</p>
              </div>
            </CardContent>
          </Card>

          {/* 詳細メトリクス */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">意見の一致度</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getScoreColor(dynamicsData.opinion_alignment)}`}>
                  {(dynamicsData.opinion_alignment * 100).toFixed(1)}%
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">文化的形成度</CardTitle>
                <PieChart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getScoreColor(dynamicsData.cultural_formation)}`}>
                  {(dynamicsData.cultural_formation * 100).toFixed(1)}%
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">共通トピック数</CardTitle>
                <Lightbulb className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {dynamicsData.common_topics.length}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 共通トピック */}
          {dynamicsData.common_topics.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>共通トピック</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {dynamicsData.common_topics.map((topic, index) => (
                    <Badge key={index} variant="outline" className="text-sm">
                      {topic}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* 改善提案 */}
          <Card>
            <CardHeader>
              <CardTitle>改善提案</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-blue-800">{dynamicsData.improvement_suggestions}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* データがない場合 */}
      {!dynamicsData && !loading && (
        <Card>
          <CardContent className="text-center py-8">
            <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">データがありません</h3>
            <p className="text-gray-600 mb-4">
              チームダイナミクス分析を実行してデータを取得してください
            </p>
            <div className="flex space-x-2 justify-center">
              <Button onClick={analyzeInteractions}>
                <Activity className="w-4 h-4 mr-2" />
                相互作用分析
              </Button>
              <Button onClick={calculateCompatibility}>
                <Users className="w-4 h-4 mr-2" />
                相性計算
              </Button>
              <Button onClick={analyzeCohesion}>
                <Target className="w-4 h-4 mr-2" />
                結束力分析
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
