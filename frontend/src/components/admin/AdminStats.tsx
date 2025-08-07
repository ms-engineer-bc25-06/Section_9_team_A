// // 統計情報表示部品
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Users, CreditCard, TrendingUp, AlertCircle } from "lucide-react"

const mockStats = {
  totalUsers: 25,
  maxUsers: 30,
  monthlyRevenue: 15000,
  activeUsers: 22,
  pendingPayments: 2,
}

export function AdminStats() {
  const usagePercentage = (mockStats.totalUsers / mockStats.maxUsers) * 100

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>利用状況</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">現在の利用人数</span>
            <Badge variant="secondary" className="text-lg px-3 py-1">
              {mockStats.totalUsers} / {mockStats.maxUsers}人
            </Badge>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${usagePercentage}%` }}
            />
          </div>

          <div className="text-sm text-gray-600">利用率: {usagePercentage.toFixed(1)}%</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CreditCard className="h-5 w-5" />
            <span>収益情報</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">月間収益</span>
            <span className="text-2xl font-bold text-green-600">¥{mockStats.monthlyRevenue.toLocaleString()}</span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">アクティブユーザー</span>
            <Badge variant="default">{mockStats.activeUsers}人</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5" />
            <span>注意事項</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {mockStats.pendingPayments > 0 && (
              <div className="flex items-center space-x-2 text-yellow-600">
                <AlertCircle className="h-4 w-4" />
                <span className="text-sm">{mockStats.pendingPayments}件の未処理決済があります</span>
              </div>
            )}

            {usagePercentage > 80 && (
              <div className="flex items-center space-x-2 text-orange-600">
                <TrendingUp className="h-4 w-4" />
                <span className="text-sm">利用率が80%を超えています</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}