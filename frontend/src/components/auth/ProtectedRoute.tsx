"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { Spinner } from "@/components/ui/Spinner"

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: "user" | "admin" | "team_member"
  redirectTo?: string
  showLoading?: boolean
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole = "user",
  redirectTo = "/auth/login",
  showLoading = true
}) => {
  const { user, backendToken, isLoading } = useAuth()
  const router = useRouter()
  const [isChecking, setIsChecking] = useState(true)
  const [hasPermission, setHasPermission] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      // ローディング中は待機
      if (isLoading) return

      // ユーザーが未ログインの場合
      if (!user) {
        router.push(redirectTo)
        return
      }

      // 権限チェックが必要な場合
      if (requiredRole !== "user" && backendToken) {
        try {
          // 管理者権限チェック
          if (requiredRole === "admin") {
            const response = await fetch('http://localhost:8000/api/v1/admin-role/check-admin', {
              headers: {
                'Authorization': `Bearer ${backendToken}`,
                'Content-Type': 'application/json'
              }
            })
            
            if (!response.ok) {
              router.push("/auth/login?error=insufficient_permissions")
              return
            }
          }

          // チームメンバー権限チェック
          if (requiredRole === "team_member") {
            const response = await fetch('http://localhost:8000/api/v1/teams/my-teams', {
              headers: {
                'Authorization': `Bearer ${backendToken}`,
                'Content-Type': 'application/json'
              }
            })
            
            if (!response.ok || (await response.json()).teams.length === 0) {
              router.push("/auth/login?error=no_team_access")
              return
            }
          }

          setHasPermission(true)
        } catch (error) {
          console.error("権限チェックエラー:", error)
          router.push("/auth/login?error=auth_error")
          return
        }
      } else {
        setHasPermission(true)
      }

      setIsChecking(false)
    }

    checkAuth()
  }, [user, backendToken, isLoading, requiredRole, redirectTo, router])

  // ローディング中
  if (isLoading || isChecking) {
    return showLoading ? (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Spinner className="h-8 w-8 mx-auto mb-4" />
          <p className="text-gray-600">認証確認中...</p>
        </div>
      </div>
    ) : null
  }

  if (!hasPermission) {
    return null
  }

  // 認証済みで権限がある場合、子コンポーネントを表示
  return <>{children}</>
}

export default ProtectedRoute