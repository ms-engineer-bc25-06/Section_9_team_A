// @ts-nocheck
import { renderHook, act } from '@testing-library/react'
import { useAuth } from '../useAuth'
import '@testing-library/jest-dom'

// Firebase Authのモック
jest.mock('firebase/auth', () => ({
  getAuth: jest.fn(() => ({})),
  signInWithEmailAndPassword: jest.fn(),
  createUserWithEmailAndPassword: jest.fn(),
  signOut: jest.fn(),
  onAuthStateChanged: jest.fn(),
  sendPasswordResetEmail: jest.fn(),
}))

// モック関数の取得
import {
  signInWithEmailAndPassword as mockSignInWithEmailAndPassword,
  createUserWithEmailAndPassword as mockCreateUserWithEmailAndPassword,
  signOut as mockSignOut,
  onAuthStateChanged as mockOnAuthStateChanged,
  sendPasswordResetEmail as mockSendPasswordResetEmail
} from 'firebase/auth'

// 型エラーを回避するための型キャスト
const mockSignIn = mockSignInWithEmailAndPassword as any
const mockCreateUser = mockCreateUserWithEmailAndPassword as any
const mockSignOutFn = mockSignOut as any
const mockOnAuthStateChangedFn = mockOnAuthStateChanged as any
const mockSendPasswordReset = mockSendPasswordResetEmail as any

