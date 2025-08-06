// TODO この機能は将来的に実装する(管理者が新しいユーザーを追加するフォーム)
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Badge } from "@/components/ui/Badge"
import { Separator } from "@/components/ui/Separator"
import { Users, CreditCard, Calculator, CheckCircle, AlertCircle } from "lucide-react"
import { useRouter } from "next/navigation"

const PRICE_PER_USER = 500
const currentUsers = 25
const maxUsers = 30

export function AddUsersForm() {
  const [additionalUsers, setAdditionalUsers] = useState(1)
  const [isProcessing, setIsProcessing] = useState(false)
  const [paymentSuccess, setPaymentSuccess] = useState(false)
  const router = useRouter()

  const totalCost = additionalUsers * PRICE_PER_USER
  const newTotalUsers = currentUsers + additionalUsers
  const availableSlots = maxUsers - currentUsers

  const handlePayment = async () => {
    setIsProcessing(true)

    // Stripe決済処理のシミュレーション
    setTimeout(() => {
      setIsProcessing(false)
      setPaymentSuccess(true)

      // 3秒後に決済管理画面に戻る
      setTimeout(() => {
        router.push("/admin/billing")
      }, 3000)
    }, 2000)
  }

  const handleUserCountChange = (value: string) => {
    const num = Number.parseInt(value) || 0
    if (num >= 1 && num <= availableSlots) {
      setAdditionalUsers(num)
    }
  }

  if (paymentSuccess) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card className="border-green-200 bg-green-50">
          <CardContent className="p-8 text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-green-800 mb-2">決済完了</h2>
            <p className="text-green-700 mb-4">{additionalUsers}人分のユーザー枠追加が完了しました。</p>
            <Badge variant="default" className="bg-green-500 text-lg px-4 py-2">
              ¥{totalCost.toLocaleString()} 決済完了
            </Badge>
            <p className="text-sm text-green-600 mt-4">3秒後に決済管理画面に戻ります...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* 現在の状況 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>現在の利用状況</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{currentUsers}</div>
              <div className="text-sm text-gray-600">現在の利用人数</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-600">{maxUsers}</div>
              <div className="text-sm text-gray-600">最大利用人数</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{availableSlots}</div>
              <div className="text-sm text-gray-600">追加可能人数</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 追加人数選択 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calculator className="h-5 w-5" />
            <span>追加人数の選択</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="additional-users">追加したい人数</Label>
            <Input
              id="additional-users"
              type="number"
              min="1"
              max={availableSlots}
              value={additionalUsers}
              onChange={(e) => handleUserCountChange(e.target.value)}
              className="text-lg font-semibold"
            />
            <div className="text-sm text-gray-600">最大 {availableSlots} 人まで追加可能です</div>
          </div>

          {availableSlots === 0 && (
            <div className="flex items-center space-x-2 text-orange-600 bg-orange-50 p-3 rounded-lg">
              <AlertCircle className="h-5 w-5" />
              <span>現在、追加可能な人数枠がありません。</span>
            </div>
          )}

          <div className="flex justify-between items-center">
            <span className="text-lg">1人あたりの料金:</span>
            <Badge variant="secondary" className="text-lg px-3 py-1">
              ¥{PRICE_PER_USER}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* 料金計算 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CreditCard className="h-5 w-5" />
            <span>決済内容</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex justify-between">
              <span>追加人数:</span>
              <span className="font-semibold">{additionalUsers} 人</span>
            </div>
            <div className="flex justify-between">
              <span>単価:</span>
              <span>¥{PRICE_PER_USER} / 人</span>
            </div>
            <Separator />
            <div className="flex justify-between text-lg font-bold">
              <span>合計金額:</span>
              <span className="text-green-600">¥{totalCost.toLocaleString()}</span>
            </div>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-2">決済後の状況</h4>
            <div className="text-sm text-blue-700">
              <div>
                利用人数: {currentUsers} 人 → {newTotalUsers} 人
              </div>
              <div>
                月額料金: ¥{(currentUsers * PRICE_PER_USER).toLocaleString()} → ¥
                {(newTotalUsers * PRICE_PER_USER).toLocaleString()}
              </div>
            </div>
          </div>

          <Button
            onClick={handlePayment}
            className="w-full bg-green-600 hover:bg-green-700 text-lg py-3"
            disabled={isProcessing || availableSlots === 0}
          >
            <CreditCard className="h-5 w-5 mr-2" />
            {isProcessing ? "決済処理中..." : `¥${totalCost.toLocaleString()} で決済する`}
          </Button>

          <div className="text-xs text-gray-500 text-center">Stripe決済システムを使用して安全に決済されます</div>
        </CardContent>
      </Card>
    </div>
  )
}
