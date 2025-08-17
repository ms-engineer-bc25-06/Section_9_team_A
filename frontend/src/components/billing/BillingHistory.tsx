// REVIEW: 請求履歴コンポーネント仮実装（るい）
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Download, Eye, Calendar, DollarSign } from "lucide-react"

interface BillingRecord {
  id: string
  date: string
  amount: number
  status: "paid" | "pending" | "failed"
  description: string
  invoiceNumber: string
}

export function BillingHistory() {
  const [billingRecords] = useState<BillingRecord[]>([
    {
      id: "1",
      date: "2024-01-15",
      amount: 2980,
      status: "paid",
      description: "Pro Plan - 1月分",
      invoiceNumber: "INV-2024-001"
    },
    {
      id: "2",
      date: "2023-12-15",
      amount: 2980,
      status: "paid",
      description: "Pro Plan - 12月分",
      invoiceNumber: "INV-2023-012"
    },
    {
      id: "3",
      date: "2023-11-15",
      amount: 2980,
      status: "paid",
      description: "Pro Plan - 11月分",
      invoiceNumber: "INV-2023-011"
    }
  ])

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "paid":
        return <Badge variant="default">支払い済み</Badge>
      case "pending":
        return <Badge variant="secondary">支払い待ち</Badge>
      case "failed":
        return <Badge variant="destructive">支払い失敗</Badge>
      default:
        return <Badge variant="outline">不明</Badge>
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY'
    }).format(amount)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Calendar className="h-5 w-5" />
          請求履歴
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {billingRecords.map((record) => (
            <div
              key={record.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
            >
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    <DollarSign className="h-4 w-4 text-gray-500" />
                    <span className="font-medium">{formatCurrency(record.amount)}</span>
                  </div>
                  {getStatusBadge(record.status)}
                </div>
                <p className="text-sm text-gray-600 mt-1">{record.description}</p>
                <p className="text-xs text-gray-500 mt-1">
                  請求書番号: {record.invoiceNumber}
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">
                  <Eye className="h-4 w-4 mr-1" />
                  詳細
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-1" />
                  ダウンロード
                </Button>
              </div>
            </div>
          ))}
          
          {billingRecords.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500">請求履歴がありません</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}