// WebSocket関連のエラーメッセージ国際化
export interface WebSocketMessages {
  ja: WebSocketMessageLocale
  en: WebSocketMessageLocale
}

export interface WebSocketMessageLocale {
  connection: {
    connecting: string
    connected: string
    disconnected: string
    reconnecting: string
    timeout: string
    error: string
    authFailed: string
    serverError: string
  }
  errors: {
    connectionFailed: string
    authenticationFailed: string
    serverUnavailable: string
    networkError: string
    protocolError: string
    unsupportedDataType: string
    abnormalClosure: string
    policyViolation: string
    internalServerError: string
    sessionNotFound: string
    permissionDenied: string
    invalidMessage: string
    messageTooLarge: string
  }
  actions: {
    retry: string
    reconnect: string
    reauthenticate: string
    close: string
    refresh: string
  }
  details: {
    connectionTimeout: (seconds: number) => string
    reconnectAttempt: (attempt: number) => string
    errorCode: (code: number) => string
    sessionId: (id: string) => string
  }
}

export const websocketMessages: WebSocketMessages = {
  ja: {
    connection: {
      connecting: "接続中...",
      connected: "接続済み",
      disconnected: "接続されていません",
      reconnecting: "再接続中...",
      timeout: "接続タイムアウト",
      error: "接続エラー",
      authFailed: "認証失敗",
      serverError: "サーバーエラー"
    },
    errors: {
      connectionFailed: "接続に失敗しました",
      authenticationFailed: "認証に失敗しました",
      serverUnavailable: "サーバーが利用できません",
      networkError: "ネットワークエラーが発生しました",
      protocolError: "プロトコルエラーが発生しました",
      unsupportedDataType: "サポートされていないデータ型です",
      abnormalClosure: "サーバーとの接続が異常終了しました",
      policyViolation: "認証に失敗しました",
      internalServerError: "サーバーでエラーが発生しました",
      sessionNotFound: "セッションが見つかりません",
      permissionDenied: "権限がありません",
      invalidMessage: "無効なメッセージです",
      messageTooLarge: "メッセージが大きすぎます"
    },
    actions: {
      retry: "再試行",
      reconnect: "再接続",
      reauthenticate: "再認証",
      close: "閉じる",
      refresh: "更新"
    },
    details: {
      connectionTimeout: (seconds: number) => `サーバーからの応答がありません（${seconds}秒）`,
      reconnectAttempt: (attempt: number) => `再接続を試行中です (試行回数: ${attempt})`,
      errorCode: (code: number) => `接続が閉じられました (コード: ${code})`,
      sessionId: (id: string) => `セッションID: ${id}`
    }
  },
  en: {
    connection: {
      connecting: "Connecting...",
      connected: "Connected",
      disconnected: "Disconnected",
      reconnecting: "Reconnecting...",
      timeout: "Connection Timeout",
      error: "Connection Error",
      authFailed: "Authentication Failed",
      serverError: "Server Error"
    },
    errors: {
      connectionFailed: "Connection failed",
      authenticationFailed: "Authentication failed",
      serverUnavailable: "Server unavailable",
      networkError: "Network error occurred",
      protocolError: "Protocol error occurred",
      unsupportedDataType: "Unsupported data type",
      abnormalClosure: "Connection abnormally closed by server",
      policyViolation: "Authentication failed",
      internalServerError: "Internal server error occurred",
      sessionNotFound: "Session not found",
      permissionDenied: "Permission denied",
      invalidMessage: "Invalid message",
      messageTooLarge: "Message too large"
    },
    actions: {
      retry: "Retry",
      reconnect: "Reconnect",
      reauthenticate: "Re-authenticate",
      close: "Close",
      refresh: "Refresh"
    },
    details: {
      connectionTimeout: (seconds: number) => `No response from server (${seconds}s)`,
      reconnectAttempt: (attempt: number) => `Reconnecting... (Attempt: ${attempt})`,
      errorCode: (code: number) => `Connection closed (Code: ${code})`,
      sessionId: (id: string) => `Session ID: ${id}`
    }
  }
}

// 現在の言語設定を取得（デフォルトは日本語）
export const getCurrentLocale = (): keyof WebSocketMessages => {
  if (typeof window !== 'undefined') {
    const browserLang = navigator.language.split('-')[0]
    if (browserLang === 'en') return 'en'
  }
  return 'ja'
}

// 現在の言語に基づいてメッセージを取得
export const getWebSocketMessage = (locale?: keyof WebSocketMessages) => {
  const currentLocale = locale || getCurrentLocale()
  return websocketMessages[currentLocale]
}

// エラーコードに基づくメッセージ取得
export const getErrorMessageByCode = (code: number, locale?: keyof WebSocketMessages) => {
  const messages = getWebSocketMessage(locale)
  
  switch (code) {
    case 1000:
      return messages.errors.connectionFailed
    case 1001:
      return messages.errors.connectionFailed
    case 1002:
      return messages.errors.protocolError
    case 1003:
      return messages.errors.unsupportedDataType
    case 1006:
      return messages.errors.abnormalClosure
    case 1008:
      return messages.errors.policyViolation
    case 1011:
      return messages.errors.internalServerError
    default:
      return messages.details.errorCode(code)
  }
}

// 接続状態に基づくメッセージ取得
export const getConnectionStatusMessage = (
  state: string, 
  locale?: keyof WebSocketMessages,
  details?: { attempt?: number; timeout?: number; code?: number }
) => {
  const messages = getWebSocketMessage(locale)
  
  switch (state) {
    case 'connecting':
      return {
        message: messages.connection.connecting,
        details: messages.details.connectionTimeout(details?.timeout || 15),
        canRetry: false
      }
    case 'connected':
      return {
        message: messages.connection.connected,
        details: "WebSocket接続が確立されています",
        canRetry: false
      }
    case 'reconnecting':
      return {
        message: messages.connection.reconnecting,
        details: messages.details.reconnectAttempt(details?.attempt || 0),
        canRetry: false
      }
    case 'timeout':
      return {
        message: messages.connection.timeout,
        details: messages.details.connectionTimeout(details?.timeout || 15),
        canRetry: true,
        retryAction: messages.actions.reconnect
      }
    case 'error':
      return {
        message: messages.connection.error,
        details: "不明なエラーが発生しました",
        canRetry: true,
        retryAction: messages.actions.retry
      }
    case 'auth_failed':
      return {
        message: messages.connection.authFailed,
        details: messages.errors.authenticationFailed,
        canRetry: true,
        retryAction: messages.actions.reauthenticate
      }
    case 'server_error':
      return {
        message: messages.connection.serverError,
        details: messages.errors.internalServerError,
        canRetry: true,
        retryAction: messages.actions.reconnect
      }
    default:
      return {
        message: messages.connection.disconnected,
        details: "WebSocket接続が確立されていません",
        canRetry: true,
        retryAction: messages.actions.reconnect
      }
  }
}
