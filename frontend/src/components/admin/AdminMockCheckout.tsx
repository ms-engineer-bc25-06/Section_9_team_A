"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Badge } from "@/components/ui/Badge"
import { CreditCard, X, AlertTriangle, Loader2, CheckCircle } from "lucide-react"

interface AdminMockCheckoutProps {
  amount: number
  additionalUsers: number
  onSuccess: (paymentIntentId: string) => void
  onError: (errorMessage: string) => void
  onCancel: () => void
}

export function AdminMockCheckout({
  amount,
  additionalUsers,
  onSuccess,
  onError,
  onCancel
}: AdminMockCheckoutProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [step, setStep] = useState<'input' | 'processing' | 'success'>('input')
  const [cardNumber, setCardNumber] = useState('')
  const [expiryDate, setExpiryDate] = useState('')
  const [cvv, setCvv] = useState('')
  const [cardholderName, setCardholderName] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // 基本的なバリデーション
    if (!cardNumber || !expiryDate || !cvv || !cardholderName) {
      setError("すべての項目を入力してください")
      return
    }

    if (cardNumber.length < 16) {
      setError("カード番号が正しくありません")
      return
    }

    setIsLoading(true)
    setError(null)
    setStep('processing')

    try {
      // モック決済処理（3秒待機）
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      // 成功確率90%（ランダム）
      const isSuccess = Math.random() > 0.1
      
      if (isSuccess) {
        setStep('success')
        
        // 成功メッセージを表示（2秒）
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // モック決済IDを生成
        const mockPaymentIntentId = `pi_mock_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        
        onSuccess(mockPaymentIntentId)
      } else {
        throw new Error('決済処理に失敗しました。カード情報を確認してください。')
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "決済処理中にエラーが発生しました"
      setError(errorMessage)
      onError(errorMessage)
      setStep('input')
    } finally {
      setIsLoading(false)
    }
  }

  const formatCardNumber = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '')
    const matches = v.match(/\d{4,16}/g)
    const match = matches && matches[0] || ''
    const parts = []
    
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4))
    }
    
    if (parts.length) {
      return parts.join(' ')
    } else {
      return v
    }
  }

  const formatExpiryDate = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '')
    if (v.length >= 2) {
      return v.substring(0, 2) + '/' + v.substring(2, 4)
    }
    return v
  }

  if (step === 'processing') {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg max-w-md w-full p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">決済処理中</h3>
          <p className="text-gray-600">決済を処理しています。しばらくお待ちください...</p>
        </div>
      </div>
    )
  }

  if (step === 'success') {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg max-w-md w-full p-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">決済完了</h3>
          <p className="text-gray-600">決済が正常に完了しました！</p>
        </div>
      </div>
    )
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
                  <span>モック決済手続き</span>
                </CardTitle>
                <CardDescription>
                  {additionalUsers}人分の追加料金を決済します（開発環境用）
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
            {/* 開発環境用の注意書き */}
            <Alert className="mb-6 border-yellow-200 bg-yellow-50">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <AlertDescription className="text-yellow-800">
                <strong>開発環境用:</strong> これはモック決済です。実際の決済は行われません。
              </AlertDescription>
            </Alert>

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

            {/* カード情報入力フォーム */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  カード番号
                </label>
                <input
                  type="text"
                  value={cardNumber}
                  onChange={(e) => setCardNumber(formatCardNumber(e.target.value))}
                  placeholder="1234 5678 9012 3456"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  maxLength={19}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    有効期限
                  </label>
                  <input
                    type="text"
                    value={expiryDate}
                    onChange={(e) => setExpiryDate(formatExpiryDate(e.target.value))}
                    placeholder="MM/YY"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    maxLength={5}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CVV
                  </label>
                  <input
                    type="text"
                    value={cvv}
                    onChange={(e) => setCvv(e.target.value.replace(/\D/g, ''))}
                    placeholder="123"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    maxLength={4}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  カード名義人
                </label>
                <input
                  type="text"
                  value={cardholderName}
                  onChange={(e) => setCardholderName(e.target.value)}
                  placeholder="TARO TANAKA"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* 決済ボタン */}
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
                    <span>¥{amount.toLocaleString()}を決済する（モック）</span>
                  </div>
                )}
              </Button>
            </form>

            {/* 注意事項 */}
            <div className="mt-6 text-xs text-gray-500 text-center">
              <p>この決済は開発環境用のモックです</p>
              <p>実際の決済は行われません</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
