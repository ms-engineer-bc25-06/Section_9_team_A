// 管理者用Stripe決済フォームコンポーネント
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Badge } from "@/components/ui/Badge"
import { CreditCard, X, AlertTriangle, Loader2 } from "lucide-react"
import { loadStripe } from "@stripe/stripe-js"
import { getAuthToken } from "@/lib/apiClient"

interface AdminStripeCheckoutProps {
  amount: number
  additionalUsers: number
  onSuccess: (paymentIntentId: string) => void
  onError: (errorMessage: string) => void
  onCancel: () => void
}

export function AdminStripeCheckout({
  amount,
  additionalUsers,
  onSuccess,
  onError,
  onCancel
}: AdminStripeCheckoutProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stripe, setStripe] = useState<any>(null)

  useEffect(() => {
    // Stripe.jsを初期化
    const initStripe = async () => {
      const stripeInstance = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)
      setStripe(stripeInstance)
    }
    initStripe()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!stripe) {
      setError("Stripeが初期化されていません")
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      // バックエンドでCheckout Sessionを作成
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
      
      // 認証トークンを取得
      const authToken = await getAuthToken()
      
      // デバッグ用ログ
      console.log('送信する決済データ:', {
        amount,
        additionalUsers,
        organization_id: 1,
        currency: 'jpy'
      })
      
      const response = await fetch(`${apiBaseUrl}/api/v1/admin/billing/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          amount: amount, // 円単位のまま送信
          additional_users: additionalUsers,
          organization_id: 1, // TODO: 実際の組織IDを取得
          currency: 'jpy'
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        throw new Error(`Checkout Sessionの作成に失敗しました: ${errorMessage}`)
      }

      const { checkout_url } = await response.json()
      
      // Stripe Checkoutページにリダイレクト
      window.location.href = checkout_url
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "決済処理中にエラーが発生しました"
      setError(errorMessage)
      onError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }



  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="flex items-center space-x-2">
                  <CreditCard className="h-5 w-5 text-blue-600" />
                  <span>決済手続き</span>
                </CardTitle>
                <CardDescription>
                  {additionalUsers}人分の追加料金を決済します
                </CardDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onCancel}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          
          <CardContent>
            {/* 決済概要 */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">決済金額</span>
                <span className="text-2xl font-bold text-blue-600">
                  ¥{amount.toLocaleString()}
                </span>
              </div>
              <div className="text-sm text-gray-500">
                {additionalUsers}人 × ¥500/月
              </div>
            </div>

            {/* エラーメッセージ */}
            {error && (
              <Alert className="mb-6 border-red-200 bg-red-50">
                <AlertTriangle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">{error}</AlertDescription>
              </Alert>
            )}

            {/* 決済ボタン */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>決済処理中...</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <CreditCard className="h-4 w-4" />
                    <span>¥{amount.toLocaleString()}を決済する</span>
                  </div>
                )}
              </Button>
            </form>

            {/* 注意事項 */}
            <div className="mt-6 text-xs text-gray-500 text-center">
              <p>決済はStripeによって安全に処理されます</p>
              <p>カード情報は暗号化されて送信されます</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
