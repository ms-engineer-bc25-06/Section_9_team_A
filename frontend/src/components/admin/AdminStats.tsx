// 統計情報表示部品
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Users, CreditCard, TrendingUp, AlertCircle } from "lucide-react"
import { apiClient } from "@/lib/apiClient"

interface SystemStats {
  totalUsers: number
  maxUsers: number
  monthlyRevenue: number
  activeUsers: number
  pendingPayments: number
}

export function AdminStats() {
  const [stats, setStats] = useState<SystemStats>({
    totalUsers: 0,
    maxUsers: 10, // 無料枠
    monthlyRevenue: 0,
    activeUsers: 0,
    pendingPayments: 0
  })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSystemStats()
  }, [])

  const fetchSystemStats = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // ユーザー数を取得
      const userCountData = await apiClient.get('/admin/billing/user-count')

      // データを組み合わせて統計情報を作成
      const totalUsers = userCountData.total_users || 0
      const maxUsers = 10 // 無料枠
      const monthlyRevenue = userCountData.total_additional_cost || 0
      const activeUsers = totalUsers // 現在は全ユーザーをアクティブとして扱う
      const pendingPayments = 0 // 現在は未実装

      setStats({
        totalUsers,
        maxUsers,
        monthlyRevenue,
        activeUsers,
        pendingPayments
      })

    } catch (err) {
      console.error('システム統計の取得でエラー:', err)
      setError('システム統計の取得に失敗しました')
      
      // エラー時はデフォルト値を設定
      setStats({
        totalUsers: 0,
        maxUsers: 10,
        monthlyRevenue: 0,
        activeUsers: 0,
        pendingPayments: 0
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="border border-orange-200">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-orange-900">
                <div className="h-5 w-5 bg-orange-200 rounded animate-pulse"></div>
                <div className="h-5 w-20 bg-orange-200 rounded animate-pulse"></div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="h-4 bg-orange-100 rounded animate-pulse"></div>
                <div className="h-6 bg-orange-100 rounded animate-pulse"></div>
                <div className="h-4 bg-orange-100 rounded animate-pulse"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 mb-4">{error}</div>
        <button 
          onClick={fetchSystemStats}
          className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700"
        >
          再試行
        </button>
      </div>
    )
  }

  const usagePercentage = (stats.totalUsers / stats.maxUsers) * 100

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
              {stats.totalUsers} / {stats.maxUsers}人
            </Badge>
          </div>

          <div className="w-full bg-orange-200 rounded-full h-2">
            <div
              className="bg-orange-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(100, usagePercentage)}%` }}
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
            <span>請求情報</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">月間請求額</span>
            <span className="text-2xl font-bold text-orange-600">¥{stats.monthlyRevenue.toLocaleString()}</span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">アクティブユーザー</span>
            <Badge variant="default" className="bg-orange-500 text-white">{stats.activeUsers}人</Badge>
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
            {stats.monthlyRevenue > 0 && (
              <div className="flex items-start space-x-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <CreditCard className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="text-sm font-medium text-blue-800">お支払いがあります</span>
                  <p className="text-sm text-blue-700">月間請求額: ¥{stats.monthlyRevenue.toLocaleString()}</p>
                </div>
              </div>
            )}

            {stats.pendingPayments > 0 && (
              <div className="flex items-start space-x-2 p-3 bg-amber-50 rounded-lg border border-amber-200">
                <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="text-sm font-medium text-amber-800">未処理決済</span>
                  <p className="text-sm text-amber-700">{stats.pendingPayments}件の未処理決済があります</p>
                </div>
              </div>
            )}

            {usagePercentage >= 100 && (
              <div className="flex items-start space-x-2 p-3 bg-red-50 rounded-lg border border-red-200">
                <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="text-sm font-medium text-red-800">利用率上限到達</span>
                  <p className="text-sm text-red-700">利用率が100%に達しています。新規ユーザーの追加には追加料金が発生します。</p>
                </div>
              </div>
            )}

            {usagePercentage > 80 && usagePercentage < 100 && (
              <div className="flex items-start space-x-2 p-3 bg-orange-50 rounded-lg border border-orange-200">
                <TrendingUp className="h-4 w-4 text-orange-600 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="text-sm font-medium text-orange-800">利用率高</span>
                  <p className="text-sm text-orange-700">利用率が80%を超えています</p>
                </div>
              </div>
            )}

            {stats.monthlyRevenue === 0 && stats.pendingPayments === 0 && usagePercentage <= 80 && (
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