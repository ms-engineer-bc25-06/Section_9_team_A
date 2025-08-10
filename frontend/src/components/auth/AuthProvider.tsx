// 認証状態をアプリ全体に提供するコンテキスト
"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { onAuthStateChanged, signInWithEmailAndPassword, signOut, User as FirebaseUser } from "firebase/auth"
import { auth } from "@/lib/firebase"

interface AuthContextType {
  user: FirebaseUser | null
  backendToken: string | null
  login: (email: string, password: string) => Promise<string | null>
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
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser || null) // nullを明示
      if (!firebaseUser) {
        setBackendToken(null) // ユーザーがログアウトした場合、バックエンドトークンもクリア
      }
      setIsLoading(false)           // 読み込み完了
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
            console.log("✅ バックエンドユーザー登録・同期完了")
            return token
          } else {
            console.warn("バックエンドユーザー登録に失敗 (ステータス:", response.status, ") - Firebase認証は成功")
            // バックエンド認証が失敗しても、Firebase認証は成功しているのでログインを継続
            return null
          }
        } catch (backendError) {
          console.warn("バックエンド連携エラー (接続問題):", backendError)
          // Firebase認証は成功しているので、バックエンドエラーでもログインを継続
          return null
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

  // ログアウト
  const logout = async () => {
    await signOut(auth)
    setUser(null)
    setBackendToken(null)
  }

  return (
    <AuthContext.Provider value={{ user, backendToken, login, logout, isLoading }}>
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
