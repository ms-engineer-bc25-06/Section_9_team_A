'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Textarea } from '@/components/ui/Textarea';
import { Badge } from '@/components/ui/Badge';
import Spinner from '@/components/ui/Spinner';
import { 
  User, 
  MessageSquare, 
  Brain, 
  Briefcase,
  Save,
  Edit,
  X,
  ArrowLeft
} from 'lucide-react';

interface TeamMemberProfile {
  user_id: number;
  team_id: number;
  communication_style: string;
  personality_traits: Record<string, number>;
  work_preferences: Record<string, any>;
  interaction_patterns: Record<string, any>;
}

interface TeamMemberProfileFormProps {
  teamId: number;
  userId: number;
  onSave?: (profile: TeamMemberProfile) => void;
  onCancel?: () => void;
}

const COMMUNICATION_STYLES = [
  { value: 'assertive', label: 'アサーティブ', description: '直接的で明確なコミュニケーション' },
  { value: 'collaborative', label: '協調的', description: '協力的で建設的なコミュニケーション' },
  { value: 'analytical', label: '分析的', description: '論理的で詳細を重視' },
  { value: 'supportive', label: '支持的', description: '聞き手に寄り添うコミュニケーション' }
];

const PERSONALITY_TRAITS = [
  { key: 'extroversion', label: '外向性', description: '社交的で活動的' },
  { key: 'introversion', label: '内向性', description: '内省的で控えめ' },
  { key: 'openness', label: '開放性', description: '新しい経験に開放的' },
  { key: 'conscientiousness', label: '誠実性', description: '責任感が強く几帳面' },
  { key: 'agreeableness', label: '協調性', description: '親切で協力的' },
  { key: 'emotional_stability', label: '情緒安定性', description: '感情的に安定している' }
];

const WORK_PREFERENCES = [
  { key: 'work_environment', label: '作業環境', type: 'select', options: ['オフィス', 'リモート', 'ハイブリッド'] },
  { key: 'work_schedule', label: '作業スケジュール', type: 'select', options: ['朝型', '夜型', 'フレックス'] },
  { key: 'team_size', label: 'チームサイズ', type: 'select', options: ['小規模(2-4人)', '中規模(5-8人)', '大規模(9人以上)'] },
  { key: 'decision_making', label: '意思決定スタイル', type: 'select', options: ['個人判断', 'チーム合意', 'リーダー決定'] },
  { key: 'feedback_frequency', label: 'フィードバック頻度', type: 'select', options: ['毎日', '週1回', '月1回', '必要時のみ'] }
];

