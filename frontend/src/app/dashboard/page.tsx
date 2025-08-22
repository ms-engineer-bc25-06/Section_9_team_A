// ダッシュボードトップ
"use client"

import type React from "react"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { DashboardCards } from "@/components/dashboard/DashboardCards"
import { apiClient } from "@/lib/apiClient"

const DashboardPage: React.FC = () => {
  const { user, backendToken, isLoading } = useAuth()
  const [backendAuthChecked, setBackendAuthChecked] = useState(false)
  const router = useRouter()

  useEffect(() => {
    if (!user && !isLoading) {
      router.push("/")
      return
    }

    // バックエンド認証確認（1回のみ実行）
    if (user && backendToken && !backendAuthChecked) {
      const checkBackendAuth = async () => {
        try {
          console.log("② バックエンド認証確認開始...")
          const response = await apiClient.get('/api/v1/auth/me')
          
          if (response.ok) {
            const userData = await response.json()
            console.log("✅ バックエンド認証確認済み")
            setBackendAuthChecked(true)
          } else {
            const errorText = await response.text()
            console.warn("⚠️ バックエンド認証失敗 (ステータス:", response.status, ")", errorText)
            // バックエンドエラーでもダッシュボード表示を継続（Firebase認証は成功済み）
            setBackendAuthChecked(true)
          }
        } catch (error) {
          console.error("❌ バックエンド認証エラー (接続問題):", error)
          // 接続エラーでもダッシュボード表示を継続（Firebase認証は成功済み）
          setBackendAuthChecked(true)
        }
      }
      
      checkBackendAuth()
    } else if (user && !backendToken && !backendAuthChecked) {
      // バックエンドトークンがない場合は、Firebase認証のみでダッシュボードを表示
      setBackendAuthChecked(true)
    }
  }, [user, backendToken, isLoading, backendAuthChecked, router])

  if (isLoading || !user || !backendAuthChecked) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return <DashboardCards />
}

export default DashboardPage