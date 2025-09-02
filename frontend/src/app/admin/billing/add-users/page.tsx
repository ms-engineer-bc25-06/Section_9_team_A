"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { ArrowLeft, Users, Plus, Minus, CreditCard, ChevronDown, Copy, Eye, EyeOff } from "lucide-react"
import Link from "next/link"
import { generateTemporaryPassword } from "@/lib/utils"
import { getAuth } from "firebase/auth"
import { apiClient } from "@/lib/apiClient"
import { useAuth } from "@/components/auth/AuthProvider"
import { PlanService } from "@/services/planService"

interface UserInput {
  email: string
  name: string
  department: string
  role: string
  temporaryPassword: string
}

export default function AddUsersPage() {
  const { user, isLoading } = useAuth()
  const [newUsers, setNewUsers] = useState<UserInput[]>([
    { 
      email: "", 
      name: "", 
      department: "", 
      role: "member",
      temporaryPassword: ""
    }
  ])
  const [currentUserCount, setCurrentUserCount] = useState(0) // 現在のユーザー数（APIから取得）
  const [isLoadingUserCount, setIsLoadingUserCount] = useState(true)
  const [showPasswords, setShowPasswords] = useState<boolean[]>([false])



  // 認証チェック
  useEffect(() => {
    if (!user && !isLoading) {
      window.location.href = "/admin/login"
    }
  }, [user, isLoading])

  // ユーザー数を取得する関数
  const fetchUserCount = async () => {
    try {
      setIsLoadingUserCount(true)
      
      // apiClientを使用してユーザー数を取得
      const data = await apiClient.get('/admin/billing/user-count')
      setCurrentUserCount(data.total_users)
    } catch (err) {
      console.error('ユーザー数取得エラー:', err)
      // 開発環境ではエラーでもモックデータを使用
      if (process.env.NODE_ENV === 'development') {
        setCurrentUserCount(15)
      }
    } finally {
      setIsLoadingUserCount(false)
    }
  }

  // ページ読み込み時にユーザー数を取得
  useEffect(() => {
    fetchUserCount()
  }, [])

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
      
      // バックエンドAPIにユーザー作成リクエストを送信
      const createdUser = await apiClient.post('/admin/users', {
        email: user.email,
        name: user.name,
        department: user.department,
        role: user.role
      })
      
      // 成功メッセージ（仮パスワードは表示しない）
      alert(`${user.name}さんを追加しました`)
      
      // 現在のユーザー数を更新
      setCurrentUserCount(prev => prev + 1)
      

      
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
    
    // メールアドレスが入力された場合、仮パスワードは空にする（バックエンドで生成される）
    if (field === "email" && value) {
      updatedUsers[index].temporaryPassword = ""
    }
    
    setNewUsers(updatedUsers)
  }

  const regeneratePassword = (index: number) => {
    const updatedUsers = [...newUsers]
    updatedUsers[index].temporaryPassword = "" // バックエンドで生成されるため空にする
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

  // 料金計算（動的プラン情報を使用）
  const currentPlan = PlanService.getCurrentPlanByUserCount(currentUserCount)
  const planInfo = PlanService.getPlanDisplayInfo(currentPlan)
  const maxUsers = planInfo.maxUsers === '無制限' ? 999999 : parseInt(planInfo.maxUsers.replace('名', ''))
  
  const totalUsersAfter = currentUserCount + newUsers.length
  const overLimit = totalUsersAfter > maxUsers
  const additionalUsers = Math.max(0, totalUsersAfter - maxUsers)
  const additionalCost = 0 // プラン料金ベースなので追加料金は0

    return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-gradient-to-br from-orange-50 to-amber-50 shadow-sm border-b border-orange-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/admin/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                ダッシュボードに戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-orange-900 flex-1 text-center">ユーザー追加</h1>
            <div className="w-32"></div>
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
                    <div key={index} className="space-y-4 p-4 border border-gray-300 rounded-lg bg-white shadow-sm">
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
                              仮パスワードはユーザー一覧画面で確認できます
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
                      className="w-full hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-colors duration-200"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      追加する
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>



          {/* 料金計算・決済 */}
          <div className="max-w-2xl space-y-6">
            {/* 現在の利用状況 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">現在の利用状況</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {isLoadingUserCount ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="ml-2 text-gray-600">読み込み中...</span>
                  </div>
                ) : (
                  <>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">現在のユーザー数</span>
                      <span className="font-semibold">{currentUserCount}人</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">現在のプラン</span>
                      <span className="font-semibold">{PlanService.getPlanDisplayInfo(PlanService.getCurrentPlanByUserCount(currentUserCount)).name}</span>
                    </div>
                    <div className="border-t pt-2">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">現在の月額料金</span>
                        <span className="font-semibold">
                          {PlanService.getPlanDisplayInfo(PlanService.getCurrentPlanByUserCount(currentUserCount)).monthlyPrice.toLocaleString()}円
                        </span>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            

            {/* 決済ボタン */}
            <Button
              onClick={async () => {
                try {
                  // セッションの有効性を確認
                  // useAuthによってログイン状態が管理されているため、ここでは不要
                  // ただし、バックエンドAPIにトークンを渡すために、ユーザー情報を取得
                  const auth = getAuth()
                  const currentUser = auth.currentUser
                  
                  if (!currentUser) {
                    alert('ログインが必要です。再度ログインしてください。')
                    return
                  }

                  // トークンの有効性を確認
                  const token = await currentUser.getIdToken(true)
                  console.log('認証確認完了:', currentUser.email)
                  
                  // 決済画面に遷移
                  window.location.href = '/admin/billing'
                } catch (error) {
                  console.error('認証エラー:', error)
                  alert('認証エラーが発生しました。再度ログインしてください。')
                }
              }}
              disabled={!user || isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white disabled:bg-gray-400"
              size="lg"
            >
              <CreditCard className="h-5 w-5 mr-2" />
              {isLoading ? '読み込み中...' : '決済確認画面に進む'}
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
