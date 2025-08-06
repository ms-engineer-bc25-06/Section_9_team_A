// 認証状態をアプリ全体に提供するコンテキスト
"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"

interface User {
  id: string
  name: string
  email: string
  department: string
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = () => {
      try {
        // 自動ログイン機能を無効化
        // const savedUser = localStorage.getItem("bridge-line-user")
        // if (savedUser) {
        //   setUser(JSON.parse(savedUser))
        // }

        // 常にログアウト状態から開始
        setUser(null)
      } catch (error) {
        console.error("Auth check failed:", error)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      // シミュレート
      await new Promise((resolve) => setTimeout(resolve, 1000))

      const mockUser = {
        id: "1",
        name: "田中太郎",
        email,
        department: "開発部",
      }

      setUser(mockUser)
      localStorage.setItem("bridge-line-user", JSON.stringify(mockUser))
    } catch (error) {
      console.error("Login failed:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem("bridge-line-user")
  }

  return <AuthContext.Provider value={{ user, login, logout, isLoading }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
