// 管理者用決済アクションコンポーネント
"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Badge } from "@/components/ui/Badge"
import { CreditCard, Plus, AlertTriangle, CheckCircle } from "lucide-react"
import { AdminStripeCheckout } from "./AdminStripeCheckout"

interface AdminBillingActionsProps {
  userCount: number
  additionalUsers: number
  additionalCost: number
  onRefresh: () => void
}

export function AdminBillingActions({
  userCount,
  additionalUsers,
  additionalCost,
  onRefresh
}: AdminBillingActionsProps) {
  const [showCheckout, setShowCheckout] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [paymentSuccess, setPaymentSuccess] = useState(false)

  const handlePaymentClick = () => {
    if (additionalUsers > 0) {
      setShowCheckout(true)
    }
  }

  const handlePaymentSuccess = async (paymentIntentId: string) => {
    setPaymentSuccess(true)
    setShowCheckout(false)
    setIsProcessing(false)
    
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 決済アクション */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CreditCard className="h-5 w-5 text-blue-600" />
              <span>決済処理</span>
            </CardTitle>
            <CardDescription>超過分の料金を決済します</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {additionalUsers > 0 ? (
              <>
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    <span className="font-medium text-orange-800">決済が必要です</span>
                  </div>
                  <div className="text-sm text-orange-700">
                    {additionalUsers}人分の追加料金（¥{additionalCost.toLocaleString()}）が発生しています
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-sm">
                    <span>超過人数:</span>
                    <Badge variant="destructive">{additionalUsers}人</Badge>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span>単価:</span>
                    <span>¥500/人/月</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span>合計金額:</span>
                    <span className="font-bold text-lg text-orange-600">
                      ¥{additionalCost.toLocaleString()}
                    </span>
                  </div>
                </div>
                
                <Button 
                  onClick={handlePaymentClick}
                  disabled={isProcessing}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {isProcessing ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>処理中...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <CreditCard className="h-4 w-4" />
                      <span>決済を実行する</span>
                    </div>
                  )}
                </Button>
              </>
            ) : (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
                <div className="font-medium text-green-800 mb-1">決済は不要です</div>
                <div className="text-sm text-green-700">
                  現在の利用者数は無料枠内です
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* ユーザー管理アクション */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Plus className="h-5 w-5 text-green-600" />
              <span>ユーザー管理</span>
            </CardTitle>
            <CardDescription>ユーザーの追加・管理を行います</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span>現在の利用者:</span>
                <Badge variant="outline">{userCount}人</Badge>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span>無料枠:</span>
                <span>10人まで</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span>残り枠:</span>
                <Badge variant={userCount < 10 ? "secondary" : "destructive"}>
                  {Math.max(0, 10 - userCount)}人
                </Badge>
              </div>
            </div>
            
            <div className="space-y-2">
              <Button 
                onClick={handleAddUsers}
                variant="outline"
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                ユーザーを追加
              </Button>
              
              <Button 
                onClick={onRefresh}
                variant="ghost"
                className="w-full"
              >
                情報を更新
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Stripe決済フォーム */}
      {showCheckout && (
        <AdminStripeCheckout
          amount={additionalCost}
          additionalUsers={additionalUsers}
          onSuccess={handlePaymentSuccess}
          onError={handlePaymentError}
          onCancel={handlePaymentCancel}
        />
      )}
    </div>
  )
}
