"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Shield, CheckCircle, AlertTriangle } from "lucide-react"

export default function CreateDevAdminPage() {
  const [email, setEmail] = useState("")
  const [name, setName] = useState("")
  const [department, setDepartment] = useState("")
  const [role, setRole] = useState("admin")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)
  const [createdUser, setCreatedUser] = useState<any>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    try {
      const response = await fetch("/api/v1/auth/dev/create-admin", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          name,
          department,
          role
        })
      })

      if (response.ok) {
        const data = await response.json()
        setCreatedUser(data.user)
        setSuccess(true)
      } else {
        const errorData = await response.json()
        console.error("サーバーエラー:", errorData)
        setError(errorData.detail || "管理者作成に失敗しました")
      }
    } catch (error) {
      console.error("管理者作成エラー:", error)
      setError(`管理者作成中にエラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsLoading(false)
    }
  }

  if (success && createdUser) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              管理者作成完了
            </h2>
            <div className="text-left space-y-3 mb-4">
              <div>
                <span className="font-semibold">メールアドレス:</span> {createdUser.email}
              </div>
              <div>
                <span className="font-semibold">氏名:</span> {createdUser.name}
              </div>
              <div>
                <span className="font-semibold">部署:</span> {createdUser.department}
              </div>
              <div>
                <span className="font-semibold">権限:</span> {createdUser.role}
              </div>
              <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                <span className="font-semibold text-yellow-800">仮パスワード:</span>
                <div className="font-mono text-lg mt-1">{createdUser.temporary_password}</div>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              この仮パスワードでログインしてください。<br />
              初回ログイン時に新しいパスワードを設定できます。
            </p>
            <Button
              onClick={() => window.location.href = "/auth/login"}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              ログイン画面へ
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <Shield className="h-6 w-6 text-red-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            開発環境用管理者作成
          </CardTitle>
          <p className="text-gray-600 mt-2">
            このページは開発環境でのみ使用してください
          </p>
        </CardHeader>
        
        <CardContent>
          <Alert className="mb-4 border-yellow-200 bg-yellow-50">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800">
              <strong>注意:</strong> この機能は開発環境でのみ使用してください。
              本番環境では使用しないでください。
              <br />
              <strong>Firebase設定:</strong> Firebase設定が不完全な場合は、開発用のダミーUIDが生成されます。
            </AlertDescription>
          </Alert>

          {error && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">
                {error}
              </AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email">メールアドレス *</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@example.com"
                required
              />
            </div>

            <div>
              <Label htmlFor="name">氏名 *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="管理者太郎"
                required
              />
            </div>

            <div>
              <Label htmlFor="department">部署 *</Label>
              <Input
                id="department"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="管理部"
                required
              />
            </div>

            <div>
              <Label htmlFor="role">権限</Label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="admin">管理者</option>
                <option value="member">メンバー</option>
              </select>
            </div>

            <Button
              type="submit"
              className="w-full bg-red-600 hover:bg-red-700 text-white"
              disabled={isLoading}
            >
              {isLoading ? "作成中..." : "管理者を作成"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
