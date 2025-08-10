// ダッシュボード内のカード部品
"use client"

import { Button } from "@/components/ui/Button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Bell, Settings, LogOut, Shield } from "lucide-react"
import { useRouter } from "next/navigation"

export function AdminDashboardHeader() {
  const router = useRouter()
  const adminName = "管理者" // 実際は管理者情報から取得

  const handleLogout = () => {
    router.push("/auth/login")
  }

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Shield className="h-6 w-6 text-slate-600" />
              <h1 className="text-2xl font-bold text-gray-900">Bridge Line 管理画面</h1>
            </div>
            <div className="text-lg text-gray-600">{adminName}さん、お疲れ様です</div>
          </div>

          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="icon">
              <Bell className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <Settings className="h-5 w-5" />
            </Button>
            <Avatar className="cursor-pointer">
              <AvatarImage src="/placeholder.svg?height=40&width=40" />
              <AvatarFallback>管理</AvatarFallback>
            </Avatar>
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}