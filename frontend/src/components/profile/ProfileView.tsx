//FIXME（プロフィール閲覧）
"use client"

import { ProfileTabs } from "./ProfileTabs"
import { useProfile } from "@/hooks/useProfile"
import { useApprovalList } from "@/hooks/useFeedbackApproval"
import Link from "next/link"
import { useEffect } from "react"

// モックデータを削除 - 実際のユーザープロフィールデータを使用

export function ProfileView() {
  const { profile, isLoading: profileLoading, error: profileError } = useProfile()
  
  // フィードバック承認関連のフック
  const {
    approvals: feedbackApprovals,
    loading: feedbackLoading,
    error: feedbackError,
    loadMyApprovals
  } = useApprovalList()

  // フィードバックデータを読み込み
  useEffect(() => {
    if (profile) {
      loadMyApprovals()
    }
  }, [profile, loadMyApprovals])

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
              <Link 
                href="/profile/edit" 
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                プロフィールを編集する
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // フィードバックデータを処理
  const processFeedbackData = () => {
    if (!feedbackApprovals || feedbackApprovals.length === 0) {
      return []
    }

    return feedbackApprovals.map(approval => {
      // 承認リクエストからフィードバックメッセージを生成
      let feedbackMessage = ""
      
      if (approval.approval_status === 'approved') {
        feedbackMessage = `✅ 分析結果が承認されました`
        if (approval.review_notes) {
          feedbackMessage += ` - ${approval.review_notes}`
        }
      } else if (approval.approval_status === 'rejected') {
        feedbackMessage = `❌ 分析結果が却下されました`
        if (approval.rejection_reason) {
          feedbackMessage += ` - ${approval.rejection_reason}`
        }
      } else if (approval.approval_status === 'requires_changes') {
        feedbackMessage = `⚠️ 分析結果に修正が必要です`
        if (approval.review_notes) {
          feedbackMessage += ` - ${approval.review_notes}`
        }
      } else if (approval.approval_status === 'pending') {
        feedbackMessage = `⏳ 分析結果の承認待ちです`
      } else if (approval.approval_status === 'under_review') {
        feedbackMessage = `🔍 分析結果をレビュー中です`
      }

      // 分析タイトルがある場合は追加
      if (approval.analysis_title) {
        feedbackMessage = `「${approval.analysis_title}」: ${feedbackMessage}`
      }

      return feedbackMessage
    }).filter(message => message !== "") // 空のメッセージを除外
  }

  // 実際のプロフィールデータをProfileTabsの期待する形式に変換
  const profileData = {
    name: profile.full_name || "名前未設定",
    nickname: profile.nickname || "ニックネーム未設定",
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
    feedback: processFeedbackData() // 実際のフィードバックデータを使用
  }

  return (
    <ProfileTabs profile={profileData}>
      <div className="space-y-6">
        {/* AI分析結果セクション */}
        {/* AI分析更新フォーム */}
      </div>
    </ProfileTabs>
  )
}
