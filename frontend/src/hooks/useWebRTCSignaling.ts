"use client"

import { useCallback, useRef } from 'react'
import { useWebSocket } from './useWebSocket'

interface WebRTCMessage {
  type: 'offer' | 'answer' | 'ice-candidate' | 'peer-joined' | 'peer-left'
  from: string
  to?: string
  roomId: string
  data: any
  timestamp: string
}

interface UseWebRTCSignalingReturn {
  // シグナリングメッセージの送信
  sendOffer: (to: string, offer: RTCSessionDescriptionInit) => void
  sendAnswer: (to: string, answer: RTCSessionDescriptionInit) => void
  sendIceCandidate: (to: string, candidate: RTCIceCandidateInit) => void
  
  // メッセージハンドラーの更新
  updateMessageHandlers: (handlers: Partial<{
    onOffer?: (from: string, offer: RTCSessionDescriptionInit) => void
    onAnswer?: (from: string, answer: RTCSessionDescriptionInit) => void
    onIceCandidate?: (from: string, candidate: RTCIceCandidateInit) => void
    onPeerJoined?: (peerId: string) => void
    onPeerLeft?: (peerId: string) => void
  }>) => void
  
  // 接続状態
  isConnected: boolean
  
  // エラーハンドリング
  error: string | null
}

export const useWebRTCSignaling = (
  roomId: string,
  onOffer?: (from: string, offer: RTCSessionDescriptionInit) => void,
  onAnswer?: (from: string, answer: RTCSessionDescriptionInit) => void,
  onIceCandidate?: (from: string, candidate: RTCIceCandidateInit) => void,
  onPeerJoined?: (peerId: string) => void,
  onPeerLeft?: (peerId: string) => void
): UseWebRTCSignalingReturn => {
  
  const { sendJson, isConnected, lastMessage } = useWebSocket(
    `/api/v1/websocket/voice-sessions/${roomId}`,
    {
      onMessage: (message) => {
        handleSignalingMessage(message)
      },
    }
  )

  const messageHandlersRef = useRef({
    onOffer,
    onAnswer,
    onIceCandidate,
    onPeerJoined,
    onPeerLeft,
  })

  // メッセージハンドラーの更新
  const updateMessageHandlers = useCallback((handlers: Partial<typeof messageHandlersRef.current>) => {
    messageHandlersRef.current = { ...messageHandlersRef.current, ...handlers }
  }, [])

  // シグナリングメッセージの処理
  const handleSignalingMessage = useCallback((message: any) => {
    try {
      if (!message || typeof message !== 'object') return

      const { type, from, data } = message
      console.log('シグナリングメッセージ受信:', { type, from, data })

      switch (type) {
        case 'offer':
          if (messageHandlersRef.current.onOffer) {
            messageHandlersRef.current.onOffer(from, data)
          }
          break

        case 'answer':
          if (messageHandlersRef.current.onAnswer) {
            messageHandlersRef.current.onAnswer(from, data)
          }
          break

        case 'ice-candidate':
          if (messageHandlersRef.current.onIceCandidate) {
            messageHandlersRef.current.onIceCandidate(from, data)
          }
          break

        case 'peer-joined':
          if (messageHandlersRef.current.onPeerJoined) {
            messageHandlersRef.current.onPeerJoined(from)
          }
          break

        case 'peer-left':
          if (messageHandlersRef.current.onPeerLeft) {
            messageHandlersRef.current.onPeerLeft(from)
          }
          break

        default:
          console.log('未対応のシグナリングメッセージ:', type)
      }
    } catch (error) {
      console.error('シグナリングメッセージ処理エラー:', error)
    }
  }, [])

  // Offer送信
  const sendOffer = useCallback((to: string, offer: RTCSessionDescriptionInit) => {
    const message: WebRTCMessage = {
      type: 'offer',
      from: 'current-user', // TODO: 実際のユーザーIDに置き換え
      to,
      roomId,
      data: offer,
      timestamp: new Date().toISOString(),
    }
    
    sendJson(message)
    console.log('Offer送信:', { to, offer })
  }, [sendJson, roomId])

  // Answer送信
  const sendAnswer = useCallback((to: string, answer: RTCSessionDescriptionInit) => {
    const message: WebRTCMessage = {
      type: 'answer',
      from: 'current-user', // TODO: 実際のユーザーIDに置き換え
      to,
      roomId,
      data: answer,
      timestamp: new Date().toISOString(),
    }
    
    sendJson(message)
    console.log('Answer送信:', { to, answer })
  }, [sendJson, roomId])

  // ICE候補送信
  const sendIceCandidate = useCallback((to: string, candidate: RTCIceCandidateInit) => {
    const message: WebRTCMessage = {
      type: 'ice-candidate',
      from: 'current-user', // TODO: 実際のユーザーIDに置き換え
      to,
      roomId,
      data: candidate,
      timestamp: new Date().toISOString(),
    }
    
    sendJson(message)
    console.log('ICE候補送信:', { to, candidate })
  }, [sendJson, roomId])

  return {
    sendOffer,
    sendAnswer,
    sendIceCandidate,
    isConnected,
    error: null,
    updateMessageHandlers,
  }
}
