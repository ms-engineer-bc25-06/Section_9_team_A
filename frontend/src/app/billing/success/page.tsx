// REVIEW: 決済成功ページ仮実装（るい）
"use client"

import { CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/Button"
import Link from "next/link"

export default function BillingSuccessPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="mb-6">
          <CheckCircle className="h-16 w-16 text-green-500 mx-auto" />
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          お支払い完了
        </h1>
        
        <p className="text-gray-600 mb-8">
          サブスクリプションの登録が完了しました。
          ご利用いただき、ありがとうございます。
        </p>
        
        <div className="space-y-3">
          <Link href="/dashboard" className="block">
            <Button className="w-full">
              ダッシュボードへ
            </Button>
          </Link>
          
          <Link href="/billing" className="block">
            <Button variant="outline" className="w-full">
              請求詳細を確認
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}