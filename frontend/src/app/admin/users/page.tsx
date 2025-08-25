// TODO この機能は将来的に実装する(登録されているユーザーの一覧を管理者が閲覧・編集できるページ)
"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useSession } from "@/hooks/useSession"
import { AdminUserList } from "@/components/admin/AdminUserList"
import { Button } from "@/components/ui/Button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { SessionExpiredAlert } from "@/components/ui/SessionExpiredAlert"

export default function AdminUsersPage() {
  const { user, loading, isSessionValid, sessionExpired } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (!isSessionValid && !loading) {
      router.push("/login")
    }
  }, [isSessionValid, loading, router])

  if (loading || !isSessionValid) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-gradient-to-br from-orange-50 to-amber-50 shadow-sm border-b border-orange-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/admin/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                ダッシュボードへ戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-orange-900 flex-1 text-center">ユーザー管理</h1>
            <div className="w-32"></div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* セッション期限切れアラート */}
        {sessionExpired && (
          <SessionExpiredAlert />
        )}
        
        <AdminUserList />
      </main>
    </div>
  )
}
