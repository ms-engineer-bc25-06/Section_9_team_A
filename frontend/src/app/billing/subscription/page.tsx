// 決済処理とStripe連携
"use client"

import { useState, useEffect, Suspense } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Badge } from "@/components/ui/Badge"
import { Users, CreditCard, ArrowLeft, CheckCircle, AlertCircle } from "lucide-react"
import { useRouter, useSearchParams } from "next/navigation"
import { StripeCheckout } from "@/components/billing/StripeCheckout"

interface SubscriptionDetails {
  additionalUsers: number
  cost: number
  returnUrl: string
  currentUsers: number
  newTotal: number
}

function SubscriptionContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [subscriptionDetails, setSubscriptionDetails] = useState<SubscriptionDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    // URLパラメータから詳細を取得
    const additionalUsers = parseInt(searchParams.get('additionalUsers') || '0')
    const cost = parseInt(searchParams.get('cost') || '0')
    const returnUrl = searchParams.get('returnUrl') || '/admin/billing'
    
    if (additionalUsers > 0 && cost > 0) {
      // TODO: APIから現在のユーザー数を取得
      const currentUsers = 10 // 例: APIから取得
      
      setSubscriptionDetails({
        additionalUsers,
        cost,
        returnUrl,
        currentUsers,
        newTotal: currentUsers + additionalUsers
      })
    }
    setLoading(false)
  }, [searchParams])

  const handlePaymentSuccess = async (paymentIntentId: string) => {
    setProcessing(true)
    
    try {
      // TODO: バックエンドAPIでユーザー枠の更新
      const response = await fetch('/api/billing/update-subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          additionalUsers: subscriptionDetails?.additionalUsers,
          paymentIntentId,
        }),
      })

      if (response.ok) {
        // 成功ページにリダイレクト
        router.push(`/billing/success?users=${subscriptionDetails?.additionalUsers}&returnUrl=${subscriptionDetails?.returnUrl}`)
      } else {
        throw new Error('Failed to update subscription')
      }
    } catch (error) {
      console.error('Error updating subscription:', error)
      alert('決済は完了しましたが、ユーザー枠の更新でエラーが発生しました。サポートにお問い合わせください。')
    } finally {
      setProcessing(false)
    }
  }

  const handlePaymentError = (error: string) => {
    console.error('Payment error:', error)
    alert(`決済でエラーが発生しました: ${error}`)
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8 px-4 max-w-2xl">
        <div className="text-center">読み込み中...</div>
      </div>
    )
  }

  if (!subscriptionDetails) {
    return (
      <div className="container mx-auto py-8 px-4 max-w-2xl">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            無効なパラメータです。管理者ダッシュボードからやり直してください。
          </AlertDescription>
        </Alert>
        <Button 
          onClick={() => router.push('/admin/billing')} 
          className="mt-4"
        >
          管理者ダッシュボードに戻る
        </Button>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-2xl">
      {/* ヘッダー */}
      <div className="mb-8">
        <Button
          variant="ghost"
          onClick={() => router.back()}
          className="mb-4"
          disabled={processing}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          戻る
        </Button>
        <h1 className="text-3xl font-bold mb-2">ユーザー枠の追加</h1>
        <p className="text-gray-600">決済を完了して、使用可能な人数を増やします。</p>
      </div>

      {/* 注文内容の確認 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            注文内容
          </CardTitle>
          <CardDescription>
            以下の内容で決済を行います
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
            <span>追加ユーザー数</span>
            <Badge variant="secondary">
              +{subscriptionDetails.additionalUsers}人
            </Badge>
          </div>
          <div className="flex justify-between items-center">
            <span>現在の枠数</span>
            <span>{subscriptionDetails.currentUsers}人</span>
          </div>
          <div className="flex justify-between items-center">
            <span>追加後の総枠数</span>
            <span className="font-semibold">{subscriptionDetails.newTotal}人</span>
          </div>
          <hr />
          <div className="flex justify-between items-center text-lg">
            <span className="font-semibold">合計金額</span>
            <span className="font-bold text-blue-600">
              ¥{subscriptionDetails.cost.toLocaleString()}
            </span>
          </div>
          <div className="text-sm text-gray-600">
            ※ 料金は1人あたり¥500です（10人まで無料）
          </div>
        </CardContent>
      </Card>

      {/* 重要な注意事項 */}
      <Alert className="mb-6">
        <CheckCircle className="h-4 w-4" />
        <AlertDescription>
          <div className="space-y-2">
            <p><strong>決済について：</strong></p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>決済は安全なStripe経由で行われます</li>
              <li>決済完了後、すぐにユーザー枠が追加されます</li>
              <li>領収書は決済完了後にメールで送信されます</li>
              <li>月額課金ではなく、一回限りの支払いです</li>
            </ul>
          </div>
        </AlertDescription>
      </Alert>

      {/* Stripe決済コンポーネント */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            お支払い方法
          </CardTitle>
        </CardHeader>
        <CardContent>
          <StripeCheckout
            amount={subscriptionDetails.cost}
            currency="jpy"
            description={`ユーザー枠追加 (+${subscriptionDetails.additionalUsers}人)`}
            onSuccess={handlePaymentSuccess}
            onError={handlePaymentError}
            disabled={processing}
          />
          
          {processing && (
            <div className="mt-4 text-center">
              <div className="inline-flex items-center gap-2 text-blue-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                ユーザー枠を更新中...
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* セキュリティ表示 */}
      <div className="mt-6 text-center text-sm text-gray-500">
        <div className="flex items-center justify-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
            <CheckCircle className="h-3 w-3 text-white" />
          </div>
          SSL暗号化により安全に保護されています
        </div>
      </div>
    </div>
  )
}

export default function SubscriptionPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto py-8 px-4 max-w-2xl">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    }>
      <SubscriptionContent />
    </Suspense>
  )
}