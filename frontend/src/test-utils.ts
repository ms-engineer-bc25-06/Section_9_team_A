/**
 * フロントエンドテスト用の共通ヘルパー関数
 */

import { render, RenderOptions } from '@testing-library/react'
import { ReactElement } from 'react'
import userEvent from '@testing-library/user-event'

// テスト用の共通プロバイダー
interface TestProvidersProps {
  children: React.ReactNode
}

// カスタムレンダー関数（プロバイダー付き）
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  const AllTheProviders = ({ children }: TestProvidersProps) => {
    return children
  }

  return render(ui, { wrapper: AllTheProviders, ...options })
}

// モックユーザーの作成
export const createMockUser = (overrides: Partial<any> = {}) => ({
  uid: 'test-user-123',
  email: 'test@example.com',
  displayName: 'Test User',
  photoURL: null,
  ...overrides
})

// モック認証状態の作成
export const createMockAuthState = (overrides: Partial<any> = {}) => ({
  user: createMockUser(),
  isAuthenticated: true,
  isLoading: false,
  error: null,
  ...overrides
})

// モックプロフィールの作成
export const createMockProfile = (overrides: Partial<any> = {}) => ({
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  fullName: 'Test User',
  avatar: null,
  bio: 'Test bio',
  ...overrides
})

// モックサブスクリプションプランの作成
export const createMockPlan = (overrides: Partial<any> = {}) => ({
  id: 'basic',
  name: 'Basic Plan',
  monthly_price: 980,
  yearly_price: 9800,
  features: ['10 members', '50 sessions/month'],
  trial_days: 7,
  ...overrides
})

// モック請求データの作成
export const createMockBillingData = (overrides: Partial<any> = {}) => ({
  id: 'inv_123',
  amount: 2980,
  currency: 'JPY',
  status: 'pending',
  due_date: new Date().toISOString(),
  description: 'Premium Plan - Monthly Subscription',
  ...overrides
})

// モック決済データの作成
export const createMockPaymentData = (overrides: Partial<any> = {}) => ({
  id: 'pi_test_123',
  amount: 2980,
  currency: 'jpy',
  status: 'requires_payment_method',
  client_secret: 'pi_test_secret_123',
  ...overrides
})

// モック音声セッションデータの作成
export const createMockVoiceSession = (overrides: Partial<any> = {}) => ({
  id: 'session_123',
  title: 'Test Session',
  description: 'A test voice session',
  status: 'active',
  is_recording: false,
  participants: [],
  created_at: new Date().toISOString(),
  ...overrides
})

// モック転写データの作成
export const createMockTranscription = (overrides: Partial<any> = {}) => ({
  id: 'trans_123',
  text: 'これはテスト用の転写テキストです。',
  confidence: 0.95,
  language: 'ja',
  speaker_id: 1,
  timestamp: new Date().toISOString(),
  ...overrides
})

// モック分析データの作成
export const createMockAnalysis = (overrides: Partial<any> = {}) => ({
  id: 'analysis_123',
  type: 'personality',
  content: 'テスト用の分析コンテンツ',
  status: 'completed',
  created_at: new Date().toISOString(),
  ...overrides
})

// モック通知データの作成
export const createMockNotification = (overrides: Partial<any> = {}) => ({
  id: 'notif_123',
  type: 'info',
  title: 'Test Notification',
  message: 'This is a test notification',
  is_read: false,
  created_at: new Date().toISOString(),
  ...overrides
})

// モックアナウンスメントデータの作成
export const createMockAnnouncement = (overrides: Partial<any> = {}) => ({
  id: 'announce_123',
  title: 'Test Announcement',
  content: 'This is a test announcement',
  priority: 'normal',
  is_active: true,
  created_at: new Date().toISOString(),
  ...overrides
})

// モックチームデータの作成
export const createMockTeam = (overrides: Partial<any> = {}) => ({
  id: 'team_123',
  name: 'Test Team',
  description: 'A test team',
  owner_id: 1,
  members: [],
  is_active: true,
  created_at: new Date().toISOString(),
  ...overrides
})

