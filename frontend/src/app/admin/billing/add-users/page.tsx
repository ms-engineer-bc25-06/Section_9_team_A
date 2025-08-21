"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { ArrowLeft, Users, Plus, Minus, CreditCard, ChevronDown, Copy, Eye, EyeOff } from "lucide-react"
import Link from "next/link"
import { generateTemporaryPassword } from "@/lib/utils"
import { getAuth } from "firebase/auth"

interface UserInput {
  email: string
  name: string
  department: string
  role: string
  temporaryPassword: string
}

export default function AddUsersPage() {
  const [newUsers, setNewUsers] = useState<UserInput[]>([
    { 
      email: "", 
      name: "", 
      department: "", 
      role: "member",
      temporaryPassword: ""
    }
  ])
  const [currentUserCount, setCurrentUserCount] = useState(15) // 現在のユーザー数（APIから取得予定）
  const [showPasswords, setShowPasswords] = useState<boolean[]>([false])

  const addUser = () => {
    setNewUsers([...newUsers, { 
      email: "", 
      name: "", 
      department: "", 
      role: "member",
      temporaryPassword: ""
    }])
    setShowPasswords([...showPasswords, false])
  }

  const addUserToList = async (userIndex: number) => {
    const user = newUsers[userIndex]
    
    // バリデーション
    if (!user.email || !user.name || !user.department) {
      alert("すべての必須項目を入力してください")
      return
    }
    
    try {
      // Firebase Authトークンを取得
      const auth = getAuth()
      const currentUser = auth.currentUser
      if (!currentUser) {
        alert("ログインが必要です")
        return
      }
      
      const token = await currentUser.getIdToken()
      
      // バックエンドAPIにユーザー作成リクエストを送信（開発用エンドポイント）
      const response = await fetch('/api/v1/admin/users/dev', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: user.email,
          name: user.name,
          department: user.department,
          role: user.role
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'ユーザー作成に失敗しました')
      }
      
      const createdUser = await response.json()
      
      // 成功メッセージ
      alert(`${user.name}さんを追加しました\n仮パスワード: ${createdUser.temporary_password}`)
      
      // 現在のユーザー数を更新
      setCurrentUserCount(prev => prev + 1)
      
      // 追加料金が発生する場合の通知
      const newTotalUsers = currentUserCount + 1
      if (newTotalUsers > freeUserLimit) {
        const additionalUsers = newTotalUsers - freeUserLimit
        const additionalCost = additionalUsers * costPerUser
        alert(`追加料金が発生しています\n追加料金対象ユーザー: ${additionalUsers}人\n追加料金: ${additionalCost}円`)
      }
      
      // 入力欄をクリア
      const updatedUsers = [...newUsers]
      updatedUsers[userIndex] = { 
        email: "", 
        name: "", 
        department: "", 
        role: "member",
        temporaryPassword: ""
      }
      setNewUsers(updatedUsers)
      setShowPasswords(prev => {
        const newShowPasswords = [...prev]
        newShowPasswords[userIndex] = false
        return newShowPasswords
      })
      
    } catch (error) {
      console.error('ユーザー作成エラー:', error)
      const errorMessage = error instanceof Error ? error.message : 'ユーザー作成に失敗しました'
      alert(`ユーザー作成に失敗しました: ${errorMessage}`)
    }
  }

  const removeUser = (index: number) => {
    if (newUsers.length > 1) {
      setNewUsers(newUsers.filter((_, i) => i !== index))
      setShowPasswords(showPasswords.filter((_, i) => i !== index))
    }
  }

  const updateUser = (index: number, field: keyof UserInput, value: string) => {
    const updatedUsers = [...newUsers]
    updatedUsers[index][field] = value
    
    // メールアドレスが入力された場合、仮パスワードを自動生成
    if (field === "email" && value && !updatedUsers[index].temporaryPassword) {
      updatedUsers[index].temporaryPassword = generateTemporaryPassword()
    }
    
    setNewUsers(updatedUsers)
  }

  const regeneratePassword = (index: number) => {
    const updatedUsers = [...newUsers]
    updatedUsers[index].temporaryPassword = generateTemporaryPassword()
    setNewUsers(updatedUsers)
  }

  const togglePasswordVisibility = (index: number) => {
    const updatedShowPasswords = [...showPasswords]
    updatedShowPasswords[index] = !updatedShowPasswords[index]
    setShowPasswords(updatedShowPasswords)
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      // コピー成功のフィードバックを表示（実際の実装ではtoastなどを使用）
      alert("パスワードをコピーしました")
    } catch (err) {
      console.error('Failed to copy: ', err)
      alert("コピーに失敗しました")
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // バリデーション
    const hasEmptyFields = newUsers.some(user => 
      !user.email || !user.name || !user.department
    )
    
    if (hasEmptyFields) {
      alert("すべての必須項目を入力してください")
      return
    }
    
    // ユーザー追加処理（実際の実装ではAPIを呼び出し）
    console.log("ユーザー追加処理:", newUsers)
    
    // 決済が必要な場合は決済画面に遷移
    if (overLimit) {
      // ユーザー情報をセッションストレージに保存
      sessionStorage.setItem('pendingUsers', JSON.stringify(newUsers))
      
      // 決済画面に遷移
      window.location.href = '/admin/billing'
      } else {
      // 決済不要の場合は直接ユーザー管理画面に遷移
      // ユーザー情報をセッションストレージに保存（即座に反映用）
      sessionStorage.setItem('pendingUsers', JSON.stringify(newUsers))
      alert("ユーザーが正常に追加されました")
      window.location.href = '/admin/users'
    }
  }

  // 料金計算
  const freeUserLimit = 10
  const costPerUser = 500
  const totalUsersAfter = currentUserCount + newUsers.length
  const overLimit = totalUsersAfter > freeUserLimit
  const additionalUsers = Math.max(0, totalUsersAfter - freeUserLimit)
  const additionalCost = additionalUsers * costPerUser

    return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/admin/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                ダッシュボードに戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">ユーザー追加・決済</h1>
          </div>
      </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* ユーザー入力フォーム */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5 text-blue-500" />
                  <span>ユーザー情報入力</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  {newUsers.map((user, index) => (
                    <div key={index} className="space-y-4 p-4 border rounded-lg">
                      {/* 1行目: 名前、部署、権限 */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <Label htmlFor={`name-${index}`}>氏名 *</Label>
                          <Input
                            id={`name-${index}`}
                            value={user.name}
                            onChange={(e) => updateUser(index, "name", e.target.value)}
                            placeholder="田中太郎"
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor={`department-${index}`}>部署</Label>
                          <Input
                            id={`department-${index}`}
                            value={user.department}
                            onChange={(e) => updateUser(index, "department", e.target.value)}
                            placeholder="開発部"
                          />
                        </div>
                                              <div className="flex items-end space-x-2">
                        <div className="flex-1">
                          <Label htmlFor={`role-${index}`}>権限</Label>
                          <select
                            id={`role-${index}`}
                            value={user.role}
                            onChange={(e) => updateUser(index, "role", e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="member">メンバー</option>
                            <option value="admin">管理者</option>
                          </select>
                        </div>
                        {newUsers.length > 1 && (
                          <Button 
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => removeUser(index)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Minus className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                      </div>

                      {/* 2行目: メール、仮パスワード */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor={`email-${index}`}>メールアドレス *</Label>
                          <Input
                            id={`email-${index}`}
                            type="email"
                            value={user.email}
                            onChange={(e) => updateUser(index, "email", e.target.value)}
                            placeholder="user@company.com"
                            required
                          />
                        </div>
                                                <div>
                          <Label htmlFor={`password-${index}`}>仮パスワード</Label>
                          {user.temporaryPassword ? (
                            <div className="flex space-x-2">
                              <div className="flex-1 relative">
                                <Input
                                  id={`password-${index}`}
                                  type={showPasswords[index] ? "text" : "password"}
                                  value={user.temporaryPassword}
                                  readOnly
                                  className="pr-20"
                                />
                                <div className="absolute right-0 top-0 h-full flex">
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => togglePasswordVisibility(index)}
                                    className="h-full px-2 hover:bg-gray-100"
                                  >
                                    {showPasswords[index] ? (
                                      <EyeOff className="h-4 w-4" />
                                    ) : (
                                      <Eye className="h-4 w-4" />
                                    )}
                                  </Button>
                                </div>
                              </div>
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => copyToClipboard(user.temporaryPassword)}
                                className="px-2 hover:bg-blue-50"
                                title="パスワードをコピー"
                              >
                                <Copy className="h-4 w-4" />
                              </Button>
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => regeneratePassword(index)}
                                className="px-2 hover:bg-green-50 text-green-600"
                                title="新しいパスワードを生成"
                              >
                                <span className="text-xs">再生成</span>
                              </Button>
                            </div>
                          ) : (
                            <div className="text-sm text-gray-500 italic">
                              メールアドレスを入力すると仮パスワードが自動生成されます
                            </div>
                          )}
                          {user.temporaryPassword && (
                            <p className="text-xs text-gray-500 mt-1">
                              このパスワードは初回ログイン時に変更してください
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}

                  <div className="flex space-x-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        // 現在入力されているユーザーを一覧に追加
                        const currentUser = newUsers[0]
                        if (currentUser.email && currentUser.name && currentUser.department) {
                          addUserToList(0)
                        } else {
                          alert("すべての必須項目を入力してください")
                        }
                      }}
                      className="flex-[8]"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      追加する
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={addUser}
                      className="flex-[2]"
                    >
                      <Users className="h-4 w-4 mr-2" />
                      他のメンバーも追加する
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* 追加料金通知 */}
          {currentUserCount > freeUserLimit && (
            <Card className="bg-orange-50 border-orange-200">
              <CardContent className="pt-6">
                <div className="text-sm text-orange-800">
                  <h4 className="font-semibold mb-2 flex items-center">
                    <span className="text-orange-600 mr-2">💰</span>
                    追加料金が発生しています
                  </h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span>追加料金対象ユーザー:</span>
                      <span className="font-semibold text-orange-700">
                        {currentUserCount - freeUserLimit}人
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>追加料金:</span>
                      <span className="font-semibold text-orange-700">
                        {(currentUserCount - freeUserLimit) * costPerUser}円
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 料金計算・決済 */}
          <div className="max-w-2xl space-y-6">
            {/* 現在の利用状況 */}
            <Card>
        <CardHeader>
                <CardTitle className="text-lg">現在の利用状況</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
                  <span className="text-gray-600">現在のユーザー数</span>
                  <span className="font-semibold">{currentUserCount}人</span>
          </div>
          <div className="flex justify-between items-center">
                  <span className="text-gray-600">無料枠</span>
                  <span className="font-semibold">{freeUserLimit}人</span>
          </div>
          <div className="flex justify-between items-center">
                  <span className="text-gray-600">追加ユーザー</span>
                  <span className="font-semibold">
                    {Math.max(0, currentUserCount - freeUserLimit)}人
                  </span>
          </div>
                <div className="border-t pt-2">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">現在の月額料金</span>
                    <span className="font-semibold">
                      {Math.max(0, currentUserCount - freeUserLimit) * costPerUser}円
            </span>
          </div>
          </div>
        </CardContent>
      </Card>

            

            {/* 決済ボタン */}
            <Button
              onClick={() => {
                // 決済画面に直接遷移（入力項目のバリデーションなし）
                window.location.href = '/admin/billing'
              }}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              size="lg"
            >
              <CreditCard className="h-5 w-5 mr-2" />
              決済確認画面に進む
            </Button>
            
            {/* 注意事項 */}
            <Card className="bg-yellow-50 border-yellow-200">
              <CardContent className="pt-6">
                <div className="text-sm text-yellow-800">
                  <h4 className="font-semibold mb-2">注意事項</h4>
                  <ul className="space-y-1 list-disc list-inside">
                    <li>追加するユーザーは、反映に少し時間がかかる場合があります</li>
                    <li>決済は月額サブスクリプションとして処理されます</li>
                    <li>ユーザーの削除は別途管理画面から行ってください</li>
                    <li>料金は翌月の請求書に反映されます</li>
                    <li>仮パスワードは各ユーザーに安全に共有してください</li>
                    <li>仮パスワードは初回ログイン時に変更する必要があります</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
        </div>
      </div>
      </main>
    </div>
  )
}
