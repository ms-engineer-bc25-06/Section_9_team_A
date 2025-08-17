// REVIEW: OAuthログイン後のコールバック画面仮実装（るい）
"use client"

import { useAuth } from "@/components/auth/AuthProvider"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import Spinner from "@/components/ui/Spinner"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function AuthCallbackPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading) {
      if (user) {
        // 認証成功時はダッシュボードにリダイレクト
        router.push("/dashboard")
      } else {
        // 認証失敗時はログインページにリダイレクト
        router.push("/auth/login")
      }
    }
  }, [user, isLoading, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">Bridge Line</CardTitle>
          <CardDescription>認証処理中...</CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <Spinner className="h-8 w-8 mx-auto mb-4" />
          <p className="text-gray-600">認証を処理しています</p>
        </CardContent>
      </Card>
    </div>
  )
}