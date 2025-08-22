// 管理者用ダッシュボード。登録者数や課金状況、利用状況を表示。
"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { AdminDashboardHeader } from "@/components/admin/AdminDashboardHeader"
import { AdminDashboardMain } from "@/components/admin/AdminDashboardMain"

export default function AdminDashboardPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!user && !isLoading) {
      router.push("/")
    }
  }, [user, isLoading, router])

  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <AdminDashboardHeader />
      <AdminDashboardMain />
    </div>
  )
}

