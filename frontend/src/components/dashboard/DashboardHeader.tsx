// ダッシュボードページのヘッダー
"use client"

import type React from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { Bell, Settings, LogOut } from "lucide-react"

const DashboardHeader: React.FC = () => {
  const router = useRouter()
  const { user, logout } = useAuth()

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

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">Bridge Line</h1>
            <div className="text-lg text-gray-600">
              {user?.name}さん、{getGreeting()}！
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100">
              <Bell className="h-5 w-5" />
            </button>
            <button className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100">
              <Settings className="h-5 w-5" />
            </button>
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
              {user?.name?.slice(0, 2)}
            </div>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export { DashboardHeader }
