"use client";

// APIクライアントの設定
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// JWTトークンを取得する関数
function getJWTToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('jwt_token');
  }
  return null;
}

// 認証ヘッダー付きのfetch関数
export async function fetchWithAuth(
  url: string, 
  options: RequestInit = {}
): Promise<Response> {
  const token = getJWTToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });

  // 401エラーの場合、トークンを削除
  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('jwt_token');
    }
  }

  return response;
}

// 基本的なAPI関数
export const apiClient = {
  get: (url: string, options?: RequestInit) => 
    fetchWithAuth(url, { ...options, method: 'GET' }),
  
  post: (url: string, data?: any, options?: RequestInit) => 
    fetchWithAuth(url, { 
      ...options, 
      method: 'POST', 
      body: data ? JSON.stringify(data) : undefined 
    }),
  
  put: (url: string, data?: any, options?: RequestInit) => 
    fetchWithAuth(url, { 
      ...options, 
      method: 'PUT', 
      body: data ? JSON.stringify(data) : undefined 
    }),
  
  delete: (url: string, options?: RequestInit) => 
    fetchWithAuth(url, { ...options, method: 'DELETE' }),
  
  patch: (url: string, data?: any, options?: RequestInit) => 
    fetchWithAuth(url, { 
      ...options, 
      method: 'PATCH', 
      body: data ? JSON.stringify(data) : undefined 
    }),
};

export default apiClient;
