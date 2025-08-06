// 管理者用の課金管理画面
import { AdminBillingOverview } from "@/components/admin/AdminBillingOverview"
import { Button } from "@/components/ui/Button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function AdminBillingPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/admin/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                ダッシュボードへ戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">決済・サブスクリプション管理</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <AdminBillingOverview />
      </main>
    </div>
  )
}
