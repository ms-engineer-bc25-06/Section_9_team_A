// 管理者用決済アクションコンポーネント
"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Badge } from "@/components/ui/Badge"
import { CreditCard, Plus, AlertTriangle, CheckCircle } from "lucide-react"
import { AdminStripeCheckout } from "./AdminStripeCheckout"
import { PlanService } from "@/services/planService"
// import { useToast } from "@/components/ui/use-toast"

interface AdminBillingActionsProps {
  userCount: number
  additionalUsers: number
  additionalCost: number
  onRefresh: () => void
  currentPlan?: string
}

export function AdminBillingActions({
  userCount,
  additionalUsers,
  additionalCost,
  onRefresh,
  currentPlan = 'premium'
}: AdminBillingActionsProps) {
  const planInfo = PlanService.getPlanDisplayInfo(currentPlan)
  const planUsage = PlanService.checkPlanUsage(userCount, currentPlan)
  const [showCheckout, setShowCheckout] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [paymentSuccess, setPaymentSuccess] = useState(false)
  // const { toast } = useToast()

  const handlePaymentClick = () => {
    setShowCheckout(true)
  }

  const handlePaymentSuccess = async (paymentIntentId: string) => {
    setPaymentSuccess(true)
    setShowCheckout(false)
    setIsProcessing(false)
    
    // TODO: 通知設定を実装（トースト通知を表示）
    // toast({
    //   title: "決済完了",
    //   description: "決済が正常に完了しました。ユーザーが追加されます。",
    //   variant: "success",
    // })
    
    // 成功メッセージを一定時間後に非表示
    setTimeout(() => {
      setPaymentSuccess(false)
    }, 5000)
    
    // データを再取得
    onRefresh()
    

  }

  const handlePaymentError = (errorMessage: string) => {
    console.error('Payment error:', errorMessage)
    setShowCheckout(false)
    setIsProcessing(false)
  }

  const handlePaymentCancel = () => {
    setShowCheckout(false)
    setIsProcessing(false)
  }

  const handleAddUsers = () => {
    // ユーザー追加ページへ移動
    window.location.href = '/admin/billing/add-users'
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">決済アクション</h2>
      
      {/* 成功メッセージ */}
      {paymentSuccess && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            <strong>決済完了:</strong> 決済が正常に完了しました。課金状態が更新されています。
          </AlertDescription>
        </Alert>
      )}

      <div className="max-w-2xl mx-auto">
        {/* 決済アクション */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CreditCard className="h-5 w-5 text-blue-600" />
              <span>決済処理</span>
            </CardTitle>
            <CardDescription>超過分の料金を決済します</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {planUsage.isOverLimit ? (
              <>
                {/* 決済警告 */}
                <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-6">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                      <AlertTriangle className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-orange-800 text-lg">プラン上限を超過しています</h3>
                      <p className="text-sm text-orange-700">
                        現在の利用者数が{planInfo.name}の上限を超えています
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* 料金詳細 */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h4 className="font-semibold text-gray-900 mb-4">料金詳細</h4>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <span className="text-gray-600">現在の利用者数</span>
                      <span className="font-semibold">{userCount}人</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <span className="text-gray-600">現在のプラン</span>
                      <span className="font-semibold">{planInfo.name}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <span className="text-gray-600">プラン料金</span>
                      <span className="font-semibold">¥{planInfo.monthlyPrice.toLocaleString()}/月</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <span className="text-gray-600">利用可能人数</span>
                      <span className="font-semibold">最大{planInfo.maxUsers}</span>
                    </div>
                    <div className="flex justify-between items-center py-3 bg-blue-50 rounded-lg px-3">
                      <span className="text-lg font-semibold text-blue-900">月額料金</span>
                      <span className="text-2xl font-bold text-blue-600">
                        ¥{planInfo.monthlyPrice.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* 決済ボタン */}
                <div className="space-y-4">
                  <Button 
                    onClick={handlePaymentClick}
                    disabled={isProcessing}
                    className="w-full bg-blue-600 hover:bg-blue-700 h-12 text-lg font-semibold text-white"
                  >
                    {isProcessing ? (
                      <div className="flex items-center space-x-3">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                        <span>決済処理中...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-3">
                        <CreditCard className="h-5 w-5" />
                        <span>¥{planInfo.monthlyPrice.toLocaleString()}を決済する</span>
                      </div>
                    )}
                  </Button>
                  

                </div>
              </>
            ) : (
              <>
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6 text-center mb-6">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold text-green-800 text-lg mb-2">プラン上限内です</h3>
                  <p className="text-green-700 text-sm">
                    現在の利用者数（{userCount}人）は{planInfo.name}の上限内です
                  </p>
                </div>
                
                {/* 決済ボタン */}
                <div className="space-y-4">
                  <Button 
                    onClick={handlePaymentClick}
                    disabled={isProcessing}
                    className="w-full bg-blue-600 hover:bg-blue-700 h-12 text-lg font-semibold text-white"
                  >
                    {isProcessing ? (
                      <div className="flex items-center space-x-3">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                        <span>決済処理中...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-3">
                        <CreditCard className="h-5 w-5" />
                        <span>¥{planInfo.monthlyPrice.toLocaleString()}を決済する</span>
                      </div>
                    )}
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>



      {/* 決済フォーム */}
      {showCheckout && (
        <AdminStripeCheckout
          amount={planInfo.monthlyPrice}
          additionalUsers={0}
          currentUserCount={userCount}
          onSuccess={handlePaymentSuccess}
          onError={handlePaymentError}
          onCancel={handlePaymentCancel}
        />
      )}
    </div>
  )
}
