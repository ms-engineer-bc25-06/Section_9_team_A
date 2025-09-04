import { useState, useEffect, useCallback } from 'react'
import { 
  getAuth, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged,
  sendPasswordResetEmail,
  User
} from 'firebase/auth'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
}

interface LoginCredentials {
  email: string
  password: string
}

interface RegisterData {
  email: string
  password: string
  username: string
  fullName: string
}

interface AuthHook extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  resetPassword: (email: string) => Promise<void>
}

export const useAuth = (): AuthHook => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true
  })

  const auth = getAuth()

  // 認証状態の監視
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setAuthState({
        user,
        isAuthenticated: !!user,
        isLoading: false
      })
    })

    return () => unsubscribe()
  }, [auth])

  // バリデーション関数
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const validatePassword = (password: string): boolean => {
    return password.length >= 6
  }

  // ログイン
  const login = useCallback(async (email: string, password: string): Promise<void> => {
    if (!validateEmail(email)) {
      throw new Error('Invalid email format')
    }
    if (!validatePassword(password)) {
      throw new Error('Password must be at least 6 characters')
    }

    try {
      await signInWithEmailAndPassword(auth, email, password)
    } catch (error: any) {
      // Firebase固有のエラーメッセージを日本語に変換
      if (error.code === 'auth/user-not-found') {
        throw new Error('User not found')
      } else if (error.code === 'auth/wrong-password') {
        throw new Error('Wrong password')
      } else if (error.code === 'auth/invalid-email') {
        throw new Error('Invalid email')
      } else if (error.code === 'auth/user-disabled') {
        throw new Error('User account has been disabled')
      } else if (error.code === 'auth/too-many-requests') {
        throw new Error('Too many failed login attempts')
      } else {
        throw error
      }
    }
  }, [auth])

  // 登録
  const register = useCallback(async (data: RegisterData): Promise<void> => {
    const { email, password, username, fullName } = data

    if (!validateEmail(email)) {
      throw new Error('Invalid email format')
    }
    if (!validatePassword(password)) {
      throw new Error('Password must be at least 6 characters')
    }
    if (!username.trim()) {
      throw new Error('Username is required')
    }
    if (!fullName.trim()) {
      throw new Error('Full name is required')
    }

    try {
      await createUserWithEmailAndPassword(auth, email, password)
    } catch (error: any) {
      if (error.code === 'auth/email-already-in-use') {
        throw new Error('Email already in use')
      } else if (error.code === 'auth/invalid-email') {
        throw new Error('Invalid email')
      } else if (error.code === 'auth/weak-password') {
        throw new Error('Password is too weak')
      } else {
        throw error
      }
    }
  }, [auth])

  // ログアウト
  const logout = useCallback(async (): Promise<void> => {
    try {
      await signOut(auth)
    } catch (error: any) {
      throw new Error('Logout failed')
    }
  }, [auth])

  // パスワードリセット
  const resetPassword = useCallback(async (email: string): Promise<void> => {
    if (!validateEmail(email)) {
      throw new Error('Invalid email format')
    }

    try {
      await sendPasswordResetEmail(auth, email)
    } catch (error: any) {
      if (error.code === 'auth/user-not-found') {
        throw new Error('User not found')
      } else if (error.code === 'auth/invalid-email') {
        throw new Error('Invalid email')
      } else {
        throw error
      }
    }
  }, [auth])

  return {
    ...authState,
    login,
    register,
    logout,
    resetPassword
  }
}
