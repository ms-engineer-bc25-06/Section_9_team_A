import { renderHook, act } from '@testing-library/react'
import { useWebRTCQualityMonitor } from '../useWebRTCQualityMonitor'

// WebRTC関連のモック
const mockRTCPeerConnection = {
  getStats: jest.fn(),
  connectionState: 'connected',
}

const mockRTCStatsReport = {
  forEach: jest.fn(),
}

describe('useWebRTCQualityMonitor', () => {
  const mockPeerConnections = new Map([
    ['peer-1', mockRTCPeerConnection],
    ['peer-2', mockRTCPeerConnection],
  ])

  beforeEach(() => {
    jest.clearAllMocks()
    
    // モックの統計データ
    const mockStats = [
      {
        type: 'inbound-rtp',
        mediaType: 'audio',
        bytesReceived: 1000,
        packetsReceived: 10,
        packetsLost: 1,
        jitter: 0.5,
        roundTripTime: 0.1,
      },
      {
        type: 'outbound-rtp',
        mediaType: 'audio',
        bytesSent: 2000,
        packetsSent: 20,
        packetsLost: 2,
      },
      {
        type: 'candidate-pair',
        state: 'succeeded',
        currentRoundTripTime: 0.15,
        availableOutgoingBitrate: 1000000,
      },
    ]

    mockRTCStatsReport.forEach.mockImplementation((callback) => {
      mockStats.forEach(callback)
    })

    mockRTCPeerConnection.getStats.mockResolvedValue(mockRTCStatsReport)
  })

  it('初期化時に正しい状態を持つ', () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    expect(result.current.qualityMetrics).toEqual({
      audioLevel: 0,
      latency: 0,
      packetLoss: 0,
      jitter: 0,
      bandwidth: 0,
      connectionQuality: 'unknown',
    })
    expect(result.current.isMonitoring).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('品質監視の開始が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    act(() => {
      result.current.startMonitoring()
    })

    expect(result.current.isMonitoring).toBe(true)
  })

  it('品質監視の停止が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    act(() => {
      result.current.startMonitoring()
    })

    expect(result.current.isMonitoring).toBe(true)

    act(() => {
      result.current.stopMonitoring()
    })

    expect(result.current.isMonitoring).toBe(false)
  })

  it('品質メトリクスの更新が正しく動作する', async () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    act(() => {
      result.current.startMonitoring()
    })

    // 統計収集を実行
    await act(async () => {
      await result.current.collectStats()
    })

    expect(result.current.qualityMetrics.latency).toBeGreaterThan(0)
    expect(result.current.qualityMetrics.packetLoss).toBeGreaterThan(0)
    expect(result.current.qualityMetrics.jitter).toBeGreaterThan(0)
    expect(result.current.qualityMetrics.bandwidth).toBeGreaterThan(0)
  })

  it('接続品質の評価が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    // 高品質のメトリクス
    act(() => {
      result.current.updateQualityMetrics({
        audioLevel: 0.8,
        latency: 50,
        packetLoss: 0.001,
        jitter: 2,
        bandwidth: 1000000,
        connectionQuality: 'excellent',
      })
    })

    expect(result.current.qualityMetrics.connectionQuality).toBe('excellent')

    // 低品質のメトリクス
    act(() => {
      result.current.updateQualityMetrics({
        audioLevel: 0.2,
        latency: 500,
        packetLoss: 0.1,
        jitter: 50,
        bandwidth: 100000,
        connectionQuality: 'poor',
      })
    })

    expect(result.current.qualityMetrics.connectionQuality).toBe('poor')
  })

  it('エラー状態の処理が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    const errorMessage = 'Connection failed'

    act(() => {
      result.current.setError(errorMessage)
    })

    expect(result.current.error).toBe(errorMessage)
  })

  it('品質アラートの生成が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    // 低品質のメトリクスを設定
    act(() => {
      result.current.updateQualityMetrics({
        audioLevel: 0.1,
        latency: 1000,
        packetLoss: 0.2,
        jitter: 100,
        bandwidth: 50000,
        connectionQuality: 'poor',
      })
    })

    const alerts = result.current.getQualityAlerts()

    expect(alerts).toHaveLength(1)
    expect(alerts[0].type).toBe('warning')
    expect(alerts[0].message).toContain('音声品質が低下')
  })

  it('品質改善の提案が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    // 低品質のメトリクスを設定
    act(() => {
      result.current.updateQualityMetrics({
        audioLevel: 0.1,
        latency: 1000,
        packetLoss: 0.2,
        jitter: 100,
        bandwidth: 50000,
        connectionQuality: 'poor',
      })
    })

    const suggestions = result.current.getQualitySuggestions()

    expect(suggestions).toHaveLength(1)
    expect(suggestions[0].type).toBe('suggestion')
    expect(suggestions[0].message).toContain('ネットワーク接続を確認')
  })

  it('統計データのリセットが正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    // メトリクスを設定
    act(() => {
      result.current.updateQualityMetrics({
        audioLevel: 0.8,
        latency: 100,
        packetLoss: 0.01,
        jitter: 5,
        bandwidth: 500000,
        connectionQuality: 'good',
      })
    })

    expect(result.current.qualityMetrics.audioLevel).toBe(0.8)

    // リセット
    act(() => {
      result.current.resetStats()
    })

    expect(result.current.qualityMetrics).toEqual({
      audioLevel: 0,
      latency: 0,
      packetLoss: 0,
      jitter: 0,
      bandwidth: 0,
      connectionQuality: 'unknown',
    })
  })

  it('複数のピア接続の監視が正しく動作する', async () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    act(() => {
      result.current.startMonitoring()
    })

    // 統計収集を実行
    await act(async () => {
      await result.current.collectStats()
    })

    // 両方のピア接続から統計が収集されることを確認
    expect(mockRTCPeerConnection.getStats).toHaveBeenCalledTimes(2)
  })

  it('接続状態の変更が正しく処理される', () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    act(() => {
      result.current.onConnectionStateChange('peer-1', 'failed')
    })

    expect(result.current.qualityMetrics.connectionQuality).toBe('poor')
  })

  it('監視の自動停止が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCQualityMonitor(mockPeerConnections))

    act(() => {
      result.current.startMonitoring()
    })

    expect(result.current.isMonitoring).toBe(true)

    // コンポーネントのアンマウントをシミュレート
    act(() => {
      result.current.cleanup()
    })

    expect(result.current.isMonitoring).toBe(false)
  })
})
