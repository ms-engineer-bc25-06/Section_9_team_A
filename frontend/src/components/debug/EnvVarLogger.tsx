"use client"

import { useEffect } from 'react'

/**
 * 環境変数の読み込み状況を確認するデバッグコンポーネント
 * 開発環境でのみ動作し、本番環境では何も表示しない
 */
export function EnvVarLogger() {
  useEffect(() => {
    // 開発環境でのみ実行
    if (process.env.NODE_ENV !== 'development') {
      return
    }

    console.group('🔧 環境変数読み込み状況確認')
    
    // Firebase設定
    console.group('Firebase設定')
    console.log('NEXT_PUBLIC_FIREBASE_API_KEY:', process.env.NEXT_PUBLIC_FIREBASE_API_KEY ? '✅ 設定済み' : '❌ 未設定')
    console.log('NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN:', process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || '❌ 未設定')
    console.log('NEXT_PUBLIC_FIREBASE_PROJECT_ID:', process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || '❌ 未設定')
    console.log('NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET:', process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || '❌ 未設定')
    console.log('NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID:', process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || '❌ 未設定')
    console.log('NEXT_PUBLIC_FIREBASE_APP_ID:', process.env.NEXT_PUBLIC_FIREBASE_APP_ID || '❌ 未設定')
    console.groupEnd()
    
    // API設定
    console.group('API設定')
    console.log('NEXT_PUBLIC_API_BASE_URL:', process.env.NEXT_PUBLIC_API_BASE_URL || '❌ 未設定')
    console.log('NEXT_PUBLIC_WS_BASE_URL:', process.env.NEXT_PUBLIC_WS_BASE_URL || '⚠️ 未設定（デフォルト値使用）')
    console.groupEnd()
    
    // 環境情報
    console.group('環境情報')
    console.log('NODE_ENV:', process.env.NODE_ENV)
    console.log('NEXT_PUBLIC_VERCEL_ENV:', process.env.NEXT_PUBLIC_VERCEL_ENV || '未設定')
    console.groupEnd()
    
    console.groupEnd()
    
    // 設定の整合性チェック
    const firebaseConfig = {
      apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
      authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
      projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
      messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
      appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
    }
    
    // Firebase設定の妥当性チェック
    const missingKeys = Object.entries(firebaseConfig)
      .filter(([key, value]) => !value)
      .map(([key]) => key)
    
    if (missingKeys.length > 0) {
      console.warn('⚠️ 不足しているFirebase設定:', missingKeys)
    } else {
      console.log('✅ すべてのFirebase設定が完了しています')
    }
    
    // プロジェクトIDの整合性チェック
    const projectId = process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID
    const authDomain = process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
    const storageBucket = process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
    
    if (projectId && authDomain && storageBucket) {
      const isConsistent = authDomain.includes(projectId) && storageBucket.includes(projectId)
      if (isConsistent) {
        console.log('✅ プロジェクトIDの整合性が確認できました')
      } else {
        console.warn('⚠️ プロジェクトIDの整合性に問題があります')
      }
    }
    
  }, [])
  
  // このコンポーネントは何も表示しない（ログ出力のみ）
  return null
}