// モック参加者データの作成
export const createMockParticipant = (overrides: Partial<any> = {}) => ({
  id: 'participant_123',
  user_id: 1,
  session_id: 'session_123',
  role: 'participant',
  status: 'active',
  joined_at: new Date().toISOString(),
  ...overrides
})

// モック音声品質データの作成
export const createMockAudioQuality = (overrides: Partial<any> = {}) => ({
  session_id: 'session_123',
  user_id: 1,
  sample_rate: 16000,
  channels: 1,
  bit_depth: 16,
  quality_score: 0.95,
  network_latency: 50,
  packet_loss: 0.01,
  timestamp: new Date().toISOString(),
  ...overrides
})

// モックWebSocketメッセージの作成
export const createMockWebSocketMessage = (overrides: Partial<any> = {}) => ({
  type: 'message',
  session_id: 'session_123',
  user_id: 1,
  content: 'Test message',
  timestamp: new Date().toISOString(),
  ...overrides
})

// モックエラーレスポンスの作成
export const createMockErrorResponse = (overrides: Partial<any> = {}) => ({
  error: 'Test error',
  message: 'This is a test error message',
  status_code: 400,
  details: {},
  ...overrides
})

// モック成功レスポンスの作成
export const createMockSuccessResponse = (overrides: Partial<any> = {}) => ({
  success: true,
  message: 'Operation completed successfully',
  data: {},
  ...overrides
})

// モックAPIクライアントの作成
export const createMockApiClient = () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  patch: jest.fn(),
})

// モックFirebase認証の作成
export const createMockFirebaseAuth = () => ({
  currentUser: null,
  onAuthStateChanged: jest.fn(),
  signInWithEmailAndPassword: jest.fn(),
  createUserWithEmailAndPassword: jest.fn(),
  signOut: jest.fn(),
  sendPasswordResetEmail: jest.fn(),
  updatePassword: jest.fn(),
})

// モックStripeの作成
export const createMockStripe = () => ({
  createPaymentMethod: jest.fn(),
  confirmCardPayment: jest.fn(),
  createToken: jest.fn(),
  createSource: jest.fn(),
  retrieveSource: jest.fn(),
  createCustomer: jest.fn(),
  createSubscription: jest.fn(),
  cancelSubscription: jest.fn(),
})

// モックWebSocketの作成
export const createMockWebSocket = () => ({
  readyState: WebSocket.OPEN,
  send: jest.fn(),
  close: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn(),
})

// モックMediaRecorderの作成
export const createMockMediaRecorder = () => ({
  start: jest.fn(),
  stop: jest.fn(),
  pause: jest.fn(),
  resume: jest.fn(),
  requestData: jest.fn(),
  state: 'inactive',
  onstart: null,
  onstop: null,
  ondataavailable: null,
  onerror: null,
  onpause: null,
  onresume: null,
})

// モックMediaStreamの作成
export const createMockMediaStream = () => ({
  id: 'stream_123',
  active: true,
  getTracks: jest.fn(() => []),
  getVideoTracks: jest.fn(() => []),
  getAudioTracks: jest.fn(() => []),
  addTrack: jest.fn(),
  removeTrack: jest.fn(),
  clone: jest.fn(),
  onaddtrack: null,
  onremovetrack: null,
})

// モックAudioContextの作成
export const createMockAudioContext = () => ({
  sampleRate: 44100,
  currentTime: 0,
  destination: {},
  createAnalyser: jest.fn(),
  createGain: jest.fn(),
  createOscillator: jest.fn(),
  createMediaElementSource: jest.fn(),
  createMediaStreamSource: jest.fn(),
  createMediaStreamDestination: jest.fn(),
  createScriptProcessor: jest.fn(),
  createBiquadFilter: jest.fn(),
  createDelay: jest.fn(),
  createConvolver: jest.fn(),
  createDynamicsCompressor: jest.fn(),
  createPanner: jest.fn(),
  createStereoPanner: jest.fn(),
  createChannelSplitter: jest.fn(),
  createChannelMerger: jest.fn(),
  createWaveShaper: jest.fn(),
  createPeriodicWave: jest.fn(),
  decodeAudioData: jest.fn(),
  suspend: jest.fn(),
  resume: jest.fn(),
  close: jest.fn(),
  state: 'running',
  onstatechange: null,
})

