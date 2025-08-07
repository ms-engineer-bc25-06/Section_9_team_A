// Firebase トークン取得 & API呼び出し
// import { auth } from "./firebase";

// export async function getAuthToken() {
//   const user = auth.currentUser;
//   if (!user) return null;
//   return await user.getIdToken();
// }

// export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
//   const token = await getAuthToken();
//   const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  
//   return fetch(`${baseUrl}${endpoint}`, {
//     ...options,
//     headers: {
//       ...options.headers,
//       Authorization: token ? `Bearer ${token}` : "",
//       "Content-Type": "application/json",
//     },
//   });
// }

import { auth } from "@/lib/firebase"

export async function getAuthToken() {
  const user = auth.currentUser
  if (!user) {
    console.warn("⚠️ 現在のユーザーが取得できません（未ログインか初期化前）")
    return null
  }
  try {
    const token = await user.getIdToken()
    console.log("✅ フロントで取得したトークン:", token)
    return token
  } catch (error) {
    console.error("❌ トークン取得エラー:", error)
    return null
  }
}

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = await getAuthToken()
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL

  console.log("📡 API呼び出し:", `${baseUrl}${endpoint}`)
  console.log("📦 送信ヘッダー Authorization:", token ? `Bearer ${token}` : "なし")

  return fetch(`${baseUrl}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: token ? `Bearer ${token}` : "",
      "Content-Type": "application/json",
    },
  })
}
