// 認証状態をアプリ全体に提供するコンテキスト
"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { onAuthStateChanged, signInWithEmailAndPassword, signOut, User as FirebaseUser } from "firebase/auth"
import { useRouter } from "next/navigation"
import { auth } from "@/lib/auth"

interface AuthContextType {
  user: FirebaseUser | null
  backendToken: string | null
  login: (email: string, password: string) => Promise<string | null>
  temporaryLogin: (email: string, password: string) => Promise<string | null>
  logout: () => Promise<void>
  isLoading: boolean
  adminLogin: (email: string, password: string) => Promise<string | null>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export { AuthContext }

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<FirebaseUser | null>(null)
  const [backendToken, setBackendToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Firebaseログイン状態を監視
  useEffect(() => {
    let profileSyncCleanup: (() => void) | null = null
    
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser || null) // nullを明示
      
      if (firebaseUser) {
        // Firebase認証が成功した場合、バックエンドトークンが既に存在するかチェック
        const existingToken = localStorage.getItem('jwt_token')
        if (existingToken) {
          // 既存のトークンがある場合は、そのトークンを使用
          setBackendToken(existingToken)
          console.log("✅ 既存のバックエンドトークンを使用")
          
          // Firebaseプロフィール変更の監視を開始
          profileSyncCleanup = startProfileSync(firebaseUser, existingToken)
        } else {
          // バックエンドトークンがない場合は、明示的なログインが必要
          console.log("⚠️ バックエンドトークンがありません。明示的なログインが必要です。")
          setBackendToken(null)
        }
      } else {
        // ユーザーがログアウトした場合
        setBackendToken(null)
        localStorage.removeItem('jwt_token')
        console.log("🔒 ユーザーログアウト、バックエンドトークンをクリア")
        
        // プロフィール同期のクリーンアップ
        if (profileSyncCleanup) {
          profileSyncCleanup()
          profileSyncCleanup = null
        }
      }
      
      setIsLoading(false)
    })

