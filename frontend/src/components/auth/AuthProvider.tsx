// 認証状態をアプリ全体に提供するコンテキスト
"use client"

import { createContext, useContext, type ReactNode } from "react"
import { useAuth as useAuthHook } from "@/hooks/useAuth"

interface AuthContextType {
  user: any
  firebaseUser: any
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  isLoading: boolean
  error: string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const auth = useAuthHook()

  return (
    <AuthContext.Provider value={auth}>
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
