'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import Link from 'next/link';
import { 
  Brain, 
  User, 
  Target, 
  TrendingUp, 
  Lightbulb, 
  Heart,
  MessageSquare,
  Users,
  Zap,
  BarChart3,
  Star,
  AlertTriangle
} from 'lucide-react';

interface PersonalityAnalysis {
  personality_type: string;
  description: string;
  strengths: string[];
  weaknesses: string[];
  communication_style: string;
  team_role_preference: string;
}

interface SkillAnalysis {
  technical_skills: {
    name: string;
    level: number;
    category: string;
  }[];
  soft_skills: {
    name: string;
    level: number;
    category: string;
  }[];
  overall_score: number;
}

interface BehavioralAnalysis {
  leadership_style: string;
  problem_solving_approach: string;
  stress_tolerance: number;
  motivation_factors: string[];
  work_style: string;
}

interface AIAnalysisResult {
  personality: PersonalityAnalysis;
  skills: SkillAnalysis;
  behavior: BehavioralAnalysis;
  last_updated: string;
  confidence_score: number;
}

export function AIAnalysisEmbed() {
  const [analysisResult, setAnalysisResult] = useState<AIAnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 実際のAPIからデータを取得
  useEffect(() => {
    const fetchAnalysisData = async () => {
      try {
        setIsLoading(true);
        // TODO: 実際のAPIエンドポイントに置き換える
        // const response = await apiGet<AIAnalysisResult>('/analyses/ai-analysis');
        // setAnalysisResult(response);
        
        // 一時的に空のデータを設定
        setAnalysisResult(null);
      } catch (error) {
        console.error('AI分析データの取得に失敗:', error);
        setAnalysisResult(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalysisData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const getSkillLevelColor = (level: number) => {
    if (level >= 80) return 'text-green-600';
    if (level >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSkillLevelBadge = (level: number) => {
    if (level >= 80) return 'bg-green-100 text-green-800';
    if (level >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6">
      {/* AI分析結果の概要 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="h-5 w-5 text-purple-500" />
            <span>AI分析結果サマリー</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <Brain className="h-8 w-8 mx-auto mb-2 text-purple-600" />
              <p className="text-sm text-gray-600">分析信頼度</p>
              <p className="text-2xl font-bold text-purple-600">{analysisResult?.confidence_score}%</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <Target className="h-8 w-8 mx-auto mb-2 text-blue-600" />
              <p className="text-sm text-gray-600">総合スキルスコア</p>
              <p className="text-2xl font-bold text-blue-600">{analysisResult?.skills.overall_score}</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <TrendingUp className="h-8 w-8 mx-auto mb-2 text-green-600" />
              <p className="text-sm text-gray-600">最終更新</p>
              <p className="text-lg font-bold text-green-600">{analysisResult?.last_updated}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* パーソナリティ分析 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <User className="h-5 w-5 text-blue-500" />
            <span>パーソナリティ分析</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2">{analysisResult?.personality.personality_type}</h3>
              <p className="text-gray-600 mb-4">{analysisResult?.personality.description}</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-green-700 mb-3 flex items-center">
                  <Star className="h-4 w-4 mr-2" />
                  強み
                </h4>
                <ul className="space-y-2">
                  {analysisResult?.personality.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="font-semibold text-orange-700 mb-3 flex items-center">
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  改善点
                </h4>
                <ul className="space-y-2">
                  {analysisResult?.personality.weaknesses.map((weakness, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm text-gray-700">{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">コミュニケーションスタイル</h4>
                <Badge variant="outline">{analysisResult?.personality.communication_style}</Badge>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">チーム内での役割</h4>
                <Badge variant="outline">{analysisResult?.personality.team_role_preference}</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* スキル分析 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Target className="h-5 w-5 text-green-500" />
            <span>スキル分析</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* 技術スキル */}
            <div>
              <h4 className="font-semibold text-lg mb-4 flex items-center">
                <Zap className="h-4 w-4 mr-2" />
                技術スキル
              </h4>
              <div className="space-y-3">
                {analysisResult?.skills.technical_skills.map((skill, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Badge className={getSkillLevelBadge(skill.level)}>
                        {skill.category}
                      </Badge>
                      <span className="font-medium">{skill.name}</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Progress value={skill.level} className="w-20 h-2" />
                      <span className={`font-bold ${getSkillLevelColor(skill.level)}`}>
                        {skill.level}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ソフトスキル */}
            <div>
              <h4 className="font-semibold text-lg mb-4 flex items-center">
                <Heart className="h-4 w-4 mr-2" />
                ソフトスキル
              </h4>
              <div className="space-y-3">
                {analysisResult?.skills.soft_skills.map((skill, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Badge className={getSkillLevelBadge(skill.level)}>
                        {skill.category}
                      </Badge>
                      <span className="font-medium">{skill.name}</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Progress value={skill.level} className="w-20 h-2" />
                      <span className={`font-bold ${getSkillLevelColor(skill.level)}`}>
                        {skill.level}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 行動パターン分析 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5 text-indigo-500" />
            <span>行動パターン分析</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-3">リーダーシップスタイル</h4>
              <Badge variant="outline" className="text-lg px-3 py-1">
                {analysisResult?.behavior.leadership_style}
              </Badge>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3">問題解決アプローチ</h4>
              <Badge variant="outline" className="text-lg px-3 py-1">
                {analysisResult?.behavior.problem_solving_approach}
              </Badge>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3">ストレス耐性</h4>
              <div className="space-y-2">
                <Progress value={analysisResult?.behavior.stress_tolerance || 0} className="h-3" />
                <p className="text-sm text-gray-600">{analysisResult?.behavior.stress_tolerance}%</p>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3">ワークスタイル</h4>
              <Badge variant="outline" className="text-lg px-3 py-1">
                {analysisResult?.behavior.work_style}
              </Badge>
            </div>
          </div>
          
          <div className="mt-6">
            <h4 className="font-semibold mb-3">モチベーション要因</h4>
            <div className="flex flex-wrap gap-2">
              {analysisResult?.behavior.motivation_factors.map((factor, index) => (
                <Badge key={index} variant="secondary" className="px-3 py-1">
                  {factor}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 詳細分析ページへのリンク */}
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <BarChart3 className="h-12 w-12 text-blue-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">より詳細なAI分析結果</h3>
            <p className="text-gray-600 mb-4">
              包括的なAI分析レポート、詳細なスキル分析、成長提案を確認できます。
            </p>
            <Link href="/analytics">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <BarChart3 className="h-4 w-4 mr-2" />
                詳細分析ページで確認
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
