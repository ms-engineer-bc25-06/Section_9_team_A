// WebSocket 通信管理（クライアント専用）
"use client"

import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { getAuthToken } from "@/lib/apiClient"

type JsonValue = unknown

export interface UseWebSocketOptions {
  autoReconnect?: boolean
  reconnectMaxDelayMs?: number
  heartbeatIntervalMs?: number
  connectionTimeoutMs?: number // 接続タイムアウトを追加
  maxReconnectAttempts?: number // 最大再接続試行回数を追加
  skipAuth?: boolean // テスト用：認証をスキップ
  onOpen?: () => void
  onClose?: (ev: CloseEvent) => void
  onError?: (ev: Event) => void
  onMessage?: (data: any) => void
  onMaxAttemptsReached?: () => void // 最大試行回数到達時のコールバックを追加
}

export interface UseWebSocketReturn {
  isConnected: boolean
  isConnecting: boolean // 接続中状態を追加
  lastMessage: any | null
  connectError: string | null
  connectionState: ConnectionState // 接続状態の詳細を追加
  sendJson: (payload: JsonValue) => boolean
  close: () => void
  reconnect: () => void // 手動再接続機能を追加
  getConnectionStatus: () => ConnectionStatus // 接続状態詳細取得機能を追加
}

export enum ConnectionState {
  DISCONNECTED = "disconnected",
  CONNECTING = "connecting",
  CONNECTED = "connected",
  RECONNECTING = "reconnecting",
  ERROR = "error",
  TIMEOUT = "timeout",
  AUTH_FAILED = "auth_failed",
  SERVER_ERROR = "server_error",
  MAX_ATTEMPTS_REACHED = "max_attempts_reached" // 最大試行回数到達状態を追加
}

export interface ConnectionStatus {
  state: ConnectionState
  message: string
  details?: string
  canRetry: boolean
  retryAction?: string
}

function resolveWsBaseUrl(): string | null {
  const explicit = process.env.NEXT_PUBLIC_WS_BASE_URL
  if (explicit) return explicit.replace(/\/$/, "")

  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL
  if (!apiBase) return null

  try {
    const url = new URL(apiBase)
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:"
    return url.toString().replace(/\/$/, "")
  } catch {
    return null
  }
}

