import { renderHook, act } from '@testing-library/react'
import { useVoiceChat } from '../useVoiceChat'
import { useWebSocket } from '../useWebSocket'

// WebSocketフックのモック
jest.mock('../useWebSocket')
const mockUseWebSocket = useWebSocket as jest.MockedFunction<typeof useWebSocket>

// WebRTC関連のモック
const mockRTCPeerConnection = jest.fn()
const mockMediaStream = {
  getTracks: jest.fn(() => []),
  getAudioTracks: jest.fn(() => []),
}

// グローバルオブジェクトのモック
Object.defineProperty(global, 'RTCPeerConnection', {
  writable: true,
  value: mockRTCPeerConnection,
})

Object.defineProperty(global, 'MediaStream', {
  writable: true,
  value: jest.fn(() => mockMediaStream),
})

Object.defineProperty(global.navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: jest.fn(),
  },
})

describe('useVoiceChat', () => {
  const mockRoomId = 'test-room-123'
  const mockSendJson = jest.fn()
  const mockLastMessage = null

  beforeEach(() => {
    jest.clearAllMocks()
    
    mockUseWebSocket.mockReturnValue({
      sendJson: mockSendJson,
      isConnected: true,
      lastMessage: mockLastMessage,
    })

    // RTCPeerConnectionのモック実装
    mockRTCPeerConnection.mockImplementation(() => ({
      createOffer: jest.fn().mockResolvedValue({ type: 'offer', sdp: 'mock-sdp' }),
      createAnswer: jest.fn().mockResolvedValue({ type: 'answer', sdp: 'mock-sdp' }),
      setLocalDescription: jest.fn().mockResolvedValue(undefined),
      setRemoteDescription: jest.fn().mockResolvedValue(undefined),
      addIceCandidate: jest.fn().mockResolvedValue(undefined),
      addTrack: jest.fn(),
      ontrack: null,
      onicecandidate: null,
      onconnectionstatechange: null,
      connectionState: 'new',
      close: jest.fn(),
    }))
  })

  it('初期化時に正しい状態を持つ', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))

    expect(result.current.localStream).toBeNull()
    expect(result.current.remoteStreams).toEqual([])
    expect(result.current.participants).toEqual([])
    expect(result.current.isInitialized).toBe(false)
    expect(result.current.isConnected).toBe(false)
    expect(result.current.connectionState).toBe('new')
    expect(result.current.isMuted).toBe(false)
    expect(result.current.isSpeakerOn).toBe(true)
    expect(result.current.error).toBeNull()
  })

  it('WebSocket接続が正しく設定される', () => {
    renderHook(() => useVoiceChat(mockRoomId))

    expect(mockUseWebSocket).toHaveBeenCalledWith(
      `/api/v1/websocket/voice-sessions/${mockRoomId}`,
      expect.objectContaining({
        onMessage: expect.any(Function),
        debugMode: true,
      })
    )
  })

  it('マイクのミュート/アンミュートが正しく動作する', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))

    act(() => {
      result.current.toggleMute()
    })

    expect(result.current.isMuted).toBe(true)

    act(() => {
      result.current.toggleMute()
    })

    expect(result.current.isMuted).toBe(false)
  })

  it('スピーカーのオン/オフが正しく動作する', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))

    act(() => {
      result.current.toggleSpeaker()
    })

    expect(result.current.isSpeakerOn).toBe(false)

    act(() => {
      result.current.toggleSpeaker()
    })

    expect(result.current.isSpeakerOn).toBe(true)
  })

  it('参加者の追加が正しく動作する', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))

    act(() => {
      result.current.addParticipant('user-1')
    })

    expect(result.current.participants).toContain('user-1')
  })

  it('参加者の削除が正しく動作する', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))

    act(() => {
      result.current.addParticipant('user-1')
      result.current.addParticipant('user-2')
    })

    expect(result.current.participants).toHaveLength(2)

    act(() => {
      result.current.removeParticipant('user-1')
    })

    expect(result.current.participants).toContain('user-2')
    expect(result.current.participants).not.toContain('user-1')
  })

  it('エラー状態の設定が正しく動作する', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))
    const errorMessage = 'Test error message'

    act(() => {
      result.current.setError(errorMessage)
    })

    expect(result.current.error).toBe(errorMessage)
  })

  it('統計情報の更新が正しく動作する', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))

    act(() => {
      result.current.updateStats({
        totalPeers: 3,
        connectedPeers: 2,
        failedConnections: 1,
        audioLevel: 0.5,
        latency: 100,
        packetLoss: 0.01,
      })
    })

    expect(result.current.stats.totalPeers).toBe(3)
    expect(result.current.stats.connectedPeers).toBe(2)
    expect(result.current.stats.failedConnections).toBe(1)
    expect(result.current.stats.audioLevel).toBe(0.5)
    expect(result.current.stats.latency).toBe(100)
    expect(result.current.stats.packetLoss).toBe(0.01)
  })

  it('WebRTC設定の読み込みが正しく動作する', async () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))

    // モックのWebRTC設定レスポンス
    const mockConfig = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'turn:turn.example.com', username: 'user', credential: 'pass' }
      ],
      iceCandidatePoolSize: 10
    }

    // fetchのモック
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockConfig)
    })

    await act(async () => {
      await result.current.loadWebRTCConfig()
    })

    expect(result.current.webrtcConfigLoaded).toBe(true)
    expect(result.current.config.iceServers).toEqual(mockConfig.iceServers)
  })

  it('シグナリングメッセージの処理が正しく動作する', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))

    const mockMessage = {
      type: 'peer-joined',
      from: 'user-123',
      data: {}
    }

    act(() => {
      // シグナリングメッセージハンドラーを直接呼び出し
      const messageHandler = mockUseWebSocket.mock.calls[0][1].onMessage
      messageHandler(mockMessage)
    })

    expect(result.current.participants).toContain('user-123')
  })

  it('接続状態の変更が正しく処理される', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))

    act(() => {
      result.current.setConnectionState('connected')
    })

    expect(result.current.connectionState).toBe('connected')
    expect(result.current.isConnected).toBe(true)
  })

  it('リモートストリームの追加が正しく動作する', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))
    const mockStream = mockMediaStream

    act(() => {
      result.current.addRemoteStream('user-123', mockStream)
    })

    expect(result.current.remoteStreams).toHaveLength(1)
    expect(result.current.remoteStreams[0].peerId).toBe('user-123')
    expect(result.current.remoteStreams[0].stream).toBe(mockStream)
    expect(result.current.remoteStreams[0].isActive).toBe(true)
  })

  it('リモートストリームの削除が正しく動作する', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))
    const mockStream = mockMediaStream

    act(() => {
      result.current.addRemoteStream('user-123', mockStream)
    })

    expect(result.current.remoteStreams).toHaveLength(1)

    act(() => {
      result.current.removeRemoteStream('user-123')
    })

    expect(result.current.remoteStreams).toHaveLength(0)
  })

  it('クリーンアップが正しく動作する', () => {
    const { result } = renderHook(() => useVoiceChat(mockRoomId))

    act(() => {
      result.current.cleanup()
    })

    expect(result.current.localStream).toBeNull()
    expect(result.current.remoteStreams).toEqual([])
    expect(result.current.participants).toEqual([])
    expect(result.current.isInitialized).toBe(false)
    expect(result.current.isConnected).toBe(false)
  })
})
