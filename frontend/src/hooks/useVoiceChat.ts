// 音声チャット用の高レベルフック
"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { useWebSocket } from "@/hooks/useWebSocket"
import { WS_EVENT } from "@/../../shared/constants/websocket-events"
import type {
  IncomingWsMessage,
  OutgoingWsMessage,
  SessionParticipantsMessage,
} from "@/../../shared/types/websocket"

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
        const msg = data as IncomingWsMessage
        if (
          msg.type === WS_EVENT.SESSION_PARTICIPANTS ||
          msg.type === WS_EVENT.SESSION_PARTICIPANTS_INFO
        ) {
          const sp = msg as SessionParticipantsMessage
          const list = sp.participants ?? []
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
      const message: OutgoingWsMessage | Record<string, unknown> = {
        type: type as any,
        session_id: sessionId,
        ...payload,
      }
      sendJson(message)
    },
    [sendJson, sessionId]
  )

  const join = useCallback(() => {
    send(WS_EVENT.JOIN_SESSION)
  }, [send])

  const leave = useCallback(() => {
    try {
      send(WS_EVENT.LEAVE_SESSION)
    } finally {
      close()
    }
  }, [close, send])

  return { isConnected, participants, join, leave, send, lastMessage }
}

// 音声チャット操作