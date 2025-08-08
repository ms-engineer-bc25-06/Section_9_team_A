// 管理者ログインページ。認証フォームを表示。
"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Mail, Lock, Shield } from "lucide-react"
import { useAuth } from "@/components/auth/AuthProvider"
import { auth } from "@/lib/firebase"

export default function AdminLoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { login } = useAuth()

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await login(email, password)
      const user = auth.currentUser
      const userEmail = user?.email

      // 管理者権限をチェック
      try {
        const idToken = await user?.getIdToken()
        
        // デバッグログ（必要に応じてコメントアウト）
        // console.log("=== 管理者チェック開始 ===")
        // console.log("Firebase UID:", user?.uid)
        // console.log("Email:", user?.email)
        // console.log("🔑 ID Token (最初の50文字):", idToken?.substring(0, 50))
        
        const response = await fetch('http://localhost:8000/api/v1/admin-role/check-admin', {
          headers: {
            'Authorization': `Bearer ${idToken}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          alert("このアカウントは管理者ではありません")
          return
        }
      } catch (error) {
        console.error("管理者権限チェック失敗:", error)
        alert("管理者権限の確認に失敗しました")
        return
      }

      router.push("/admin/dashboard")
    } catch (error) {
      console.error("管理者ログイン失敗:", error)
      alert("ログインに失敗しました")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-md p-6">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">管理者ログイン</h1>
          <p className="text-gray-600">Bridge Line 管理者専用ページ</p>
        </div>

        <form onSubmit={handleAdminLogin} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="admin-email" className="text-sm font-medium text-gray-700">
              管理者メールアドレス
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                id="admin-email"
                type="email"
                placeholder="admin@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="admin-password" className="text-sm font-medium text-gray-700">
              管理者パスワード
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                id="admin-password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center px-4 py-2 bg-slate-900 text-white rounded-md hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Shield className="mr-2 h-4 w-4" />
            {isLoading ? "ログイン中..." : "管理者ログイン"}
          </button>
        </form>
      </div>
    </div>
  )
}
