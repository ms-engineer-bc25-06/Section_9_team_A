// APIクライアント用の型定義
// 認証ヘッダー付きのヘッダー型
export type AuthHeaders = HeadersInit & {
  Authorization?: string;
  'Content-Type'?: string;
};

// APIレスポンスの基本型
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

// APIクライアントの設定型
export interface ApiClientConfig {
  baseUrl: string;
  apiPrefix: string;
  defaultHeaders?: AuthHeaders;
}

// 認証トークンの型
export type AuthToken = string | null;

// エラーハンドリング用の型
export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

// HTTPメソッドの型
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// APIリクエストオプションの型
export interface ApiRequestOptions extends RequestInit {
  headers?: AuthHeaders;
  timeout?: number;
  retryCount?: number;
}

// 認証状態の型
export interface AuthState {
  isAuthenticated: boolean;
  token: AuthToken;
  user?: any;
}
