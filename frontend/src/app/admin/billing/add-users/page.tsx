// 管理者用ユーザー追加ページ
"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Badge } from "@/components/ui/Badge"
import { ArrowLeft, Plus, Users, AlertTriangle, CheckCircle } from "lucide-react"
import Link from "next/link"

export default function AddUsersPage() {
  const [newUsers, setNewUsers] = useState<Array<{
    email: string
    name: string
    role: string
  }>>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addUser = () => {
    setNewUsers([
      ...newUsers,
      { email: "", name: "", role: "member" }
    ])
  }

  const removeUser = (index: number) => {
    setNewUsers(newUsers.filter((_, i) => i !== index))
  }

  const updateUser = (index: number, field: string, value: string) => {
    const updatedUsers = [...newUsers]
    updatedUsers[index] = { ...updatedUsers[index], [field]: value }
    setNewUsers(updatedUsers)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (newUsers.length === 0) {
      setError("ユーザーを追加してください")
      return
    }

    // バリデーション
    for (const user of newUsers) {
      if (!user.email || !user.name) {
        setError("すべてのユーザーのメールアドレスと名前を入力してください")
        return
      }
    }

    setIsSubmitting(true)
    setError(null)

    try {
      // 実際のAPI呼び出しをここに実装
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      setSuccess(true)
      setNewUsers([])
      
      // 成功メッセージを一定時間後に非表示
      setTimeout(() => {
        setSuccess(false)
      }, 5000)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : "ユーザー追加中にエラーが発生しました")
    } finally {
      setIsSubmitting(false)
    }
  }

  const currentUserCount = 15 // 仮の値、実際はAPIから取得
  const freeLimit = 10
  const additionalUsers = Math.max(0, currentUserCount - freeLimit)
  const additionalCost = additionalUsers * 500

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
      {/* ヘッダー */}
      <div className="mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <Link href="/admin/billing">
              <Button variant="ghost" size="sm">
          <ArrowLeft className="h-4 w-4 mr-2" />
                決済管理に戻る
        </Button>
            </Link>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">ユーザー追加</h1>
          <p className="text-gray-600">新しいユーザーをシステムに追加します</p>
      </div>

        {/* 現在の状況 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-600" />
                <span>現在の利用者数</span>
          </CardTitle>
        </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600 mb-2">{currentUserCount}人</div>
              <div className="text-sm text-gray-500">
                {currentUserCount > freeLimit ? (
                  <span className="text-orange-600">無料枠超過</span>
                ) : (
                  <span className="text-green-600">無料枠内</span>
                )}
          </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">無料枠</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600 mb-2">10人まで</div>
              <div className="text-sm text-gray-500">
                残り{Math.max(0, freeLimit - currentUserCount)}人分
          </div>
        </CardContent>
      </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">追加料金</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600 mb-2">
                ¥{additionalCost.toLocaleString()}
              </div>
              <div className="text-sm text-gray-500">
                {additionalUsers > 0 ? `${additionalUsers}人 × ¥500` : 'なし'}
              </div>
            </CardContent>
          </Card>
          </div>

        {/* 成功メッセージ */}
        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              <strong>ユーザー追加完了:</strong> 新しいユーザーが正常に追加されました。
        </AlertDescription>
      </Alert>
        )}

        {/* エラーメッセージ */}
        {error && (
          <Alert className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* ユーザー追加フォーム */}
      <Card>
        <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Plus className="h-5 w-5 text-green-600" />
              <span>ユーザー追加</span>
          </CardTitle>
            <CardDescription>
              追加するユーザーの情報を入力してください
            </CardDescription>
        </CardHeader>
        <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* ユーザーリスト */}
              {newUsers.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>追加するユーザーがいません</p>
                  <p className="text-sm">下のボタンからユーザーを追加してください</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {newUsers.map((user, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="font-medium">ユーザー {index + 1}</h3>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeUser(index)}
                          className="text-red-600 hover:text-red-700"
                        >
                          削除
                        </Button>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor={`email-${index}`}>メールアドレス</Label>
                          <Input
                            id={`email-${index}`}
                            type="email"
                            value={user.email}
                            onChange={(e) => updateUser(index, "email", e.target.value)}
                            placeholder="user@example.com"
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor={`name-${index}`}>名前</Label>
                          <Input
                            id={`name-${index}`}
                            type="text"
                            value={user.name}
                            onChange={(e) => updateUser(index, "name", e.target.value)}
                            placeholder="山田太郎"
                            required
                          />
                        </div>
                      </div>
                      
                      <div className="mt-4">
                        <Label htmlFor={`role-${index}`}>役割</Label>
                        <select
                          id={`role-${index}`}
                          value={user.role}
                          onChange={(e) => updateUser(index, "role", e.target.value)}
                          className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="member">メンバー</option>
                          <option value="admin">管理者</option>
                          <option value="viewer">閲覧者</option>
                        </select>
              </div>
            </div>
                  ))}
                </div>
              )}

              {/* アクションボタン */}
              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={addUser}
                  className="flex-1"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  ユーザーを追加
                </Button>
                
                {newUsers.length > 0 && (
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 bg-green-600 hover:bg-green-700"
                  >
                    {isSubmitting ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>処理中...</span>
                      </div>
                    ) : (
                      <span>ユーザーを追加する</span>
                    )}
                  </Button>
                )}
              </div>
            </form>
        </CardContent>
      </Card>

        {/* 注意事項 */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">注意事項</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-gray-600">
              <p>• ユーザーを追加すると、無料枠（10人）を超過した場合、追加料金が発生します</p>
              <p>• 追加料金は1人500円/月で計算されます</p>
              <p>• ユーザー追加後、決済管理ページで決済手続きを行ってください</p>
              <p>• 追加したユーザーには招待メールが自動送信されます</p>
          </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
