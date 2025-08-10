// 音声チャット用の高レベルフック
"use client"

import { useState, useCallback, useEffect } from 'react'
import { useWebSocket } from './useWebSocket'

// テスト用の簡易型定義
interface Participant {
  id: number
  name: string
  email: string
}

export const useVoiceChat = (sessionId: string) => {
  const [participants, setParticipants] = useState<Participant[]>([])
  const [isConnected, setIsConnected] = useState(false)

  // メッセージ処理関数
  const handleMessage = useCallback((message: any) => {
    if (!message || typeof message !== "object") return
    
    console.log('メッセージ処理:', message)
    
    // 参加者情報の処理
    if (message.type === 'session_participants') {
      const participantList = message.participants ?? []
      setParticipants(participantList)
    }
  }, [])

  const { sendJson, lastMessage } = useWebSocket(
    `/api/v1/test/voice-sessions/${sessionId}`, // テスト用エンドポイント
    {
      skipAuth: true, // テスト用：認証をスキップ
      onOpen: () => {
        console.log('WebSocket接続確立')
        setIsConnected(true)
      },
      onClose: () => {
        console.log('WebSocket接続切断')
        setIsConnected(false)
      },
      onMessage: (message) => {
        console.log('WebSocketメッセージ受信:', message)
        handleMessage(message)
      },
    }
  )

  // セッション参加
  const join = useCallback(() => {
    if (isConnected) {
      sendJson({
        type: 'join_session',
        session_id: sessionId,
        timestamp: new Date().toISOString()
      })
    }
  }, [isConnected, sendJson, sessionId])

  // セッション退出
  const leave = useCallback(() => {
    if (isConnected) {
      sendJson({
        type: 'leave_session',
        session_id: sessionId,
        timestamp: new Date().toISOString()
      })
    }
  }, [isConnected, sendJson, sessionId])

  // 接続時に自動参加
  useEffect(() => {
    if (isConnected) {
      join()
    }
  }, [isConnected, join])

  return {
    isConnected,
    participants,
    join,
    leave,
    sendJson
  }
}