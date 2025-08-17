// REVIEW: サブスクリプション管理ページ仮実装（るい）
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Check, X, AlertCircle } from "lucide-react"

export default function SubscriptionPage() {
  const [currentPlan] = useState({
    name: "Pro Plan",
    status: "active",
    nextBilling: "2024-02-01",
    price: "¥2,980",
    features: [
      "AI分析（月100回）",
      "チーム動態分析",
      "音声チャット（無制限）",
      "比較分析レポート",
      "優先サポート"
    ]
  })

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">サブスクリプション管理</h1>
      
      <div className="grid gap-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              現在のプラン
              <Badge variant={currentPlan.status === "active" ? "default" : "secondary"}>
                {currentPlan.status === "active" ? "アクティブ" : "非アクティブ"}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="text-xl font-semibold">{currentPlan.name}</h3>
                <p className="text-2xl font-bold text-blue-600">{currentPlan.price}/月</p>
              </div>
              
              <div>
                <p className="text-sm text-gray-600">
                  次回請求日: {currentPlan.nextBilling}
                </p>
              </div>
              
              <div>
                <h4 className="font-medium mb-2">含まれる機能:</h4>
                <ul className="space-y-2">
                  {currentPlan.features.map((feature, index) => (
                    <li key={index} className="flex items-center space-x-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>プラン変更</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-gray-600">
                プランの変更やキャンセルについては、サポートチームまでお問い合わせください。
              </p>
              <Button variant="outline">
                サポートに連絡
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}