// テスト用のユーティリティ関数
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const createTestElement = (tag: string, attributes: Record<string, string> = {}) => {
  const element = document.createElement(tag)
  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, value)
  })
  return element
}

export const createTestEvent = (type: string, options: any = {}) => {
  return new Event(type, options)
}

export const createTestMouseEvent = (type: string, options: any = {}) => {
  return new MouseEvent(type, options)
}

export const createTestKeyboardEvent = (type: string, options: any = {}) => {
  return new KeyboardEvent(type, options)
}

export const createTestTouchEvent = (type: string, options: any = {}) => {
  return new TouchEvent(type, options)
}

// テスト用のアサーション関数
export const expectElementToBeVisible = (element: HTMLElement) => {
  expect(element).toBeInTheDocument()
  expect(element).toBeVisible()
}

export const expectElementToBeHidden = (element: HTMLElement) => {
  expect(element).toBeInTheDocument()
  expect(element).not.toBeVisible()
}

export const expectElementToHaveText = (element: HTMLElement, text: string) => {
  expect(element).toHaveTextContent(text)
}

export const expectElementToHaveClass = (element: HTMLElement, className: string) => {
  expect(element).toHaveClass(className)
}

export const expectElementToHaveAttribute = (element: HTMLElement, attribute: string, value?: string) => {
  if (value) {
    expect(element).toHaveAttribute(attribute, value)
  } else {
    expect(element).toHaveAttribute(attribute)
  }
}

export const expectElementToBeDisabled = (element: HTMLElement) => {
  expect(element).toBeDisabled()
}

export const expectElementToBeEnabled = (element: HTMLElement) => {
  expect(element).not.toBeDisabled()
}

export const expectElementToBeRequired = (element: HTMLElement) => {
  expect(element).toBeRequired()
}

export const expectElementToBeOptional = (element: HTMLElement) => {
  expect(element).not.toBeRequired()
}

// テスト用のセットアップ関数
export const setupTestEnvironment = () => {
  // テスト環境のセットアップ
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  })

  // ResizeObserverのモック
  global.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  }))

  // IntersectionObserverのモック
  global.IntersectionObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  }))
}

// テスト用のクリーンアップ関数
export const cleanupTestEnvironment = () => {
  // テスト環境のクリーンアップ
  jest.clearAllMocks()
  jest.clearAllTimers()
}

// テスト用の共通設定
export const testConfig = {
  timeout: 10000,
  retries: 3,
  delay: 100,
}

// テスト用のエラーハンドリング
export const handleTestError = (error: Error, context: string = 'Test') => {
  console.error(`${context} Error:`, error)
  throw error
}

// テスト用のログ出力
export const logTestInfo = (message: string, data?: any) => {
  if (process.env.NODE_ENV === 'test') {
    console.log(`[TEST] ${message}`, data || '')
  }
}

// テスト用のパフォーマンス測定
export const measureTestPerformance = async <T>(
  testFunction: () => Promise<T>,
  testName: string = 'Test'
): Promise<T> => {
  const startTime = performance.now()
  try {
    const result = await testFunction()
    const endTime = performance.now()
    const duration = endTime - startTime
    logTestInfo(`${testName} completed in ${duration.toFixed(2)}ms`)
    return result
  } catch (error) {
    const endTime = performance.now()
    const duration = endTime - startTime
    logTestInfo(`${testName} failed after ${duration.toFixed(2)}ms`)
    throw error
  }
}
