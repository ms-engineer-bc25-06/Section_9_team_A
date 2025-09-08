"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { CreditCard, Loader2 } from "lucide-react"

interface StripeCheckoutProps {
  amount: number
  currency: string
  description: string
  onSuccess: (paymentIntentId: string) => void
  onError: (error: string) => void
  disabled?: boolean
}

export function StripeCheckout({
  amount,
  currency,
  description,
  onSuccess,
  onError,
  disabled = false
}: StripeCheckoutProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handlePayment = async () => {
    setLoading(true)
    setError(null)

    try {
      // Step 1: バックエンドでStripe Checkoutセッションを作成
      const response = await fetch('/api/admin/billing/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          amount,
          currency,
          description,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create checkout session')
      }

      const { checkout_url, session_id } = await response.json()

      // Step 2: Stripe Checkoutページにリダイレクト
      window.location.href = checkout_url

      // TODO: 実際の決済完了はwebhookとsuccess pageで処理
    } catch (err) {
      console.error('Payment error:', err)
      const errorMessage = err instanceof Error ? err.message : '決済処理でエラーが発生しました'
      setError(errorMessage)
      onError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* エラー表示 */}
      {error && (
        <Alert>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 決済内容の表示 */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-2">
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">サービス</span>
          <span className="text-sm">{description}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">金額</span>
          <span className="text-sm font-semibold">
            ¥{amount.toLocaleString()} {currency.toUpperCase()}
          </span>
        </div>
      </div>

      {/* 決済ボタン */}
      <Button
        onClick={handlePayment}
        disabled={disabled || loading}
        className="w-full"
        size="lg"
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            処理中...
          </>
        ) : (
          <>
            <CreditCard className="mr-2 h-4 w-4" />
            Stripeで決済する
          </>
        )}
      </Button>

      {/* 注意事項 */}
      <div className="text-xs text-gray-500 text-center">
        <p>• 決済はStripeの安全なサーバーで処理されます</p>
        <p>• クレジットカード情報は当サイトに保存されません</p>
        <p>• 決済完了後、すぐにサービスが利用可能になります</p>
      </div>
    </div>
  )
}