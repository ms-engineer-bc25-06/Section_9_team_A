import { apiGet, apiPost, apiDelete } from '../apiClient'

// テスト用のAPIクライアント（認証なし）
const testApiGet = async <T>(path: string): Promise<T> => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1${path}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }
    
    return response.json()
  } catch (error) {
    console.error('API call failed:', error)
    throw error
  }
}

export interface UserInput {
  email: string
  name: string
  department: string
  role: string
}

export interface UserResponse {
  id: number
  email: string
  name: string
  department: string
  role: string
  is_active: boolean
  created_at: string
}

export const adminUsersApi = {
  // ユーザー一覧を取得
  getUsers: async (): Promise<UserResponse[]> => {
    // 開発環境ではテスト用エンドポイントを使用
    if (process.env.NODE_ENV === 'development') {
      try {
        // まずシンプルなエンドポイントで接続テスト
        console.log('Testing simple endpoint...')
        await testApiGet<{message: string, status: string}>('/admin/users/simple')
        console.log('Simple endpoint successful')
        
        // 次にpingエンドポイントでテスト
        console.log('Testing ping endpoint...')
        await testApiGet<{message: string, status: string}>('/admin/users/ping')
        console.log('Ping successful')
        
        // 実際のユーザーデータを取得
        console.log('Fetching real users...')
        const realUsers = await testApiGet<UserResponse[]>('/admin/users/test')
        console.log('Real users fetched successfully:', realUsers.length, 'users')
        return realUsers
        
        // モックデータが必要な場合は以下を使用
        // console.log('Fetching mock users...')
        // const mockUsers = await testApiGet<UserResponse[]>('/admin/users/mock')
        // console.log('Mock users fetched successfully:', mockUsers.length, 'users')
        // return mockUsers
      } catch (error) {
        console.error('Failed to fetch users:', error)
        // エラーの場合は空配列を返す
        return []
      }
    }
    return await apiGet<UserResponse[]>('/admin/users')
  },

  // ユーザーを一括作成
  createUsers: async (users: UserInput[]): Promise<UserResponse[]> => {
    return await apiPost<UserResponse[]>('/admin/users', users)
  },

  // ユーザーを削除
  deleteUser: async (userId: number): Promise<void> => {
    await apiDelete<void>(`/admin/users/${userId}`)
  },

  // パスワードリセット
  resetPassword: async (userId: number): Promise<{temp_password: string, user_email: string}> => {
    return await apiPost<{temp_password: string, user_email: string}>(`/admin/users/${userId}/reset-password`, {})
  }
}
