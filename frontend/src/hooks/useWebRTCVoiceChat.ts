"use client"

import { useCallback, useEffect, useRef, useState } from 'react'
import { useWebRTC } from './useWebRTC'
import { useWebRTCSignaling } from './useWebRTCSignaling'

interface RemoteStream {
  peerId: string
  stream: MediaStream
  isActive: boolean
}

interface UseWebRTCVoiceChatReturn {
  // 接続状態
  isConnected: boolean
  isInitialized: boolean
  connectionState: RTCPeerConnectionState
  
  // 音声制御
  isMuted: boolean
  isSpeakerOn: boolean
  toggleMute: () => void
  toggleSpeaker: () => void
  
  // 参加者管理
  localStream: MediaStream | null
  remoteStreams: RemoteStream[]
  participants: string[]
  
  // ルーム管理
  joinRoom: (roomId: string) => Promise<void>
  leaveRoom: () => Promise<void>
  
  // エラーハンドリング
  error: string | null
  
  // 接続統計
  connectionStats: {
    totalPeers: number
    connectedPeers: number
    failedConnections: number
  }
}

export const useWebRTCVoiceChat = (roomId: string): UseWebRTCVoiceChatReturn => {
  const [remoteStreams, setRemoteStreams] = useState<RemoteStream[]>([])
  const [participants, setParticipants] = useState<string[]>([])
  const [connectionStats, setConnectionStats] = useState({
    totalPeers: 0,
    connectedPeers: 0,
    failedConnections: 0,
  })

  const remoteStreamsRef = useRef<Map<string, MediaStream>>(new Map())
  const peerConnectionsRef = useRef<Map<string, RTCPeerConnection>>(new Map())

  // WebRTCフック
  const {
    localStream,
    isInitialized,
    error: webrtcError,
    initialize,
    joinRoom: webrtcJoinRoom,
    leaveRoom: webrtcLeaveRoom,
    toggleMute,
    toggleSpeaker,
    isMuted,
    isSpeakerOn,
    connectionState,
  } = useWebRTC()

  // シグナリングフック
  const {
    isConnected: signalingConnected,
    sendOffer,
    sendAnswer,
    sendIceCandidate,
    updateMessageHandlers,
  } = useWebRTCSignaling(roomId)

  // シグナリングメッセージハンドラーの設定
  useEffect(() => {
    updateMessageHandlers({
      onOffer: handleOffer,
      onAnswer: handleAnswer,
      onIceCandidate: handleIceCandidate,
      onPeerJoined: handlePeerJoined,
      onPeerLeft: handlePeerLeft,
    })
  }, [updateMessageHandlers])

  // Offer処理
  const handleOffer = useCallback(async (from: string, offer: RTCSessionDescriptionInit) => {
    try {
      console.log(`Offer受信 from ${from}:`, offer)
      
      // 新しいピア接続を作成
      const peerConnection = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' },
        ],
      })

      // ローカルストリームを追加
      if (localStream) {
        localStream.getTracks().forEach(track => {
          peerConnection.addTrack(track, localStream)
        })
      }

      // リモートストリームの処理
      peerConnection.ontrack = (event) => {
        console.log(`リモートストリーム受信 from ${from}:`, event.streams[0])
        const stream = event.streams[0]
        
        // リモートストリームを保存
        remoteStreamsRef.current.set(from, stream)
        
        setRemoteStreams(prev => [
          ...prev.filter(rs => rs.peerId !== from),
          { peerId: from, stream, isActive: true }
        ])
      }

      // ICE候補の処理
      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          sendIceCandidate(from, event.candidate)
        }
      }

      // 接続状態の監視
      peerConnection.onconnectionstatechange = () => {
        console.log(`Peer ${from} 接続状態:`, peerConnection.connectionState)
        
        if (peerConnection.connectionState === 'connected') {
          setConnectionStats(prev => ({
            ...prev,
            connectedPeers: prev.connectedPeers + 1,
          }))
        } else if (peerConnection.connectionState === 'failed') {
          setConnectionStats(prev => ({
            ...prev,
            failedConnections: prev.failedConnections + 1,
          }))
        }
      }

      // ピア接続を保存
      peerConnectionsRef.current.set(from, peerConnection)

      // Offerを設定
      await peerConnection.setRemoteDescription(offer)

      // Answerを作成して送信
      const answer = await peerConnection.createAnswer()
      await peerConnection.setLocalDescription(answer)
      
      sendAnswer(from, answer)
      
      console.log(`Answer送信 to ${from}:`, answer)
      
    } catch (error) {
      console.error(`Offer処理エラー from ${from}:`, error)
      setConnectionStats(prev => ({
        ...prev,
        failedConnections: prev.failedConnections + 1,
      }))
    }
  }, [localStream, sendAnswer, sendIceCandidate])

  // Answer処理
  const handleAnswer = useCallback(async (from: string, answer: RTCSessionDescriptionInit) => {
    try {
      console.log(`Answer受信 from ${from}:`, answer)
      
      const peerConnection = peerConnectionsRef.current.get(from)
      if (peerConnection) {
        await peerConnection.setRemoteDescription(answer)
        console.log(`Remote description設定完了 for ${from}`)
      }
    } catch (error) {
      console.error(`Answer処理エラー from ${from}:`, error)
    }
  }, [])

  // ICE候補処理
  const handleIceCandidate = useCallback(async (from: string, candidate: RTCIceCandidateInit) => {
    try {
      console.log(`ICE候補受信 from ${from}:`, candidate)
      
      const peerConnection = peerConnectionsRef.current.get(from)
      if (peerConnection) {
        await peerConnection.addIceCandidate(candidate)
        console.log(`ICE候補追加完了 for ${from}`)
      }
    } catch (error) {
      console.error(`ICE候補処理エラー from ${from}:`, error)
    }
  }, [])

  // ピア参加処理
  const handlePeerJoined = useCallback((peerId: string) => {
    console.log(`ピア参加: ${peerId}`)
    setParticipants(prev => [...prev, peerId])
    setConnectionStats(prev => ({
      ...prev,
      totalPeers: prev.totalPeers + 1,
    }))
  }, [])

  // ピア退出処理
  const handlePeerLeft = useCallback((peerId: string) => {
    console.log(`ピア退出: ${peerId}`)
    
    // ピア接続を閉じる
    const peerConnection = peerConnectionsRef.current.get(peerId)
    if (peerConnection) {
      peerConnection.close()
      peerConnectionsRef.current.delete(peerId)
    }
    
    // リモートストリームを削除
    remoteStreamsRef.current.delete(peerId)
    setRemoteStreams(prev => prev.filter(rs => rs.peerId !== peerId))
    
    // 参加者リストから削除
    setParticipants(prev => prev.filter(id => id !== peerId))
    
    setConnectionStats(prev => ({
      ...prev,
      totalPeers: Math.max(0, prev.totalPeers - 1),
      connectedPeers: Math.max(0, prev.connectedPeers - 1),
    }))
  }, [])

  // ルーム参加
  const joinRoom = useCallback(async (roomId: string) => {
    try {
      await webrtcJoinRoom(roomId)
      console.log(`ルーム ${roomId} に参加しました`)
    } catch (error) {
      console.error('ルーム参加エラー:', error)
    }
  }, [webrtcJoinRoom])

  // ルーム退出
  const leaveRoom = useCallback(async () => {
    try {
      // すべてのピア接続を閉じる
      peerConnectionsRef.current.forEach((connection, peerId) => {
        connection.close()
        console.log(`Peer ${peerId} 接続を閉じました`)
      })
      peerConnectionsRef.current.clear()

      // リモートストリームをクリア
      remoteStreamsRef.current.clear()
      setRemoteStreams([])
      setParticipants([])

      // WebRTCルーム退出
      await webrtcLeaveRoom()
      
      console.log('ルームから退出しました')
    } catch (error) {
      console.error('ルーム退出エラー:', error)
    }
  }, [webrtcLeaveRoom])

  // 初期化時にWebRTCを初期化
  useEffect(() => {
    if (!isInitialized) {
      initialize()
    }
  }, [isInitialized, initialize])

  // クリーンアップ
  useEffect(() => {
    return () => {
      leaveRoom()
    }
  }, [leaveRoom])

  return {
    isConnected: signalingConnected,
    isInitialized,
    connectionState,
    isMuted,
    isSpeakerOn,
    toggleMute,
    toggleSpeaker,
    localStream,
    remoteStreams,
    participants,
    joinRoom,
    leaveRoom,
    error: webrtcError,
    connectionStats,
  }
}
