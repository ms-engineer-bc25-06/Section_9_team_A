// REVIEW: 支払い方法登録・変更フォーム仮実装 （るい）
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Badge } from "@/components/ui/Badge"
import { CreditCard, Plus, Edit, Trash2, Check } from "lucide-react"

interface PaymentMethod {
  id: string
  type: "card" | "bank"
  last4: string
  brand: string
  expiryMonth: number
  expiryYear: number
  isDefault: boolean
}

export function PaymentMethod() {
  const [paymentMethods] = useState<PaymentMethod[]>([
    {
      id: "1",
      type: "card",
      last4: "4242",
      brand: "Visa",
      expiryMonth: 12,
      expiryYear: 2025,
      isDefault: true
    }
  ])

  const [showAddForm, setShowAddForm] = useState(false)

  const getCardIcon = (brand: string) => {
    switch (brand.toLowerCase()) {
      case "visa":
        return "💳"
      case "mastercard":
        return "💳"
      case "amex":
        return "💳"
      default:
        return "💳"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center space-x-2">
            <CreditCard className="h-5 w-5" />
            支払い方法
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            <Plus className="h-4 w-4 mr-1" />
            追加
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* 既存の支払い方法 */}
          {paymentMethods.map((method) => (
            <div
              key={method.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <div className="text-2xl">{getCardIcon(method.brand)}</div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">
                      {method.brand} •••• {method.last4}
                    </span>
                    {method.isDefault && (
                      <Badge variant="default">デフォルト</Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">
                    有効期限: {method.expiryMonth}/{method.expiryYear}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">
                  <Edit className="h-4 w-4 mr-1" />
                  編集
                </Button>
                <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                  <Trash2 className="h-4 w-4 mr-1" />
                  削除
                </Button>
              </div>
            </div>
          ))}

          {/* 新規追加フォーム */}
          {showAddForm && (
            <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
              <h4 className="font-medium mb-4">新しい支払い方法を追加</h4>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="cardNumber">カード番号</Label>
                  <Input
                    id="cardNumber"
                    placeholder="1234 5678 9012 3456"
                    className="mt-1"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="expiryMonth">有効期限（月）</Label>
                    <Input
                      id="expiryMonth"
                      placeholder="12"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="expiryYear">有効期限（年）</Label>
                    <Input
                      id="expiryYear"
                      placeholder="2025"
                      className="mt-1"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="cvv">CVV</Label>
                  <Input
                    id="cvv"
                    placeholder="123"
                    className="mt-1"
                  />
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowAddForm(false)}
                  >
                    キャンセル
                  </Button>
                  <Button>
                    <Check className="h-4 w-4 mr-1" />
                    追加
                  </Button>
                </div>
              </div>
            </div>
          )}

          {paymentMethods.length === 0 && !showAddForm && (
            <div className="text-center py-8">
              <p className="text-gray-500">登録された支払い方法がありません</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}