"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Users, CreditCard, AlertTriangle, CheckCircle, DollarSign, ArrowLeft } from "lucide-react"
import { AdminBillingOverview } from "@/components/admin/AdminBillingOverview"
import { AdminBillingActions } from "@/components/admin/AdminBillingActions"
import Link from "next/link"
import { getAuth, onAuthStateChanged } from "firebase/auth"
import { apiClient } from "@/lib/apiClient"
import { PlanService } from "@/services/planService"

export default function AdminBillingPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [userCount, setUserCount] = useState(0)
  const [isLoadingData, setIsLoadingData] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // 認証チェック
  useEffect(() => {
    if (!user && !isLoading) {
      router.push("/admin/login")
    }
  }, [user, isLoading, router])

  useEffect(() => {
    if (!user) return
    
    if (process.env.NODE_ENV === 'development') {
      const auth = getAuth()
      console.log('現在の認証状態:', auth.currentUser ? 'ログイン済み' : '未ログイン')
    }
    
    fetchUserCount()
    
    // 定期的にユーザー数を更新（5分ごと）
    const interval = setInterval(fetchUserCount, 5 * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [user])

  const fetchUserCount = async () => {
    try {
      setIsLoadingData(true)
      
      const data = await apiClient.get('/admin/billing/user-count')
      setUserCount(data.total_users)
    } catch (err) {
      console.error('ユーザー数取得エラー:', err)

      if (process.env.NODE_ENV === 'development') {
        const mockUserCount = 15
        setUserCount(mockUserCount)
        setError(null)
      } else {
        setError(err instanceof Error ? err.message : 'エラーが発生しました')
      }
    } finally {
      setIsLoadingData(false)
    }
  }

  const currentPlan = PlanService.getCurrentPlanByUserCount(userCount)
  const planInfo = PlanService.getPlanDisplayInfo(currentPlan)
  const maxUsers = planInfo.maxUsers === '無制限' ? 999999 : parseInt(planInfo.maxUsers.replace('名', ''))
  
  const isFreeTier = userCount <= maxUsers
  const overLimit = userCount > maxUsers
  const additionalUsers = Math.max(0, userCount - maxUsers)
  const additionalCost = 0

  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-gradient-to-br from-orange-50 to-amber-50 shadow-sm border-b border-orange-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/admin/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                ダッシュボードに戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-orange-900 flex-1 text-center">決済・利用状況</h1>
            <div className="w-32"></div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">

        {error && (
          <Alert className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {successMessage && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">{successMessage}</AlertDescription>
          </Alert>
        )}

        {/* 情報更新ボタン */}
        <div className="mb-6 flex justify-end">
          <Button 
            onClick={fetchUserCount} 
            variant="outline" 
            disabled={isLoadingData}
            className="flex items-center space-x-2"
          >
            {isLoadingData ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span>更新中...</span>
              </>
            ) : (
              <>
                <div className="w-4 h-4">🔄</div>
                <span>情報を更新</span>
              </>
            )}
          </Button>
        </div>

        {/* 詳細情報 */}
        <AdminBillingOverview 
          userCount={userCount}
          isFreeTier={isFreeTier}
          additionalUsers={additionalUsers}
          additionalCost={additionalCost}
          currentPlan={currentPlan}
        />

        {/* 決済情報 */}
        <div className="mt-12">
          <AdminBillingActions 
            userCount={userCount}
            additionalUsers={additionalUsers}
            additionalCost={additionalCost}
            onRefresh={fetchUserCount}
            currentPlan={currentPlan}
          />
        </div>

      </div>
    </div>
  )
}