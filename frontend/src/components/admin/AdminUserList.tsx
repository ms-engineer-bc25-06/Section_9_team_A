// TODO この機能は将来的に実装する(ユーザー一覧表示)
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Badge } from "@/components/ui/Badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table"
import { Search, Users, UserCheck, MoreHorizontal, Copy } from "lucide-react"
import { useState, useEffect } from "react"
import Link from "next/link"

// モックデータ（開発環境用）- コメントアウト
/*
const mockUsers = [
  {
    id: 1,
    name: "田中太郎",
    email: "tanaka@company.com",
    department: "開発部",
    joinDate: "2023-04-01",
    lastLogin: "2024-01-15 14:30",
    role: "member",
    hasTemporaryPassword: false,
  },
  {
    id: 2,
    name: "佐藤花子",
    email: "sato@company.com",
    department: "デザイン部",
    joinDate: "2023-03-15",
    lastLogin: "2024-01-15 10:15",
    role: "member",
    hasTemporaryPassword: false,
  },
  {
    id: 3,
    name: "鈴木一郎",
    email: "suzuki@company.com",
    department: "営業部",
    joinDate: "2023-02-01",
    lastLogin: "2024-01-14 16:45",
    role: "member",
    hasTemporaryPassword: false,
  },
  {
    id: 4,
    name: "高橋美咲",
    email: "takahashi@company.com",
    department: "マーケティング部",
    joinDate: "2023-01-10",
    lastLogin: "2024-01-15 09:20",
    role: "admin",
    hasTemporaryPassword: false,
  },
]
*/

// ユーザーの型定義
interface User {
  id: number
  name: string
  email: string
  department: string
  joinDate: string
  lastLogin: string
  role: string
  hasTemporaryPassword: boolean
  temporaryPassword?: string
}

export function AdminUserList() {
  const [searchTerm, setSearchTerm] = useState("")
  const [users, setUsers] = useState<User[]>([])

  // バックエンドAPIからユーザー一覧を取得
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        console.log('Fetching users from backend...')
        const response = await fetch('/api/v1/admin/users', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          const userData = await response.json()
          console.log('Users fetched:', userData)
          
          // バックエンドのデータ形式に合わせて変換
          const formattedUsers = userData.map((user: any) => ({
            id: user.id,
            name: user.name,
            email: user.email,
            department: user.department,
            joinDate: user.created_at ? new Date(user.created_at).toISOString().split('T')[0] : '未設定',
            lastLogin: "未ログイン", // バックエンドにlast_login_atフィールドがあれば使用
            role: user.role,
            hasTemporaryPassword: user.has_temporary_password,
            temporaryPassword: user.temporary_password
          }))
          
          setUsers(formattedUsers)
        } else {
          console.error('Failed to fetch users:', response.status)
        }
      } catch (error) {
        console.error('Error fetching users:', error)
      }
    }
    
    fetchUsers()
  }, [])

  const filteredUsers = users.filter(
    (user) =>
      (user.name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
      (user.email?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
      (user.department?.toLowerCase() || '').includes(searchTerm.toLowerCase()),
  )

  const getRoleBadge = (role: string) => {
    switch (role) {
      case "admin":
        return (
          <Badge variant="outline" className="border-purple-500 text-purple-700">
            管理者
          </Badge>
        )
      case "member":
        return <Badge variant="outline">メンバー</Badge>
      default:
        return <Badge variant="outline">不明</Badge>
    }
  }

  const totalUsers = users.length

  return (
    <div className="space-y-6">
      {/* ユーザー一覧 */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>ユーザー一覧</CardTitle>
            <div className="flex items-center space-x-4">
              <div className="relative w-64">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="ユーザーを検索..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Link href="/admin/billing/add-users">
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                  <Users className="h-4 w-4 mr-2" />
                  ユーザー追加
                </Button>
              </Link>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ユーザー</TableHead>
                <TableHead>部署</TableHead>
                <TableHead>権限</TableHead>
                <TableHead>パスワード状態</TableHead>
                <TableHead>操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.length > 0 ? (
                filteredUsers.map((user: User) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <Avatar>
                          <AvatarImage src={`/placeholder.svg?height=32&width=32&query=${user.name || 'user'}`} />
                          <AvatarFallback>{(user.name || 'U').slice(0, 2)}</AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium">{user.name || '名前未設定'}</div>
                          <div className="text-sm text-gray-600">{user.email || 'メール未設定'}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{user.department || '部署未設定'}</TableCell>
                    <TableCell>{getRoleBadge(user.role)}</TableCell>
                    <TableCell>
                      {user.role === "admin" ? (
                        <Badge variant="outline" className="border-green-500 text-green-700">
                          設定済み
                        </Badge>
                      ) : user.hasTemporaryPassword ? (
                        <div className="space-y-2">
                          <Badge variant="outline" className="border-orange-500 text-orange-700">
                            仮パスワード
                          </Badge>
                          {user.temporaryPassword && (
                            <div className="text-xs">
                              <div className="font-mono bg-gray-100 p-1 rounded">
                                {user.temporaryPassword}
                              </div>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 w-6 p-0"
                                onClick={() => {
                                  if (user.temporaryPassword) {
                                    const password = user.temporaryPassword
                                    navigator.clipboard.writeText(password).then(() => {
                                      alert('パスワードをコピーしました')
                                    }).catch(() => {
                                      // フォールバック: 古いブラウザ対応
                                      const textArea = document.createElement('textarea')
                                      textArea.value = password
                                      document.body.appendChild(textArea)
                                      textArea.select()
                                      document.execCommand('copy')
                                      document.body.removeChild(textArea)
                                      alert('パスワードをコピーしました')
                                    })
                                  }
                                }}
                                title="パスワードをコピー"
                              >
                                <Copy className="h-3 w-3" />
                              </Button>
                            </div>
                          )}
                        </div>
                      ) : (
                        <Badge variant="outline" className="border-green-500 text-green-700">
                          設定済み
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">
                    <div className="text-gray-500">
                      <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p className="text-lg font-medium">ユーザーが登録されていません</p>
                      <p className="text-sm">ユーザー追加ボタンから新しいユーザーを追加してください</p>
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* 統計情報 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-500" />
              <span>総ユーザー数</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">{totalUsers}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2">
              <UserCheck className="h-5 w-5 text-green-500" />
              <span>管理者数</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{users.filter((user) => user.role === "admin").length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2">
              <span className="text-orange-500">🔑</span>
              <span>仮パスワード</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">{users.filter((user) => user.hasTemporaryPassword).length}</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
