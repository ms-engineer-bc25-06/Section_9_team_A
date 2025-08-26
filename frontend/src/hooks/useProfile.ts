import { useState, useEffect } from "react"
import { apiGet } from "@/lib/apiClient"
import { useAuth } from "@/components/auth/AuthProvider"

export interface UserProfile {
  full_name: string
  nickname: string
  department: string
  join_date: string
  birth_date: string
  hometown: string
  residence: string
  hobbies: string
  student_activities: string
  holiday_activities: string
  favorite_food: string
  favorite_media: string
  favorite_music: string
  pets_oshi: string
  respected_person: string
  motto: string
  future_goals: string
}

export function useProfile() {
  const { user, isLoading: authLoading } = useAuth()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (authLoading) {
      // 認証状態の読み込み中は何もしない
      return
    }

    if (user) {
      fetchProfile()
    } else {
      // ユーザーがログインしていない場合
      setError("ログインが必要です")
      setIsLoading(false)
    }
  }, [user, authLoading])

  const fetchProfile = async () => {
    if (!user) {
      setError("ログインが必要です")
      setIsLoading(false)
      return
    }

    try {
      setIsLoading(true)
      setError(null)
      const data = await apiGet<UserProfile>("/users/profile")
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
    const hasBasicInfo = profile.nickname || profile.department
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
