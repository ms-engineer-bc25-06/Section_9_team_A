"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { auth } from "@/lib/auth"
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
      console.log("1. ログイン試行中:", email)
      await login(email, password)
      console.log("2. Firebase ログイン成功")
      
      const currentUser = auth.currentUser
      console.log("3. Current User:", currentUser)
      
      if (!currentUser) {
        alert("ログインに失敗しました")
        return
      }

      // バックエンドにユーザー登録してから管理者権限をチェック
      try {
        console.log("4. IDトークン取得中...")
        const idToken = await currentUser?.getIdToken()

        // デバッグログ（トラブルシューティング時に有効化）
        // console.log("IDトークン取得成功:", idToken?.substring(0, 50) + "...")
        
        // バックエンドにユーザー登録（必要に応じて有効化）
        // try {
        //   const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
        //     method: 'POST',
        //     headers: {
        //       'Content-Type': 'application/json',
        //       'Authorization': `Bearer ${idToken}`
        //     },
        //     body: JSON.stringify({
        //       id_token: idToken,
        //       display_name: currentUser.displayName || currentUser.email || "管理者"
        //     })
        //   })
        // } catch (regError: any) {
        //   console.warn("ユーザー登録失敗、管理者チェックを続行:", regError)
        // }
        
        const response = await fetch('http://localhost:8000/api/v1/admin-role/check-admin', {
          headers: {
            'Authorization': `Bearer ${idToken}`,
            'Content-Type': 'application/json'
          }
        })
        
        console.log("9. 管理者チェックレスポンス:", response.status, response.statusText)
        
        if (!response.ok) {
          const errorText = await response.text()
          console.error("管理者権限エラー:", errorText)
          alert(`管理者権限がありません: ${response.status}`)
          return
        }
        
        console.log("10. 管理者権限確認成功!")
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
