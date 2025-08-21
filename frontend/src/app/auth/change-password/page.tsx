"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Eye, EyeOff, Shield, CheckCircle } from "lucide-react"
import { getAuth } from "firebase/auth"

export default function ChangePasswordPage() {
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)
  
  const router = useRouter()
  const auth = getAuth()

  useEffect(() => {
    // ログイン状態をチェック
    const unsubscribe = auth.onAuthStateChanged((user) => {
      if (!user) {
        router.push("/auth/login")
        return
      }
      
      // ログイン状態を確認
      checkLoginStatus()
    })

    return () => unsubscribe()
  }, [router, auth])

  const checkLoginStatus = async () => {
    try {
      const token = await auth.currentUser?.getIdToken()
      if (!token) return

      const response = await fetch("/api/v1/auth/login-status", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        if (!data.needs_password_setup) {
          // パスワード設定が不要な場合はダッシュボードにリダイレクト
          router.push("/dashboard")
        }
      }
    } catch (error) {
      console.error("ログイン状態確認エラー:", error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    // バリデーション
    if (newPassword !== confirmPassword) {
      setError("新しいパスワードが一致しません")
      setIsLoading(false)
      return
    }

    if (newPassword.length < 8) {
      setError("パスワードは8文字以上で入力してください")
      setIsLoading(false)
      return
    }

    try {
      const token = await auth.currentUser?.getIdToken()
      if (!token) {
        setError("認証トークンが取得できません")
        setIsLoading(false)
        return
      }

      const response = await fetch("/api/v1/auth/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      })

      if (response.ok) {
        setSuccess(true)
        setTimeout(() => {
          router.push("/dashboard")
        }, 2000)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || "パスワード変更に失敗しました")
      }
    } catch (error) {
      console.error("パスワード変更エラー:", error)
      setError("パスワード変更中にエラーが発生しました")
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              パスワード設定完了
            </h2>
            <p className="text-gray-600">
              パスワードが正常に設定されました。<br />
              ダッシュボードに移動します...
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <Shield className="h-6 w-6 text-blue-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            パスワードを設定してください
          </CardTitle>
          <p className="text-gray-600 mt-2">
            初回ログインのため、新しいパスワードを設定してください
          </p>
        </CardHeader>
        
        <CardContent>
          {error && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">
                {error}
              </AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="current-password">現在のパスワード（仮パスワード）</Label>
              <div className="relative">
                <Input
                  id="current-password"
                  type={showCurrentPassword ? "text" : "password"}
                  value={currentPassword}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentPassword(e.target.value)}
                  required
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  className="absolute right-0 top-0 h-full px-2 hover:bg-gray-100"
                >
                  {showCurrentPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <div>
              <Label htmlFor="new-password">新しいパスワード</Label>
              <div className="relative">
                <Input
                  id="new-password"
                  type={showNewPassword ? "text" : "password"}
                  value={newPassword}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-0 top-0 h-full px-2 hover:bg-gray-100"
                >
                  {showNewPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                8文字以上で入力してください
              </p>
            </div>

            <div>
              <Label htmlFor="confirm-password">新しいパスワード（確認）</Label>
              <div className="relative">
                <Input
                  id="confirm-password"
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setConfirmPassword(e.target.value)}
                  required
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-0 top-0 h-full px-2 hover:bg-gray-100"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              disabled={isLoading}
            >
              {isLoading ? "設定中..." : "パスワードを設定"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
