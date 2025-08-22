// 共通関数
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 仮パスワード生成関数（Firebase認証に安全な文字のみ）
export function generateTemporaryPassword(length: number = 12): string {
  // 大文字、小文字、数字のみ（特殊文字を完全に除外）
  const uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  const lowercase = "abcdefghijklmnopqrstuvwxyz"
  const digits = "0123456789"
  const allChars = uppercase + lowercase + digits
  
  let password = ""
  
  // 最低1つの大文字、小文字、数字を含む
  password += uppercase.charAt(Math.floor(Math.random() * uppercase.length))
  password += lowercase.charAt(Math.floor(Math.random() * lowercase.length))
  password += digits.charAt(Math.floor(Math.random() * digits.length))
  
  // 残りの文字をランダムに生成（特殊文字なし）
  for (let i = 3; i < length; i++) {
    password += allChars.charAt(Math.floor(Math.random() * allChars.length))
  }
  
  // パスワードをシャッフル
  return password.split('').sort(() => Math.random() - 0.5).join('')
}
// その他のユーティリティ関数
export function formatCurrency(amount: number, currency = 'JPY'): string {
  return new Intl.NumberFormat('ja-JP', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('ja-JP').format(d)
}