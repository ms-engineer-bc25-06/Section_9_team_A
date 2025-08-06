// firebase初期化
import { initializeApp } from "firebase/app"
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
console.log(firebaseConfig)

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)

// セッションを「記憶しない」設定
setPersistence(auth, inMemoryPersistence)
  .then(() => {
    console.log("Firebase Auth set to inMemoryPersistence")
  })
  .catch((error) => {
    console.error("Firebase Auth persistence setting error:", error)
  })

export { auth }
export const db = getFirestore(app)
