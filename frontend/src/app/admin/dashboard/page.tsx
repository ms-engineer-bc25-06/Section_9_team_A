// 管理者用ダッシュボード。登録者数や課金状況、利用状況を表示。
import { AdminDashboardHeader } from "@/components/admin/AdminDashboardHeader"
import { AdminDashboardMain } from "@/components/admin/AdminDashboardMain"

export default function AdminDashboardPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <AdminDashboardHeader />
      <AdminDashboardMain />
    </div>
  )
}

