// Firebase トークン取得 & API呼び出し
import { auth } from "./firebase";

export async function getAuthToken() {
  const user = auth.currentUser;
  if (!user) return null;
  return await user.getIdToken();
}

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = await getAuthToken();
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  
  return fetch(`${baseUrl}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: token ? `Bearer ${token}` : "",
      "Content-Type": "application/json",
    },
  });
}