// REVIEW: 料金プランカードコンポーネント仮実装（るい）
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Check, Star } from "lucide-react"

interface PricingPlan {
  id: string
  name: string
  price: number
  period: "month" | "year"
  features: string[]
  isPopular?: boolean
  isCurrent?: boolean
}

export function PricingCard() {
  const [selectedPeriod, setSelectedPeriod] = useState<"month" | "year">("month")
  
  const plans: PricingPlan[] = [
    {
      id: "free",
      name: "Free",
      price: 0,
      period: selectedPeriod,
      features: [
        "AI分析（月5回）",
        "基本的な音声チャット",
        "チーム作成（最大3人）"
      ]
    },
    {
      id: "pro",
      name: "Pro",
      price: selectedPeriod === "month" ? 2980 : 29800,
      period: selectedPeriod,
      features: [
        "AI分析（月100回）",
        "チーム動態分析",
        "音声チャット（無制限）",
        "比較分析レポート",
        "優先サポート"
      ],
      isPopular: true,
      isCurrent: true
    },
    {
      id: "enterprise",
      name: "Enterprise",
      price: selectedPeriod === "month" ? 9980 : 99800,
      period: selectedPeriod,
      features: [
        "AI分析（無制限）",
        "高度なチーム分析",
        "カスタム分析モデル",
        "API アクセス",
        "専任サポート",
        "SLA保証"
      ]
    }
  ]

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY'
    }).format(amount)
  }

  const getPeriodLabel = (period: string) => {
    return period === "month" ? "月" : "年"
  }

  const getSavings = (monthlyPrice: number, yearlyPrice: number) => {
    const monthlyTotal = monthlyPrice * 12
    const savings = monthlyTotal - yearlyPrice
    return Math.round((savings / monthlyTotal) * 100)
  }

  return (
    <div className="space-y-6">
      {/* 期間選択 */}
      <div className="flex justify-center">
        <div className="bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setSelectedPeriod("month")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedPeriod === "month"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            月額
          </button>
          <button
            onClick={() => setSelectedPeriod("year")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedPeriod === "year"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            年額
            {selectedPeriod === "year" && (
              <Badge variant="default" className="ml-2 text-xs">
                {getSavings(2980, 29800)}%OFF
              </Badge>
            )}
          </button>
        </div>
      </div>

      {/* プラン一覧 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <Card
            key={plan.id}
            className={`relative ${
              plan.isPopular
                ? "ring-2 ring-blue-500 shadow-lg"
                : "border-gray-200"
            }`}
          >
            {plan.isPopular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge variant="default" className="bg-blue-600">
                  <Star className="h-3 w-3 mr-1" />
                  人気
                </Badge>
              </div>
            )}
            
            {plan.isCurrent && (
              <div className="absolute -top-3 right-4">
                <Badge variant="secondary">現在のプラン</Badge>
              </div>
            )}

            <CardHeader className="text-center pb-4">
              <CardTitle className="text-xl">{plan.name}</CardTitle>
              <div className="mt-4">
                <span className="text-4xl font-bold">
                  {formatCurrency(plan.price)}
                </span>
                <span className="text-gray-600 ml-2">
                  /{getPeriodLabel(plan.period)}
                </span>
              </div>
            </CardHeader>

            <CardContent>
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-center space-x-2">
                    <Check className="h-4 w-4 text-green-500 flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                className={`w-full ${
                  plan.isCurrent
                    ? "bg-gray-600 hover:bg-gray-700"
                    : plan.isPopular
                    ? "bg-blue-600 hover:bg-blue-700"
                    : "bg-gray-900 hover:bg-gray-800"
                }`}
                disabled={plan.isCurrent}
              >
                {plan.isCurrent
                  ? "現在のプラン"
                  : plan.price === 0
                  ? "無料で開始"
                  : "プランを選択"}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}