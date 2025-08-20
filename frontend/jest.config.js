
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Next.jsアプリのパスを指定
  dir: './',
  // ESLintエラーを回避するための設定
  eslint: {
    ignoreDuringBuilds: true,
  },
})

// Jestのカスタム設定
const customJestConfig = {
  // テスト環境のセットアップ
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  
  // テストファイルのパターン
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{test,spec}.{js,jsx,ts,tsx}',
    '<rootDir>/__tests__/**/*.{js,jsx,ts,tsx}',
  ],
  
  // モジュールのパス解決
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/lib/(.*)$': '<rootDir>/src/lib/$1',
    '^@/types/(.*)$': '<rootDir>/src/types/$1',
    '^@/hooks/(.*)$': '<rootDir>/src/hooks/$1',
  },
  
  // テスト環境
  testEnvironment: 'jsdom',
  
  // カバレッジ設定
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/index.{js,jsx,ts,tsx}',
  ],
  
  // カバレッジの閾値
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
  
  // モジュールファイル拡張子
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  
  // 変換対象外
  transformIgnorePatterns: [
    '/node_modules/(?!(.*\\.mjs$|@babel|@swc|@next|@radix-ui|@mui|@emotion|zustand|class-variance-authority|clsx|tailwind-merge|tailwindcss-animate|lucide-react))',
  ],
  
  // テストタイムアウト
  testTimeout: 10000,
  
  // 詳細な出力
  verbose: true,
}

module.exports = createJestConfig(customJestConfig)
