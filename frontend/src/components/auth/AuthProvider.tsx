// 認証状態をアプリ全体に提供するコンテキスト
"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { onAuthStateChanged, signInWithEmailAndPassword, signOut, User as FirebaseUser } from "firebase/auth"
import { auth } from "@/lib/auth"

interface AuthContextType {
  user: FirebaseUser | null
  backendToken: string | null
  login: (email: string, password: string) => Promise<string | null>
  temporaryLogin: (email: string, password: string) => Promise<string | null>
  logout: () => Promise<void>
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<FirebaseUser | null>(null)
  const [backendToken, setBackendToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Firebaseログイン状態を監視
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser || null) // nullを明示
      
      if (firebaseUser) {
        // Firebase認証が成功したら、自動的にバックエンドと連携
        try {
          console.log("🔄 Firebase認証成功、バックエンド連携を開始...")
          const idToken = await firebaseUser.getIdToken()
          const response = await fetch('http://localhost:8000/api/v1/auth/firebase-login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              id_token: idToken,
              display_name: firebaseUser.displayName || firebaseUser.email || "ユーザー"
            })
          })
          
          if (response.ok) {
            const data = await response.json()
            const token = data.access_token
            setBackendToken(token)
            console.log("✅ バックエンドユーザー登録・同期完了")
            
            // JWTトークンをローカルストレージに保存
            localStorage.setItem('jwt_token', token)
          } else {
            const errorData = await response.json().catch(() => ({}))
            console.warn(`バックエンド連携に失敗 (ステータス: ${response.status}) - ${errorData.detail || 'Unknown error'}`)
            
            // エラーの詳細をログに出力
            if (errorData.detail) {
              console.error("エラー詳細:", errorData.detail)
            }
            
            setBackendToken(null)
            localStorage.removeItem('jwt_token')
          }
        } catch (error) {
          console.warn("バックエンド連携エラー:", error)
          setBackendToken(null)
          localStorage.removeItem('jwt_token')
        }
      } else {
        setBackendToken(null) // ユーザーがログアウトした場合、バックエンドトークンもクリア
        localStorage.removeItem('jwt_token')
      }
      
      setIsLoading(false) // 読み込み完了
    })
    return () => unsubscribe()
  }, [])

  // ログイン
  const login = async (email: string, password: string): Promise<string | null> => {
    setIsLoading(true)
    try {
      // 1. Firebase 認証
      await signInWithEmailAndPassword(auth, email, password)
      
      // 2. バックエンドでユーザー登録・同期
      const user = auth.currentUser
      if (user) {
        try {
          const idToken = await user.getIdToken()
          console.log("バックエンドユーザー登録・同期開始...")
          const response = await fetch('http://localhost:8000/api/v1/auth/firebase-login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              id_token: idToken,
              display_name: user.displayName || user.email || "ユーザー"
            })
          })
          
          if (response.ok) {
            const data = await response.json()
            const token = data.access_token
            setBackendToken(token)
            
            // JWTトークンをローカルストレージに保存
            localStorage.setItem('jwt_token', token)
            
            console.log("✅ バックエンドユーザー登録・同期完了")
            return token
          } else {
            const errorData = await response.json().catch(() => ({}))
            console.warn(`バックエンドユーザー登録に失敗 (ステータス: ${response.status}) - ${errorData.detail || 'Unknown error'}`)
            
            // 400エラーの場合は詳細なエラーメッセージを表示
            if (response.status === 400) {
              throw new Error(`バックエンドエラー: ${errorData.detail || 'Invalid request'}`)
            }
            
            // 500エラーの場合は一般的なエラーメッセージを表示
            if (response.status === 500) {
              throw new Error('サーバー内部エラーが発生しました。しばらく待ってから再試行してください。')
            }
            
            // その他のエラーの場合
            throw new Error(`認証エラー: ${response.status} ${response.statusText}`)
          }
        } catch (backendError) {
          console.error("❌ バックエンド連携エラー:", backendError)
          // バックエンド認証が失敗した場合は、Firebase認証もロールバック
          await signOut(auth)
          throw new Error('バックエンド認証に失敗しました。しばらく待ってから再試行してください。')
        }
      }
      return null
    } catch (error: any) {
      console.error("Login failed:", error.code, error.message);
      throw error;
    } finally {
      setIsLoading(false)
    }
  }

  // 仮パスワードログイン
  const temporaryLogin = async (email: string, password: string): Promise<string | null> => {
    setIsLoading(true)
    try {
      // 1. Firebaseで仮パスワード認証
      console.log("🔥 Firebaseで仮パスワード認証を開始...")
      console.log("📧 メールアドレス:", email)
      console.log("🔑 パスワード:", password)
      console.log("🌐 Firebase設定:", auth.app.options)
      await signInWithEmailAndPassword(auth, email, password)
      
      // 2. Firebase認証が成功したら、バックエンドと連携
      const user = auth.currentUser
      if (user) {
        try {
          const idToken = await user.getIdToken()
          console.log("バックエンド連携開始...")
          const response = await fetch('http://localhost:8000/api/v1/auth/firebase-login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              id_token: idToken,
              display_name: user.displayName || user.email || "ユーザー"
            })
          })
          
          if (response.ok) {
            const data = await response.json()
            const token = data.access_token
            setBackendToken(token)
            console.log("✅ 仮パスワードログイン成功")
            return token
          } else {
            const errorData = await response.json().catch(() => ({}))
            console.warn(`バックエンド連携失敗 (ステータス: ${response.status}) - ${errorData.detail || 'Unknown error'}`)
            throw new Error(errorData.detail || 'バックエンド連携に失敗しました')
          }
        } catch (backendError) {
          console.error("❌ バックエンド連携エラー:", backendError)
          // バックエンド認証が失敗した場合は、Firebase認証もロールバック
          await signOut(auth)
          throw new Error('バックエンド連携に失敗しました。しばらく待ってから再試行してください。')
        }
      }
      return null
    } catch (error: any) {
      console.error("Temporary login failed:", error.code, error.message);
      throw error;
    } finally {
      setIsLoading(false)
    }
  }

  // ログアウト
  const logout = async () => {
    await signOut(auth)
    setUser(null)
    setBackendToken(null)
    localStorage.removeItem('jwt_token')
  }

  return (
    <AuthContext.Provider value={{ user, backendToken, login, temporaryLogin, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
