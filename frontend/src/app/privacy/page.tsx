'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { 
  Shield, 
  Eye, 
  EyeOff, 
  Users, 
  UserCheck, 
  Lock, 
  Unlock,
  Calendar,
  Trash2,
  AlertTriangle,
  CheckCircle,
  Clock,
  Settings
} from 'lucide-react';

interface PrivacySettings {
  profile_visibility: 'public' | 'team' | 'private' | 'confidential';
  analysis_visibility: 'public' | 'team' | 'private' | 'confidential';
  goals_visibility: 'public' | 'team' | 'private' | 'confidential';
  progress_visibility: 'public' | 'team' | 'private' | 'confidential';
  communication_visibility: 'public' | 'team' | 'private' | 'confidential';
  allow_team_access: boolean;
  allow_manager_access: boolean;
  allow_hr_access: boolean;
  data_retention_days: number;
  auto_delete_enabled: boolean;
}

interface DataAccessPermission {
  id: string;
  granted_to_user: string;
  data_category: string;
  permission_level: 'read' | 'write' | 'delete' | 'admin';
  expires_at?: string;
  is_active: boolean;
}

export default function PrivacyPage() {
  const [privacySettings, setPrivacySettings] = useState<PrivacySettings>({
    profile_visibility: 'team',
    analysis_visibility: 'private',
    goals_visibility: 'private',
    progress_visibility: 'team',
    communication_visibility: 'team',
    allow_team_access: true,
    allow_manager_access: true,
    allow_hr_access: false,
    data_retention_days: 365,
    auto_delete_enabled: true
  });

  const [dataAccessPermissions, setDataAccessPermissions] = useState<DataAccessPermission[]>([
    {
      id: '1',
      granted_to_user: '田中 太郎',
      data_category: 'プロフィール',
      permission_level: 'read',
      expires_at: '2025-12-31',
      is_active: true
    },
    {
      id: '2',
      granted_to_user: '佐藤 花子',
      data_category: '進捗',
      permission_level: 'read',
      expires_at: '2025-11-30',
      is_active: true
    }
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  const handlePrivacySettingChange = (key: keyof PrivacySettings, value: any) => {
    setPrivacySettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveSettings = async () => {
    setSaveStatus('saving');
    try {
      // 実際のAPI呼び出しをシミュレート
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const getVisibilityIcon = (visibility: string) => {
    switch (visibility) {
      case 'public': return <Unlock className="h-4 w-4 text-green-500" />;
      case 'team': return <Users className="h-4 w-4 text-blue-500" />;
      case 'private': return <Lock className="h-4 w-4 text-orange-500" />;
      case 'confidential': return <Shield className="h-4 w-4 text-red-500" />;
      default: return <Eye className="h-4 w-4 text-gray-500" />;
    }
  };

  const getVisibilityLabel = (visibility: string) => {
    switch (visibility) {
      case 'public': return '公開';
      case 'team': return 'チーム内';
      case 'private': return '非公開';
      case 'confidential': return '機密';
      default: return visibility;
    }
  };

  const getPermissionLevelColor = (level: string) => {
    switch (level) {
      case 'read': return 'bg-blue-100 text-blue-800';
      case 'write': return 'bg-orange-100 text-orange-800';
      case 'delete': return 'bg-red-100 text-red-800';
      case 'admin': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPermissionLevelLabel = (level: string) => {
    switch (level) {
      case 'read': return '読み取り';
      case 'write': return '書き込み';
      case 'delete': return '削除';
      case 'admin': return '管理者';
      default: return level;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <Shield className="h-8 w-8 text-blue-600" />
          プライバシー設定
        </h1>
        <p className="text-gray-600">
          あなたのデータの可視性とアクセス権限を管理し、プライバシーを保護します
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* メイン設定エリア */}
        <div className="lg:col-span-2 space-y-6">
          {/* データ可視性設定 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-blue-500" />
                データ可視性設定
              </CardTitle>
              <p className="text-sm text-gray-600">
                各データカテゴリの可視性レベルを設定してください
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="profile-visibility">プロフィール</Label>
                  <Select
                    value={privacySettings.profile_visibility}
                    onValueChange={(value) => handlePrivacySettingChange('profile_visibility', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">公開</SelectItem>
                      <SelectItem value="team">チーム内</SelectItem>
                      <SelectItem value="private">非公開</SelectItem>
                      <SelectItem value="confidential">機密</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    {getVisibilityIcon(privacySettings.profile_visibility)}
                    {getVisibilityLabel(privacySettings.profile_visibility)}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="analysis-visibility">分析結果</Label>
                  <Select
                    value={privacySettings.analysis_visibility}
                    onValueChange={(value) => handlePrivacySettingChange('analysis_visibility', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">公開</SelectItem>
                      <SelectItem value="team">チーム内</SelectItem>
                      <SelectItem value="private">非公開</SelectItem>
                      <SelectItem value="confidential">機密</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    {getVisibilityIcon(privacySettings.analysis_visibility)}
                    {getVisibilityLabel(privacySettings.analysis_visibility)}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="goals-visibility">成長目標</Label>
                  <Select
                    value={privacySettings.goals_visibility}
                    onValueChange={(value) => handlePrivacySettingChange('goals_visibility', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">公開</SelectItem>
                      <SelectItem value="team">チーム内</SelectItem>
                      <SelectItem value="private">非公開</SelectItem>
                      <SelectItem value="confidential">機密</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    {getVisibilityIcon(privacySettings.goals_visibility)}
                    {getVisibilityLabel(privacySettings.goals_visibility)}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="progress-visibility">進捗状況</Label>
                  <Select
                    value={privacySettings.progress_visibility}
                    onValueChange={(value) => handlePrivacySettingChange('progress_visibility', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">公開</SelectItem>
                      <SelectItem value="team">チーム内</SelectItem>
                      <SelectItem value="private">非公開</SelectItem>
                      <SelectItem value="confidential">機密</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    {getVisibilityIcon(privacySettings.progress_visibility)}
                    {getVisibilityLabel(privacySettings.progress_visibility)}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* アクセス制御設定 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserCheck className="h-5 w-5 text-green-500" />
                アクセス制御設定
              </CardTitle>
              <p className="text-sm text-gray-600">
                特定のユーザーグループからのアクセスを制御します
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label>チームメンバーからのアクセス</Label>
                  <p className="text-sm text-gray-600">
                    チームメンバーがあなたのデータにアクセスできるようにする
                  </p>
                </div>
                <Switch
                  checked={privacySettings.allow_team_access}
                  onCheckedChange={(checked) => handlePrivacySettingChange('allow_team_access', checked)}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label>マネージャーからのアクセス</Label>
                  <p className="text-sm text-gray-600">
                    マネージャーがあなたのデータにアクセスできるようにする
                  </p>
                </div>
                <Switch
                  checked={privacySettings.allow_manager_access}
                  onCheckedChange={(checked) => handlePrivacySettingChange('allow_manager_access', checked)}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label>HRからのアクセス</Label>
                  <p className="text-sm text-gray-600">
                    HR部門があなたのデータにアクセスできるようにする
                  </p>
                </div>
                <Switch
                  checked={privacySettings.allow_hr_access}
                  onCheckedChange={(checked) => handlePrivacySettingChange('allow_hr_access', checked)}
                />
              </div>
            </CardContent>
          </Card>

          {/* データ保持ポリシー */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-purple-500" />
                データ保持ポリシー
              </CardTitle>
              <p className="text-sm text-gray-600">
                データの自動削除と保持期間を設定します
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label>自動削除を有効化</Label>
                  <p className="text-sm text-gray-600">
                    設定された期間後にデータを自動的に削除する
                  </p>
                </div>
                <Switch
                  checked={privacySettings.auto_delete_enabled}
                  onCheckedChange={(checked) => handlePrivacySettingChange('auto_delete_enabled', checked)}
                />
              </div>

              <Separator />

              <div className="space-y-2">
                <Label htmlFor="retention-days">データ保持期間（日数）</Label>
                <Input
                  id="retention-days"
                  type="number"
                  value={privacySettings.data_retention_days}
                  onChange={(e) => handlePrivacySettingChange('data_retention_days', parseInt(e.target.value))}
                  min="1"
                  max="3650"
                />
                <p className="text-sm text-gray-600">
                  データを保持する日数を設定してください（1日〜10年）
                </p>
              </div>
            </CardContent>
          </Card>

          {/* 保存ボタン */}
          <div className="flex justify-end">
            <Button 
              onClick={handleSaveSettings}
              disabled={saveStatus === 'saving'}
              className="min-w-[120px]"
            >
              {saveStatus === 'saving' && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />}
              {saveStatus === 'saved' && <CheckCircle className="h-4 w-4 mr-2" />}
              {saveStatus === 'error' && <AlertTriangle className="h-4 w-4 mr-2" />}
              {saveStatus === 'saving' ? '保存中...' : 
               saveStatus === 'saved' ? '保存完了' : 
               saveStatus === 'error' ? 'エラー' : '設定を保存'}
            </Button>
          </div>
        </div>

        {/* サイドバー */}
        <div className="space-y-6">
          {/* 現在の設定サマリー */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">設定サマリー</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">プロフィール</span>
                <Badge variant="outline" className={getVisibilityIcon(privacySettings.profile_visibility).props.className}>
                  {getVisibilityLabel(privacySettings.profile_visibility)}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">分析結果</span>
                <Badge variant="outline" className={getVisibilityIcon(privacySettings.analysis_visibility).props.className}>
                  {getVisibilityLabel(privacySettings.analysis_visibility)}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">成長目標</span>
                <Badge variant="outline" className={getVisibilityIcon(privacySettings.goals_visibility).props.className}>
                  {getVisibilityLabel(privacySettings.goals_visibility)}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">進捗状況</span>
                <Badge variant="outline" className={getVisibilityIcon(privacySettings.progress_visibility).props.className}>
                  {getVisibilityLabel(privacySettings.progress_visibility)}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* アクセス権限一覧 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">アクセス権限</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {dataAccessPermissions.map((permission) => (
                  <div key={permission.id} className="border rounded-lg p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">{permission.granted_to_user}</span>
                      <Badge className={getPermissionLevelColor(permission.permission_level)}>
                        {getPermissionLevelLabel(permission.permission_level)}
                      </Badge>
                    </div>
                    <div className="text-xs text-gray-600">
                      {permission.data_category} • 
                      {permission.expires_at ? ` 期限: ${permission.expires_at}` : ' 期限なし'}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="outline" className="h-6 text-xs">
                        編集
                      </Button>
                      <Button size="sm" variant="outline" className="h-6 text-xs text-red-600">
                        削除
                      </Button>
                    </div>
                  </div>
                ))}
                <Button variant="outline" className="w-full">
                  <UserCheck className="h-4 w-4 mr-2" />
                  権限を付与
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* プライバシー情報 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">プライバシー情報</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Shield className="h-4 w-4" />
                データは暗号化して保存されます
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Clock className="h-4 w-4" />
                最終更新: 2025-08-14
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Settings className="h-4 w-4" />
                設定は即座に反映されます
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
