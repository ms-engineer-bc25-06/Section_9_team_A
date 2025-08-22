// ダッシュボードページのヘッダー
"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { LogOut, User, ChevronDown, Home, Users, MessageSquare, BarChart3, Target } from "lucide-react"

interface UserProfile {
  id: string
  display_name: string
  email: string
  avatar_url?: string
}

const DashboardHeader: React.FC = () => {
  const router = useRouter()
  const pathname = usePathname()
  const { user, logout, backendToken } = useAuth()
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)

  // ユーザープロファイルを取得
  useEffect(() => {
    const fetchUserProfile = async () => {
      if (backendToken) {
        try {
          const response = await fetch('http://localhost:8000/api/v1/users/me', {
            headers: {
              'Authorization': `Bearer ${backendToken}`,
              'Content-Type': 'application/json'
            }
          })
          
          if (response.ok) {
            const profile = await response.json()
            setUserProfile(profile)
          }
        } catch (error) {
          console.error('ユーザープロファイル取得エラー:', error)
        }
      }
    }

    fetchUserProfile()
  }, [backendToken])

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

  // ユーザーのイニシャルを取得（display_nameまたはメールアドレスの最初の文字）
  const getUserInitial = () => {
    if (userProfile?.display_name) {
      return userProfile.display_name.charAt(0).toUpperCase()
    }
    if (user?.email) {
      return user.email.charAt(0).toUpperCase()
    }
    return "U"
  }

  const navigationItems = [
    { name: 'ダッシュボード', href: '/dashboard', icon: Home },
    { name: 'チーム管理', href: '/team', icon: Users },
    { name: '音声チャット', href: '/voice-chat', icon: MessageSquare },
    { name: '分析', href: '/analytics', icon: BarChart3 },
    { name: 'チームダイナミクス', href: '/team-dynamics', icon: Target },
    { name: '個人成長支援', href: '/personal-growth', icon: Target },
  ]

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
            {/* 通知と歯車マークを削除 */}
            
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
                        <p className="text-sm font-medium text-gray-900">
                          {userProfile?.display_name || "ログインユーザー"}
                        </p>
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

        {/* ナビゲーションメニュー */}
        <nav className="mt-4">
          <div className="flex space-x-1">
            {navigationItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <button
                  key={item.name}
                  onClick={() => router.push(item.href)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </button>
              )
            })}
          </div>
        </nav>
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