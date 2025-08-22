"use client"

import type React from "react"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import AccessPage from "@/components/auth/AccessPage"

const HomePage: React.FC = () => {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  // ログイン済みのユーザーがいたら dashboard にリダイレクト
  useEffect(() => {
    if (!isLoading && user) {
      router.push("/dashboard")
    }
  }, [user, isLoading, router])

  // ローディング中（Firebaseなどの認証確認中）
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  // 未ログインユーザーにはアクセスページを表示
  return <AccessPage />
}

export default HomePage
