import { renderHook, act } from '@testing-library/react'
import { useWebRTCErrorHandler } from '../useWebRTCErrorHandler'

describe('useWebRTCErrorHandler', () => {
  const mockOnError = jest.fn()
  const mockOnRecovery = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('初期化時に正しい状態を持つ', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    expect(result.current.errors).toEqual([])
    expect(result.current.isRecovering).toBe(false)
    expect(result.current.recoveryAttempts).toBe(0)
    expect(result.current.lastError).toBeNull()
  })

  it('エラーの記録が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    const error = new Error('Test error')
    const errorType = 'connection'

    act(() => {
      result.current.recordError(error, errorType)
    })

    expect(result.current.errors).toHaveLength(1)
    expect(result.current.errors[0].error).toBe(error)
    expect(result.current.errors[0].type).toBe(errorType)
    expect(result.current.lastError).toBe(error)
    expect(mockOnError).toHaveBeenCalledWith(error, errorType)
  })

  it('複数のエラーが正しく記録される', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    const error1 = new Error('Error 1')
    const error2 = new Error('Error 2')

    act(() => {
      result.current.recordError(error1, 'connection')
      result.current.recordError(error2, 'audio')
    })

    expect(result.current.errors).toHaveLength(2)
    expect(result.current.errors[0].error).toBe(error1)
    expect(result.current.errors[1].error).toBe(error2)
  })

  it('エラーのクリアが正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    const error = new Error('Test error')

    act(() => {
      result.current.recordError(error, 'connection')
    })

    expect(result.current.errors).toHaveLength(1)

    act(() => {
      result.current.clearErrors()
    })

    expect(result.current.errors).toHaveLength(0)
    expect(result.current.lastError).toBeNull()
  })

  it('エラーフィルタリングが正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    const connectionError = new Error('Connection error')
    const audioError = new Error('Audio error')

    act(() => {
      result.current.recordError(connectionError, 'connection')
      result.current.recordError(audioError, 'audio')
    })

    const connectionErrors = result.current.getErrorsByType('connection')
    const audioErrors = result.current.getErrorsByType('audio')

    expect(connectionErrors).toHaveLength(1)
    expect(connectionErrors[0].error).toBe(connectionError)
    expect(audioErrors).toHaveLength(1)
    expect(audioErrors[0].error).toBe(audioError)
  })

  it('エラー統計の取得が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    act(() => {
      result.current.recordError(new Error('Error 1'), 'connection')
      result.current.recordError(new Error('Error 2'), 'connection')
      result.current.recordError(new Error('Error 3'), 'audio')
    })

    const stats = result.current.getErrorStats()

    expect(stats.totalErrors).toBe(3)
    expect(stats.errorsByType.connection).toBe(2)
    expect(stats.errorsByType.audio).toBe(1)
    expect(stats.lastErrorTime).toBeDefined()
  })

  it('回復処理の開始が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    act(() => {
      result.current.startRecovery()
    })

    expect(result.current.isRecovering).toBe(true)
    expect(result.current.recoveryAttempts).toBe(1)
    expect(mockOnRecovery).toHaveBeenCalledWith(1)
  })

  it('回復処理の完了が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    act(() => {
      result.current.startRecovery()
    })

    expect(result.current.isRecovering).toBe(true)

    act(() => {
      result.current.completeRecovery()
    })

    expect(result.current.isRecovering).toBe(false)
  })

  it('回復処理の失敗が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    act(() => {
      result.current.startRecovery()
    })

    expect(result.current.isRecovering).toBe(true)

    const recoveryError = new Error('Recovery failed')

    act(() => {
      result.current.failRecovery(recoveryError)
    })

    expect(result.current.isRecovering).toBe(false)
    expect(result.current.recoveryAttempts).toBe(1)
  })

  it('最大回復試行回数の制限が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
      maxRecoveryAttempts: 3,
    }))

    // 最大試行回数まで回復を試行
    for (let i = 0; i < 3; i++) {
      act(() => {
        result.current.startRecovery()
        result.current.failRecovery(new Error('Recovery failed'))
      })
    }

    expect(result.current.recoveryAttempts).toBe(3)

    // 4回目の試行は無視される
    act(() => {
      result.current.startRecovery()
    })

    expect(result.current.recoveryAttempts).toBe(3)
    expect(result.current.isRecovering).toBe(false)
  })

  it('エラーレベルの判定が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    const criticalError = new Error('Critical error')
    const warningError = new Error('Warning error')

    act(() => {
      result.current.recordError(criticalError, 'connection')
      result.current.recordError(warningError, 'audio')
    })

    const criticalErrors = result.current.getErrorsByLevel('critical')
    const warningErrors = result.current.getErrorsByLevel('warning')

    expect(criticalErrors).toHaveLength(1)
    expect(criticalErrors[0].error).toBe(criticalError)
    expect(warningErrors).toHaveLength(1)
    expect(warningErrors[0].error).toBe(warningError)
  })

  it('エラーの自動クリーンアップが正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
      maxErrorHistory: 5,
    }))

    // 6個のエラーを記録
    for (let i = 0; i < 6; i++) {
      act(() => {
        result.current.recordError(new Error(`Error ${i}`), 'connection')
      })
    }

    // 最大履歴数を超えたエラーは自動的にクリーンアップされる
    expect(result.current.errors).toHaveLength(5)
  })

  it('エラーの詳細情報が正しく記録される', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    const error = new Error('Test error')
    const errorType = 'connection'
    const details = {
      peerId: 'peer-123',
      timestamp: Date.now(),
      context: 'WebRTC connection',
    }

    act(() => {
      result.current.recordError(error, errorType, details)
    })

    expect(result.current.errors[0].details).toEqual(details)
  })

  it('エラーの集約が正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    // 同じタイプのエラーを複数回記録
    for (let i = 0; i < 3; i++) {
      act(() => {
        result.current.recordError(new Error('Connection failed'), 'connection')
      })
    }

    const aggregatedErrors = result.current.getAggregatedErrors()

    expect(aggregatedErrors).toHaveLength(1)
    expect(aggregatedErrors[0].type).toBe('connection')
    expect(aggregatedErrors[0].count).toBe(3)
  })

  it('クリーンアップが正しく動作する', () => {
    const { result } = renderHook(() => useWebRTCErrorHandler({
      onError: mockOnError,
      onRecovery: mockOnRecovery,
    }))

    act(() => {
      result.current.recordError(new Error('Test error'), 'connection')
      result.current.startRecovery()
    })

    expect(result.current.errors).toHaveLength(1)
    expect(result.current.isRecovering).toBe(true)

    act(() => {
      result.current.cleanup()
    })

    expect(result.current.errors).toHaveLength(0)
    expect(result.current.isRecovering).toBe(false)
    expect(result.current.recoveryAttempts).toBe(0)
    expect(result.current.lastError).toBeNull()
  })
})
