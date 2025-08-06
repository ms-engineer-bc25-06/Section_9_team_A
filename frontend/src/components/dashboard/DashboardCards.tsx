// ダッシュボード情報カード
"use client"

import type React from "react"
import { useRouter } from "next/navigation"
import { Users, MessageCircle, User, BarChart3 } from "lucide-react"

const DashboardCards: React.FC = () => {
  const router = useRouter()

  const cards = [
    {
      title: "チームメンバー一覧",
      description: "チームメンバーの情報を確認",
      icon: Users,
      action: () => router.push("/team"),
      color: "bg-blue-500",
    },
    {
      title: "雑談ルーム",
      description: "音声チャットでコミュニケーション",
      icon: MessageCircle,
      action: () => router.push("/voice-chat"),
      color: "bg-green-500",
    },
    {
      title: "マイプロフィール",
      description: "プロフィール情報の確認・編集",
      icon: User,
      action: () => router.push("/profile"),
      color: "bg-purple-500",
    },
    {
      title: "AI分析結果",
      description: "コミュニケーション分析を確認",
      icon: BarChart3,
      action: () => router.push("/analytics"),
      color: "bg-orange-500",
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {cards.map((card, index) => (
        <div key={index} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer p-6">
          <div className="flex items-center space-x-4 mb-4">
            <div className={`p-3 rounded-lg ${card.color}`}>
              <card.icon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{card.title}</h3>
              <p className="text-gray-600">{card.description}</p>
            </div>
          </div>
          <button
            onClick={card.action}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
          >
            開く
          </button>
        </div>
      ))}
    </div>
  )
}

export { DashboardCards }
