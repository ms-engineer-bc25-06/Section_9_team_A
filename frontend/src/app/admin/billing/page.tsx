// 管理者用決済・サブスクリプション管理ページ
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Users, CreditCard, AlertTriangle, CheckCircle, DollarSign, ArrowLeft } from "lucide-react"
import { AdminBillingOverview } from "@/components/admin/AdminBillingOverview"
import { AdminBillingActions } from "@/components/admin/AdminBillingActions"
import Link from "next/link"
import { getAuth, onAuthStateChanged } from "firebase/auth"

export default function AdminBillingPage() {
  const [userCount, setUserCount] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // 認証トークンを取得する関数
  const getAuthToken = async (): Promise<string | null> => {
    try {
      const auth = getAuth()
      const user = auth.currentUser
      
      if (user) {
        return await user.getIdToken()
      } else {
        // 開発環境では認証エラーでもnullを返す（モックデータを使用）
        if (process.env.NODE_ENV === 'development') {
          console.warn('認証されていませんが、開発環境のためモックデータを使用します。')
          return null
        }
        throw new Error('ユーザーが認証されていません')
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.warn('認証トークン取得エラー:', error)
        return null
      }
      throw error
    }
  }

  useEffect(() => {
    // 開発環境での認証状態を確認
    if (process.env.NODE_ENV === 'development') {
      const auth = getAuth()
      console.log('現在の認証状態:', auth.currentUser ? 'ログイン済み' : '未ログイン')
    }
    
    fetchUserCount()
    
    // 定期的にユーザー数を更新（5分ごと）
    const interval = setInterval(fetchUserCount, 5 * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [])

    const fetchUserCount = async () => {
    try {
      setIsLoading(true)
      // 認証トークンを取得（Firebase認証から）
      const token = await getAuthToken()
      
      // 開発環境でトークンが取得できない場合はモックデータを使用
      if (!token && process.env.NODE_ENV === 'development') {
        console.warn('認証トークンが取得できません。モックデータを使用します。')
        setUserCount(15)
        return
      }
      
      // トークンがない場合はAPIコールをスキップ
      if (!token) {
        throw new Error('認証が必要です。ログインしてください。')
      }
      
      const response = await fetch('/api/v1/admin/billing/user-count', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('認証が必要です。ログインしてください。')
        } else if (response.status === 404) {
          // 開発環境ではモックデータを使用
          console.warn('APIエンドポイントが見つかりません。モックデータを使用します。')
          setUserCount(15) // 開発環境用のモックデータ
          return
        }
        throw new Error('ユーザー数の取得に失敗しました')
      }
      
      const data = await response.json()
      setUserCount(data.total_users)
    } catch (err) {
      console.error('ユーザー数取得エラー:', err)
      // 開発環境ではエラーでもモックデータを使用
      if (process.env.NODE_ENV === 'development') {
        setUserCount(15)
        setError(null)
      } else {
        setError(err instanceof Error ? err.message : 'エラーが発生しました')
      }
    } finally {
      setIsLoading(false)
    }
  }

  // 開発環境用: テストのためにユーザー数を強制的に15人に設定
  // ただし、セッションストレージに新しいユーザーがいる場合はそれを考慮
  const [pendingUsers, setPendingUsers] = useState<string | null>(null)
  const [testUserCount, setTestUserCount] = useState(process.env.NODE_ENV === 'development' ? 15 : userCount)
  
  // セッションストレージの読み込みをuseEffectで実行（クライアントサイドのみ）
  useEffect(() => {
    try {
      const stored = sessionStorage.getItem('pendingUsers')
      setPendingUsers(stored)
      
      if (stored) {
        const newUsers = JSON.parse(stored)
        setTestUserCount(prev => prev + newUsers.length)
      }
    } catch (error) {
      console.error('Error parsing pending users:', error)
    }
  }, [])
  
  const isFreeTier = testUserCount <= 10
  const overLimit = testUserCount > 10
  const additionalUsers = Math.max(0, testUserCount - 10)
  const additionalCost = additionalUsers * 500

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

    return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/admin/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                ダッシュボードに戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">利用状況・課金管理</h1>
        </div>
      </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">利用状況・課金管理</h1>
          <p className="text-gray-600">システムの利用状況と決済履歴を確認できます</p>
          
          {/* 開発環境用の注意書き */}
          {process.env.NODE_ENV === 'development' && (
            <Alert className="mt-4 border-yellow-200 bg-yellow-50">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <AlertDescription className="text-yellow-800">
                <strong>開発環境:</strong> テスト用にユーザー数を15人に設定しています。モック決済機能が利用できます。
              </AlertDescription>
            </Alert>
          )}
        </div>

        {error && (
          <Alert className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {successMessage && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">{successMessage}</AlertDescription>
          </Alert>
        )}

        {/* アクションボタン */}
        <div className="mb-6 flex items-center justify-between">
          <Link href="/admin/billing/add-users">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
              <Users className="h-4 w-4 mr-2" />
              ユーザーを追加
            </Button>
          </Link>
          
          <Button 
            onClick={fetchUserCount} 
            variant="outline" 
            disabled={isLoading}
            className="flex items-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span>更新中...</span>
              </>
            ) : (
              <>
                <div className="w-4 h-4">🔄</div>
                <span>情報を更新</span>
              </>
            )}
          </Button>
          </div>

                {/* 詳細情報 */}
        <AdminBillingOverview 
          userCount={testUserCount}
          isFreeTier={isFreeTier}
          additionalUsers={additionalUsers}
          additionalCost={additionalCost}
        />

        {/* 決済情報 */}
        <div className="mt-12">
          <AdminBillingActions 
            userCount={testUserCount}
            additionalUsers={additionalUsers}
            additionalCost={additionalCost}
            onRefresh={fetchUserCount}
          />
        </div>


      </div>
    </div>
  )
}