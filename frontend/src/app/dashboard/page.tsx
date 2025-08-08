// ダッシュボードトップ
"use client"

import type React from "react"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { DashboardCards } from "@/components/dashboard/DashboardCards"

const DashboardPage: React.FC = () => {
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

  return <DashboardCards />
}

export default DashboardPage
// "use client"

// import { useEffect, useState } from "react"
// import { useRouter } from "next/navigation"
// import { useAuth } from "@/components/auth/AuthProvider"
// import { fetchWithAuth } from "@/lib/api"

// export default function DashboardPage() {
//   const { user, isLoading } = useAuth()
//   const [authChecked, setAuthChecked] = useState(false)
//   const router = useRouter()

//   useEffect(() => {
//     // Firebase認証チェックがまだなら何もしない
//     if (isLoading) return

//     // 未ログインなら即ログインページへ
//     if (!user) {
//       router.replace("/login")
//       return
//     }

//     // ログイン済み → バックエンド認証を確認
//     const checkAuth = async () => {
//       try {
//         const res = await fetchWithAuth("/auth/me")
//         if (!res.ok) {
//           router.replace("/login")
//           return
//         }
//         setAuthChecked(true) // 認証OK
//       } catch (error) {
//         console.error("Auth check failed:", error)
//         router.replace("/login")
//       }
//     }

//     checkAuth()
//   }, [isLoading, user, router])

//   // Firebase or API認証中は表示
//   if (isLoading || !authChecked) {
//     return <p>読み込み中...</p>
//   }

//   return (
//     <div>
//       <h1>ダッシュボード</h1>
//       <p>認証されたユーザーのみが見られるページです。</p>
//     </div>
//   )
// }
