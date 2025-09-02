//テスト実施のためFirebase Auth のモックを作成

export const getAuth = jest.fn(() => ({}))
export const onAuthStateChanged = jest.fn()
export const signInWithEmailAndPassword = jest.fn()
export const createUserWithEmailAndPassword = jest.fn()
export const signOut = jest.fn()
export const setPersistence = jest.fn()
export const browserLocalPersistence = 'local'
export const browserSessionPersistence = 'session'
export const inMemoryPersistence = 'none'

// デフォルトのモック実装
export default {
  getAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  setPersistence,
  browserLocalPersistence,
  browserSessionPersistence,
  inMemoryPersistence,
}
