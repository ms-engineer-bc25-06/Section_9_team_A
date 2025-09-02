"use client"

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { CheckCircle, ArrowLeft, Download, CreditCard } from 'lucide-react'

interface PaymentSuccessData {
  session_id: string
  amount: number
  additional_users: number
  organization_id: string
}

function BillingSuccessPageContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [paymentData, setPaymentData] = useState<PaymentSuccessData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // URLパラメータから決済情報を取得
    const sessionId = searchParams.get('session_id')
    const amount = searchParams.get('amount')
    const additionalUsers = searchParams.get('additional_users')
    const organizationId = searchParams.get('organization_id')

    if (sessionId && amount && additionalUsers && organizationId) {
      setPaymentData({
        session_id: sessionId,
        amount: parseInt(amount),
        additional_users: parseInt(additionalUsers),
        organization_id: organizationId
      })
    }
    setIsLoading(false)
  }, [searchParams])

  const handleBackToBilling = () => {
    router.push('/admin/billing')
  }

  const handleDownloadReceipt = () => {
    // 実際の実装では、Stripeからレシートをダウンロード
    alert('レシートのダウンロード機能は準備中です')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">決済結果を確認中...</p>
        </div>
      </div>
    )
  }

  if (!paymentData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="h-8 w-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">決済情報が見つかりません</h2>
          <p className="text-gray-600 mb-6">URLパラメータが正しく設定されていません</p>
          <Button onClick={handleBackToBilling} variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            決済画面に戻る
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-2xl">
        {/* 成功メッセージ */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="h-10 w-10 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">決済完了</h1>
          <p className="text-lg text-gray-600">お支払いが正常に完了しました</p>
        </div>

        {/* 決済詳細 */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              決済詳細
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">決済セッションID</p>
                <p className="font-mono text-sm">{paymentData.session_id}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">組織ID</p>
                <p className="font-mono text-sm">{paymentData.organization_id}</p>
              </div>
            </div>
            
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <span className="text-blue-900">追加ユーザー数</span>
                <Badge variant="secondary" className="text-blue-700">
                  +{paymentData.additional_users}人
                </Badge>
              </div>
            </div>
            
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <span className="text-green-900">決済金額</span>
                <span className="text-2xl font-bold text-green-700">
                  ¥{paymentData.amount.toLocaleString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 次のステップ */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>次のステップ</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 text-sm font-semibold">1</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">ユーザー枠の更新</p>
                  <p className="text-sm text-gray-600">追加されたユーザー枠が即座に利用可能になります</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 text-sm font-semibold">2</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">請求書の送付</p>
                  <p className="text-sm text-gray-600">決済完了後、24時間以内にメールで請求書が送付されます</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 text-sm font-semibold">3</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">ユーザー追加</p>
                  <p className="text-sm text-gray-600">追加されたユーザー枠を使用して新しいメンバーを追加できます</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* アクションボタン */}
        <div className="flex flex-col sm:flex-row gap-4">
          <Button onClick={handleBackToBilling} className="flex-1">
            <ArrowLeft className="h-4 w-4 mr-2" />
            決済画面に戻る
          </Button>
          
          <Button onClick={handleDownloadReceipt} variant="outline" className="flex-1">
            <Download className="h-4 w-4 mr-2" />
            レシートをダウンロード
          </Button>
        </div>

        {/* 注意事項 */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>決済に関するご質問がございましたら、サポートまでお問い合わせください</p>
          <p className="mt-1">サポート: support@example.com</p>
        </div>
      </div>
    </div>
  )
}

export default function BillingSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    }>
      <BillingSuccessPageContent />
    </Suspense>
  )
}
