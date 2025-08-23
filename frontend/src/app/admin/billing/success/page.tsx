"use client"

import { useState, useEffect, Suspense } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { 
  CheckCircle, 
  Users, 
  CreditCard, 
  ArrowRight, 
  Calendar,
  TrendingUp,
  ArrowLeft
} from "lucide-react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"

interface PaymentSuccessData {
  sessionId: string
  amount: number
  additionalUsers: number
  organizationId: number
  paymentDate: string
  nextBillingDate: string
}

function PaymentSuccessContent() {
  const searchParams = useSearchParams()
  const [paymentData, setPaymentData] = useState<PaymentSuccessData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // URLパラメータから決済情報を取得
    const sessionId = searchParams.get('session_id')
    const amount = searchParams.get('amount')
    const additionalUsers = searchParams.get('additional_users')
    const organizationId = searchParams.get('organization_id')

    if (sessionId && amount && additionalUsers && organizationId) {
      // 実際の実装では、セッションIDを使ってバックエンドから詳細情報を取得
      const mockData: PaymentSuccessData = {
        sessionId,
        amount: parseInt(amount),
        additionalUsers: parseInt(additionalUsers),
        organizationId: parseInt(organizationId),
        paymentDate: new Date().toLocaleDateString('ja-JP'),
        nextBillingDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString('ja-JP')
      }
      setPaymentData(mockData)
    }
    setIsLoading(false)
  }, [searchParams])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">決済情報を確認中...</p>
        </div>
      </div>
    )
  }

  if (error || !paymentData) {
    return (
      <div className="min-h-screen bg-slate-50">
        <div className="container mx-auto px-4 py-8">
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">
              決済情報の取得に失敗しました。管理者にお問い合わせください。
            </AlertDescription>
          </Alert>
          <Link href="/admin/billing">
            <Button variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              決済管理に戻る
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/admin/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                ダッシュボードに戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">決済完了</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* 成功メッセージ */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
            <CheckCircle className="h-10 w-10 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">決済が完了しました！</h1>
          <p className="text-gray-600 text-lg">
            ユーザー追加の決済が正常に完了しました
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* 決済詳細 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CreditCard className="h-5 w-5 text-blue-600" />
                <span>決済詳細</span>
              </CardTitle>
              <CardDescription>今回の決済に関する詳細情報</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">決済ID</span>
                <Badge variant="outline" className="font-mono">
                  {paymentData.sessionId.slice(0, 8)}...
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">決済金額</span>
                <span className="font-bold text-lg text-blue-600">
                  ¥{paymentData.amount.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">追加ユーザー数</span>
                <Badge variant="default" className="bg-green-600">
                  +{paymentData.additionalUsers}人
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">決済日</span>
                <span className="font-medium">{paymentData.paymentDate}</span>
              </div>
            </CardContent>
          </Card>

          {/* ユーザー追加状況 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-green-600" />
                <span>ユーザー追加状況</span>
              </CardTitle>
              <CardDescription>追加されたユーザーの反映状況</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="font-medium text-green-800">追加処理完了</span>
                </div>
                <div className="text-sm text-green-700">
                  {paymentData.additionalUsers}人のユーザーが正常に追加されました
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span>追加ユーザー数:</span>
                  <Badge variant="default" className="bg-green-600">
                    {paymentData.additionalUsers}人
                  </Badge>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span>反映状況:</span>
                  <Badge variant="default" className="bg-green-600">
                    完了
                  </Badge>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span>次回請求:</span>
                  <span className="font-medium">{paymentData.nextBillingDate}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 次のステップ */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-purple-600" />
              <span>次のステップ</span>
            </CardTitle>
            <CardDescription>決済完了後の推奨アクション</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 text-sm font-bold">1</span>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">ユーザー管理の確認</h4>
                  <p className="text-sm text-gray-600">
                    追加されたユーザーが正しくシステムに反映されているか確認してください
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 text-sm font-bold">2</span>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">利用状況の監視</h4>
                  <p className="text-sm text-gray-600">
                    定期的に利用状況・課金管理画面でユーザー数と料金を確認してください
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 text-sm font-bold">3</span>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">次回請求の準備</h4>
                  <p className="text-sm text-gray-600">
                    次回の請求日（{paymentData.nextBillingDate}）に向けて、必要に応じて追加のユーザー追加を検討してください
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* アクションボタン */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/admin/billing">
            <Button variant="outline" size="lg">
              <ArrowLeft className="h-4 w-4 mr-2" />
              決済管理に戻る
            </Button>
          </Link>
          
          <Link href="/admin/users">
            <Button 
              size="lg" 
              className="bg-blue-600 hover:bg-blue-700"
              onClick={() => {
                // 決済完了フラグを設定
                sessionStorage.setItem('paymentCompleted', 'true')
              }}
            >
              ユーザー管理を確認
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Link>
          
          <Link href="/admin/dashboard">
            <Button variant="ghost" size="lg">
              ダッシュボードに戻る
            </Button>
          </Link>
        </div>
      </main>
    </div>
  )
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    }>
      <PaymentSuccessContent />
    </Suspense>
  )
}
