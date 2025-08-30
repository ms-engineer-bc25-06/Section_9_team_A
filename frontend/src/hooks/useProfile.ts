import { useState, useEffect } from "react"
import { apiGet } from "@/lib/apiClient"
import { useAuth } from "@/components/auth/AuthProvider"
import { mockUserProfile, MockUserProfile } from "@/data/mockProfileData"

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
  is_first_login?: boolean
}

export function useProfile() {
  const { user, isLoading: authLoading, backendToken } = useAuth()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (authLoading) {
      // 認証状態の読み込み中は何もしない
      return
    }

    // if (user && backendToken) {
    //   // ログイン状態とバックエンドトークンが変更された際にプロフィールを再取得
    //   console.log("🔄 ユーザーログイン状態またはバックエンドトークン変更を検出、プロフィールを再取得中...")
    //   fetchProfile()
    // } else if (!user) {
    if (user) {
      // プレゼンテーション用：モックデータを使用
      fetchMockProfile()
    } else {
      // ユーザーがログインしていない場合
      setError("ログインが必要です")
      setIsLoading(false)
    }
  }, [user, authLoading, backendToken])

  // プレゼンテーション用：モックデータを取得
  const fetchMockProfile = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // シミュレーション用の遅延（実際のAPI呼び出しを模擬）
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // モックデータを設定
      setProfile(mockUserProfile)
    } catch (err) {
      console.error("プロフィールの取得に失敗:", err)
      setError("プロフィールの取得に失敗しました")
    } finally {
      setIsLoading(false)
    }
  }

  // 実際のAPI呼び出し（現在は無効化）
  const fetchProfile = async () => {
    if (!user) {
      setError("ログインが必要です")
      setIsLoading(false)
      return
    }

    try {
      setIsLoading(true)
      setError(null)
      console.log("🔍 プロフィール情報を取得中...")
      const data = await apiGet<UserProfile>("/users/profile")
      console.log("📊 取得したプロフィール情報:", {
        full_name: data.full_name,
        department: data.department,
        is_first_login: data.is_first_login
      })
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
    refetch: fetchMockProfile // プレゼンテーション用：モックデータ取得関数を返す
  }
}
