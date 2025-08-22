// 管理者ログインページ。認証フォームを表示。
"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Mail, Lock, Shield } from "lucide-react"
import { useAuth } from "@/components/auth/AuthProvider"
import { auth } from "@/lib/auth"

export default function AdminLoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { login, backendToken } = useAuth()

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const token = await login(email, password)
      
      // 管理者権限をチェック
      try {
        if (!token) {
          alert("バックエンド認証が完了していません。しばらく待ってから再試行してください。")
          return
        }
        
        const response = await fetch('http://localhost:8000/api/v1/admin-role/check-admin', {
          headers: {
            'Authorization': `Bearer ${token}`,
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 w-full max-w-md text-center relative overflow-hidden">
        {/* 装飾的な背景要素 */}
        <div className="absolute -top-12 -right-12 w-32 h-32 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full opacity-10"></div>
        <div className="absolute -bottom-8 -left-8 w-24 h-24 bg-gradient-to-tr from-blue-300 to-blue-500 rounded-full opacity-8"></div>
        
        {/* ロゴセクション */}
        <div className="relative z-10 mb-8">
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center">
            {/* 1人の人のアイコン */}
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">管理者ログイン</h1>
        </div>
        
        {/* ログインフォーム */}
        <div className="relative z-10">
          <form onSubmit={handleAdminLogin} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="admin-email" className="text-sm font-medium text-gray-700 text-left block">
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
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="admin-password" className="text-sm font-medium text-gray-700 text-left block">
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
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Shield className="mr-2 h-4 w-4" />
              {isLoading ? "ログイン中..." : "管理者ログイン"}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
