//テスト実施のためFirebase Auth のモックを作成
export const initializeApp = jest.fn(() => ({}))
export const getApps = jest.fn(() => [])
export const getApp = jest.fn(() => ({}))

// デフォルトのモック実装
export default {
  initializeApp,
  getApps,
  getApp,
}