export default function TeamMemberProfileForm({ 
  teamId, 
  userId, 
  onSave, 
  onCancel 
}: TeamMemberProfileFormProps) {
  const [profile, setProfile] = useState<TeamMemberProfile>({
    user_id: userId,
    team_id: teamId,
    communication_style: 'collaborative',
    personality_traits: {},
    work_preferences: {},
    interaction_patterns: {}
  });
  
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [existingProfile, setExistingProfile] = useState<TeamMemberProfile | null>(null);

  useEffect(() => {
    fetchExistingProfile();
  }, [teamId, userId]);

  const fetchExistingProfile = async () => {
    try {
      const response = await fetch(`/api/teams/${teamId}/members/${userId}/profile`);
      if (response.ok) {
        const data = await response.json();
        setExistingProfile(data);
        setProfile(data);
      }
    } catch (error) {
      console.error('プロファイルの取得に失敗:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const method = existingProfile ? 'PUT' : 'POST';
      const response = await fetch(`/api/teams/${teamId}/members/${userId}/profile`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile)
      });
      
      if (response.ok) {
        setEditing(false);
        if (onSave) {
          onSave(profile);
        }
        await fetchExistingProfile();
      }
    } catch (error) {
      console.error('プロファイルの保存に失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const updatePersonalityTrait = (trait: string, value: number) => {
    setProfile(prev => ({
      ...prev,
      personality_traits: {
        ...prev.personality_traits,
        [trait]: value
      }
    }));
  };

  const updateWorkPreference = (key: string, value: any) => {
    setProfile(prev => ({
      ...prev,
      work_preferences: {
        ...prev.work_preferences,
        [key]: value
      }
    }));
  };

  const resetToExisting = () => {
    if (existingProfile) {
      setProfile(existingProfile);
    }
    setEditing(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Spinner className="w-8 h-8" />
        <span className="ml-2">保存中...</span>
      </div>
    );
  }

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

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <User className="w-5 h-5 mr-2" />
              チームメンバープロファイル
            </CardTitle>
            <div className="flex space-x-2">
              {!editing && existingProfile && (
                <Button onClick={() => setEditing(true)} variant="outline">
                  <Edit className="w-4 h-4 mr-2" />
                  編集
                </Button>
              )}
              {editing && (
                <>
                  <Button onClick={handleSave} disabled={loading}>
                    <Save className="w-4 h-4 mr-2" />
                    保存
                  </Button>
                  <Button onClick={resetToExisting} variant="outline">
                    <X className="w-4 h-4 mr-2" />
                    キャンセル
                  </Button>
                </>
              )}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* コミュニケーションスタイル */}
          <div className="space-y-3">
            <Label className="flex items-center">
              <MessageSquare className="w-4 h-4 mr-2" />
              コミュニケーションスタイル
            </Label>
            <select
              value={profile.communication_style}
              onChange={(e) => setProfile(prev => ({ ...prev, communication_style: e.target.value }))}
              disabled={!editing}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              {COMMUNICATION_STYLES.map((style) => (
                <option key={style.value} value={style.value}>
                  {style.label} - {style.description}
                </option>
              ))}
            </select>
          </div>

          {/* 性格特性 */}
          <div className="space-y-3">
            <Label className="flex items-center">
              <Brain className="w-4 h-4 mr-2" />
              性格特性
            </Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {PERSONALITY_TRAITS.map((trait) => (
                <div key={trait.key} className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">{trait.label}</span>
                    <span className="text-xs text-gray-500">
                      {profile.personality_traits[trait.key] || 0}/10
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    value={profile.personality_traits[trait.key] || 0}
                    onChange={(e) => updatePersonalityTrait(trait.key, parseInt(e.target.value))}
                    disabled={!editing}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <p className="text-xs text-gray-500">{trait.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 仕事の好み */}
          <div className="space-y-3">
            <Label className="flex items-center">
              <Briefcase className="w-4 h-4 mr-2" />
              仕事の好み
            </Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {WORK_PREFERENCES.map((pref) => (
                <div key={pref.key} className="space-y-2">
                  <Label className="text-sm font-medium">{pref.label}</Label>
                  <select
                    value={profile.work_preferences[pref.key] || ''}
                    onChange={(e) => updateWorkPreference(pref.key, e.target.value)}
                    disabled={!editing}
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">選択してください</option>
                    {pref.options.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* 現在のプロファイル表示 */}
          {existingProfile && !editing && (
            <div className="space-y-4 pt-4 border-t">
              <h4 className="font-medium text-gray-900">現在のプロファイル</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-700">コミュニケーションスタイル</Label>
                  <Badge variant="outline" className="mt-1">
                    {COMMUNICATION_STYLES.find(s => s.value === existingProfile.communication_style)?.label}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-700">主要な性格特性</Label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {Object.entries(existingProfile.personality_traits)
                      .filter(([_, value]) => value >= 7)
                      .slice(0, 3)
                      .map(([key, value]) => (
                        <Badge key={key} variant="secondary" className="text-xs">
                          {PERSONALITY_TRAITS.find(t => t.key === key)?.label}: {value}/10
                        </Badge>
                      ))}
                  </div>
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-700">仕事の好み</Label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-1">
                  {Object.entries(existingProfile.work_preferences).map(([key, value]) => (
                    <div key={key} className="text-sm">
                      <span className="text-gray-600">{WORK_PREFERENCES.find(p => p.key === key)?.label}:</span>
                      <span className="ml-1 font-medium">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* アクションボタン */}
          {!existingProfile && (
            <div className="flex justify-end space-x-2 pt-4">
              <Button onClick={handleSave} disabled={loading}>
                <Save className="w-4 h-4 mr-2" />
                プロファイル作成
              </Button>
              {onCancel && (
                <Button onClick={onCancel} variant="outline">
                  キャンセル
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
