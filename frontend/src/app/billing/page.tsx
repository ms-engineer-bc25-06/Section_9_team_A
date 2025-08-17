// REVIEW: 請求・サブスクリプション管理ページ仮実装（るい）
"use client"

import { BillingHistory } from "@/components/billing/BillingHistory"
import { PaymentMethod } from "@/components/billing/PaymentMethod"
import { PricingCard } from "@/components/billing/PricingCard"

export default function BillingPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">請求・サブスクリプション管理</h1>
      
      <div className="grid gap-8">
        <section>
          <h2 className="text-2xl font-semibold mb-4">料金プラン</h2>
          <PricingCard />
        </section>
        
        <section>
          <h2 className="text-2xl font-semibold mb-4">支払い方法</h2>
          <PaymentMethod />
        </section>
        
        <section>
          <h2 className="text-2xl font-semibold mb-4">請求履歴</h2>
          <BillingHistory />
        </section>
      </div>
    </div>
  )
}
