"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Switch } from '@/components/ui/Switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Separator } from '@/components/ui/Separator'
import { 
  Eye, 
  Users, 
  Globe, 
  Lock, 
  Shield,
  Calendar,
  Clock,
  CheckCircle,
  AlertTriangle,
  Settings,
  BarChart3,
  TrendingUp,
  MessageSquare,
  Target,
  Heart,
  Save,
  RefreshCw,
  Info
} from 'lucide-react'
import { useAnalysisPrivacy, VISIBILITY_PRESETS, STAGED_PUBLICATION_PRESETS } from '@/hooks/useAnalysisPrivacy'
import type { VisibilityLevel } from '@/lib/api/analysisPrivacy'

// フックから型を取得
type AnalysisPrivacySettings = NonNullable<ReturnType<typeof useAnalysisPrivacy>['settings']>
type StagedPublicationSettings = NonNullable<ReturnType<typeof useAnalysisPrivacy>['stagedPublication']>

export function PersonalAnalysisPrivacyManager() {
  const {
    settings,
    stagedPublication,
    analyses,
    loading,
    error,
    updateSettings,
    advancePublication,
    cancelPublication,
    clearError
  } = useAnalysisPrivacy()

  // 型安全な初期値の設定
  const [localSettings, setLocalSettings] = useState(settings)
  const [localStagedPublication, setLocalStagedPublication] = useState(stagedPublication)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')

  // ローカル状態を同期
  useEffect(() => {
    if (settings) setLocalSettings(settings)
  }, [settings])

  useEffect(() => {
    if (stagedPublication) setLocalStagedPublication(stagedPublication)
  }, [stagedPublication])

  const handlePrivacySettingChange = (key: keyof NonNullable<typeof localSettings>, value: VisibilityLevel) => {
    if (!localSettings) return
    
    setLocalSettings(prev => prev ? ({
      ...prev,
      [key]: value
    }) : null)
  }

  const handleStagedPublicationChange = (key: keyof NonNullable<typeof localStagedPublication>, value: any) => {
    if (!localStagedPublication) return
    
    setLocalStagedPublication(prev => prev ? ({
      ...prev,
      [key]: value
    }) : null)
  }

  const handleStageChange = (stage: keyof NonNullable<typeof localStagedPublication>['stages'], value: boolean) => {
    if (!localStagedPublication) return
    
    setLocalStagedPublication(prev => prev ? ({
      ...prev,
      stages: {
        ...prev.stages,
        [stage]: value
      }
    }) : null)
  }

  const handleDelayChange = (delay: keyof NonNullable<typeof localStagedPublication>['delay_days'], value: number) => {
    if (!localStagedPublication) return
    
    setLocalStagedPublication(prev => prev ? ({
      ...prev,
      delay_days: {
        ...prev.delay_days,
        [delay]: value
      }
    }) : null)
  }

  const handlePresetApply = (preset: keyof typeof VISIBILITY_PRESETS) => {
    const presetSettings = VISIBILITY_PRESETS[preset]
    setLocalSettings(presetSettings)
  }

  const handleStagedPresetApply = (preset: keyof typeof STAGED_PUBLICATION_PRESETS) => {
    const presetSettings = STAGED_PUBLICATION_PRESETS[preset]
    setLocalStagedPublication(presetSettings)
  }

  const handleSaveSettings = async () => {
    if (!localSettings || !localStagedPublication) return
    
    setSaveStatus('saving')
    try {
      await updateSettings({
        settings: localSettings,
        staged_publication: localStagedPublication
      })
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } catch (error) {
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 3000)
    }
  }

  const handleAdvancePublication = async (analysisId: string) => {
    if (confirm('段階的公開を次の段階に進めますか？')) {
      try {
        await advancePublication(analysisId)
      } catch (error) {
        console.error('段階的公開の進行に失敗:', error)
      }
    }
  }

  const handleCancelPublication = async (analysisId: string) => {
    if (confirm('段階的公開をキャンセルしますか？')) {
      try {
        await cancelPublication(analysisId)
      } catch (error) {
        console.error('段階的公開のキャンセルに失敗:', error)
      }
    }
  }

  const getVisibilityIcon = (visibility: VisibilityLevel) => {
    switch (visibility) {
      case 'public': return <Globe className="h-4 w-4 text-green-500" />
      case 'team': return <Users className="h-4 w-4 text-blue-500" />
      case 'private': return <Lock className="h-4 w-4 text-orange-500" />
      case 'confidential': return <Shield className="h-4 w-4 text-red-500" />
      default: return <Eye className="h-4 w-4 text-gray-500" />
    }
  }

  const getVisibilityLabel = (visibility: VisibilityLevel) => {
    switch (visibility) {
      case 'public': return '公開'
      case 'team': return 'チーム内'
      case 'private': return '非公開'
      case 'confidential': return '機密'
      default: return visibility
    }
  }

  const getAnalysisTypeIcon = (type: string) => {
    switch (type) {
      case 'communication': return <MessageSquare className="h-4 w-4" />
      case 'leadership': return <TrendingUp className="h-4 w-4" />
      case 'collaboration': return <Users className="h-4 w-4" />
      case 'growth': return <Target className="h-4 w-4" />
      case 'personal': return <Heart className="h-4 w-4" />
      default: return <BarChart3 className="h-4 w-4" />
    }
  }

  const getAnalysisTypeLabel = (type: string) => {
    switch (type) {
      case 'communication': return 'コミュニケーション'
      case 'leadership': return 'リーダーシップ'
      case 'collaboration': return 'チームワーク'
      case 'growth': return '成長'
      case 'personal': return '個人'
      default: return type
    }
  }

  const getApprovalStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'approved': return 'bg-green-100 text-green-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      case 'requires_changes': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getApprovalStatusLabel = (status: string) => {
    switch (status) {
      case 'pending': return '承認待ち'
      case 'approved': return '承認済み'
      case 'rejected': return '却下'
      case 'requires_changes': return '修正要求'
      default: return status
    }
  }

  if (loading && !settings) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">設定を読み込み中...</p>
        </div>
      </div>
    )
  }

  if (!localSettings || !localStagedPublication) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="text-center py-12">
          <AlertTriangle className="h-12 w-12 text-orange-500 mx-auto mb-4" />
          <p className="text-gray-600">設定の読み込みに失敗しました</p>
          <Button onClick={() => window.location.reload()} className="mt-4">
            <RefreshCw className="h-4 w-4 mr-2" />
            再読み込み
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* ヘッダー */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <BarChart3 className="h-8 w-8 text-blue-600" />
          個人分析公開設定
        </h2>
        <p className="text-gray-600">
          AI分析結果の可視性レベルを設定し、段階的な公開を管理します
        </p>
      </div>

      {/* エラー表示 */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-red-700">
              <div className="flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2" />
                <span>エラー: {error}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={clearError}>
                閉じる
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* メイン設定エリア */}
        <div className="lg:col-span-2 space-y-6">
          {/* プリセット設定 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-purple-500" />
                プリセット設定
              </CardTitle>
              <p className="text-sm text-gray-600">
                よく使われる設定の組み合わせをプリセットとして提供します
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  onClick={() => handlePresetApply('ALL_PUBLIC')}
                  className="justify-start"
                >
                  <Globe className="h-4 w-4 mr-2" />
                  全体公開
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handlePresetApply('TEAM_ONLY')}
                  className="justify-start"
                >
                  <Users className="h-4 w-4 mr-2" />
                  チーム内のみ
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handlePresetApply('MOSTLY_PRIVATE')}
                  className="justify-start"
                >
                  <Lock className="h-4 w-4 mr-2" />
                  非公開中心
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handlePresetApply('SELECTIVE_SHARING')}
                  className="justify-start"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  選択的共有
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* 分析項目別可視性設定 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-blue-500" />
                分析項目別可視性設定
              </CardTitle>
              <p className="text-sm text-gray-600">
                各分析項目の可視性レベルを個別に設定してください
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="communication-style">コミュニケーションスタイル</Label>
                  <Select
                    value={localSettings.communication_style}
                    onValueChange={(value: VisibilityLevel) => handlePrivacySettingChange('communication_style', value)}
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
                    {getVisibilityIcon(localSettings.communication_style)}
                    {getVisibilityLabel(localSettings.communication_style)}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="collaboration-score">チームワークスコア</Label>
                  <Select
                    value={localSettings.collaboration_score}
                    onValueChange={(value: VisibilityLevel) => handlePrivacySettingChange('collaboration_score', value)}
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
                    {getVisibilityIcon(localSettings.collaboration_score)}
                    {getVisibilityLabel(localSettings.collaboration_score)}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="leadership-score">リーダーシップスコア</Label>
                  <Select
                    value={localSettings.leadership_score}
                    onValueChange={(value: VisibilityLevel) => handlePrivacySettingChange('leadership_score', value)}
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
                    {getVisibilityIcon(localSettings.leadership_score)}
                    {getVisibilityLabel(localSettings.leadership_score)}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="empathy-score">共感力スコア</Label>
                  <Select
                    value={localSettings.empathy_score}
                    onValueChange={(value: VisibilityLevel) => handlePrivacySettingChange('empathy_score', value)}
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
                    {getVisibilityIcon(localSettings.empathy_score)}
                    {getVisibilityLabel(localSettings.empathy_score)}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="assertiveness-score">主張性スコア</Label>
                  <Select
                    value={localSettings.assertiveness_score}
                    onValueChange={(value: VisibilityLevel) => handlePrivacySettingChange('assertiveness_score', value)}
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
                    {getVisibilityIcon(localSettings.assertiveness_score)}
                    {getVisibilityLabel(localSettings.assertiveness_score)}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="creativity-score">創造性スコア</Label>
                  <Select
                    value={localSettings.creativity_score}
                    onValueChange={(value: VisibilityLevel) => handlePrivacySettingChange('creativity_score', value)}
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
                    {getVisibilityIcon(localSettings.creativity_score)}
                    {getVisibilityLabel(localSettings.creativity_score)}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 段階的公開設定 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-purple-500" />
                段階的公開設定
              </CardTitle>
              <p className="text-sm text-gray-600">
                分析結果を段階的に公開し、時間をかけて可視性を拡大します
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* プリセット */}
              <div className="space-y-3">
                <Label>段階的公開プリセット</Label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleStagedPresetApply('GRADUAL_TEAM_TO_ORG')}
                    className="justify-start text-xs"
                  >
                    <Users className="h-3 w-3 mr-2" />
                    チーム→組織
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleStagedPresetApply('SLOW_PUBLIC_RELEASE')}
                    className="justify-start text-xs"
                  >
                    <Globe className="h-3 w-3 mr-2" />
                    ゆっくり全体公開
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleStagedPresetApply('QUICK_TEAM_SHARING')}
                    className="justify-start text-xs"
                  >
                    <Clock className="h-3 w-3 mr-2" />
                    素早くチーム共有
                  </Button>
                </div>
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label>段階的公開を有効化</Label>
                  <p className="text-sm text-gray-600">
                    分析結果を段階的に公開する
                  </p>
                </div>
                <Switch
                  checked={localStagedPublication.enabled}
                  onCheckedChange={(checked) => handleStagedPublicationChange('enabled', checked)}
                />
              </div>

              {localStagedPublication.enabled && (
                <>
                  <Separator />
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label>チーム内で最初に公開</Label>
                        <p className="text-sm text-gray-600">
                          分析結果を最初にチーム内で公開
                        </p>
                      </div>
                      <Switch
                        checked={localStagedPublication.stages.team_first}
                        onCheckedChange={(checked) => handleStageChange('team_first', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label>組織内で次に公開</Label>
                        <p className="text-sm text-gray-600">
                          チーム内公開から一定期間後に組織内で公開
                        </p>
                      </div>
                      <Switch
                        checked={localStagedPublication.stages.organization_second}
                        onCheckedChange={(checked) => handleStageChange('organization_second', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label>最終的に全体公開</Label>
                        <p className="text-sm text-gray-600">
                          組織内公開から一定期間後に全体公開
                        </p>
                      </div>
                      <Switch
                        checked={localStagedPublication.stages.public_final}
                        onCheckedChange={(checked) => handleStageChange('public_final', checked)}
                      />
                    </div>
                  </div>

                  <Separator />

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="team-to-org-delay">チーム→組織公開までの日数</Label>
                      <Input
                        id="team-to-org-delay"
                        type="number"
                        value={localStagedPublication.delay_days.team_to_org}
                        onChange={(e) => handleDelayChange('team_to_org', parseInt(e.target.value))}
                        min="1"
                        max="365"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="org-to-public-delay">組織→全体公開までの日数</Label>
                      <Input
                        id="org-to-public-delay"
                        type="number"
                        value={localStagedPublication.delay_days.org_to_public}
                        onChange={(e) => handleDelayChange('org_to_public', parseInt(e.target.value))}
                        min="1"
                        max="365"
                      />
                    </div>
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <Label>自動承認を有効化</Label>
                      <p className="text-sm text-gray-600">
                        段階的公開時に自動的に承認する
                      </p>
                    </div>
                    <Switch
                      checked={localStagedPublication.auto_approval}
                      onCheckedChange={(checked) => handleStagedPublicationChange('auto_approval', checked)}
                    />
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* プロフィール・目標・進捗可視性設定 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-green-500" />
                プロフィール・目標・進捗可視性設定
              </CardTitle>
              <p className="text-sm text-gray-600">
                プロフィール、成長目標、進捗状況の可視性レベルを設定してください
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="profile-visibility">プロフィール</Label>
                  <Select
                    value={localSettings.profile_visibility || 'team'}
                    onValueChange={(value: VisibilityLevel) => handlePrivacySettingChange('profile_visibility', value)}
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
                    {getVisibilityIcon(localSettings.profile_visibility || 'team')}
                    {getVisibilityLabel(localSettings.profile_visibility || 'team')}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="goals-visibility">成長目標</Label>
                  <Select
                    value={localSettings.goals_visibility || 'private'}
                    onValueChange={(value: VisibilityLevel) => handlePrivacySettingChange('goals_visibility', value)}
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
                    {getVisibilityIcon(localSettings.goals_visibility || 'private')}
                    {getVisibilityLabel(localSettings.goals_visibility || 'private')}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="progress-visibility">進捗状況</Label>
                  <Select
                    value={localSettings.progress_visibility || 'team'}
                    onValueChange={(value: VisibilityLevel) => handlePrivacySettingChange('progress_visibility', value)}
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
                    {getVisibilityIcon(localSettings.progress_visibility || 'team')}
                    {getVisibilityLabel(localSettings.progress_visibility || 'team')}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="communication-visibility">コミュニケーション</Label>
                  <Select
                    value={localSettings.communication_visibility || 'team'}
                    onValueChange={(value: VisibilityLevel) => handlePrivacySettingChange('communication_visibility', value)}
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
                    {getVisibilityIcon(localSettings.communication_visibility || 'team')}
                    {getVisibilityLabel(localSettings.communication_visibility || 'team')}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* アクセス制御設定 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-green-500" />
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
                  checked={localStagedPublication.allow_team_access || false}
                  onCheckedChange={(checked) => handleStagedPublicationChange('allow_team_access', checked)}
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
                  checked={localStagedPublication.allow_manager_access || false}
                  onCheckedChange={(checked) => handleStagedPublicationChange('allow_manager_access', checked)}
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
                  checked={localStagedPublication.allow_hr_access || false}
                  onCheckedChange={(checked) => handleStagedPublicationChange('allow_hr_access', checked)}
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
                  checked={localStagedPublication.auto_delete_enabled || false}
                  onCheckedChange={(checked) => handleStagedPublicationChange('auto_delete_enabled', checked)}
                />
              </div>

              <Separator />

              <div className="space-y-2">
                <Label htmlFor="retention-days">データ保持期間（日数）</Label>
                <Input
                  id="retention-days"
                  type="number"
                  value={localStagedPublication.data_retention_days || 365}
                  onChange={(e) => handleStagedPublicationChange('data_retention_days', parseInt(e.target.value))}
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
              disabled={saveStatus === 'saving' || loading}
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
                <Badge variant="outline" className={getVisibilityIcon(localSettings.profile_visibility || 'team').props.className}>
                  {getVisibilityLabel(localSettings.profile_visibility || 'team')}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">分析結果</span>
                <Badge variant="outline" className={getVisibilityIcon(localSettings.analysis_visibility || 'private').props.className}>
                  {getVisibilityLabel(localSettings.analysis_visibility || 'private')}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">成長目標</span>
                <Badge variant="outline" className={getVisibilityIcon(localSettings.goals_visibility || 'private').props.className}>
                  {getVisibilityLabel(localSettings.goals_visibility || 'private')}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">進捗状況</span>
                <Badge variant="outline" className={getVisibilityIcon(localSettings.progress_visibility || 'team').props.className}>
                  {getVisibilityLabel(localSettings.progress_visibility || 'team')}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">段階的公開</span>
                <Badge variant={localStagedPublication.enabled ? "default" : "outline"}>
                  {localStagedPublication.enabled ? '有効' : '無効'}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* 分析結果一覧 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">分析結果一覧</CardTitle>
            </CardHeader>
            <CardContent>
              {analyses.length === 0 ? (
                <div className="text-center py-4">
                  <BarChart3 className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">分析結果がありません</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {analyses.map((analysis) => (
                    <div key={analysis.id} className="border rounded-lg p-3 space-y-2">
                      <div className="flex items-center gap-2">
                        {getAnalysisTypeIcon(analysis.type)}
                        <span className="font-medium text-sm">{analysis.title}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className={getVisibilityIcon(analysis.current_visibility).props.className}>
                          {getVisibilityLabel(analysis.current_visibility)}
                        </Badge>
                        <Badge className={getApprovalStatusColor(analysis.approval_status)}>
                          {getApprovalStatusLabel(analysis.approval_status)}
                        </Badge>
                      </div>
                      <div className="text-xs text-gray-600">
                        {getAnalysisTypeLabel(analysis.type)} • {analysis.created_at}
                      </div>
                      
                      {/* 段階的公開コントロール */}
                      {analysis.staged_publication_enabled && (
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleAdvancePublication(analysis.id)}
                            disabled={loading}
                          >
                            次の段階へ
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleCancelPublication(analysis.id)}
                            disabled={loading}
                          >
                            キャンセル
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* 設定情報 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">設定情報</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Settings className="h-4 w-4" />
                設定は即座に反映されます
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Clock className="h-4 w-4" />
                最終更新: 2025-01-15
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Shield className="h-4 w-4" />
                データは暗号化して保存されます
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Info className="h-4 w-4" />
                段階的公開は承認後に開始されます
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
