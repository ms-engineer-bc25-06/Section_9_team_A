// 認証テスト用のJest設定
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Next.jsアプリのパスを指定
  dir: './',
})

// Jest設定をカスタマイズ
const customJestConfig = {
  // テスト環境
  testEnvironment: 'jsdom',
  
  // セットアップファイル
  setupFilesAfterEnv: ['<rootDir>/jest.setup.auth.js'],
  
  // テストファイルのパターン
  testMatch: [
    '<rootDir>/src/components/auth/__tests__/**/*.test.{js,jsx,ts,tsx}',
    '<rootDir>/src/hooks/__tests__/**/*.test.{js,jsx,ts,tsx}',
  ],
  
  // モジュールパスの解決
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  
  // カバレッジ設定
  collectCoverageFrom: [
    'src/components/auth/**/*.{js,jsx,ts,tsx}',
    'src/hooks/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
  ],
  
  // カバレッジレポート
  coverageReporters: ['text', 'lcov', 'html'],
  
  // カバレッジ閾値
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
  
  // モック設定
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^firebase/auth$': '<rootDir>/__mocks__/firebase-auth.js',
    '^firebase/app$': '<rootDir>/__mocks__/firebase-app.js',
  },
  
  // テストタイムアウト
  testTimeout: 10000,
  
  // グローバル設定
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json',
    },
  },
}

// Jest設定を作成
module.exports = createJestConfig(customJestConfig)
