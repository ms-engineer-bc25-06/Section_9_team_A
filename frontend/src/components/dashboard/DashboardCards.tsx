"use client"

import type React from "react"
import { useRouter } from "next/navigation"
import { Users, MessageCircle, BarChart3, Target } from "lucide-react"
import { useAuth } from "@/components/auth/AuthProvider"
import { useProfile } from "@/hooks/useProfile"

const DashboardCards: React.FC = () => {
  const router = useRouter()
  const { user } = useAuth()
  const { profile: userProfileData } = useProfile()

  const getGreeting = () => {
    const hour = new Date().getHours()
    let greeting = ""
    if (hour < 12) greeting = "おはようございます"
    else if (hour < 18) greeting = "こんにちは"
    else greeting = "こんばんは"
    
    // ユーザー名を取得（優先順位: nickname > display_name > email > デフォルト）
    const userName = userProfileData?.nickname || user?.email?.split('@')[0] || "ユーザー"
    
    return `${greeting}！${userName}さん！`
  }

  const getCharacter = () => {
    const hour = new Date().getHours()
    if (hour < 12) return "🌅" // 朝
    else if (hour < 18) return "☀️" // 昼
    else return "🌙" // 夜
  }

  const cards = [
    {
      title: "部署別メンバー一覧",
      description: "チームメンバーの情報を確認",
      icon: Users,
      action: () => router.push("/team"),
      color: "bg-emerald-500",
    },
    {
      title: "雑談ルーム",
      description: "音声チャットでコミュニケーション",
      icon: MessageCircle,
      action: () => router.push("/voice-chat"),
      color: "bg-amber-500",
    },
    {
      title: "AI分析結果",
      description: "コミュニケーション分析を確認",
      icon: BarChart3,
      action: () => router.push("/analytics"),
      color: "bg-rose-500",
    },
    {
      title: "個人成長支援",
      description: "AIによる成長支援とアドバイス",
      icon: Target,
      action: () => router.push("/personal-growth"),
      color: "bg-violet-500",
    },
  ]

  // 初回ログインのユーザー向けのプロフィール設定カード
  const profileSetupCard = {
    title: "プロフィール設定",
    description: "初回ログインの方は、プロフィール情報を設定してください",
    icon: Target,
    action: () => router.push("/profile/edit"),
    color: "bg-green-500",
  }

  // 初回ログインかどうかを判定
  const isFirstLogin = userProfileData?.is_first_login || false

  return (
    <div className="space-y-8">
      {/* 挨拶セクション */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center space-x-4">
          <div className="text-4xl">
            {getCharacter()}
          </div>
          <div className="text-2xl font-semibold text-gray-800">
            {getGreeting()}
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-10 max-w-7xl mx-auto">
        {/* 通常のカードを表示 */}
        {cards.map((card, index) => (
          <div key={index} className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer p-8 min-h-[200px] flex flex-col">
            <div className="flex items-center space-x-4 mb-6">
              <div className={`p-4 rounded-lg ${card.color}`}>
                <card.icon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{card.title}</h3>
                <p className="text-gray-600 text-base">{card.description}</p>
              </div>
            </div>
            <div className="flex-grow"></div>
            <button
              onClick={card.action}
              className="w-full bg-white border-2 border-gray-400 text-gray-700 py-3 px-6 rounded-md hover:bg-gray-50 hover:border-gray-500 transition-colors text-base font-medium mt-auto"
            >
              開く
            </button>
          </div>
        ))}
        
        {/* 初回ログインの場合は、プロフィール設定カードも追加表示 */}
        {isFirstLogin && (
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer p-8 min-h-[200px] flex flex-col">
            <div className="flex items-center space-x-4 mb-6">
              <div className={`p-4 rounded-lg ${profileSetupCard.color}`}>
                <profileSetupCard.icon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{profileSetupCard.title}</h3>
                <p className="text-gray-600 text-base">{profileSetupCard.description}</p>
              </div>
            </div>
            <div className="flex-grow"></div>
            <button
              onClick={profileSetupCard.action}
              className="w-full bg-white border-2 border-gray-400 text-gray-700 py-3 px-6 rounded-md hover:bg-gray-50 hover:border-gray-500 transition-colors text-base font-medium mt-auto"
            >
              プロフィールを設定する
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export { DashboardCards }
