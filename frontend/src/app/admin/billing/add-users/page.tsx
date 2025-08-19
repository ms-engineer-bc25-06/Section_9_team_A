"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { ArrowLeft, Users, Plus, Minus, CreditCard, ChevronDown } from "lucide-react"
import Link from "next/link"

interface UserInput {
  email: string
  name: string
  department: string
  role: string
}

export default function AddUsersPage() {
  const [newUsers, setNewUsers] = useState<UserInput[]>([
    { email: "", name: "", department: "", role: "member" }
  ])
  const [currentUserCount, setCurrentUserCount] = useState(15) // 現在のユーザー数（APIから取得予定）

  const addUser = () => {
    setNewUsers([...newUsers, { email: "", name: "", department: "", role: "member" }])
  }

  const removeUser = (index: number) => {
    if (newUsers.length > 1) {
      setNewUsers(newUsers.filter((_, i) => i !== index))
    }
  }

  const updateUser = (index: number, field: keyof UserInput, value: string) => {
    const updatedUsers = [...newUsers]
    updatedUsers[index][field] = value
    setNewUsers(updatedUsers)
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
                                         <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border rounded-lg">
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
                  ))}

        <Button
                    type="button"
                    variant="outline"
                    onClick={addUser}
                    className="w-full"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    他のメンバーも追加する
        </Button>
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

            {/* 追加後の料金計算 */}
      <Card>
        <CardHeader>
                <CardTitle className="text-lg">追加後の料金</CardTitle>
        </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">追加ユーザー数</span>
                  <span className="font-semibold">{newUsers.length}人</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">追加後の総ユーザー数</span>
                  <span className="font-semibold">{totalUsersAfter}人</span>
                </div>
                {overLimit && (
                  <>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">追加料金対象ユーザー</span>
                      <span className="font-semibold text-red-600">{additionalUsers}人</span>
                    </div>
                    <div className="border-t pt-2">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">追加料金</span>
                        <span className="font-semibold text-red-600">{additionalCost}円</span>
              </div>
                    </div>
                  </>
                )}
                {!overLimit && (
                  <div className="bg-green-50 p-3 rounded-lg">
                    <p className="text-green-700 text-sm">
                      無料枠内のため追加料金は発生しません
                    </p>
            </div>
          )}
        </CardContent>
      </Card>

            {/* 決済ボタン */}
            <Button
              onClick={handleSubmit}
              className="w-full bg-blue-600 hover:bg-blue-700"
              size="lg"
            >
              <CreditCard className="h-5 w-5 mr-2" />
              {overLimit ? "決済画面に進む" : "ユーザーを追加する"}
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

// Next.jsページファイルとしてdefault export
export default function AdminBillingAddUsersPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">ユーザー管理</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <AdminUserList />
      </main>
    </div>
  )
}
