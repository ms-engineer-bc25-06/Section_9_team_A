// ダッシュボードページのヘッダー
"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { Bell, Settings, LogOut,User, ChevronDown } from "lucide-react"

const DashboardHeader: React.FC = () => {
  const router = useRouter()
  const { user, logout } = useAuth()
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return "おはようございます"
    if (hour < 18) return "こんにちは"
    return "こんばんは"
  }

  // ユーザーのイニシャルを取得（メールアドレスの最初の文字）
  const getUserInitial = () => {
    if (user?.email) {
      return user.email.charAt(0).toUpperCase()
    }
    return "U"
  }

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="text-lg text-gray-600">
              {getGreeting()}！
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100">
              <Bell className="h-5 w-5" />
            </button>
            <button className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100">
              <Settings className="h-5 w-5" />
            </button>
            
            {/* ユーザーメニュー */}
            <div className="relative">
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="flex items-center space-x-2 p-2 rounded-full hover:bg-gray-100 transition-colors"
              >
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                  {getUserInitial()}
                </div>
                <ChevronDown className="h-4 w-4 text-gray-500" />
              </button>

              {/* ドロップダウンメニュー */}
              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border z-50">
                  <div className="p-4 border-b">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                        {getUserInitial()}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">ログインユーザー</p>
                        <p className="text-sm text-gray-500">{user?.email || "user@example.com"}</p>
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
  )
}

export { DashboardHeader }