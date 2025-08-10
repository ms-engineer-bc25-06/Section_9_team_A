// firebase初期化
import { initializeApp, getApps, getApp } from "firebase/app"  // REVIEW: 修正（るい）
import { getAuth, setPersistence, inMemoryPersistence } from "firebase/auth"
import { getFirestore } from "firebase/firestore"

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
}

// REVIEW: 必須環境変数の検証（開発時の見落とし検知用）(rui)
// Next.js のクライアント側では process.env["KEY"] の動的参照は解決されない。
// 必ず直接参照で収集して検証する。
const envMap = {
  NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  NEXT_PUBLIC_FIREBASE_APP_ID: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
}

const missing = Object.entries(envMap)
  .filter(([, value]) => !value)
  .map(([key]) => key)
if (missing.length > 0) {
  throw new Error(
    `Firebase 環境変数が未設定です: ${missing.join(", ")}\. frontend/.env.local に設定し、開発サーバを再起動してください。`
  )
}

// REVIEW: 重複初期化を防ぐ(rui)
const app = getApps().length ? getApp() : initializeApp(firebaseConfig)
const auth = getAuth(app)

// REVIEW: セッションを「記憶しない」設定（クライアントのみ）(rui)
if (typeof window !== "undefined") {
  setPersistence(auth, inMemoryPersistence).catch((error) => {
    // 必要に応じてここで通知
    console.error("Firebase Auth persistence setting error:", error)
  })
}

export { auth }
export const db = getFirestore(app)
