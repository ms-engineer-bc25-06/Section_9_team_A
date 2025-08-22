// ログインフォームUI
"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Separator } from "@/components/ui/Separator"
import { Mail, Lock, LogIn, Shield, AlertCircle } from "lucide-react"
import { getAuth, signInWithEmailAndPassword } from "firebase/auth"

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [isTemporaryPassword, setIsTemporaryPassword] = useState(false)
  const router = useRouter()
  const { login, temporaryLogin } = useAuth()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      if (isTemporaryPassword) {
        // 仮パスワードログイン
        console.log("🔥 仮パスワードログイン開始...")
        await temporaryLogin(email, password)
        console.log("✅ 仮パスワードログイン成功")
        // 仮パスワードログイン成功後はパスワード変更画面にリダイレクト
        router.push("/auth/change-password")
        return
      } else {
        // 通常のFirebaseログイン
        console.log("🔥 通常ログイン開始...")
        await login(email, password)
        console.log("✅ 通常ログイン成功")
        
        // 初回ログイン判定
        const auth = getAuth()
        const user = auth.currentUser
        if (user) {
          try {
            const token = await user.getIdToken()
            console.log("🔍 ログイン状態を確認中...")
            const response = await fetch("http://localhost:8000/api/v1/auth/login-status", {
              headers: {
                Authorization: `Bearer ${token}`
              }
            })

            if (response.ok) {
              const data = await response.json()
              console.log("📊 ログイン状態:", data)
              
              if (data.needs_password_setup || data.has_temporary_password || data.is_first_login) {
                // 初回ログインでパスワード設定が必要な場合
                console.log("🔄 初回ログイン - パスワード変更画面へ")
                router.push("/auth/change-password")
                return
              }
            } else {
              console.error("ログイン状態確認失敗:", response.status)
            }
          } catch (error) {
            console.error("ログイン状態確認エラー:", error)
          }
        }
        
        // 通常のダッシュボードにリダイレクト
        console.log("🔄 ダッシュボードへ")
        router.push("/dashboard")
      }
    } catch (error: any) {
      console.error("❌ ログイン失敗:", error)
      
      // エラーメッセージの設定
      let errorMessage = "ログインに失敗しました"
      
      if (error.code === "auth/invalid-credential") {
        errorMessage = "メールアドレスまたはパスワードが正しくありません"
      } else if (error.code === "auth/user-not-found") {
        errorMessage = "ユーザーが見つかりません"
      } else if (error.code === "auth/wrong-password") {
        errorMessage = "パスワードが正しくありません"
      } else if (error.code === "auth/too-many-requests") {
        errorMessage = "ログイン試行回数が多すぎます。しばらく待ってから再試行してください"
      } else if (error.message) {
        errorMessage = error.message
      }
      
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoToAdmin = () => {
    router.push("/admin/login")
  }

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2"></div>

      {error && (
        <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-md">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span className="text-sm text-red-700">{error}</span>
        </div>
      )}

      <form onSubmit={handleLogin} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">メールアドレス</Label>
          <div className="relative">
            <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              id="email"
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="pl-10"
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">パスワード</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="pl-10"
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="temporary-password"
            checked={isTemporaryPassword}
            onChange={(e) => setIsTemporaryPassword(e.target.checked)}
            className="rounded border-gray-300"
            disabled={isLoading}
          />
          <Label htmlFor="temporary-password" className="text-sm">
            仮パスワードでログイン（初回ログイン時）
          </Label>
        </div>

        <Button type="submit" className="w-full" disabled={isLoading}>
          <LogIn className="mr-2 h-4 w-4" />
          {isLoading ? "ログイン中..." : "ログイン"}
        </Button>
      </form>

      <Separator />

      <div className="text-center space-y-2">
        <p className="text-sm text-muted-foreground">
          初回ログインの際は仮パスワードを使用してください
        </p>
        <p className="text-xs text-muted-foreground">
          仮パスワードは管理者が発行した一時的なパスワードです
        </p>
      </div>

      <Button
        variant="outline"
        className="w-full bg-transparent"
        onClick={handleGoToAdmin}
        disabled={isLoading}
      >
        <Shield className="mr-2 h-4 w-4" />
        管理者ログインはこちら
      </Button>
    </div>
  )
}
