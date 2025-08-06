// 管理者用ダッシュボード。登録者数や課金状況、利用状況を表示。
import { AdminDashboardHeader } from "@/components/admin/AdminDashboardHeader"
import { AdminDashboardCards } from "@/components/admin/AdminDashboardCards"
import { AdminStats } from "@/components/admin/AdminStats"

export default function AdminDashboardPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <AdminDashboardHeader />
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <AdminDashboardCards />
          </div>
          <div>
            <AdminStats />
          </div>
        </div>
      </main>
    </div>
  )
}

