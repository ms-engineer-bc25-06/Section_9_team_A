"use client"

import { useCallback, useEffect, useRef, useState } from 'react'

interface WebRTCPeer {
  id: string
  connection: RTCPeerConnection
  stream?: MediaStream
  isConnected: boolean
}

interface UseWebRTCReturn {
  localStream: MediaStream | null
  peers: Map<string, RTCPeerConnection>
  isInitialized: boolean
  error: string | null
  
  // 初期化・接続管理
  initialize: () => Promise<void>
  joinRoom: (roomId: string) => Promise<void>
  leaveRoom: () => Promise<void>
  
  // 参加者管理
  addPeer: (peerId: string) => Promise<RTCPeerConnection>
  removePeer: (peerId: string) => void
  
  // 音声制御
  toggleMute: () => void
  toggleSpeaker: () => void
  isMuted: boolean
  isSpeakerOn: boolean
  
  // 接続状態
  connectionState: RTCPeerConnectionState
}

export const useWebRTC = (): UseWebRTCReturn => {
  const [localStream, setLocalStream] = useState<MediaStream | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isMuted, setIsMuted] = useState(false)
  const [isSpeakerOn, setIsSpeakerOn] = useState(true)
  const [connectionState, setConnectionState] = useState<RTCPeerConnectionState>('new')
  
  const peersRef = useRef<Map<string, RTCPeerConnection>>(new Map())
  const localStreamRef = useRef<MediaStream | null>(null)
  const roomIdRef = useRef<string | null>(null)

  // STUN/TURNサーバー設定
  const rtcConfiguration: RTCConfiguration = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' },
      // 本番環境ではTURNサーバーも追加
      // { urls: 'turn:your-turn-server.com:3478', username: 'username', credential: 'password' }
    ],
    iceCandidatePoolSize: 10,
  }

  // ローカルメディアストリームの取得
  const getLocalMediaStream = useCallback(async (): Promise<MediaStream> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
        video: false, // 音声のみ
      })
      
      setLocalStream(stream)
      localStreamRef.current = stream
      return stream
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`メディアストリームの取得に失敗: ${errorMessage}`)
      throw err
    }
  }, [])

  // RTCPeerConnectionの作成
  const createPeerConnection = useCallback((peerId: string): RTCPeerConnection => {
    const peerConnection = new RTCPeerConnection(rtcConfiguration)
    
    // ローカルストリームを追加
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStreamRef.current!)
      })
    }

    // ICE候補の処理
    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        // WebSocket経由でICE候補を送信
        console.log('ICE候補を送信:', event.candidate)
        // TODO: WebSocketでICE候補を送信
      }
    }

    // 接続状態の監視
    peerConnection.onconnectionstatechange = () => {
      console.log(`Peer ${peerId} 接続状態:`, peerConnection.connectionState)
      setConnectionState(peerConnection.connectionState)
    }

    // リモートストリームの処理
    peerConnection.ontrack = (event) => {
      console.log('リモートストリームを受信:', event.streams[0])
      // TODO: リモートストリームをUIに表示
    }

    // ICE接続状態の監視
    peerConnection.oniceconnectionstatechange = () => {
      console.log(`Peer ${peerId} ICE状態:`, peerConnection.iceConnectionState)
    }

    return peerConnection
  }, [])

  // 初期化
  const initialize = useCallback(async (): Promise<void> => {
    try {
      setError(null)
      
      // ローカルメディアストリームを取得
      await getLocalMediaStream()
      
      setIsInitialized(true)
      console.log('WebRTC初期化完了')
    } catch (err) {
      console.error('WebRTC初期化エラー:', err)
      setError('WebRTC初期化に失敗しました')
    }
  }, [getLocalMediaStream])

  // ルーム参加
  const joinRoom = useCallback(async (roomId: string): Promise<void> => {
    try {
      if (!isInitialized) {
        await initialize()
      }
      
      roomIdRef.current = roomId
      console.log(`ルーム ${roomId} に参加`)
      
      // TODO: WebSocket経由でルーム参加を通知
    } catch (err) {
      console.error('ルーム参加エラー:', err)
      setError('ルーム参加に失敗しました')
    }
  }, [isInitialized, initialize])

  // ルーム退出
  const leaveRoom = useCallback(async (): Promise<void> => {
    try {
      // すべてのピア接続を閉じる
      peersRef.current.forEach((peer, peerId) => {
        peer.close()
        console.log(`Peer ${peerId} 接続を閉じました`)
      })
      peersRef.current.clear()

      // ローカルストリームを停止
      if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach(track => track.stop())
        setLocalStream(null)
        localStreamRef.current = null
      }

      roomIdRef.current = null
      console.log('ルームから退出しました')
    } catch (err) {
      console.error('ルーム退出エラー:', err)
      setError('ルーム退出に失敗しました')
    }
  }, [])

  // ピア追加
  const addPeer = useCallback(async (peerId: string): Promise<RTCPeerConnection> => {
    try {
      // 既存のピア接続がある場合は削除
      if (peersRef.current.has(peerId)) {
        const existingPeer = peersRef.current.get(peerId)!
        existingPeer.close()
        peersRef.current.delete(peerId)
      }

      // 新しいピア接続を作成
      const peerConnection = createPeerConnection(peerId)
      peersRef.current.set(peerId, peerConnection)

      // Offerを作成して送信
      const offer = await peerConnection.createOffer()
      await peerConnection.setLocalDescription(offer)
      
      console.log(`Peer ${peerId} を追加し、Offerを作成`)
      
      // TODO: WebSocket経由でOfferを送信
      
      return peerConnection
    } catch (err) {
      console.error(`Peer ${peerId} 追加エラー:`, err)
      throw err
    }
  }, [createPeerConnection])

  // ピア削除
  const removePeer = useCallback((peerId: string): void => {
    const peer = peersRef.current.get(peerId)
    if (peer) {
      peer.close()
      peersRef.current.delete(peerId)
      console.log(`Peer ${peerId} を削除しました`)
    }
  }, [])

  // ミュート切り替え
  const toggleMute = useCallback((): void => {
    if (localStreamRef.current) {
      const audioTrack = localStreamRef.current.getAudioTracks()[0]
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled
        setIsMuted(!audioTrack.enabled)
        console.log(`音声を${audioTrack.enabled ? '有効' : '無効'}にしました`)
      }
    }
  }, [])

  // スピーカー切り替え
  const toggleSpeaker = useCallback((): void => {
    setIsSpeakerOn(!isSpeakerOn)
    // TODO: スピーカー出力の制御
    console.log(`スピーカーを${!isSpeakerOn ? '有効' : '無効'}にしました`)
  }, [isSpeakerOn])

  // クリーンアップ
  useEffect(() => {
    return () => {
      leaveRoom()
    }
  }, [leaveRoom])

  return {
    localStream,
    peers: peersRef.current,
    isInitialized,
    error,
    initialize,
    joinRoom,
    leaveRoom,
    addPeer,
    removePeer,
    toggleMute,
    toggleSpeaker,
    isMuted,
    isSpeakerOn,
    connectionState,
  }
}
