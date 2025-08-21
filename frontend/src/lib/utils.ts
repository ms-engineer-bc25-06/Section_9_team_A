// 共通関数
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 仮パスワード生成関数
export function generateTemporaryPassword(length: number = 12): string {
  const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
  let password = ""
  
  // 最低1つの大文字、小文字、数字、記号を含むようにする
  password += charset.charAt(Math.floor(Math.random() * 26)) // 大文字
  password += charset.charAt(26 + Math.floor(Math.random() * 26)) // 小文字
  password += charset.charAt(52 + Math.floor(Math.random() * 10)) // 数字
  password += charset.charAt(62 + Math.floor(Math.random() * 8)) // 記号
  
  // 残りの文字をランダムに生成
  for (let i = 4; i < length; i++) {
    password += charset.charAt(Math.floor(Math.random() * charset.length))
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