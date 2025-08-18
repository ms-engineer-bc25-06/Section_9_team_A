// 管理者用決済・サブスクリプション管理ページ
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Users, CreditCard, AlertTriangle, CheckCircle, DollarSign } from "lucide-react"
import { AdminBillingOverview } from "@/components/admin/AdminBillingOverview"
import { AdminBillingActions } from "@/components/admin/AdminBillingActions"
import Link from "next/link"

export default function AdminBillingPage() {
  const [userCount, setUserCount] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchUserCount()
  }, [])

  const fetchUserCount = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/admin/user-count')
      if (!response.ok) {
        throw new Error('ユーザー数の取得に失敗しました')
      }
      const data = await response.json()
      setUserCount(data.userCount)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました')
    } finally {
      setIsLoading(false)
    }
  }

  const isFreeTier = userCount <= 10
  const overLimit = userCount > 10
  const additionalUsers = Math.max(0, userCount - 10)
  const additionalCost = additionalUsers * 500

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

    return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">利用状況・課金管理</h1>
          <p className="text-gray-600">システムの利用状況と決済履歴を確認できます</p>
        </div>

        {error && (
          <Alert className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* アクションボタン */}
        <div className="mb-6">
          <Link href="/admin/users/add">
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Users className="h-4 w-4 mr-2" />
              ユーザーを追加
            </Button>
          </Link>
        </div>

        {/* 現在の状況サマリー */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-600" />
                <span>現在の利用者数</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600 mb-2">{userCount}人</div>
              <div className="flex items-center space-x-2">
                {isFreeTier ? (
                  <>
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600">無料枠内</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    <span className="text-sm text-orange-600">無料枠超過</span>
                  </>
                )}
        </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center space-x-2">
                <CreditCard className="h-5 w-5 text-purple-600" />
                <span>料金プラン</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {isFreeTier ? '無料' : `¥${additionalCost.toLocaleString()}`}
      </div>
              <div className="text-sm text-gray-600">
                {isFreeTier 
                  ? `${10 - userCount}人分の余裕があります`
                  : `${additionalUsers}人分の追加料金`
                }
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center space-x-2">
                <DollarSign className="h-5 w-5 text-green-600" />
                <span>料金体系</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>10人まで:</span>
                  <span className="font-medium">無料</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>11人以降:</span>
                  <span className="font-medium">1人500円/月</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 課金アラート */}
        {overLimit && (
          <Alert className="mb-6 border-orange-200 bg-orange-50">
            <AlertTriangle className="h-4 w-4 text-orange-600" />
            <AlertDescription className="text-orange-800">
              <strong>注意:</strong> 現在{userCount}人の利用者がおり、無料枠（10人）を{additionalUsers}人超過しています。
              追加料金¥{additionalCost.toLocaleString()}が発生しています。
            </AlertDescription>
          </Alert>
        )}

        {/* 決済アクション */}
        <AdminBillingActions 
          userCount={userCount}
          additionalUsers={additionalUsers}
          additionalCost={additionalCost}
          onRefresh={fetchUserCount}
        />

        {/* 詳細情報 */}
        <AdminBillingOverview 
          userCount={userCount}
          isFreeTier={isFreeTier}
          additionalUsers={additionalUsers}
          additionalCost={additionalCost}
        />
      </div>
    </div>
  )
}