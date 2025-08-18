import { apiGet, apiPut, apiPost } from '../apiClient'

// 分析項目の可視性レベル
export type VisibilityLevel = 'public' | 'team' | 'private' | 'confidential'

// 分析項目別の可視性設定
export interface AnalysisPrivacySettings {
  communication_style: VisibilityLevel
  collaboration_score: VisibilityLevel
  leadership_score: VisibilityLevel
  empathy_score: VisibilityLevel
  assertiveness_score: VisibilityLevel
  creativity_score: VisibilityLevel
  analytical_score: VisibilityLevel
  improvement_areas: VisibilityLevel
  growth_suggestions: VisibilityLevel
  personal_insights: VisibilityLevel
}

// 段階的公開設定
export interface StagedPublicationSettings {
  enabled: boolean
  stages: {
    team_first: boolean
    organization_second: boolean
    public_final: boolean
  }
  delay_days: {
    team_to_org: number
    org_to_public: number
  }
  auto_approval: boolean
}

// 分析結果の公開状態
export interface AnalysisPublicationStatus {
  id: string
  title: string
  type: string
  created_at: string
  current_visibility: VisibilityLevel
  is_published: boolean
  approval_status: 'pending' | 'approved' | 'rejected' | 'requires_changes'
  staged_publication_enabled: boolean
  next_publication_stage?: 'team' | 'organization' | 'public'
  next_publication_date?: string
}

// 可視性設定の更新リクエスト
export interface UpdatePrivacySettingsRequest {
  settings: Partial<AnalysisPrivacySettings>
  staged_publication?: Partial<StagedPublicationSettings>
}

// 可視性設定の更新レスポンス
export interface UpdatePrivacySettingsResponse {
  success: boolean
  message: string
  updated_settings: AnalysisPrivacySettings
  updated_staged_publication: StagedPublicationSettings
}

// 分析結果の公開範囲変更リクエスト
export interface UpdateAnalysisVisibilityRequest {
  analysis_id: string
  new_visibility: VisibilityLevel
  reason?: string
  enable_staged_publication?: boolean
}

// 分析結果の公開範囲変更レスポンス
export interface UpdateAnalysisVisibilityResponse {
  success: boolean
  message: string
  updated_analysis: AnalysisPublicationStatus
}

/**
 * 個人分析の可視性設定を取得
 */
export async function getAnalysisPrivacySettings(): Promise<{
  settings: AnalysisPrivacySettings
  staged_publication: StagedPublicationSettings
}> {
  try {
    const response = await apiGet<{
      settings: AnalysisPrivacySettings
      staged_publication: StagedPublicationSettings
    }>('/users/me/analysis-privacy')
    return response
  } catch (error) {
    console.error('可視性設定の取得に失敗:', error)
    throw new Error('可視性設定の取得に失敗しました')
  }
}

/**
 * 個人分析の可視性設定を更新
 */
export async function updateAnalysisPrivacySettings(
  request: UpdatePrivacySettingsRequest
): Promise<UpdatePrivacySettingsResponse> {
  try {
    const response = await apiPut<UpdatePrivacySettingsResponse>('/users/me/analysis-privacy', request)
    return response
  } catch (error) {
    console.error('可視性設定の更新に失敗:', error)
    throw new Error('可視性設定の更新に失敗しました')
  }
}

/**
 * 分析結果の公開範囲を変更
 */
export async function updateAnalysisVisibility(
  request: UpdateAnalysisVisibilityRequest
): Promise<UpdateAnalysisVisibilityResponse> {
  try {
    const response = await apiPut<UpdateAnalysisVisibilityResponse>(`/analyses/${request.analysis_id}/visibility`, request)
    return response
  } catch (error) {
    console.error('分析結果の公開範囲変更に失敗:', error)
    throw new Error('分析結果の公開範囲変更に失敗しました')
  }
}

/**
 * 分析結果の公開状態一覧を取得
 */
