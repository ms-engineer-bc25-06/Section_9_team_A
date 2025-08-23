"use client";

import { getAuth } from "firebase/auth";
import { AuthHeaders, ApiResponse, ApiError } from "../types";

// APIクライアントの設定
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = "/api/v1";

// URLビルダー関数
function buildUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  // パスが既にAPI_PREFIXを含んでいる場合は重複を避ける
  if (p.startsWith(API_PREFIX)) {
    return `${API_BASE_URL}${p}`;
  }
  return `${API_BASE_URL}${API_PREFIX}${p}`;
}

// Firebase トークン取得関数
export async function getAuthToken(): Promise<string | null> {
  try {
    const auth = getAuth();
    const user = auth.currentUser;
    if (!user) {
      console.warn("getAuthToken: ユーザーが認証されていません")
      return null;
    }
    
    const token = await user.getIdToken();
    
    // トークンの妥当性チェック
    if (!token || typeof token !== 'string') {
      console.warn("getAuthToken: 無効なトークンが取得されました")
      return null;
    }
    
    // トークンの長さチェック（異常に長いトークンを防ぐ）
    if (token.length > 5000) {
      console.error("getAuthToken: トークンが異常に長いです。認証に問題がある可能性があります")
      return null;
    }
    
    // JWTトークンの形式チェック（基本的な検証）
    if (!token.includes('.') || token.split('.').length !== 3) {
      console.error("getAuthToken: トークンの形式が不正です")
      return null;
    }
    
    console.log("getAuthToken: 有効なFirebase IDトークンを取得しました（長さ:", token.length, "文字）")
    return token;
  } catch (error) {
    console.error("Firebaseトークン取得エラー:", error);
    return null;
  }
}

// JWTトークンを取得する関数（フォールバック用）
function getJWTToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('jwt_token');
  }
  return null;
}

// 認証トークンを取得する関数（優先順位付き）
async function getToken(): Promise<string | null> {
  // まずJWTトークンを試行（バックエンド認証済みの場合）
  const jwtToken = getJWTToken();
  if (jwtToken) return jwtToken;
  
  // フォールバックとしてFirebaseトークンを試行
  const firebaseToken = await getAuthToken();
  if (firebaseToken) return firebaseToken;
  
  return null;
}

// 認証付きfetch関数
export async function fetchWithAuth(
  endpoint: string, 
  options: RequestInit = {}
): Promise<Response> {
  const token = await getToken();
  
  const headers: AuthHeaders = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const url = endpoint.startsWith('http') ? endpoint : buildUrl(endpoint);
  
  const response = await fetch(url, {
    ...options,
    headers,
  });

  // 401エラーの場合、JWTトークンを削除（Firebaseトークンは自動更新される）
  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('jwt_token');
    }
  }

  return response;
}

// レスポンス処理ヘルパー関数
async function handleResponse<T>(res: Response, label: string): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${label} failed: ${res.status} ${text}`);
  }
  
  try {
    return await res.json();
  } catch {
    return res.text() as T;
  }
}

// 基本的なAPI関数
export const apiClient = {
  // 個別の関数としてもエクスポート
  get: async <T = any>(url: string, options?: RequestInit): Promise<T> => {
    const response = await fetchWithAuth(url, { ...options, method: 'GET' });
    return handleResponse<T>(response, `GET ${url}`);
  },
  
  post: async <T = any>(url: string, data?: any, options?: RequestInit): Promise<T> => {
    const response = await fetchWithAuth(url, { 
      ...options, 
      method: 'POST', 
      body: data ? JSON.stringify(data) : undefined 
    });
    return handleResponse<T>(response, `POST ${url}`);
  },
  
  put: async <T = any>(url: string, data?: any, options?: RequestInit): Promise<T> => {
    const response = await fetchWithAuth(url, { 
      ...options, 
      method: 'PUT', 
      body: data ? JSON.stringify(data) : undefined 
    });
    return handleResponse<T>(response, `PUT ${url}`);
  },
  
  delete: async <T = any>(url: string, options?: RequestInit): Promise<T> => {
    const response = await fetchWithAuth(url, { ...options, method: 'DELETE' });
    return handleResponse<T>(response, `DELETE ${url}`);
  },
  
  patch: async <T = any>(url: string, data?: any, options?: RequestInit): Promise<T> => {
    const response = await fetchWithAuth(url, { 
      ...options, 
      method: 'PATCH', 
      body: data ? JSON.stringify(data) : undefined 
    });
    return handleResponse<T>(response, `PATCH ${url}`);
  },
};

// 個別の関数としてもエクスポート（useProfile.tsとの互換性のため）
export const apiGet = apiClient.get;
export const apiPost = apiClient.post;
export const apiPut = apiClient.put;
export const apiDelete = apiClient.delete;
export const apiPatch = apiClient.patch;
export default apiClient;
