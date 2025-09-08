"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { LogOut, User, ChevronDown, Home, Users, MessageSquare, BarChart3, Target } from "lucide-react"
import { useProfile } from "@/hooks/useProfile"
import { apiClient } from "@/lib/apiClient"

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
  const { profile: userProfileData } = useProfile()
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)

  // ユーザープロファイルを取得
  useEffect(() => {
    const fetchUserProfile = async () => {
      if (backendToken) {
        try {
          const profile = await apiClient.get('/auth/me')
          setUserProfile(profile)
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

  // ユーザーのイニシャルを取得（nickname、display_name、またはメールアドレスの最初の文字）
  const getUserInitial = () => {
    if (userProfileData?.nickname) {
      return userProfileData.nickname.charAt(0).toUpperCase()
    }
    if (userProfile?.display_name) {
      return userProfile.display_name.charAt(0).toUpperCase()
    }
    if (user?.email) {
      return user.email.charAt(0).toUpperCase()
    }
    return "U"
  }

  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg">
              <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              {/* 挨拶部分をダッシュボードに移動 */}
            </div>
            
            <div className="absolute left-1/2 transform -translate-x-1/2">
              <div className="text-5xl font-bold text-white px-8 py-4">
                Bridge LINE
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
                <div className="w-10 h-10 bg-white border-2 border-gray-600 rounded-full flex items-center justify-center text-gray-600 font-semibold">
                  {getUserInitial()}
                </div>
                <ChevronDown className="h-4 w-4 text-gray-500" />
              </button>

              {/* ドロップダウンメニュー */}
              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border z-50">
                  <div className="p-4 border-b">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-white border-2 border-gray-600 rounded-full flex items-center justify-center text-gray-600 font-semibold">
                        {getUserInitial()}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {userProfileData?.nickname || userProfile?.display_name || "ログインユーザー"}
                        </p>
                        <p className="text-sm text-gray-500">{user?.email || "user@example.com"}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="py-2">
                    <button
                      onClick={() => {
                        setIsUserMenuOpen(false)
                        router.push('/profile')
                      }}
                      className="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <User className="h-4 w-4 mr-3" />
                      マイプロフィール
                    </button>
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