// 管理者ダッシュボードUI
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Users, CreditCard, BarChart3, Settings, UserPlus } from "lucide-react"
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
      description: "新しいユーザー枠の追加（決済）",
      icon: UserPlus,
      action: () => router.push("/admin/billing/add-users"),
      color: "bg-purple-500",
    },
    {
      title: "決済・サブスクリプション",
      description: "料金プラン・決済状況の管理",
      icon: CreditCard,
      action: () => router.push("/admin/billing"),
      color: "bg-green-500",
    },
   
    // {
    //   title: "システム分析",
    //   description: "利用状況・パフォーマンス分析",
    //   icon: BarChart3,
    //   action: () => router.push("/admin/analytics"),
    //   color: "bg-orange-500",
    // },
    // {
    //   title: "システム設定",
    //   description: "アプリケーション設定の管理",
    //   icon: Settings,
    //   action: () => router.push("/admin/settings"),
    //   color: "bg-slate-500",
    // },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    {cards.map((card, index) => (
      <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
        <CardHeader className="pb-">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${card.color}`}>
              <card.icon className="h-6 w-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-lg">{card.title}</CardTitle>
              <CardDescription>{card.description}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Button onClick={card.action} className="w-full">
            開く
          </Button>
        </CardContent>
      </Card>
    ))}
  </div>
)
}