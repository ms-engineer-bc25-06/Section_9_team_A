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
import { Mail, Lock, LogIn, Shield } from "lucide-react"
import { getAuth } from "firebase/auth"

export function LoginForm() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { login } = useAuth()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await login(email, password)
      
      // 初回ログイン判定
      const token = await getAuth().currentUser?.getIdToken()
      if (token) {
        try {
          const response = await fetch("/api/v1/auth/login-status", {
            headers: {
              Authorization: `Bearer ${token}`
            }
          })

          if (response.ok) {
            const data = await response.json()
            if (data.needs_password_setup) {
              // 初回ログインでパスワード設定が必要な場合
              router.push("/auth/change-password")
              return
            }
          }
        } catch (error) {
          console.error("ログイン状態確認エラー:", error)
        }
      }
      
      // 通常のダッシュボードにリダイレクト
      router.push("/dashboard")
    } catch (error) {
      console.error("Login failed:", error)
      alert("ログインに失敗しました")
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoToAdmin = () => {
    router.push("/admin/login")
  }

  return (
    <div className="space-y-6">
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
            />
          </div>
        </div>

        <Button type="submit" className="w-full" disabled={isLoading}>
          <LogIn className="mr-2 h-4 w-4" />
          {isLoading ? "ログイン中..." : "ログイン"}
        </Button>
      </form>

      <Separator />

      <Button
        variant="outline"
        className="w-full bg-transparent"
        onClick={handleGoToAdmin}
      >
        <Shield className="mr-2 h-4 w-4" />
        管理者ログインはこちら
      </Button>
    </div>
  )
}
