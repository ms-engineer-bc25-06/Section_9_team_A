// 課金状況の概要表示
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table"
import { CreditCard, Users, TrendingUp, Calendar, Plus } from "lucide-react"
import { useRouter } from "next/navigation"

const mockBillingData = {
  currentPlan: {
    name: "エンタープライズプラン",
    maxUsers: 30,
    currentUsers: 25,
    pricePerUser: 500,
    monthlyTotal: 15000,
  },
  recentTransactions: [
    {
      id: "tx_001",
      date: "2024-01-15",
      description: "ユーザー枠追加（5人）",
      amount: 2500,
      status: "completed",
    },
    {
      id: "tx_002",
      date: "2024-01-01",
      description: "月額利用料（25人）",
      amount: 12500,
      status: "completed",
    },
    {
      id: "tx_003",
      date: "2023-12-15",
      description: "ユーザー枠追加（3人）",
      amount: 1500,
      status: "completed",
    },
  ],
}

export function AdminBillingOverview() {
  const router = useRouter()

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <Badge variant="default" className="bg-green-500">
            完了
          </Badge>
        )
      case "pending":
        return <Badge variant="secondary">処理中</Badge>
      case "failed":
        return <Badge variant="destructive">失敗</Badge>
      default:
        return <Badge variant="secondary">不明</Badge>
    }
  }

  return (
    <div className="space-y-8">
      {/* 現在のプラン情報 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-500" />
              <span>利用人数</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">{mockBillingData.currentPlan.currentUsers}</div>
            <div className="text-sm text-gray-600">最大 {mockBillingData.currentPlan.maxUsers} 人まで</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2">
              <CreditCard className="h-5 w-5 text-green-500" />
              <span>月額料金</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              ¥{mockBillingData.currentPlan.monthlyTotal.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">1人あたり ¥{mockBillingData.currentPlan.pricePerUser}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-purple-500" />
              <span>利用率</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">
              {((mockBillingData.currentPlan.currentUsers / mockBillingData.currentPlan.maxUsers) * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">
              残り {mockBillingData.currentPlan.maxUsers - mockBillingData.currentPlan.currentUsers} 人
            </div>
          </CardContent>
        </Card>
      </div>

      {/* アクションボタン */}
      <Card>
        <CardHeader>
          <CardTitle>アクション</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button onClick={() => router.push("/admin/billing/add-users")} className="bg-blue-600 hover:bg-blue-700">
              <Plus className="h-4 w-4 mr-2" />
              使用人数を追加
            </Button>
            <Button variant="outline">
              <Calendar className="h-4 w-4 mr-2" />
              請求履歴をダウンロード
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 決済履歴 */}
      <Card>
        <CardHeader>
          <CardTitle>最近の決済履歴</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>日付</TableHead>
                <TableHead>内容</TableHead>
                <TableHead>金額</TableHead>
                <TableHead>ステータス</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockBillingData.recentTransactions.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell>{transaction.date}</TableCell>
                  <TableCell>{transaction.description}</TableCell>
                  <TableCell className="font-medium">¥{transaction.amount.toLocaleString()}</TableCell>
                  <TableCell>{getStatusBadge(transaction.status)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
