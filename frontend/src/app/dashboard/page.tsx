// ダッシュボードトップ
"use client"

import type React from "react"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { DashboardCards } from "@/components/dashboard/DashboardCards"

const DashboardPage: React.FC = () => {
  const { user, isLoading } = useAuth()
  const [backendAuthChecked, setBackendAuthChecked] = useState(false)
  const router = useRouter()

  useEffect(() => {
    if (!user && !isLoading) {
      router.push("/")
      return
    }

    // バックエンド認証確認（1回のみ実行）
    if (user && !backendAuthChecked) {
      const checkBackendAuth = async () => {
        try {
          const idToken = await user.getIdToken()
          const response = await fetch('http://localhost:8000/api/v1/users/me', {
            headers: {
              'Authorization': `Bearer ${idToken}`,
              'Content-Type': 'application/json'
            }
          })
          
          if (response.ok) {
            console.log("バックエンド認証確認済み")
            setBackendAuthChecked(true)
          } else {
            console.warn("バックエンド認証失敗 (ステータス:", response.status, ")")
            // バックエンドエラーでもダッシュボード表示を継続（Firebase認証は成功済み）
            setBackendAuthChecked(true)
          }
        } catch (error) {
          console.error("バックエンド認証エラー (接続問題):", error)
          // 接続エラーでもダッシュボード表示を継続（Firebase認証は成功済み）
          setBackendAuthChecked(true)
        }
      }
      
      checkBackendAuth()
    }
  }, [user, isLoading, backendAuthChecked, router])

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