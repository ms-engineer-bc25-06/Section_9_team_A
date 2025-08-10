// 音声チャット用の高レベルフック
"use client"

import { useState, useCallback, useEffect } from 'react'
import { useWebSocket } from './useWebSocket'

// 参加者情報の型定義
interface Participant {
  id: string
  display_name?: string
  username: string
  email?: string
  role?: string
  status?: string
  is_active?: boolean
  is_muted?: boolean
  audioLevel?: number
  joinedAt?: string
  lastActivity?: string
  speakTimeTotal?: number
  speakTimeSession?: number
  messagesSent?: number
  permissions?: string[]
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
    
    // 参加者状態更新の処理
    if (message.type === 'participant_state_update') {
      const { participant_id, state, data } = message
      setParticipants(prev => prev.map(p => 
        p.id === participant_id 
          ? { ...p, ...data }
          : p
      ))
    }
    
    // 参加者追加の処理
    if (message.type === 'participant_joined') {
      const newParticipant = message.participant
      setParticipants(prev => [...prev, newParticipant])
    }
    
    // 参加者退出の処理
    if (message.type === 'participant_left') {
      const { participant_id } = message
      setParticipants(prev => prev.filter(p => p.id !== participant_id))
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

  // 参加者管理の関数
  const muteParticipant = useCallback((participantId: string, muted: boolean) => {
    if (isConnected) {
      sendJson({
        type: 'mute_participant',
        participant_id: participantId,
        muted: muted,
        timestamp: new Date().toISOString()
      })
    }
  }, [isConnected, sendJson])

  const changeParticipantRole = useCallback((participantId: string, newRole: string) => {
    if (isConnected) {
      sendJson({
        type: 'change_participant_role',
        participant_id: participantId,
        new_role: newRole,
        timestamp: new Date().toISOString()
      })
    }
  }, [isConnected, sendJson])

  const removeParticipant = useCallback((participantId: string) => {
    if (isConnected) {
      sendJson({
        type: 'remove_participant',
        participant_id: participantId,
        timestamp: new Date().toISOString()
      })
    }
  }, [isConnected, sendJson])

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
    sendJson,
    muteParticipant,
    changeParticipantRole,
    removeParticipant
  }
}