'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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

export default function PersonalGrowthPage() {
  const [improvementPlan, setImprovementPlan] = useState<ImprovementPlan | null>(null);
  const [growthGoals, setGrowthGoals] = useState<GrowthGoal[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // サンプルデータ（実際のAPIから取得）
  useEffect(() => {
    // シミュレーション用のデータ
    const mockData = {
      improvementPlan: {
        id: '1',
        title: 'コミュニケーションスキル向上計画',
        description: 'AI分析に基づく個別化された改善計画',
        current_skill_level: '中級',
        target_skill_level: '上級',
        overall_difficulty: 'intermediate',
        estimated_total_duration_days: 90,
        steps: [
          {
            id: '1',
            title: 'アクティブリスニングの練習',
            description: '相手の話を深く理解するための聞き方の練習',
            difficulty: 'beginner',
            estimated_duration_days: 14,
            priority: 'high',
            completed: false
          },
          {
            id: '2',
            title: 'フィードバックの受け入れ方',
            description: '建設的なフィードバックを効果的に受け入れる方法',
            difficulty: 'intermediate',
            estimated_duration_days: 21,
            priority: 'medium',
            completed: false
          },
          {
            id: '3',
            title: 'チーム内での意見表明',
            description: '会議やディスカッションで自分の意見を効果的に伝える',
            difficulty: 'advanced',
            estimated_duration_days: 30,
            priority: 'high',
            completed: false
          }
        ],
        progress_percentage: 25,
        status: 'active'
      },
      growthGoals: [
        {
          id: '1',
          title: 'プレゼンテーションスキルの向上',
          description: '3ヶ月以内に自信を持ってプレゼンできるようになる',
          category: 'コミュニケーション',
          target_date: '2025-11-14',
          status: 'in_progress',
          progress_percentage: 60,
          milestones: ['資料作成の基本', '話し方の練習', '実践練習']
        },
        {
          id: '2',
          title: 'リーダーシップの育成',
          description: 'チームをまとめるリーダーとしての能力を身につける',
          category: 'マネジメント',
          target_date: '2026-02-14',
          status: 'not_started',
          progress_percentage: 0,
          milestones: ['チームビルディング', '意思決定', 'メンタリング']
        }
      ]
    };

    setImprovementPlan(mockData.improvementPlan);
    setGrowthGoals(mockData.growthGoals);
    setIsLoading(false);
  }, []);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-blue-100 text-blue-800';
      case 'advanced': return 'bg-orange-100 text-orange-800';
      case 'expert': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'bg-gray-100 text-gray-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          個人成長支援
        </h1>
        <p className="text-gray-600">
          AI分析に基づく個別化された成長計画で、あなたのスキル向上をサポートします
        </p>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">概要</TabsTrigger>
          <TabsTrigger value="plan">改善計画</TabsTrigger>
          <TabsTrigger value="goals">成長目標</TabsTrigger>
          <TabsTrigger value="progress">進捗管理</TabsTrigger>
        </TabsList>

        {/* 概要タブ */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">現在のレベル</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{improvementPlan?.current_skill_level}</div>
                <p className="text-xs text-muted-foreground">
                  目標: {improvementPlan?.target_skill_level}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">全体進捗</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{improvementPlan?.progress_percentage}%</div>
                <Progress value={improvementPlan?.progress_percentage} className="mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">推定完了日</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {improvementPlan?.estimated_total_duration_days}日
                </div>
                <p className="text-xs text-muted-foreground">
                  残り約{Math.ceil((improvementPlan?.estimated_total_duration_days || 0) * (1 - (improvementPlan?.progress_percentage || 0) / 100))}日
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-yellow-500" />
                改善計画の概要
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-lg mb-2">{improvementPlan?.title}</h3>
                  <p className="text-gray-600">{improvementPlan?.description}</p>
                </div>
                <div className="flex items-center gap-4">
                  <Badge variant="outline" className={getDifficultyColor(improvementPlan?.overall_difficulty || '')}>
                    難易度: {improvementPlan?.overall_difficulty}
                  </Badge>
                  <Badge variant="outline">
                    ステップ数: {improvementPlan?.steps.length}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 改善計画タブ */}
        <TabsContent value="plan" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>改善ステップ一覧</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {improvementPlan?.steps.map((step, index) => (
                  <div key={step.id} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm font-medium text-blue-600">
                          {index + 1}
                        </div>
                        <div>
                          <h4 className="font-semibold">{step.title}</h4>
                          <p className="text-sm text-gray-600">{step.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {step.completed ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : (
                          <Clock className="h-5 w-5 text-gray-400" />
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-11">
                      <Badge className={getDifficultyColor(step.difficulty)}>
                        {step.difficulty}
                      </Badge>
                      <Badge className={getPriorityColor(step.priority)}>
                        {step.priority}
                      </Badge>
                      <Badge variant="outline" className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {step.estimated_duration_days}日
                      </Badge>
                    </div>
                    {step.completed && (
                      <div className="ml-11 text-sm text-green-600">
                        完了日: {step.completed_at}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 成長目標タブ */}
        <TabsContent value="goals" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">成長目標</h2>
            <Button>
              <Target className="h-4 w-4 mr-2" />
              新しい目標を設定
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {growthGoals.map((goal) => (
              <Card key={goal.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">{goal.title}</CardTitle>
                    <Badge className={getStatusColor(goal.status)}>
                      {goal.status === 'not_started' && '未開始'}
                      {goal.status === 'in_progress' && '進行中'}
                      {goal.status === 'completed' && '完了'}
                      {goal.status === 'on_hold' && '保留'}
                      {goal.status === 'cancelled' && 'キャンセル'}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">{goal.description}</p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span>進捗</span>
                      <span>{goal.progress_percentage}%</span>
                    </div>
                    <Progress value={goal.progress_percentage} />
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Calendar className="h-4 w-4" />
                    目標日: {goal.target_date}
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-sm mb-2">マイルストーン</h4>
                    <div className="space-y-1">
                      {goal.milestones.map((milestone, index) => (
                        <div key={index} className="flex items-center gap-2 text-sm">
                          <Star className="h-3 w-3 text-yellow-500" />
                          {milestone}
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 進捗管理タブ */}
        <TabsContent value="progress" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>進捗レポート</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold mb-3">週間進捗</h3>
                  <div className="grid grid-cols-7 gap-2">
                    {Array.from({ length: 7 }, (_, i) => (
                      <div key={i} className="text-center">
                        <div className="w-8 h-8 rounded bg-blue-100 flex items-center justify-center text-xs">
                          {Math.floor(Math.random() * 100)}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {['月', '火', '水', '木', '金', '土', '日'][i]}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-3">完了したタスク</h3>
                  <div className="space-y-2">
                    {improvementPlan?.steps.filter(step => step.completed).map(step => (
                      <div key={step.id} className="flex items-center gap-2 text-sm">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        {step.title}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
