//FIXME（プロフィール閲覧）
"use client"

import { ProfileTabs } from "./ProfileTabs"
import { useProfile } from "@/hooks/useProfile"
import { useApprovalList } from "@/hooks/useFeedbackApproval"
import Link from "next/link"
import { useEffect, useState } from "react"

export function ProfileView() {
  const { profile, isLoading: profileLoading, error: profileError } = useProfile()
  
  // 実際のフィードバック承認データを使用
  const {
    approvals: feedbackApprovals,
    loading: feedbackLoading,
    error: feedbackError,
    loadMyApprovals
  } = useApprovalList()

  // フィードバックメッセージを生成（承認済みのもののみ）
  const feedbackMessages = feedbackApprovals
    .filter(approval => approval.approval_status === 'approved' && approval.is_confirmed)
    .map(approval => approval.analysis_title || 'フィードバック')

  useEffect(() => {
    loadMyApprovals()
  }, [loadMyApprovals])

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
          <p className="text-gray-600 mb-4">プロフィールデータが見つかりません</p>
          <Link href="/profile/edit">
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              プロフィールを作成
            </button>
          </Link>
        </div>
      </div>
    )
  }

  // プレゼンテーション用：プロフィールデータをProfileTabsの形式に変換
  const profileForTabs = {
    name: profile.full_name,
    nickname: profile.nickname,
    department: profile.department,
    joinDate: profile.join_date,
    birthDate: profile.birth_date,
    hometown: profile.hometown,
    residence: profile.residence,
    hobbies: profile.hobbies,
    studentActivities: profile.student_activities,
    holidayActivities: profile.holiday_activities,
    favoriteFood: profile.favorite_food,
    favoriteMedia: profile.favorite_media,
    favoriteMusic: profile.favorite_music,
    petsOshi: profile.pets_oshi,
    respectedPerson: profile.respected_person,
    motto: profile.motto,
    futureGoals: profile.future_goals,
    feedback: feedbackMessages,
    avatarUrl: null // avatar_urlプロパティが存在しないため、nullに設定
  }

  return (
    <div className="max-w-6xl mx-auto">
      <ProfileTabs profile={profileForTabs}>
        <div className="space-y-6">
          {/* タブコンテンツはProfileTabs内で管理 */}
        </div>
      </ProfileTabs>
    </div>
  )
}
