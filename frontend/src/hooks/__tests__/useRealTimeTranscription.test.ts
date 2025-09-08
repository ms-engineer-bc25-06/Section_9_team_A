import { renderHook, act } from '@testing-library/react'
import { useRealTimeTranscription } from '../useRealTimeTranscription'

// WebSocketフックのモック
jest.mock('../useWebSocket')
const mockUseWebSocket = require('../useWebSocket').useWebSocket as jest.MockedFunction<typeof require('../useWebSocket').useWebSocket>

describe('useRealTimeTranscription', () => {
  const mockSessionId = 'test-session-123'
  const mockSendJson = jest.fn()
  const mockLastMessage = null

  beforeEach(() => {
    jest.clearAllMocks()
    
    mockUseWebSocket.mockReturnValue({
      sendJson: mockSendJson,
      isConnected: true,
      lastMessage: mockLastMessage,
    })
  })

  it('初期化時に正しい状態を持つ', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    expect(result.current.isActive).toBe(false)
    expect(result.current.isProcessing).toBe(false)
    expect(result.current.language).toBe('ja')
    expect(result.current.transcriptions).toEqual([])
    expect(result.current.partialTranscriptions).toEqual({})
    expect(result.current.error).toBeNull()
    expect(result.current.stats).toEqual({
      totalChunks: 0,
      totalDuration: 0,
      averageConfidence: 0,
      uniqueSpeakers: 0,
      languagesDetected: [],
      qualityDistribution: {},
    })
  })

  it('転写の開始が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    act(() => {
      result.current.startTranscription('en')
    })

    expect(result.current.isActive).toBe(true)
    expect(result.current.language).toBe('en')
    expect(mockSendJson).toHaveBeenCalledWith({
      type: 'transcription-start',
      session_id: mockSessionId,
      language: 'en',
    })
  })

  it('転写の停止が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    act(() => {
      result.current.startTranscription('ja')
    })

    expect(result.current.isActive).toBe(true)

    act(() => {
      result.current.stopTranscription()
    })

    expect(result.current.isActive).toBe(false)
    expect(mockSendJson).toHaveBeenCalledWith({
      type: 'transcription-stop',
      session_id: mockSessionId,
    })
  })

  it('音声データの送信が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))
    const mockAudioData = new ArrayBuffer(1024)

    act(() => {
      result.current.sendAudioData(mockAudioData)
    })

    expect(result.current.isProcessing).toBe(true)
    expect(mockSendJson).toHaveBeenCalledWith({
      type: 'audio-data',
      session_id: mockSessionId,
      data: expect.any(String), // Base64エンコードされたデータ
      timestamp: expect.any(String),
    })
  })

  it('転写結果の追加が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    const transcription = {
      id: 'trans-1',
      text: 'こんにちは、テストです。',
      startTime: 0,
      endTime: 3,
      confidence: 0.95,
      speakerId: 1,
      language: 'ja',
      isFinal: true,
    }

    act(() => {
      result.current.addTranscription(transcription)
    })

    expect(result.current.transcriptions).toHaveLength(1)
    expect(result.current.transcriptions[0]).toEqual(transcription)
  })

  it('部分転写の更新が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    act(() => {
      result.current.updatePartialTranscription(1, 'こんにちは')
    })

    expect(result.current.partialTranscriptions[1]).toBe('こんにちは')

    act(() => {
      result.current.updatePartialTranscription(1, 'こんにちは、テスト')
    })

    expect(result.current.partialTranscriptions[1]).toBe('こんにちは、テスト')
  })

  it('部分転写のクリアが正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    act(() => {
      result.current.updatePartialTranscription(1, 'こんにちは')
      result.current.updatePartialTranscription(2, 'テスト')
    })

    expect(result.current.partialTranscriptions[1]).toBe('こんにちは')
    expect(result.current.partialTranscriptions[2]).toBe('テスト')

    act(() => {
      result.current.clearPartialTranscription(1)
    })

    expect(result.current.partialTranscriptions[1]).toBeUndefined()
    expect(result.current.partialTranscriptions[2]).toBe('テスト')
  })

  it('統計情報の更新が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    const newStats = {
      totalChunks: 10,
      totalDuration: 30,
      averageConfidence: 0.85,
      uniqueSpeakers: 2,
      languagesDetected: ['ja', 'en'],
      qualityDistribution: { high: 8, medium: 2, low: 0 },
    }

    act(() => {
      result.current.updateStats(newStats)
    })

    expect(result.current.stats).toEqual(newStats)
  })

  it('エラー状態の設定が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    const errorMessage = '転写エラーが発生しました'

    act(() => {
      result.current.setError(errorMessage)
    })

    expect(result.current.error).toBe(errorMessage)
  })

  it('転写履歴の取得が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    const transcription1 = {
      id: 'trans-1',
      text: '最初の転写',
      startTime: 0,
      endTime: 2,
      confidence: 0.9,
      speakerId: 1,
      language: 'ja',
      isFinal: true,
    }

    const transcription2 = {
      id: 'trans-2',
      text: '2番目の転写',
      startTime: 2,
      endTime: 4,
      confidence: 0.85,
      speakerId: 2,
      language: 'ja',
      isFinal: true,
    }

    act(() => {
      result.current.addTranscription(transcription1)
      result.current.addTranscription(transcription2)
    })

    const history = result.current.getTranscriptionHistory()

    expect(history).toHaveLength(2)
    expect(history[0]).toEqual(transcription1)
    expect(history[1]).toEqual(transcription2)
  })

  it('話者別転写の取得が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    const transcription1 = {
      id: 'trans-1',
      text: '話者1の転写',
      startTime: 0,
      endTime: 2,
      confidence: 0.9,
      speakerId: 1,
      language: 'ja',
      isFinal: true,
    }

    const transcription2 = {
      id: 'trans-2',
      text: '話者2の転写',
      startTime: 2,
      endTime: 4,
      confidence: 0.85,
      speakerId: 2,
      language: 'ja',
      isFinal: true,
    }

    act(() => {
      result.current.addTranscription(transcription1)
      result.current.addTranscription(transcription2)
    })

    const speaker1Transcriptions = result.current.getTranscriptionsBySpeaker(1)
    const speaker2Transcriptions = result.current.getTranscriptionsBySpeaker(2)

    expect(speaker1Transcriptions).toHaveLength(1)
    expect(speaker1Transcriptions[0]).toEqual(transcription1)
    expect(speaker2Transcriptions).toHaveLength(1)
    expect(speaker2Transcriptions[0]).toEqual(transcription2)
  })

  it('転写の検索が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    const transcription1 = {
      id: 'trans-1',
      text: 'こんにちは、テストです',
      startTime: 0,
      endTime: 2,
      confidence: 0.9,
      speakerId: 1,
      language: 'ja',
      isFinal: true,
    }

    const transcription2 = {
      id: 'trans-2',
      text: 'テストが成功しました',
      startTime: 2,
      endTime: 4,
      confidence: 0.85,
      speakerId: 2,
      language: 'ja',
      isFinal: true,
    }

    act(() => {
      result.current.addTranscription(transcription1)
      result.current.addTranscription(transcription2)
    })

    const searchResults = result.current.searchTranscriptions('テスト')

    expect(searchResults).toHaveLength(2)
    expect(searchResults[0]).toEqual(transcription1)
    expect(searchResults[1]).toEqual(transcription2)
  })

  it('転写のフィルタリングが正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    const transcription1 = {
      id: 'trans-1',
      text: '高信頼度の転写',
      startTime: 0,
      endTime: 2,
      confidence: 0.95,
      speakerId: 1,
      language: 'ja',
      isFinal: true,
    }

    const transcription2 = {
      id: 'trans-2',
      text: '低信頼度の転写',
      startTime: 2,
      endTime: 4,
      confidence: 0.6,
      speakerId: 2,
      language: 'ja',
      isFinal: true,
    }

    act(() => {
      result.current.addTranscription(transcription1)
      result.current.addTranscription(transcription2)
    })

    const highConfidenceTranscriptions = result.current.filterTranscriptionsByConfidence(0.8)

    expect(highConfidenceTranscriptions).toHaveLength(1)
    expect(highConfidenceTranscriptions[0]).toEqual(transcription1)
  })

  it('転写のエクスポートが正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    const transcription1 = {
      id: 'trans-1',
      text: '最初の転写',
      startTime: 0,
      endTime: 2,
      confidence: 0.9,
      speakerId: 1,
      language: 'ja',
      isFinal: true,
    }

    const transcription2 = {
      id: 'trans-2',
      text: '2番目の転写',
      startTime: 2,
      endTime: 4,
      confidence: 0.85,
      speakerId: 2,
      language: 'ja',
      isFinal: true,
    }

    act(() => {
      result.current.addTranscription(transcription1)
      result.current.addTranscription(transcription2)
    })

    const exportedData = result.current.exportTranscriptions()

    expect(exportedData).toHaveProperty('transcriptions')
    expect(exportedData).toHaveProperty('metadata')
    expect(exportedData.transcriptions).toHaveLength(2)
    expect(exportedData.metadata.totalChunks).toBe(2)
    expect(exportedData.metadata.totalDuration).toBe(4)
  })

  it('クリーンアップが正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    act(() => {
      result.current.startTranscription('ja')
      result.current.addTranscription({
        id: 'trans-1',
        text: 'テスト転写',
        startTime: 0,
        endTime: 2,
        confidence: 0.9,
        speakerId: 1,
        language: 'ja',
        isFinal: true,
      })
      result.current.updatePartialTranscription(1, '部分転写')
    })

    expect(result.current.isActive).toBe(true)
    expect(result.current.transcriptions).toHaveLength(1)
    expect(result.current.partialTranscriptions[1]).toBe('部分転写')

    act(() => {
      result.current.cleanup()
    })

    expect(result.current.isActive).toBe(false)
    expect(result.current.transcriptions).toHaveLength(0)
    expect(result.current.partialTranscriptions).toEqual({})
    expect(result.current.error).toBeNull()
  })

  it('WebSocketメッセージの処理が正しく動作する', () => {
    const { result } = renderHook(() => useRealTimeTranscription(mockSessionId))

    const mockMessage = {
      type: 'transcription-result',
      data: {
        id: 'trans-1',
        text: 'WebSocket経由の転写',
        startTime: 0,
        endTime: 2,
        confidence: 0.9,
        speakerId: 1,
        language: 'ja',
        isFinal: true,
      },
    }

    act(() => {
      // WebSocketメッセージハンドラーを直接呼び出し
      const messageHandler = mockUseWebSocket.mock.calls[0][1].onMessage
      messageHandler(mockMessage)
    })

    expect(result.current.transcriptions).toHaveLength(1)
    expect(result.current.transcriptions[0].text).toBe('WebSocket経由の転写')
  })
})
