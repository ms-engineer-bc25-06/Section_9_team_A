// 管理者用ダッシュボード。登録者数や課金状況、利用状況を表示。
"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useSession } from "@/hooks/useSession"
import { AdminDashboardHeader } from "@/components/admin/AdminDashboardHeader"
import { AdminDashboardMain } from "@/components/admin/AdminDashboardMain"
import { SessionExpiredAlert } from "@/components/ui/SessionExpiredAlert"

export default function AdminDashboardPage() {
  const { user, loading, isSessionValid, sessionExpired } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (!isSessionValid && !loading) {
      router.push("/login")
    }
  }, [isSessionValid, loading, router])

  if (loading || !isSessionValid) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <AdminDashboardHeader />
      <main className="container mx-auto px-4 py-8">
        {/* セッション期限切れアラート */}
        {sessionExpired && (
          <SessionExpiredAlert />
        )}
        <AdminDashboardMain />
      </main>
    </div>
  )
}