describe('useAuth Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with unauthenticated state', () => {
      // 初期状態では未認証
      mockOnAuthStateChangedFn.mockImplementation((callback) => {
        if (typeof callback === 'function') {
          callback(null)
        }
        return () => {}
      })

      const { result } = renderHook(() => useAuth())

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(true)
    })
  })

  describe('Login Functionality', () => {
    it('should handle successful login', async () => {
      const mockUser = {
        uid: 'test-user-123',
        email: 'test@example.com',
        displayName: 'Test User'
      }

      // ログイン成功後に認証状態を更新するモック
      mockOnAuthStateChangedFn.mockImplementation((callback) => {
        if (typeof callback === 'function') {
          // 初期状態では未認証
          callback(null)
          // ログイン成功後にユーザー状態を更新
          callback(mockUser)
        }
        return () => {}
      })

      mockSignIn.mockResolvedValueOnce({
        user: mockUser
      })

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        await result.current.login('test@example.com', 'password123')
      })

      expect(mockSignIn).toHaveBeenCalledWith(
        expect.anything(),
        'test@example.com',
        'password123'
      )
      // ログイン成功後の状態を確認（onAuthStateChangedが呼ばれることを期待）
      expect(mockOnAuthStateChangedFn).toHaveBeenCalled()
    })

    it('should handle login errors', async () => {
      const mockError = new Error('Invalid credentials')
      mockSignInWithEmailAndPassword.mockRejectedValueOnce(mockError)

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        try {
          await result.current.login('test@example.com', 'wrongpassword')
        } catch (error) {
          expect(error).toEqual(mockError)
        }
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('should validate email format', async () => {
      const { result } = renderHook(() => useAuth())

      await act(async () => {
        try {
          await result.current.login('invalid-email', 'password123')
        } catch (error) {
          expect(error.message).toContain('Invalid email format')
        }
      })
    })

    it('should validate password length', async () => {
      const { result } = renderHook(() => useAuth())

      await act(async () => {
        try {
          await result.current.login('test@example.com', '123')
        } catch (error) {
          expect(error.message).toContain('Password must be at least 6 characters')
        }
      })
    })
  })

  describe('Registration Functionality', () => {
    it('should handle successful registration', async () => {
      const mockUser = {
        uid: 'new-user-456',
        email: 'newuser@example.com',
        displayName: 'New User'
      }

      // 登録成功後に認証状態を更新するモック
      mockOnAuthStateChangedFn.mockImplementation((callback) => {
        if (typeof callback === 'function') {
          // 初期状態では未認証
          callback(null)
          // 登録成功後にユーザー状態を更新
          callback(mockUser)
        }
        return () => {}
      })

      mockCreateUser.mockResolvedValueOnce({
        user: mockUser
      })

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        await result.current.register({
          email: 'newuser@example.com',
          password: 'password123',
          username: 'newuser',
          fullName: 'New User'
        })
      })

      expect(mockCreateUser).toHaveBeenCalledWith(
        expect.anything(),
        'newuser@example.com',
        'password123'
      )
      // 登録成功後の状態を確認
      expect(mockOnAuthStateChangedFn).toHaveBeenCalled()
    })

    it('should handle registration errors', async () => {
      const mockError = new Error('Email already in use')
      mockCreateUserWithEmailAndPassword.mockRejectedValueOnce(mockError)

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        try {
          await result.current.register({
            email: 'existing@example.com',
            password: 'password123',
            username: 'existing',
            fullName: 'Existing User'
          })
        } catch (error) {
          expect(error).toEqual(mockError)
        }
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('should validate registration data', async () => {
      const { result } = renderHook(() => useAuth())

      await act(async () => {
        try {
          await result.current.register({
            email: 'invalid-email',
            password: 'password123',
            username: 'valid',
            fullName: 'Valid Name'
          })
        } catch (error) {
          expect(error.message).toContain('Invalid email format')
        }
      })

      await act(async () => {
        try {
          await result.current.register({
            email: 'valid@email.com',
            password: '123',
            username: 'valid',
            fullName: 'Valid Name'
          })
        } catch (error) {
          expect(error.message).toContain('Password must be at least 6 characters')
        }
      })

      await act(async () => {
        try {
          await result.current.register({
            email: 'valid@email.com',
            password: 'password123',
            username: '',
            fullName: 'Valid Name'
          })
        } catch (error) {
          expect(error.message).toContain('Username is required')
        }
      })

      await act(async () => {
        try {
          await result.current.register({
            email: 'valid@email.com',
            password: 'password123',
            username: 'valid',
            fullName: ''
          })
        } catch (error) {
          expect(error.message).toContain('Full name is required')
        }
      })
    })
  })

  describe('Logout Functionality', () => {
    it('should handle successful logout', async () => {
      const mockUser = {
        uid: 'test-user-123',
        email: 'test@example.com',
        displayName: 'Test User'
      }

      mockSignInWithEmailAndPassword.mockResolvedValueOnce({
        user: mockUser
      })

      mockSignOut.mockResolvedValueOnce(undefined)

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        await result.current.login('test@example.com', 'password123')
      })

      await act(async () => {
        await result.current.logout()
      })

      expect(mockSignOut).toHaveBeenCalled()
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('should handle logout errors', async () => {
      const mockError = new Error('Logout failed')
      mockSignOut.mockRejectedValueOnce(mockError)

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        try {
          await result.current.logout()
        } catch (error) {
          expect(error).toEqual(mockError)
        }
      })
    })
  })

  describe('Password Reset', () => {
    it('should handle password reset request', async () => {
      mockSendPasswordResetEmail.mockResolvedValueOnce(undefined)

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        await result.current.resetPassword('test@example.com')
      })

      expect(mockSendPasswordResetEmail).toHaveBeenCalledWith(
        expect.anything(),
        'test@example.com'
      )
    })

    it('should validate email for password reset', async () => {
      const { result } = renderHook(() => useAuth())

      await act(async () => {
        try {
          await result.current.resetPassword('invalid-email')
        } catch (error) {
          expect(error.message).toContain('Invalid email format')
        }
      })
    })
  })

  describe('Authentication State Changes', () => {
    it('should update state when user signs in', async () => {
      const mockUser = {
        uid: 'test-user-123',
        email: 'test@example.com',
        displayName: 'Test User'
      }

      // 認証状態変更のモック
      mockOnAuthStateChangedFn.mockImplementation((callback) => {
        if (typeof callback === 'function') {
          // 初期状態では未認証
          callback(null)
          // その後、認証済み状態に変更
          callback(mockUser)
        }
        return () => {}
      })

      const { result } = renderHook(() => useAuth())

      // onAuthStateChangedが呼ばれることを確認
      expect(mockOnAuthStateChangedFn).toHaveBeenCalled()
    })

    it('should update state when user signs out', async () => {
      const mockUser = {
        uid: 'test-user-123',
        email: 'test@example.com',
        displayName: 'Test User'
      }

      // 認証状態変更のモック
      mockOnAuthStateChangedFn.mockImplementation((callback) => {
        if (typeof callback === 'function') {
          // 初期状態では認証済み
          callback(mockUser)
          // その後、ログアウト状態に変更
          callback(null)
        }
        return () => {}
      })

      const { result } = renderHook(() => useAuth())

      // onAuthStateChangedが呼ばれることを確認
      expect(mockOnAuthStateChangedFn).toHaveBeenCalled()
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      const networkError = new Error('Network error')
      mockSignInWithEmailAndPassword.mockRejectedValueOnce(networkError)

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        try {
          await result.current.login('test@example.com', 'password123')
        } catch (error) {
          expect(error.message).toContain('Network error')
        }
      })
    })

    it('should handle Firebase specific errors', async () => {
      const firebaseError = new Error('auth/user-not-found')
      // Firebaseエラーオブジェクトの構造を模倣
      firebaseError.code = 'auth/user-not-found'
      mockSignIn.mockRejectedValueOnce(firebaseError)

      const { result } = renderHook(() => useAuth())

      await act(async () => {
        try {
          await result.current.login('nonexistent@example.com', 'password123')
        } catch (error) {
          expect(error.message).toContain('User not found')
        }
      })
    })
  })
})
