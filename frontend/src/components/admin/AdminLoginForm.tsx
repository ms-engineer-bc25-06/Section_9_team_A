"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { auth } from "@/lib/firebase"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { LogIn } from "lucide-react"

export function AdminLoginForm() {
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
      const currentUser = auth.currentUser
      const userEmail = currentUser?.email

      // 管理者専用フォーム admin 以外は拒否
      if (userEmail !== "admin@example.com") {
        alert("管理者専用です")
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
    <form onSubmit={handleLogin} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">管理者メール</Label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">パスワード</Label>
        <Input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>

      <Button type="submit" disabled={isLoading}>
        <LogIn className="mr-2 h-4 w-4" />
        {isLoading ? "ログイン中..." : "ログイン"}
      </Button>
    </form>
  )
}
