/**
 * アバター画像のURL生成ユーティリティ
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * アバター画像のURLを生成する
 * @param avatarUrl - アバターのURL（相対パス）
 * @param fallbackName - フォールバック用の名前
 * @param size - 画像サイズ（デフォルト: 96）
 * @returns 完全なアバター画像URL
 */
export function getAvatarUrl(
  avatarUrl?: string | null, 
  fallbackName?: string, 
  size: number = 96
): string {
  if (avatarUrl) {
    // 既に完全なURLの場合はそのまま返す
    if (avatarUrl.startsWith('http')) {
      return avatarUrl;
    }
    // 相対パスの場合はAPIベースURLを付与
    return `${API_BASE_URL}${avatarUrl}`;
  }
  
  // フォールバック画像を生成
  const query = fallbackName || 'user';
  return `/placeholder.svg?height=${size}&width=${size}&query=${encodeURIComponent(query)}`;
}

/**
 * アバター画像のsrc属性用のURLを生成する（プレビュー対応）
 * @param previewUrl - プレビュー用のURL（Base64など）
 * @param avatarUrl - アバターのURL（相対パス）
 * @param fallbackName - フォールバック用の名前
 * @param size - 画像サイズ（デフォルト: 96）
 * @returns 完全なアバター画像URL
 */
export function getAvatarSrc(
  previewUrl?: string,
  avatarUrl?: string | null,
  fallbackName?: string,
  size: number = 96
): string {
  // プレビューがある場合はそれを優先
  if (previewUrl) {
    return previewUrl;
  }
  
  return getAvatarUrl(avatarUrl, fallbackName, size);
}
