import { useState, useEffect, useCallback } from 'react'
import {
  getAnalysisPrivacySettings,
  updateAnalysisPrivacySettings,
  updateAnalysisVisibility,
  getAnalysisPublicationStatus,
  getStagedPublicationSchedule,
  advanceStagedPublication,
  cancelStagedPublication,
  type AnalysisPrivacySettings,
  type StagedPublicationSettings,
  type AnalysisPublicationStatus,
  type UpdatePrivacySettingsRequest,
  type UpdateAnalysisVisibilityRequest
} from '@/lib/api/analysisPrivacy'

export function useAnalysisPrivacy() {
  const [settings, setSettings] = useState<AnalysisPrivacySettings | null>(null)
  const [stagedPublication, setStagedPublication] = useState<StagedPublicationSettings | null>(null)
  const [analyses, setAnalyses] = useState<AnalysisPublicationStatus[]>([])
  const [schedule, setSchedule] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 初期データの読み込み
  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      // 可視性設定と段階的公開設定を並行して取得
      const [privacyData, publicationStatus, publicationSchedule] = await Promise.all([
        getAnalysisPrivacySettings(),
        getAnalysisPublicationStatus(),
        getStagedPublicationSchedule()
      ])

      setSettings(privacyData.settings)
      setStagedPublication(privacyData.staged_publication)
      setAnalyses(publicationStatus)
      setSchedule(publicationSchedule)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'データの読み込みに失敗しました')
      console.error('分析プライバシー設定の読み込みに失敗:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  // 可視性設定の更新
  const updateSettings = useCallback(async (request: UpdatePrivacySettingsRequest) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await updateAnalysisPrivacySettings(request)
      
      // ローカル状態を更新
      if (response.updated_settings) {
        setSettings(response.updated_settings)
      }
      if (response.updated_staged_publication) {
        setStagedPublication(response.updated_staged_publication)
      }
      
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '設定の更新に失敗しました'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  // 分析結果の可視性変更
  const updateAnalysisVisibilityLevel = useCallback(async (request: UpdateAnalysisVisibilityRequest) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await updateAnalysisVisibility(request)
      
      // ローカル状態を更新
      setAnalyses(prev => 
        prev.map(analysis => 
          analysis.id === request.analysis_id 
            ? response.updated_analysis 
            : analysis
        )
      )
      
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '可視性の変更に失敗しました'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  // 段階的公開の手動進行
  const advancePublication = useCallback(async (analysisId: string) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await advanceStagedPublication(analysisId)
      
      // ローカル状態を更新
      setAnalyses(prev => 
        prev.map(analysis => 
          analysis.id === analysisId 
            ? { 
                ...analysis, 
                current_visibility: response.new_stage as any,
                next_publication_stage: response.next_stage_date ? 'public' : undefined,
                next_publication_date: response.next_stage_date
              }
            : analysis
        )
      )
      
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '段階的公開の進行に失敗しました'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  // 段階的公開のキャンセル
  const cancelPublication = useCallback(async (analysisId: string) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await cancelStagedPublication(analysisId)
      
      // ローカル状態を更新
      setAnalyses(prev => 
        prev.map(analysis => 
          analysis.id === analysisId 
            ? { 
                ...analysis, 
                staged_publication_enabled: false,
                next_publication_stage: undefined,
                next_publication_date: undefined
              }
            : analysis
        )
      )
      
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '段階的公開のキャンセルに失敗しました'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  // 設定のリセット
  const resetSettings = useCallback(() => {
    setSettings(null)
    setStagedPublication(null)
    setAnalyses([])
    setSchedule(null)
    setError(null)
  }, [])

  // エラーのクリア
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  // 初回読み込み
  useEffect(() => {
    loadData()
  }, [loadData])

  return {
    // 状態
    settings,
    stagedPublication,
    analyses,
    schedule,
    loading,
    error,
    
    // アクション
    loadData,
    updateSettings,
    updateAnalysisVisibilityLevel,
    advancePublication,
    cancelPublication,
    resetSettings,
    clearError,
    
    // 計算値
    hasSettings: !!settings,
    hasStagedPublication: !!stagedPublication,
    hasAnalyses: analyses.length > 0,
    pendingAnalyses: analyses.filter(a => a.approval_status === 'pending'),
    approvedAnalyses: analyses.filter(a => a.approval_status === 'approved'),
    rejectedAnalyses: analyses.filter(a => a.approval_status === 'rejected'),
    stagedAnalyses: analyses.filter(a => a.staged_publication_enabled)
  }
}

// 可視性設定のプリセット
export const VISIBILITY_PRESETS = {
  ALL_PUBLIC: {
    communication_style: 'public' as const,
    collaboration_score: 'public' as const,
    leadership_score: 'public' as const,
    empathy_score: 'public' as const,
    assertiveness_score: 'public' as const,
    creativity_score: 'public' as const,
    analytical_score: 'public' as const,
    improvement_areas: 'public' as const,
    growth_suggestions: 'public' as const,
    personal_insights: 'public' as const
  },
  TEAM_ONLY: {
    communication_style: 'team' as const,
    collaboration_score: 'team' as const,
    leadership_score: 'team' as const,
    empathy_score: 'team' as const,
    assertiveness_score: 'team' as const,
    creativity_score: 'team' as const,
    analytical_score: 'team' as const,
    improvement_areas: 'team' as const,
    growth_suggestions: 'team' as const,
    personal_insights: 'team' as const
  },
  MOSTLY_PRIVATE: {
    communication_style: 'private' as const,
    collaboration_score: 'private' as const,
    leadership_score: 'private' as const,
    empathy_score: 'private' as const,
    assertiveness_score: 'private' as const,
    creativity_score: 'private' as const,
    analytical_score: 'private' as const,
    improvement_areas: 'private' as const,
    growth_suggestions: 'private' as const,
    personal_insights: 'private' as const
  },
  SELECTIVE_SHARING: {
    communication_style: 'team' as const,
    collaboration_score: 'team' as const,
    leadership_score: 'private' as const,
    empathy_score: 'private' as const,
    assertiveness_score: 'private' as const,
    creativity_score: 'team' as const,
    analytical_score: 'team' as const,
    improvement_areas: 'private' as const,
    growth_suggestions: 'private' as const,
    personal_insights: 'private' as const
  }
}

// 段階的公開のプリセット
export const STAGED_PUBLICATION_PRESETS = {
  GRADUAL_TEAM_TO_ORG: {
    enabled: true,
    stages: {
      team_first: true,
      organization_second: true,
      public_final: false
    },
    delay_days: {
      team_to_org: 7,
      org_to_public: 30
    },
    auto_approval: false
  },
  SLOW_PUBLIC_RELEASE: {
    enabled: true,
    stages: {
      team_first: true,
      organization_second: true,
      public_final: true
    },
    delay_days: {
      team_to_org: 14,
      org_to_public: 60
    },
    auto_approval: true
  },
  QUICK_TEAM_SHARING: {
    enabled: true,
    stages: {
      team_first: true,
      organization_second: false,
      public_final: false
    },
    delay_days: {
      team_to_org: 3,
      org_to_public: 30
    },
    auto_approval: true
  }
}
