// 音声チャット用の高レベルフック
"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { useWebSocket } from "@/hooks/useWebSocket"

export interface UseVoiceChatOptions {
  onParticipants?: (participants: any[]) => void
}

export interface UseVoiceChatReturn {
  isConnected: boolean
  participants: any[]
  join: () => void
  leave: () => void
  send: (type: string, payload?: Record<string, unknown>) => void
  lastMessage: any | null
}

export function useVoiceChat(sessionId: string, options: UseVoiceChatOptions = {}): UseVoiceChatReturn {
  const [participants, setParticipants] = useState<any[]>([])

  const { isConnected, lastMessage, sendJson, close } = useWebSocket(
    `/api/v1/voice-sessions/${sessionId}`,
    {
      onMessage: (data) => {
        if (!data || typeof data !== "object") return
        const type = (data as any).type
        if (type === "session_participants" || type === "session_participants_info") {
          const list = (data as any).participants ?? []
          setParticipants(list)
          options.onParticipants?.(list)
        }
      },
    }
  )

  useEffect(() => {
    if (!lastMessage) return
    const m = lastMessage as any
    if (m.type === "user_joined" || m.type === "user_left") {
      // 最新の参加者一覧はサーバから follow-up される前提
      // ここでは軽量な楽観更新のみ（必要なら再取得要求を送る）
    }
  }, [lastMessage])

  const send = useCallback(
    (type: string, payload: Record<string, unknown> = {}) => {
      sendJson({ type, session_id: sessionId, ...payload })
    },
    [sendJson, sessionId]
  )

  const join = useCallback(() => {
    send("join_session")
  }, [send])

  const leave = useCallback(() => {
    try {
      send("leave_session")
    } finally {
      close()
    }
  }, [close, send])

  return { isConnected, participants, join, leave, send, lastMessage }
}

// 音声チャット操作