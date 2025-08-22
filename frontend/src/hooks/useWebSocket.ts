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
  skipAuth?: boolean // テスト用：認証をスキップ
  onOpen?: () => void
  onClose?: (ev: CloseEvent) => void
  onError?: (ev: Event) => void
  onMessage?: (data: any) => void
}

export interface UseWebSocketReturn {
  isConnected: boolean
  isConnecting: boolean // 接続中状態を追加
  lastMessage: any | null
  connectError: string | null
  connectionState: string // 接続状態の詳細を追加
  sendJson: (payload: JsonValue) => boolean
  close: () => void
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
    skipAuth = false, // テスト用：認証をスキップ
    onOpen,
    onClose,
    onError,
    onMessage,
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
  const [connectionState, setConnectionState] = useState<string>("disconnected") // 接続状態の詳細

  const wsUrlBuilder = useMemo(() => {
    const base = resolveWsBaseUrl()
    return async () => {
      if (!base) throw new Error("WS base URL not configured (NEXT_PUBLIC_WS_BASE_URL or NEXT_PUBLIC_API_BASE_URL)")
      
      // テスト用：認証をスキップ
      if (skipAuth) {
        return `${base}${urlPath}`
      }
      
      const token = await getAuthToken()
      const search = new URLSearchParams()
      if (token) search.set("token", token)
      return `${base}${urlPath}?${search.toString()}`
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
    const delay = Math.min(1000 * Math.pow(2, attempt - 1), reconnectMaxDelayMs)
    window.setTimeout(() => {
      void connect()
    }, delay)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoReconnect, reconnectMaxDelayMs])

  const connect = useCallback(async () => {
    // 重複接続チェック
    if (isConnectingRef.current) {
      console.log("WebSocket: 既に接続中です。重複接続をスキップします。")
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
      // 接続状態を設定
      isConnectingRef.current = true
      setIsConnecting(true)
      setConnectionState("connecting")
      setConnectError(null)

      const fullUrl = await wsUrlBuilder()
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
          setConnectionState("timeout")
          setConnectError(`接続タイムアウト: サーバーからの応答がありません（${connectionTimeoutMs / 1000}秒）`)
        }
      }, connectionTimeoutMs)

      ws.onopen = () => {
        console.log("WebSocket: 接続が確立されました")
        cleanupConnectionTimeout()
        isConnectingRef.current = false
        setIsConnecting(false)
        setIsConnected(true)
        setConnectionState("connected")
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
        setConnectionState("error")
        setConnectError("WebSocket error")
        onError?.(ev)
      }

      ws.onclose = (ev: CloseEvent) => {
        console.log("WebSocket: 接続が閉じられました", ev.code, ev.reason)
        cleanupConnectionTimeout()
        isConnectingRef.current = false
        setIsConnecting(false)
        setIsConnected(false)
        setConnectionState("disconnected")
        cleanupHeartbeat()
        onClose?.(ev)
        scheduleReconnect()
      }
    } catch (e: any) {
      console.error("WebSocket: 接続エラー", e)
      cleanupConnectionTimeout()
      isConnectingRef.current = false
      setIsConnecting(false)
      setConnectionState("error")
      setConnectError(e?.message ?? "Failed to open WebSocket")
      scheduleReconnect()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [wsUrlBuilder, onOpen, onClose, onError, onMessage, startHeartbeat, connectionTimeoutMs])

  useEffect(() => {
    void connect()
    return () => {
      try {
        cleanupConnectionTimeout()
        isConnectingRef.current = false
        setIsConnecting(false)
        setConnectionState("disconnected")
        wsRef.current?.close()
      } catch {}
      cleanupHeartbeat()
    }
  }, [connect])

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
      setConnectionState("disconnected")
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
    close 
  }
}

// WebSocket 通信管理