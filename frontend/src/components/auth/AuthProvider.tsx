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
    let profileSyncCleanup: (() => void) | null = null
    
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
            
            // Firebaseプロフィール変更の監視を開始
            profileSyncCleanup = startProfileSync(firebaseUser, token)
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
          console.error("バックエンド連携でエラー:", error)
          setBackendToken(null)
          localStorage.removeItem('jwt_token')
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
            
            // 初回ログイン判定 (本パスワード設定後)
            try {
              const profileResponse = await fetch('http://localhost:8000/api/v1/users/profile', {
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
              });
              if (profileResponse.ok) {
                const profileData = await profileResponse.json();
                // 名前と部署は自動で入るので、初回ログインフラグのみチェック
                if (profileData.is_first_login) {
                  window.location.href = '/profile/edit';
                  return token;
                }
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
            
            // 仮パスワードでのログインの場合は、本パスワード登録ページにリダイレクト
            if (data.has_temporary_password) {
              window.location.href = '/auth/change-password';
              return token;
            }
            
            // 初回ログイン判定 (本パスワード設定後)
            try {
              const profileResponse = await fetch('http://localhost:8000/api/v1/users/profile', {
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
              });
              if (profileResponse.ok) {
                const profileData = await profileResponse.json();
                // 名前と部署は自動で入るので、初回ログインフラグのみチェック
                if (profileData.is_first_login) {
                  window.location.href = '/profile/edit';
                  return token;
                }
              }
            } catch (profileError) {
              console.warn("プロフィール確認に失敗:", profileError)
              // プロフィール確認に失敗した場合は通常のフローを継続
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
