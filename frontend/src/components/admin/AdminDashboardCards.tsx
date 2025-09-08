"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Users, CreditCard, BarChart3, Settings, UserPlus, Shield } from "lucide-react"
import { useRouter } from "next/navigation"

export function AdminDashboardCards() {
  const router = useRouter()

  const cards = [
    {
      title: "ユーザー管理",
      description: "登録ユーザーの管理・確認",
      icon: Users,
      action: () => router.push("/admin/users"),
      color: "bg-blue-500",
    },
    {
      title: "使用人数追加",
      description: "新規ユーザーの追加",
      icon: UserPlus,
      action: () => router.push("/admin/billing/add-users"),
      color: "bg-green-500",
    },
    {
      title: "決済管理",
      description: "料金・決済状況の確認",
      icon: CreditCard,
      action: () => router.push("/admin/billing"),
      color: "bg-purple-500",
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-7xl mx-auto">
      {cards.map((card, index) => (
        <div key={index} className="bg-white border border-orange-200 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer p-6 min-h-[180px] flex flex-col">
          <div className="flex items-center space-x-3 mb-4">
            <div className={`p-3 rounded-lg ${card.color}`}>
              <card.icon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-orange-900 mb-1">{card.title}</h3>
              <p className="text-gray-700 text-sm">{card.description}</p>
            </div>
          </div>
          <div className="flex-grow"></div>
          <button
            onClick={card.action}
            className="w-full bg-white border-2 border-orange-400 text-orange-700 py-2 px-4 rounded-md hover:bg-orange-50 hover:border-orange-500 transition-colors text-sm font-medium mt-auto"
          >
            開く
          </button>
        </div>
      ))}
    </div>
  )
}