    return () => {
      unsubscribe()
      if (profileSyncCleanup) {
        profileSyncCleanup()
      }
    }
  }, [])

  // Firebaseプロフィール変更の監視と同期
  const startProfileSync = (firebaseUser: FirebaseUser, backendToken: string) => {
    // 現在のdisplay_nameを保存
    let lastDisplayName = firebaseUser.displayName
    
    // FirebaseのIDトークン変更を監視（プロフィール変更時に発火）
    const idTokenUnsubscribe = auth.onIdTokenChanged(async (user) => {
      if (user && user.displayName !== lastDisplayName && user.displayName) {
        console.log(`🔄 名前の変更を検出: "${lastDisplayName}" → "${user.displayName}"`)
        
        try {
          const syncResponse = await fetch('http://localhost:8000/api/v1/users/profile', {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${backendToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              full_name: user.displayName
            })
          })
          
          if (syncResponse.ok) {
            console.log("✅ 名前の自動同期完了")
            lastDisplayName = user.displayName
          } else {
            console.warn("名前の自動同期に失敗:", syncResponse.status)
          }
        } catch (syncError) {
          console.error("名前の自動同期でエラー:", syncError)
        }
      }
    })
    
    // 定期的な同期チェック（フォールバック用、10分ごと）
    const profileSyncInterval = setInterval(async () => {
      try {
        // Firebaseの現在のプロフィールを取得
        await firebaseUser.reload()
        const currentDisplayName = firebaseUser.displayName
        
        // display_nameが変更された場合、バックエンドに同期
        if (currentDisplayName !== lastDisplayName && currentDisplayName) {
          console.log(`🔄 定期的な名前変更検出: "${lastDisplayName}" → "${currentDisplayName}"`)
          
          try {
            const syncResponse = await fetch('http://localhost:8000/api/v1/users/profile', {
              method: 'PUT',
              headers: {
                'Authorization': `Bearer ${backendToken}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                full_name: currentDisplayName
              })
            })
            
            if (syncResponse.ok) {
              console.log("✅ 名前の定期同期完了")
              lastDisplayName = currentDisplayName
            } else {
              console.warn("名前の定期同期に失敗:", syncResponse.status)
            }
          } catch (syncError) {
            console.error("名前の定期同期でエラー:", syncError)
          }
        }
      } catch (error) {
        console.error("プロフィール同期チェックでエラー:", error)
      }
    }, 10 * 60 * 1000) // 10分ごと
    
    // クリーンアップ関数を返す
    return () => {
      idTokenUnsubscribe()
      clearInterval(profileSyncInterval)
    }
  }

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
            console.log("✅ バックエンドユーザー登録・同期完了")
            
            // JWTトークンをローカルストレージに保存
            localStorage.setItem('jwt_token', token)
            
            // ログイン後にプロフィール情報を強制的に再取得
            // 管理者が作成したユーザーの名前と部署を正しく反映するため
            try {
              console.log("🔄 ログイン後のプロフィール情報を再取得中...")
              const profileResponse = await fetch('http://localhost:8000/api/v1/users/profile', {
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
              });
              if (profileResponse.ok) {
                const profileData = await profileResponse.json();
                console.log("📊 取得したプロフィール情報:", {
                  full_name: profileData.full_name,
                  department: profileData.department,
                  is_first_login: profileData.is_first_login
                });
                
                // 初回ログインフラグは記録するが、自動リダイレクトは行わない
                console.log("初回ログイン状態:", profileData.is_first_login);
              } else {
                console.warn("プロフィール取得に失敗:", profileResponse.status);
              }
            } catch (profileError) {
              console.warn("プロフィール確認に失敗:", profileError);
            }
            
            return token
          } else {
            const errorData = await response.json().catch(() => ({}))
            console.warn(`バックエンド連携に失敗 (ステータス: ${response.status}) - ${errorData.detail || 'Unknown error'}`)
            
            // エラーの詳細をログに出力
            if (errorData.detail) {
              console.error("エラー詳細:", errorData.detail)
            }
            
            setBackendToken(null)
            localStorage.removeItem('jwt_token')
            
            // バックエンド連携に失敗した場合は、Firebase認証もロールバック
            await signOut(auth)
            throw new Error('サーバー内部エラーが発生しました。しばらく待ってから再試行してください。')
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
            
            // JWTトークンをローカルストレージに保存
            localStorage.setItem('jwt_token', token)
            
            // パスワード設定が必要な場合のみパスワード変更画面にリダイレクト
            if (data.needs_password_setup) {
              window.location.href = '/auth/change-password';
              return token;
            }
            
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

  // 管理者ログイン
  const adminLogin = async (email: string, password: string): Promise<string | null> => {
    setIsLoading(true)
    try {
      // 1. Firebase 認証
      await signInWithEmailAndPassword(auth, email, password)
      
      // 2. バックエンドでユーザー登録・同期
      const user = auth.currentUser
      if (user) {
        try {
          const idToken = await user.getIdToken()
          console.log("管理者バックエンドユーザー登録・同期開始...")
          const response = await fetch('http://localhost:8000/api/v1/auth/firebase-login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              id_token: idToken,
              display_name: user.displayName || user.email || "管理者"
            })
          })
          
          if (response.ok) {
            const data = await response.json()
            const token = data.access_token
            setBackendToken(token)
            console.log("✅ 管理者バックエンドユーザー登録・同期完了")
            
            // JWTトークンをローカルストレージに保存
            localStorage.setItem('jwt_token', token)
            
            return token
          } else {
            const errorData = await response.json().catch(() => ({}))
            console.warn(`管理者バックエンド連携に失敗 (ステータス: ${response.status}) - ${errorData.detail || 'Unknown error'}`)
            
            // エラーの詳細をログに出力
            if (errorData.detail) {
              console.error("エラー詳細:", errorData.detail)
            }
            
            setBackendToken(null)
            localStorage.removeItem('jwt_token')
            
            // バックエンド連携に失敗した場合は、Firebase認証もロールバック
            await signOut(auth)
            throw new Error('サーバー内部エラーが発生しました。しばらく待ってから再試行してください。')
          }
        } catch (backendError) {
          console.error("❌ 管理者バックエンド連携エラー:", backendError)
          // バックエンド認証が失敗した場合は、Firebase認証もロールバック
          await signOut(auth)
          throw new Error('バックエンド認証に失敗しました。しばらく待ってから再試行してください。')
        }
      }
      return null
    } catch (error: any) {
      console.error("管理者Login failed:", error.code, error.message);
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
    <AuthContext.Provider value={{ user, backendToken, login, temporaryLogin, logout, isLoading, adminLogin }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  const router = useRouter()
  
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  
  // 追加の機能を提供
  const requireAuth = (): boolean => {
    return !!context.user
  }
  
  const redirectToLogin = () => {
    router.push('/auth/login')
  }
  
  return {
    ...context,
    isAuthenticated: !!context.user,
    requireAuth,
    redirectToLogin,
  }
}
