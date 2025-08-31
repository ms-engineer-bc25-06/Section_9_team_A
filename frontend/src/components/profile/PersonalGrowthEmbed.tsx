'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import Link from 'next/link';
import { 
  Target, 
  TrendingUp, 
  Lightbulb, 
  Calendar,
  CheckCircle,
  Clock,
  Star
} from 'lucide-react';

interface ImprovementStep {
  id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  estimated_duration_days: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  completed: boolean;
  completed_at?: string;
}

interface ImprovementPlan {
  id: string;
  title: string;
  description: string;
  current_skill_level: string;
  target_skill_level: string;
  overall_difficulty: string;
  estimated_total_duration_days: number;
  steps: ImprovementStep[];
  progress_percentage: number;
  status: string;
}

interface GrowthGoal {
  id: string;
  title: string;
  description: string;
  category: string;
  target_date: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'on_hold' | 'cancelled';
  progress_percentage: number;
  milestones: string[];
}

export function PersonalGrowthEmbed() {
  const [improvementPlan, setImprovementPlan] = useState<ImprovementPlan | null>(null);
  const [growthGoals, setGrowthGoals] = useState<GrowthGoal[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // 実際のAPIからデータを取得
  useEffect(() => {
    const fetchGrowthData = async () => {
      try {
        setIsLoading(true);
        // TODO: 実際のAPIエンドポイントに置き換える
        // const response = await apiGet<{improvementPlan: ImprovementPlan, growthGoals: GrowthGoal[]}>('/personal-growth');
        // setImprovementPlan(response.improvementPlan);
        // setGrowthGoals(response.growthGoals);
        
        // 一時的に空のデータを設定
        setImprovementPlan(null);
        setGrowthGoals([]);
      } catch (error) {
        console.error('個人成長データの取得に失敗:', error);
        setImprovementPlan(null);
        setGrowthGoals([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchGrowthData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-orange-100 text-orange-800';
      case 'expert': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'bg-gray-100 text-gray-800';
      case 'medium': return 'bg-blue-100 text-blue-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'not_started': return 'bg-gray-100 text-gray-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'on_hold': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* 改善計画サマリー */}
      {improvementPlan && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-blue-500" />
              <span>現在の改善計画</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">{improvementPlan.title}</h3>
                <p className="text-gray-600 mb-3">{improvementPlan.description}</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm text-gray-600">現在レベル</p>
                    <p className="text-lg font-bold text-blue-600">{improvementPlan.current_skill_level}</p>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <p className="text-sm text-gray-600">目標レベル</p>
                    <p className="text-lg font-bold text-green-600">{improvementPlan.target_skill_level}</p>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <p className="text-sm text-gray-600">難易度</p>
                    <p className="text-lg font-bold text-purple-600">{improvementPlan.overall_difficulty}</p>
                  </div>
                  <div className="text-center p-3 bg-orange-50 rounded-lg">
                    <p className="text-sm text-gray-600">推定期間</p>
                    <p className="text-lg font-bold text-orange-600">{improvementPlan.estimated_total_duration_days}日</p>
                  </div>
                </div>
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>進捗</span>
                    <span>{improvementPlan.progress_percentage}%</span>
                  </div>
                  <Progress value={improvementPlan.progress_percentage} className="h-2" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 成長目標 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Star className="h-5 w-5 text-yellow-500" />
            <span>成長目標</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {growthGoals.map((goal) => (
              <div key={goal.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-1">{goal.title}</h3>
                    <p className="text-gray-600 text-sm mb-2">{goal.description}</p>
                    <div className="flex items-center space-x-4 text-sm">
                      <span className="text-gray-500">カテゴリ: {goal.category}</span>
                      <span className="text-gray-500">目標日: {goal.target_date}</span>
                    </div>
                  </div>
                  <Badge className={getStatusColor(goal.status)}>
                    {goal.status === 'not_started' && '未開始'}
                    {goal.status === 'in_progress' && '進行中'}
                    {goal.status === 'completed' && '完了'}
                    {goal.status === 'on_hold' && '保留'}
                    {goal.status === 'cancelled' && 'キャンセル'}
                  </Badge>
                </div>
                <div className="mb-3">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>進捗</span>
                    <span>{goal.progress_percentage}%</span>
                  </div>
                  <Progress value={goal.progress_percentage} className="h-2" />
                </div>
                <div className="text-sm">
                  <p className="font-medium text-gray-700 mb-2">マイルストーン:</p>
                  <ul className="space-y-1">
                    {goal.milestones.map((milestone, index) => (
                      <li key={index} className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-gray-600">{milestone}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 詳細ページへのリンク */}
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <Lightbulb className="h-12 w-12 text-blue-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">より詳細な分析と計画</h3>
            <p className="text-gray-600 mb-4">
              個人成長支援システムの詳細ページで、より包括的な分析結果と改善計画を確認できます。
            </p>
            <Link href="/personal-growth">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <TrendingUp className="h-4 w-4 mr-2" />
                詳細ページで確認
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
