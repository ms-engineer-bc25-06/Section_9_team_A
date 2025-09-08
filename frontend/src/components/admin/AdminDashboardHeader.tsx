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
  const adminName = "管理者"

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
    <header className="bg-orange-500 shadow-sm border-b border-orange-600">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-white" />
              <h1 className="text-3xl font-bold text-white">Bridge LINE 管理画面</h1>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-lg text-white">{adminName}さん、お疲れ様です😊</div>

            {/* 管理者ユーザーメニュー */}
            <div className="relative">
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="flex items-center space-x-2 p-2 rounded-full hover:bg-orange-600 transition-colors"
              >
                <Avatar className="cursor-pointer w-10 h-10">
                  <AvatarImage src="/placeholder.svg?height=40&width=40" />
                  <AvatarFallback className="bg-orange-600 text-white font-semibold">
                    {getAdminInitial()}
                  </AvatarFallback>
                </Avatar>
                <ChevronDown className="h-4 w-4 text-white" />
              </button>

              {/* ドロップダウンメニュー */}
              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-orange-200 z-50">
                  <div className="p-4 border-b border-orange-200">
                    <div className="flex items-center space-x-3">
                      <Avatar className="w-12 h-12">
                        <AvatarImage src="/placeholder.svg?height=48&width=48" />
                        <AvatarFallback className="bg-orange-500 text-white font-semibold">
                          {getAdminInitial()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium text-orange-900">管理者</p>
                        <p className="text-sm text-orange-600">{user?.email || "admin@example.com"}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="py-2">
                    <button
                      onClick={() => {
                        setIsUserMenuOpen(false)
                        handleLogout()
                      }}
                      className="w-full flex items-center px-4 py-2 text-sm text-orange-700 hover:bg-orange-100"
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
  )
}