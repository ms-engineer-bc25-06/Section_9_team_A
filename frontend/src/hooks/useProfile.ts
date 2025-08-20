import { useState, useEffect } from "react"
import { apiGetWithToken } from "@/lib/apiClient"
import { useAuth } from "@/components/auth/AuthProvider"

export interface UserProfile {
  id: string
  email: string
  username: string
  full_name: string | null
  avatar_url: string | null
  bio: string | null
  nickname: string | null
  department: string | null
  join_date: string | null
  birth_date: string | null
  hometown: string | null
  residence: string | null
  hobbies: string | null
  student_activities: string | null
  holiday_activities: string | null
  favorite_food: string | null
  favorite_media: string | null
  favorite_music: string | null
  pets_oshi: string | null
  respected_person: string | null
  motto: string | null
  future_goals: string | null
  feedback?: string[] | null
  ai_analysis?: {
    collaboration_score?: number | null
    leadership_score?: number | null
    empathy_score?: number | null
    assertiveness_score?: number | null
    creativity_score?: number | null
    analytical_score?: number | null
    communication_style?: string | null
    team_dynamics_insights?: string | null
    improvement_suggestions?: string[] | null
    last_updated?: string | null
  } | null
}

export function useProfile() {
  const { backendToken, isLoading: authLoading } = useAuth()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (authLoading) {
      // 認証状態の読み込み中は何もしない
      return
    }

    if (backendToken) {
      fetchProfile()
    } else {
      // バックエンドトークンがない場合は未認証状態
      setError("ログインが必要です")
      setIsLoading(false)
    }
  }, [backendToken, authLoading])

  const fetchProfile = async () => {
    if (!backendToken) {
      setError("認証トークンがありません")
      setIsLoading(false)
      return
    }

    try {
      setIsLoading(true)
      setError(null)
      const data = await apiGetWithToken<UserProfile>("/users/me", backendToken)
      setProfile(data)
    } catch (err) {
      console.error("プロフィールの取得に失敗:", err)
      setError("プロフィールの取得に失敗しました")
    } finally {
      setIsLoading(false)
    }
  }

  const hasProfileData = () => {
    if (!profile) return false
    
    // 基本的なプロフィール項目が設定されているかチェック
    const hasBasicInfo = profile.nickname || profile.department || profile.bio
    const hasPersonalInfo = profile.hobbies || profile.favorite_food || profile.motto
    
    return hasBasicInfo || hasPersonalInfo
  }

  return {
    profile,
    isLoading: isLoading || authLoading,
    error,
    hasProfileData: hasProfileData(),
    refetch: fetchProfile
  }
}
