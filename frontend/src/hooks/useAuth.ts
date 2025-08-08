import { useState, useEffect } from "react"
import { User as FirebaseUser, onAuthStateChanged } from "firebase/auth"
import { auth } from "@/lib/firebase"
import { fetchWithAuth } from "@/lib/auth"

interface User {
  id: number
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  bio?: string
  is_active: boolean
  is_verified: boolean
  is_premium: boolean
  subscription_status: string
  created_at: string
  updated_at?: string
  last_login_at?: string
}

interface AuthContextType {
  user: User | null
  firebaseUser: FirebaseUser | null
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  isLoading: boolean
  error: string | null
}

export function useAuth(): AuthContextType {
  const [user, setUser] = useState<User | null>(null)
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Firebase認証状態の監視
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setFirebaseUser(firebaseUser)
      
      if (firebaseUser) {
        try {
          // Firebaseユーザーが存在する場合、バックエンドからユーザー情報を取得
          const response = await fetchWithAuth("/api/v1/auth/me")
          if (response.ok) {
            const userData = await response.json()
            setUser(userData)
          } else {
            console.error("Failed to fetch user data from backend")
            setUser(null)
          }
        } catch (error) {
          console.error("Error fetching user data:", error)
          setUser(null)
        }
      } else {
        setUser(null)
      }
      
      setIsLoading(false)
    })

    return () => unsubscribe()
  }, [])

  // ログイン処理
  const login = async (email: string, password: string) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const { signInWithEmailAndPassword } = await import("firebase/auth")
      await signInWithEmailAndPassword(auth, email, password)
    } catch (error: any) {
      console.error("Login failed:", error.code, error.message)
      setError(getErrorMessage(error.code))
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  // ログアウト処理
  const logout = async () => {
    try {
      const { signOut } = await import("firebase/auth")
      await signOut(auth)
      setUser(null)
    } catch (error) {
      console.error("Logout failed:", error)
      throw error
    }
  }

  // エラーメッセージの変換
  const getErrorMessage = (errorCode: string): string => {
    switch (errorCode) {
      case "auth/user-not-found":
        return "ユーザーが見つかりません"
      case "auth/wrong-password":
        return "パスワードが間違っています"
      case "auth/invalid-email":
        return "無効なメールアドレスです"
      case "auth/weak-password":
        return "パスワードが弱すぎます"
      case "auth/email-already-in-use":
        return "このメールアドレスは既に使用されています"
      case "auth/too-many-requests":
        return "試行回数が多すぎます。しばらく待ってから再試行してください"
      default:
        return "認証エラーが発生しました"
    }
  }

  return {
    user,
    firebaseUser,
    login,
    logout,
    isLoading,
    error
  }
}
