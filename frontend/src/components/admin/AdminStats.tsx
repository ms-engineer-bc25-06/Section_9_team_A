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
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* 利用状況カード */}
      <Card className="border border-orange-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-orange-900">
            <Users className="h-5 w-5 text-orange-600" />
            <span>利用状況</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">現在の利用人数</span>
            <Badge variant="secondary" className="text-lg px-3 py-1 bg-orange-100 text-orange-800 border-orange-300">
              {mockStats.totalUsers} / {mockStats.maxUsers}人
            </Badge>
          </div>

          <div className="w-full bg-orange-200 rounded-full h-2">
            <div
              className="bg-orange-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${usagePercentage}%` }}
            />
          </div>

          <div className="text-sm text-gray-600">利用率: {usagePercentage.toFixed(1)}%</div>
        </CardContent>
      </Card>

      {/* 収益情報カード */}
      <Card className="border border-orange-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-orange-900">
            <CreditCard className="h-5 w-5 text-orange-600" />
            <span>収益情報</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">月間収益</span>
            <span className="text-2xl font-bold text-orange-600">¥{mockStats.monthlyRevenue.toLocaleString()}</span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">アクティブユーザー</span>
            <Badge variant="default" className="bg-orange-500 text-white">{mockStats.activeUsers}人</Badge>
          </div>
        </CardContent>
      </Card>

      {/* 注意事項カード */}
      <Card className="border-l-4 border-orange-500 border border-orange-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-orange-500" />
            <span className="text-orange-900">注意事項</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockStats.pendingPayments > 0 && (
              <div className="flex items-start space-x-2 p-3 bg-amber-50 rounded-lg border border-amber-200">
                <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="text-sm font-medium text-amber-800">未処理決済</span>
                  <p className="text-sm text-amber-700">{mockStats.pendingPayments}件の未処理決済があります</p>
                </div>
              </div>
            )}

            {usagePercentage > 80 && (
              <div className="flex items-start space-x-2 p-3 bg-orange-50 rounded-lg border border-orange-200">
                <TrendingUp className="h-4 w-4 text-orange-600 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="text-sm font-medium text-orange-800">利用率高</span>
                  <p className="text-sm text-orange-700">利用率が80%を超えています</p>
                </div>
              </div>
            )}

            {mockStats.pendingPayments === 0 && usagePercentage <= 80 && (
              <div className="flex items-center space-x-2 text-orange-600">
                <div className="h-2 w-2 bg-orange-600 rounded-full"></div>
                <span className="text-sm">システムは正常に稼働中です</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}