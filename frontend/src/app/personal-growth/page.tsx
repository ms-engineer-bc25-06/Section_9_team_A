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
  Star,
  Brain,
  Settings,
  Plus,
  Download,
  Trash2,
  ArrowLeft
} from 'lucide-react';
import { Switch } from '@/components/ui/Switch';

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
            difficulty: 'beginner' as const,
            estimated_duration_days: 14,
            priority: 'high' as const,
            completed: false
          },
          {
            id: '2',
            title: 'フィードバックの受け入れ方',
            description: '建設的なフィードバックを効果的に受け入れる方法',
            difficulty: 'intermediate' as const,
            estimated_duration_days: 21,
            priority: 'medium' as const,
            completed: false
          },
          {
            id: '3',
            title: 'チーム内での意見表明',
            description: '会議やディスカッションで自分の意見を効果的に伝える',
            difficulty: 'advanced' as const,
            estimated_duration_days: 30,
            priority: 'high' as const,
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
          status: 'in_progress' as const,
          progress_percentage: 60,
          milestones: ['資料作成の基本', '話し方の練習', '実践練習']
        },
        {
          id: '2',
          title: 'リーダーシップの育成',
          description: 'チームをまとめるリーダーとしての能力を身につける',
          category: 'マネジメント',
          target_date: '2026-02-14',
          status: 'not_started' as const,
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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-br from-blue-50 to-indigo-50 shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                ダッシュボードへ戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900 absolute left-1/2 transform -translate-x-1/2">
              個人成長支援
            </h1>
            <div className="w-32">
              {/* 右側のスペースを確保して中央配置を維持 */}
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <p className="text-gray-600">
            AI分析に基づく個別化された成長計画で、あなたのスキル向上をサポートします
          </p>
        </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">概要</TabsTrigger>
          <TabsTrigger value="plan">改善計画</TabsTrigger>
          <TabsTrigger value="goals">成長目標</TabsTrigger>
          <TabsTrigger value="progress">進捗管理</TabsTrigger>
          <TabsTrigger value="ai-analysis">AI分析結果</TabsTrigger>
          <TabsTrigger value="settings">設定</TabsTrigger>
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

        {/* AI分析結果タブ */}
        <TabsContent value="ai-analysis" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-500" />
                AI分析結果
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* スキルレベル分析 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">現在のスキルレベル</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-blue-600 mb-2">
                          {improvementPlan?.current_skill_level}
                        </div>
                        <Progress value={25} className="h-3 mb-2" />
                        <p className="text-sm text-gray-600">レベル25%</p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">目標スキルレベル</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-green-600 mb-2">
                          {improvementPlan?.target_skill_level}
                        </div>
                        <Progress value={100} className="h-3 mb-2" />
                        <p className="text-sm text-gray-600">レベル100%</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* 改善提案 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">AI改善提案</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="p-4 bg-blue-50 rounded-lg">
                        <h4 className="font-semibold text-blue-800 mb-2">コミュニケーション能力の向上</h4>
                        <p className="text-blue-700 text-sm">
                          現在のレベル: 中級 → 目標レベル: 上級<br/>
                          推奨改善期間: 90日<br/>
                          重点改善項目: アクティブリスニング、フィードバック受容、意見表明
                        </p>
                      </div>
                      
                      <div className="p-4 bg-green-50 rounded-lg">
                        <h4 className="font-semibold text-green-800 mb-2">リーダーシップスキル</h4>
                        <p className="text-green-700 text-sm">
                          現在のレベル: 初級 → 目標レベル: 中級<br/>
                          推奨改善期間: 120日<br/>
                          重点改善項目: チームマネジメント、意思決定、メンタリング
                        </p>
                      </div>
                      
                      <div className="p-4 bg-purple-50 rounded-lg">
                        <h4 className="font-semibold text-purple-800 mb-2">問題解決能力</h4>
                        <p className="text-purple-700 text-sm">
                          現在のレベル: 中級 → 目標レベル: 上級<br/>
                          推奨改善期間: 60日<br/>
                          重点改善項目: 分析思考、創造的問題解決、意思決定
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* 詳細分析レポート */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">詳細分析レポート</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-2">強み</h4>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          <li>技術的な問題解決能力が高い</li>
                          <li>チームワークを重視する姿勢</li>
                          <li>継続的な学習意欲</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold mb-2">改善点</h4>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          <li>会議での発言機会の創出</li>
                          <li>フィードバックの効果的な活用</li>
                          <li>リーダーシップの実践機会</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold mb-2">推奨アクション</h4>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          <li>週1回のチームミーティングでの積極的な発言</li>
                          <li>月1回の1on1でのフィードバック収集</li>
                          <li>小規模プロジェクトでのリーダー役の経験</li>
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 設定タブ */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-gray-500" />
                設定・カスタマイズ
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* 基本設定 */}
                <div>
                  <h4 className="font-semibold text-lg mb-4">基本設定</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        目標スキルレベル
                      </label>
                      <select 
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={improvementPlan?.target_skill_level || ''}
                        onChange={(e) => setImprovementPlan(prev => prev ? { ...prev, target_skill_level: e.target.value } : null)}
                      >
                        <option value="初級">初級</option>
                        <option value="中級">中級</option>
                        <option value="上級">上級</option>
                        <option value="専門家">専門家</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        全体の難易度
                      </label>
                      <select 
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={improvementPlan?.overall_difficulty || ''}
                        onChange={(e) => setImprovementPlan(prev => prev ? { ...prev, overall_difficulty: e.target.value } : null)}
                      >
                        <option value="beginner">初心者</option>
                        <option value="intermediate">中級</option>
                        <option value="advanced">上級</option>
                        <option value="expert">専門家</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* 改善ステップの追加 */}
                <div>
                  <h4 className="font-semibold text-lg mb-4">改善ステップの追加</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        ステップタイトル
                      </label>
                      <input
                        type="text"
                        placeholder="例: アクティブリスニングの練習"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        説明
                      </label>
                      <textarea
                        placeholder="ステップの詳細な説明を入力してください"
                        rows={3}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          難易度
                        </label>
                        <select className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                          <option value="beginner">初心者</option>
                          <option value="intermediate">中級</option>
                          <option value="advanced">上級</option>
                          <option value="expert">専門家</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          優先度
                        </label>
                        <select className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                          <option value="low">低</option>
                          <option value="medium">中</option>
                          <option value="high">高</option>
                          <option value="critical">緊急</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          推定日数
                        </label>
                        <input
                          type="number"
                          placeholder="日数"
                          min="1"
                          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                    
                    <Button className="w-full bg-blue-600 hover:bg-blue-700">
                      <Plus className="h-4 w-4 mr-2" />
                      改善ステップを追加
                    </Button>
                  </div>
                </div>

                {/* 通知設定 */}
                <div>
                  <h4 className="font-semibold text-lg mb-4">通知設定</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">進捗リマインダー</p>
                        <p className="text-sm text-gray-600">週1回の進捗確認通知</p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">目標期限の通知</p>
                        <p className="text-sm text-gray-600">目標期限の1週間前に通知</p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">新しい改善提案</p>
                        <p className="text-sm text-gray-600">AIによる新しい改善提案の通知</p>
                      </div>
                      <Switch />
                    </div>
                  </div>
                </div>

                {/* データ管理 */}
                <div>
                  <h4 className="font-semibold text-lg mb-4">データ管理</h4>
                  <div className="space-y-3">
                    <Button variant="outline" className="w-full">
                      <Download className="h-4 w-4 mr-2" />
                      進捗データをエクスポート
                    </Button>
                    
                    <Button variant="outline" className="w-full text-red-600 hover:text-red-700 hover:bg-red-50">
                      <Trash2 className="h-4 w-4 mr-2" />
                      すべてのデータをリセット
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      </main>
    </div>
  );
}