export async function getAnalysisPublicationStatus(): Promise<AnalysisPublicationStatus[]> {
  try {
    const response = await apiGet<AnalysisPublicationStatus[]>('/users/me/analyses/publication-status')
    return response
  } catch (error) {
    console.error('分析結果の公開状態取得に失敗:', error)
    throw new Error('分析結果の公開状態取得に失敗しました')
  }
}

/**
 * 段階的公開のスケジュールを取得
 */
export async function getStagedPublicationSchedule(): Promise<{
  enabled: boolean
  current_stage: 'team' | 'organization' | 'public'
  next_stage?: 'team' | 'organization' | 'public'
  next_stage_date?: string
  schedule: Array<{
    stage: 'team' | 'organization' | 'public'
    scheduled_date: string
    status: 'completed' | 'pending' | 'cancelled'
  }>
}> {
  try {
    const response = await apiGet<{
      enabled: boolean
      current_stage: 'team' | 'organization' | 'public'
      next_stage?: 'team' | 'organization' | 'public'
      next_stage_date?: string
      schedule: Array<{
        stage: 'team' | 'organization' | 'public'
        scheduled_date: string
        status: 'completed' | 'pending' | 'cancelled'
      }>
    }>('/users/me/analysis-privacy/staged-publication-schedule')
    return response
  } catch (error) {
    console.error('段階的公開スケジュールの取得に失敗:', error)
    throw new Error('段階的公開スケジュールの取得に失敗しました')
  }
}

/**
 * 段階的公開を手動で進める
 */
export async function advanceStagedPublication(analysis_id: string): Promise<{
  success: boolean
  message: string
  new_stage: 'team' | 'organization' | 'public'
  next_stage_date?: string
}> {
  try {
    const response = await apiPost<{
      success: boolean
      message: string
      new_stage: 'team' | 'organization' | 'public'
      next_stage_date?: string
    }>(`/analyses/${analysis_id}/advance-publication`, {})
    return response
  } catch (error) {
    console.error('段階的公開の手動進行に失敗:', error)
    throw new Error('段階的公開の手動進行に失敗しました')
  }
}

/**
 * 段階的公開をキャンセル
 */
export async function cancelStagedPublication(analysis_id: string): Promise<{
  success: boolean
  message: string
}> {
  try {
    const response = await apiPost<{
      success: boolean
      message: string
    }>(`/analyses/${analysis_id}/cancel-publication`, {})
    return response
  } catch (error) {
    console.error('段階的公開のキャンセルに失敗:', error)
    throw new Error('段階的公開のキャンセルに失敗しました')
  }
}

/**
 * 可視性レベルの説明を取得
 */
export function getVisibilityDescription(level: VisibilityLevel): string {
  switch (level) {
    case 'public':
      return '組織内の全員が閲覧可能'
    case 'team':
      return '所属チームのメンバーのみ閲覧可能'
    case 'private':
      return '本人のみ閲覧可能'
    case 'confidential':
      return '機密情報として扱われ、限られた権限を持つ者のみ閲覧可能'
    default:
      return '設定されていません'
  }
}

/**
 * 可視性レベルのアイコンクラスを取得
 */
export function getVisibilityIconClass(level: VisibilityLevel): string {
  switch (level) {
    case 'public':
      return 'text-green-500'
    case 'team':
      return 'text-blue-500'
    case 'private':
      return 'text-orange-500'
    case 'confidential':
      return 'text-red-500'
    default:
      return 'text-gray-500'
  }
}

/**
 * 段階的公開の説明を取得
 */
export function getStagedPublicationDescription(settings: StagedPublicationSettings): string {
  if (!settings.enabled) {
    return '段階的公開は無効になっています'
  }

  const stages = []
  if (settings.stages.team_first) stages.push('チーム内')
  if (settings.stages.organization_second) stages.push('組織内')
  if (settings.stages.public_final) stages.push('全体')

  if (stages.length === 0) {
    return '段階的公開が有効ですが、公開段階が設定されていません'
  }

  return `${stages.join(' → ')}の順序で段階的に公開されます`
}
