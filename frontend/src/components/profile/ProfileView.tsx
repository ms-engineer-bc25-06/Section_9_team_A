//FIXME（プロフィール閲覧）
"use client"


import { AIAnalysisSection } from "./AIAnalysisSection"
import { AnalysisUpdateForm } from "./AnalysisUpdateForm"
import { ProfileTabs } from "./ProfileTabs"
import { useAIAnalysis } from "@/hooks/useAIAnalysis"
import { useProfile } from "@/hooks/useProfile"

// モックデータを削除 - 実際のユーザープロフィールデータを使用

export function ProfileView() {
  const { analyses, isLoading, error, createAnalysis } = useAIAnalysis()
  const { profile, isLoading: profileLoading, error: profileError } = useProfile()
  
  const handleAnalysisUpdate = async (text: string, analysisTypes: string[]) => {
    try {
      await createAnalysis(text, analysisTypes)
    } catch (error) {
      console.error('Analysis update failed:', error)
      throw error
    }
  }

  // プロフィールデータが読み込み中の場合はローディング表示
  if (profileLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">プロフィールを読み込み中...</p>
        </div>
      </div>
    )
  }

  // プロフィールデータの読み込みに失敗した場合
  if (profileError) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <p className="text-red-600 mb-4">プロフィールの読み込みに失敗しました</p>
          <p className="text-gray-600">{profileError}</p>
        </div>
      </div>
    )
  }

  // プロフィールデータが存在しない場合
  if (!profile) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <p className="text-gray-600 mb-4">プロフィールが見つかりません</p>
          <p className="text-sm text-gray-500">プロフィール編集画面で情報を設定してください</p>
        </div>
      </div>
    )
  }

  // プロフィールデータが存在するが、内容が空の場合
  const hasProfileContent = profile.nickname || profile.department || profile.join_date || 
                           profile.birth_date || profile.hometown || profile.residence || 
                           profile.hobbies || profile.student_activities || profile.holiday_activities || 
                           profile.favorite_food || profile.favorite_media || profile.favorite_music || 
                           profile.pets_oshi || profile.respected_person || profile.motto || profile.future_goals

  if (!hasProfileContent) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center max-w-md mx-auto">
          <div className="mb-6">
            <div className="w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">マイプロフィールを登録しよう</h2>
            <p className="text-gray-600 mb-6">あなたのことを知ってもらうために、プロフィール情報を登録してみませんか？</p>
          </div>
          
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-medium text-blue-900 mb-2">プロフィールに含まれる情報</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• ニックネームや趣味</li>
                <li>• 出身地や居住地</li>
                <li>• 学生時代の活動</li>
                <li>• 将来の目標など</li>
              </ul>
            </div>
            
            <div className="flex justify-center">
              <a 
                href="/profile/edit" 
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                プロフィールを編集する
              </a>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // 実際のプロフィールデータをProfileTabsの期待する形式に変換
  const profileData = {
    name: profile.nickname || "ユーザー",
    nickname: profile.nickname || "",
    department: profile.department || "",
    joinDate: profile.join_date || "",
    birthDate: profile.birth_date || "",
    hometown: profile.hometown || "",
    residence: profile.residence || "",
    hobbies: profile.hobbies || "",
    studentActivities: profile.student_activities || "",
    holidayActivities: profile.holiday_activities || "",
    favoriteFood: profile.favorite_food || "",
    favoriteMedia: profile.favorite_media || "",
    favoriteMusic: profile.favorite_music || "",
    petsOshi: profile.pets_oshi || "",
    respectedPerson: profile.respected_person || "",
    motto: profile.motto || "",
    futureGoals: profile.future_goals || "",
    feedback: [] // フィードバックは現在実装されていないため空配列
  }

  return (
    <ProfileTabs profile={profileData}>
      <div className="space-y-6">
        {/* AI分析結果セクション */}
        <AIAnalysisSection analyses={analyses} isLoading={isLoading} />
        
        {/* AI分析更新フォーム */}
        <AnalysisUpdateForm onAnalysisUpdate={handleAnalysisUpdate} isLoading={isLoading} />
      </div>
    </ProfileTabs>
  )
}