export function useWebSocket(urlPath: string, options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    autoReconnect = true,
    reconnectMaxDelayMs = 10_000,
    heartbeatIntervalMs = 30_000,
    connectionTimeoutMs = 15_000, // デフォルト15秒
    maxReconnectAttempts = 5, // デフォルト5回
    skipAuth = false, // テスト用：認証をスキップ
    onOpen,
    onClose,
    onError,
    onMessage,
    onMaxAttemptsReached,
  } = options

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptRef = useRef<number>(0)
  const heartbeatTimerRef = useRef<number | null>(null)
  // 接続状態管理を追加
  const isConnectingRef = useRef<boolean>(false)
  const connectionTimeoutRef = useRef<number | null>(null)

  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false) // 接続中状態を追加
  const [lastMessage, setLastMessage] = useState<any | null>(null)
  const [connectError, setConnectError] = useState<string | null>(null)
  const [connectionState, setConnectionState] = useState<ConnectionState>(ConnectionState.DISCONNECTED) // 接続状態の詳細

  // 接続状態に基づく詳細情報を提供
  const getConnectionStatus = useCallback((): ConnectionStatus => {
    switch (connectionState) {
      case ConnectionState.DISCONNECTED:
        return {
          state: ConnectionState.DISCONNECTED,
          message: "接続されていません",
          details: "WebSocket接続が確立されていません",
          canRetry: true,
          retryAction: "接続を開始"
        }
      
      case ConnectionState.CONNECTING:
        return {
          state: ConnectionState.CONNECTING,
          message: "接続中...",
          details: "サーバーへの接続を試行中です",
          canRetry: false
        }
      
      case ConnectionState.CONNECTED:
        return {
          state: ConnectionState.CONNECTED,
          message: "接続済み",
          details: "WebSocket接続が確立されています",
          canRetry: false
        }
      
      case ConnectionState.RECONNECTING:
        return {
          state: ConnectionState.RECONNECTING,
          message: "再接続中...",
          details: `再接続を試行中です (試行回数: ${reconnectAttemptRef.current}/${maxReconnectAttempts})`,
          canRetry: false
        }
      
      case ConnectionState.ERROR:
        return {
          state: ConnectionState.ERROR,
          message: "接続エラー",
          details: connectError || "不明なエラーが発生しました",
          canRetry: true,
          retryAction: "再接続"
        }
      
      case ConnectionState.TIMEOUT:
        return {
          state: ConnectionState.TIMEOUT,
          message: "接続タイムアウト",
          details: `サーバーからの応答がありません (${connectionTimeoutMs / 1000}秒)`,
          canRetry: true,
          retryAction: "再接続"
        }
      
      case ConnectionState.AUTH_FAILED:
        return {
          state: ConnectionState.AUTH_FAILED,
          message: "認証失敗",
          details: "認証トークンが無効です",
          canRetry: true,
          retryAction: "再認証"
        }
      
      case ConnectionState.SERVER_ERROR:
        return {
          state: ConnectionState.SERVER_ERROR,
          message: "サーバーエラー",
          details: "サーバー側でエラーが発生しました",
          canRetry: true,
          retryAction: "再接続"
        }
      
      case ConnectionState.MAX_ATTEMPTS_REACHED:
        return {
          state: ConnectionState.MAX_ATTEMPTS_REACHED,
          message: "接続失敗",
          details: `接続試行回数上限(${maxReconnectAttempts}回)に達しました`,
          canRetry: false
        }
      
      default:
        return {
          state: ConnectionState.DISCONNECTED,
          message: "不明な状態",
          details: "接続状態が不明です",
          canRetry: true,
          retryAction: "再接続"
        }
    }
  }, [connectionState, connectError, connectionTimeoutMs, maxReconnectAttempts])

  const wsUrlBuilder = useMemo(() => {
    const base = resolveWsBaseUrl()
    return async () => {
      if (!base) throw new Error("WS base URL not configured (NEXT_PUBLIC_WS_BASE_URL or NEXT_PUBLIC_API_BASE_URL)")
      
      // テスト用：認証をスキップ
      if (skipAuth) {
        return `${base}${urlPath}`
      }
      
      try {
        const token = await getAuthToken()
        
        // トークンの妥当性チェック
        if (!token) {
          console.warn("WebSocket: 認証トークンが取得できません")
          setConnectionState(ConnectionState.AUTH_FAILED)
          setConnectError("認証トークンが取得できません")
          return `${base}${urlPath}`
        }
        
        // トークンの長さチェック（異常に長いトークンを防ぐ）
        if (token.length > 5000) {
          console.error("WebSocket: トークンが異常に長いです。認証に問題がある可能性があります")
          setConnectionState(ConnectionState.AUTH_FAILED)
          setConnectError("認証トークンが無効です")
          return `${base}${urlPath}`
        }
        
        const search = new URLSearchParams()
        search.set("token", token)
        return `${base}${urlPath}?${search.toString()}`
      } catch (error) {
        console.error("WebSocket: トークン取得エラー", error)
        setConnectionState(ConnectionState.AUTH_FAILED)
        setConnectError("認証トークンの取得に失敗しました")
        return `${base}${urlPath}`
      }
    }
  }, [urlPath, skipAuth])

  const cleanupHeartbeat = () => {
    if (heartbeatTimerRef.current) {
      window.clearInterval(heartbeatTimerRef.current)
      heartbeatTimerRef.current = null
    }
  }

  // 接続タイムアウトのクリーンアップ
  const cleanupConnectionTimeout = () => {
    if (connectionTimeoutRef.current) {
      window.clearTimeout(connectionTimeoutRef.current)
      connectionTimeoutRef.current = null
    }
  }

  const startHeartbeat = useCallback(() => {
    cleanupHeartbeat()
    heartbeatTimerRef.current = window.setInterval(() => {
      try {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: "ping" }))
        }
      } catch {
        // noop
      }
    }, heartbeatIntervalMs)
  }, [heartbeatIntervalMs])

  const scheduleReconnect = useCallback(() => {
    if (!autoReconnect) return
    
    const attempt = reconnectAttemptRef.current + 1
    reconnectAttemptRef.current = attempt
    
    // 最大試行回数に達した場合
    if (attempt >= maxReconnectAttempts) {
      setConnectionState(ConnectionState.MAX_ATTEMPTS_REACHED)
      setConnectError(`接続試行回数上限(${maxReconnectAttempts}回)に達しました`)
      onMaxAttemptsReached?.()
      return
    }
    
    const delay = Math.min(1000 * Math.pow(2, attempt - 1), reconnectMaxDelayMs)
    
    setConnectionState(ConnectionState.RECONNECTING)
    
    window.setTimeout(() => {
      void connect()
    }, delay)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoReconnect, reconnectMaxDelayMs, maxReconnectAttempts, onMaxAttemptsReached])

  const connect = useCallback(async () => {
    // 重複接続チェック - 接続状態とrefの両方をチェック
    if (isConnectingRef.current || isConnecting || connectionState === ConnectionState.CONNECTING) {
      console.log("WebSocket: 既に接続中です。重複接続をスキップします。")
      return
    }

    // 再接続中の場合は何もしない
    if (connectionState === ConnectionState.RECONNECTING) {
      console.log("WebSocket: 再接続中です。重複接続をスキップします。")
      return
    }

    // 最大試行回数に達している場合は何もしない
    if (connectionState === ConnectionState.MAX_ATTEMPTS_REACHED) {
      console.log("WebSocket: 最大試行回数に達しています。再接続を停止します。")
      return
    }

    // 既存の接続がある場合のチェック
    if (wsRef.current && wsRef.current.readyState === WebSocket.CONNECTING) {
      console.log("WebSocket: 接続中のWebSocketが既に存在します。重複接続をスキップします。")
      return
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log("WebSocket: 既に接続済みです。重複接続をスキップします。")
      return
    }

    if (typeof window === "undefined") return

    try {
      // 認証トークンの事前チェック
      if (!skipAuth) {
        try {
          const token = await getAuthToken()
          if (!token) {
            console.error("WebSocket: 認証トークンが取得できません。接続を中止します。")
            setConnectionState(ConnectionState.AUTH_FAILED)
            setConnectError("認証トークンが取得できません。ログインしてください。")
            return
          }
        } catch (authError) {
          console.error("WebSocket: 認証エラーが発生しました。接続を中止します。", authError)
          setConnectionState(ConnectionState.AUTH_FAILED)
          setConnectError("認証に失敗しました。ログインしてください。")
          return
        }
      }

      // 接続状態を設定
      isConnectingRef.current = true
      setIsConnecting(true)
      setConnectionState(ConnectionState.CONNECTING)
      setConnectError(null)

      const fullUrl = await wsUrlBuilder()
      
      // デバッグ用：URLの詳細情報をログ出力
      try {
        const url = new URL(fullUrl)
        const token = url.searchParams.get('token')
        if (token) {
          console.log("WebSocket: トークン情報 - 長さ:", token.length, "文字")
          if (token.length > 5000) {
            console.error("WebSocket: 警告 - トークンが異常に長いです")
          }
        } else {
          console.log("WebSocket: トークンなしで接続を試行")
        }
      } catch (e) {
        console.warn("WebSocket: URL解析エラー", e)
      }
      
      console.log("WebSocket: 接続を開始します:", fullUrl)
      
      const ws = new WebSocket(fullUrl)
      wsRef.current = ws

      // 接続タイムアウトを設定（設定可能）
      connectionTimeoutRef.current = window.setTimeout(() => {
        if (ws.readyState === WebSocket.CONNECTING) {
          console.warn(`WebSocket: 接続タイムアウト（${connectionTimeoutMs / 1000}秒）`)
          ws.close()
          isConnectingRef.current = false
          setIsConnecting(false)
          setConnectionState(ConnectionState.TIMEOUT)
          setConnectError(`接続タイムアウト: サーバーからの応答がありません（${connectionTimeoutMs / 1000}秒）`)
        }
      }, connectionTimeoutMs)

      ws.onopen = () => {
        console.log("WebSocket: 接続が確立されました")
        cleanupConnectionTimeout()
        isConnectingRef.current = false
        setIsConnecting(false)
        setIsConnected(true)
        setConnectionState(ConnectionState.CONNECTED)
        reconnectAttemptRef.current = 0
        startHeartbeat()
        onOpen?.()
      }

      ws.onmessage = (ev: MessageEvent) => {
        try {
          const data = JSON.parse(ev.data)
          setLastMessage(data)
          onMessage?.(data)
        } catch {
          // 非JSONのメッセージはそのまま渡す
          setLastMessage(ev.data)
          onMessage?.(ev.data)
        }
      }

      ws.onerror = (ev: Event) => {
        console.error("WebSocket: エラーが発生しました", ev)
        cleanupConnectionTimeout()
        isConnectingRef.current = false
        setIsConnecting(false)
        
        // エラーの詳細を分析して適切な状態を設定
        let errorState = ConnectionState.ERROR
        let errorMessage = "WebSocket接続エラー"
        
        // WebSocketの状態をチェック
        if (ws.readyState === WebSocket.CLOSED || ws.readyState === WebSocket.CLOSING) {
          errorState = ConnectionState.SERVER_ERROR
          errorMessage = "サーバーとの接続が切断されました"
        }
        
        setConnectionState(errorState)
        setConnectError(errorMessage)
        onError?.(ev)
      }

      ws.onclose = (ev: CloseEvent) => {
        console.log("WebSocket: 接続が閉じられました", ev.code, ev.reason)
        cleanupConnectionTimeout()
        isConnectingRef.current = false
        setIsConnecting(false)
        setIsConnected(false)
        
        // 閉じられた理由に基づいて状態を設定
        let newState = ConnectionState.DISCONNECTED
        let errorMessage = null
        
        switch (ev.code) {
          case 1000: // 正常終了
            newState = ConnectionState.DISCONNECTED
            break
          case 1001: // エンドポイントが離脱
            newState = ConnectionState.DISCONNECTED
            break
          case 1002: // プロトコルエラー
            newState = ConnectionState.ERROR
            errorMessage = "プロトコルエラーが発生しました"
            break
          case 1003: // サポートされていないデータ型
            newState = ConnectionState.ERROR
            errorMessage = "サポートされていないデータ型です"
            break
          case 1006: // 異常終了
            newState = ConnectionState.ERROR
            errorMessage = "サーバーとの接続が異常終了しました"
            break
          case 1008: // ポリシー違反
            newState = ConnectionState.AUTH_FAILED
            errorMessage = "認証に失敗しました"
            break
          case 1011: // サーバーエラー
            newState = ConnectionState.SERVER_ERROR
            errorMessage = "サーバーでエラーが発生しました"
            break
          default:
            newState = ConnectionState.ERROR
            errorMessage = `接続が閉じられました (コード: ${ev.code})`
        }
        
        setConnectionState(newState)
        if (errorMessage) {
          setConnectError(errorMessage)
        }
        
        cleanupHeartbeat()
        onClose?.(ev)
        
        // 自動再接続の条件を改善
        if (autoReconnect && ev.code !== 1000) { // 正常終了以外の場合のみ再接続
          scheduleReconnect()
        }
      }
    } catch (e: any) {
      console.error("WebSocket: 接続エラー", e)
      cleanupConnectionTimeout()
      isConnectingRef.current = false
      setIsConnecting(false)
      setConnectionState(ConnectionState.ERROR)
      setConnectError(e?.message ?? "Failed to open WebSocket")
      scheduleReconnect()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [wsUrlBuilder, onOpen, onClose, onError, onMessage, startHeartbeat, connectionTimeoutMs])

  // 手動再接続機能
  const reconnect = useCallback(() => {
    // 現在の接続を閉じる
    if (wsRef.current) {
      wsRef.current.close()
    }
    
    // 再接続試行回数をリセット
    reconnectAttemptRef.current = 0
    
    // 接続状態をリセット
    setConnectionState(ConnectionState.DISCONNECTED)
    setConnectError(null)
    
    // 接続を開始
    void connect()
  }, [connect])

  useEffect(() => {
    void connect()
    return () => {
      try {
        cleanupConnectionTimeout()
        isConnectingRef.current = false
        setIsConnecting(false)
        setConnectionState(ConnectionState.DISCONNECTED)
        wsRef.current?.close()
      } catch {}
      cleanupHeartbeat()
    }
  }, [connect])

  // 接続状態の整合性チェック
  useEffect(() => {
    // 接続状態とrefの整合性を確保
    if (connectionState === ConnectionState.CONNECTED && !isConnected) {
      console.warn("WebSocket: 状態の不整合を検出。接続状態を修正します。")
      setIsConnected(true)
    }
    
    if (connectionState === ConnectionState.DISCONNECTED && isConnected) {
      console.warn("WebSocket: 状態の不整合を検出。接続状態を修正します。")
      setIsConnected(false)
    }
  }, [connectionState, isConnected])

  const sendJson = useCallback((payload: JsonValue): boolean => {
    try {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(payload))
        return true
      }
    } catch {}
    return false
  }, [])

  const close = useCallback(() => {
    try {
      autoReconnect && (reconnectAttemptRef.current = 0) // 次回マウント時に再接続
      cleanupConnectionTimeout()
      isConnectingRef.current = false
      setIsConnecting(false)
      setConnectionState(ConnectionState.DISCONNECTED)
      wsRef.current?.close()
    } catch {}
  }, [autoReconnect])

  return { 
    isConnected, 
    isConnecting, 
    lastMessage, 
    connectError, 
    connectionState,
    sendJson, 
    close,
    reconnect,
    getConnectionStatus
  }
}

// WebSocket 通信管理