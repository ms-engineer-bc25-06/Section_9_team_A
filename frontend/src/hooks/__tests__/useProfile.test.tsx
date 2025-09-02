import { renderHook, act, waitFor } from '@testing-library/react'
import { useProfile } from '../useProfile'
import '@testing-library/jest-dom'

// モック
jest.mock('@/lib/apiClient', () => ({
  apiGet: jest.fn()
}))

jest.mock('@/components/auth/AuthProvider', () => ({
  useAuth: jest.fn()
}))

const mockApiGet = require('@/lib/apiClient').apiGet
const mockUseAuth = require('@/components/auth/AuthProvider').useAuth

describe('useProfile Hook', () => {
  const mockUser = {
    uid: 'test-user-123',
    email: 'test@example.com',
    displayName: 'Test User'
  }

  const mockProfile = {
    full_name: 'Test User',
    nickname: 'Test',
    department: 'Engineering',
    join_date: '2024-01-01',
    birth_date: '1990-01-01',
    hometown: 'Tokyo',
    residence: 'Tokyo',
    hobbies: 'Programming',
    student_activities: 'Coding Club',
    holiday_activities: 'Travel',
    favorite_food: 'Sushi',
    favorite_media: 'Movies',
    favorite_music: 'J-Pop',
    pets_oshi: 'Dogs',
    respected_person: 'Steve Jobs',
    motto: 'Stay hungry, stay foolish',
    future_goals: 'Build great software',
    is_first_login: false
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      backendToken: null
    })
  })

  describe('Initial State', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => useProfile())
      expect(result.current.profile).toBeNull()
      expect(result.current.isLoading).toBe(false)
    })

    it('should handle auth loading state', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        isLoading: true,
        backendToken: null
      })

      const { result } = renderHook(() => useProfile())
      expect(result.current.isLoading).toBe(true)
    })
  })

  describe('Authentication State Changes', () => {
    it('should fetch profile when user logs in', async () => {
      mockUseAuth.mockReturnValue({
        user: mockUser,
        isLoading: false,
        backendToken: 'mock-token'
      })
      mockApiGet.mockResolvedValue(mockProfile)

      const { result } = renderHook(() => useProfile())

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/users/profile')
      })

      expect(result.current.profile).toEqual(mockProfile)
      expect(result.current.isLoading).toBe(false)
    })

    it('should handle user logout', () => {
      // 最初にログイン状態
      mockUseAuth.mockReturnValue({
        user: mockUser,
        isLoading: false,
        backendToken: 'mock-token'
      })

      const { result, rerender } = renderHook(() => useProfile())

      // ログアウト状態に変更
      mockUseAuth.mockReturnValue({
        user: null,
        isLoading: false,
        backendToken: null
      })

      rerender()

      expect(result.current.error).toBe('ログインが必要です')
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('Profile Fetching', () => {
    it('should fetch profile successfully', async () => {
      mockUseAuth.mockReturnValue({
        user: mockUser,
        isLoading: false,
        backendToken: 'mock-token'
      })
      mockApiGet.mockResolvedValue(mockProfile)

      const { result } = renderHook(() => useProfile())

      await waitFor(() => {
        expect(result.current.profile).toEqual(mockProfile)
      })

      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('should handle profile fetch error', async () => {
      mockUseAuth.mockReturnValue({
        user: mockUser,
        isLoading: false,
        backendToken: 'mock-token'
      })
      mockApiGet.mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useProfile())

      await waitFor(() => {
        expect(result.current.error).toBe('Network error')
      })

      expect(result.current.profile).toBeNull()
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('Profile Data Validation', () => {
    it('should detect profile data presence', async () => {
      mockUseAuth.mockReturnValue({
        user: mockUser,
        isLoading: false,
        backendToken: 'mock-token'
      })
      mockApiGet.mockResolvedValue(mockProfile)

      const { result } = renderHook(() => useProfile())

      await waitFor(() => {
        expect(result.current.profile).toEqual(mockProfile)
      })

      // hasProfileDataは関数の結果を返すので、正しい値を期待
      expect(result.current.hasProfileData).toBe(true)
    })

    it('should detect empty profile data', async () => {
      const emptyProfile = {
        ...mockProfile,
        nickname: '',
        department: '',
        hobbies: '',
        favorite_food: '',
        motto: ''
      }

      mockUseAuth.mockReturnValue({
        user: mockUser,
        isLoading: false,
        backendToken: 'mock-token'
      })
      mockApiGet.mockResolvedValue(emptyProfile)

      const { result } = renderHook(() => useProfile())

      await waitFor(() => {
        expect(result.current.hasProfileData).toBe(false)
      })
    })
  })

  describe('Manual Profile Refresh', () => {
    it('should allow manual profile refresh', async () => {
      mockUseAuth.mockReturnValue({
        user: mockUser,
        isLoading: false,
        backendToken: 'mock-token'
      })
      mockApiGet.mockResolvedValue(mockProfile)

      const { result } = renderHook(() => useProfile())

      await waitFor(() => {
        expect(result.current.profile).toEqual(mockProfile)
      })

      // 手動でリフレッシュ
      const updatedProfile = { ...mockProfile, nickname: 'Updated' }
      mockApiGet.mockResolvedValue(updatedProfile)

      await act(async () => {
        await result.current.refetch()
      })

      expect(result.current.profile).toEqual(updatedProfile)
    })
  })
})
