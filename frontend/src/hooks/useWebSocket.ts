// WebSocket 通信管理（クライアント専用）
"use client"

import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { getAuthToken } from "@/lib/apiClient"

type JsonValue = unknown

export interface UseWebSocketOptions {
  autoReconnect?: boolean
  reconnectMaxDelayMs?: number
  heartbeatIntervalMs?: number
  skipAuth?: boolean // テスト用：認証をスキップ
  onOpen?: () => void
  onClose?: (ev: CloseEvent) => void
  onError?: (ev: Event) => void
  onMessage?: (data: any) => void
}

export interface UseWebSocketReturn {
  isConnected: boolean
  lastMessage: any | null
  connectError: string | null
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
    skipAuth = false, // テスト用：認証をスキップ
    onOpen,
    onClose,
    onError,
    onMessage,
  } = options

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptRef = useRef<number>(0)
  const heartbeatTimerRef = useRef<number | null>(null)

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any | null>(null)
  const [connectError, setConnectError] = useState<string | null>(null)

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
    if (typeof window === "undefined") return
    try {
      const fullUrl = await wsUrlBuilder()
      const ws = new WebSocket(fullUrl)
      wsRef.current = ws
      setConnectError(null)

      ws.onopen = () => {
        setIsConnected(true)
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
        setConnectError("WebSocket error")
        onError?.(ev)
      }

      ws.onclose = (ev: CloseEvent) => {
        setIsConnected(false)
        cleanupHeartbeat()
        onClose?.(ev)
        scheduleReconnect()
      }
    } catch (e: any) {
      setConnectError(e?.message ?? "Failed to open WebSocket")
      scheduleReconnect()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [wsUrlBuilder, onOpen, onClose, onError, onMessage, startHeartbeat])

  useEffect(() => {
    void connect()
    return () => {
      try {
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
      wsRef.current?.close()
    } catch {}
  }, [autoReconnect])

  return { isConnected, lastMessage, connectError, sendJson, close }
}

// WebSocket 通信管理