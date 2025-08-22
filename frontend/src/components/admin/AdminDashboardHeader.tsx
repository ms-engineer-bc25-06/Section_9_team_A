// ダッシュボード内のカード部品
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Bell, Settings, LogOut, Shield,User, ChevronDown} from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"

export function AdminDashboardHeader() {
  const router = useRouter()
  const { user, logout } = useAuth()
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const adminName = "管理者" // 実際は管理者情報から取得

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  // 管理者のイニシャルを取得
  const getAdminInitial = () => {
    if (user?.email) {
      return user.email.charAt(0).toUpperCase()
    }
    return "管"
  }

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Shield className="h-6 w-6 text-slate-600" />
              <h1 className="text-2xl font-bold text-gray-900">Bridge LINE 管理画面</h1>
            </div>
            <div className="text-lg text-gray-600">{adminName}さん、お疲れ様です</div>
          </div>

          <div className="flex items-center space-x-4">

            {/* 管理者ユーザーメニュー */}
            <div className="relative">
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="flex items-center space-x-2 p-2 rounded-full hover:bg-gray-100 transition-colors"
              >
                <Avatar className="cursor-pointer w-10 h-10">
                  <AvatarImage src="/placeholder.svg?height=40&width=40" />
                  <AvatarFallback className="bg-slate-500 text-white font-semibold">
                    {getAdminInitial()}
                  </AvatarFallback>
                </Avatar>
                <ChevronDown className="h-4 w-4 text-gray-500" />
              </button>

              {/* ドロップダウンメニュー */}
              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border z-50">
                  <div className="p-4 border-b">
                    <div className="flex items-center space-x-3">
                      <Avatar className="w-12 h-12">
                        <AvatarImage src="/placeholder.svg?height=48&width=48" />
                        <AvatarFallback className="bg-slate-500 text-white font-semibold">
                          {getAdminInitial()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium text-gray-900">管理者</p>
                        <p className="text-sm text-gray-500">{user?.email || "admin@example.com"}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="py-2">
                    <button
                      onClick={() => {
                        setIsUserMenuOpen(false)
                        handleLogout()
                      }}
                      className="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <LogOut className="h-4 w-4 mr-3" />
                      ログアウト
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* メニューが開いている時の背景オーバーレイ */}
      {isUserMenuOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsUserMenuOpen(false)}
        />
      )}
    </header>
  )}