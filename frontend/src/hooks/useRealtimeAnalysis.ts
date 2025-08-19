import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import { AnalysisResponse } from '@/lib/api/analytics'

interface UseRealtimeAnalysisReturn {
  isConnected: boolean
  lastUpdate: Date | null
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
  connect: () => void
  disconnect: () => void
  subscribeToAnalysis: (analysisId: string) => void
  unsubscribeFromAnalysis: (analysisId: string) => void
  requestAnalysis: (text: string, analysisTypes: string[]) => void
  getAnalysisProgress: (analysisId: string) => void
  cancelAnalysis: (analysisId: string) => void
  // 分析状態の管理
  analysisStates: Record<string, AnalysisState>
  // イベントハンドラー
  onAnalysisUpdate?: (analysis: Partial<AnalysisResponse>) => void
  onAnalysisComplete?: (analysis: AnalysisResponse) => void
  onAnalysisFailed?: (error: string) => void
}

interface AnalysisState {
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  title?: string
  summary?: string
  error?: string
  lastUpdate: Date
}

interface AnalysisUpdateMessage {
  type: 'analysis_update'
  analysis_id: string
  data: Partial<AnalysisResponse>
  timestamp: string
}

interface AnalysisCompleteMessage {
  type: 'analysis_completed'
  analysis_id: string
  data: AnalysisResponse
  timestamp: string
}

interface AnalysisProgressMessage {
  type: 'analysis_progress'
  analysis_id: string
  status: string
  progress: number
  title?: string
  summary?: string
  timestamp: string
}

interface AnalysisFailedMessage {
  type: 'analysis_failed'
  analysis_id: string
  error: string
  timestamp: string
}

interface AnalysisCancelledMessage {
  type: 'analysis_cancelled'
  analysis_id: string
  timestamp: string
}

type WebSocketMessage = 
  | AnalysisUpdateMessage 
  | AnalysisCompleteMessage
  | AnalysisProgressMessage
  | AnalysisFailedMessage
  | AnalysisCancelledMessage

export function useRealtimeAnalysis(options?: {
  onAnalysisUpdate?: (analysis: Partial<AnalysisResponse>) => void
  onAnalysisComplete?: (analysis: AnalysisResponse) => void
  onAnalysisFailed?: (error: string) => void
}): UseRealtimeAnalysisReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const [analysisStates, setAnalysisStates] = useState<Record<string, AnalysisState>>({})
  
  const { backendToken } = useAuth()
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const subscribedAnalyses = useRef<Set<string>>(new Set())
  const pendingAnalyses = useRef<Set<string>>(new Set())

  // オプションのイベントハンドラー
  const onAnalysisUpdate = options?.onAnalysisUpdate
  const onAnalysisComplete = options?.onAnalysisComplete
  const onAnalysisFailed = options?.onAnalysisFailed

  // WebSocket接続を確立
  const connect = useCallback(() => {
    if (!backendToken || wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      setConnectionStatus('connecting')
      
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
      const ws = new WebSocket(`${wsUrl}?token=${backendToken}`)
      
      ws.onopen = () => {
        console.log('WebSocket接続が確立されました')
        setIsConnected(true)
        setConnectionStatus('connected')
        
        // 既存の購読を再設定
        subscribedAnalyses.current.forEach(analysisId => {
          ws.send(JSON.stringify({
            action: 'subscribe',
            analysis_id: analysisId
          }))
        })
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          handleMessage(message)
          setLastUpdate(new Date())
        } catch (error) {
          console.error('WebSocketメッセージの解析に失敗:', error)
        }
      }

      ws.onclose = (event) => {
        console.log('WebSocket接続が閉じられました:', event.code, event.reason)
        setIsConnected(false)
        setConnectionStatus('disconnected')
        
        // 自動再接続（指数バックオフ）
        if (event.code !== 1000) { // 正常終了でない場合
          scheduleReconnect()
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocketエラー:', error)
        setConnectionStatus('error')
      }

      wsRef.current = ws
      
    } catch (error) {
      console.error('WebSocket接続の確立に失敗:', error)
      setConnectionStatus('error')
    }
  }, [backendToken])

  // 接続を切断
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close(1000, 'User initiated disconnect')
      wsRef.current = null
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    setIsConnected(false)
    setConnectionStatus('disconnected')
  }, [])

  // 分析結果の購読
  const subscribeToAnalysis = useCallback((analysisId: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return
    }

    subscribedAnalyses.current.add(analysisId)
    
    wsRef.current.send(JSON.stringify({
      type: 'ai_analysis_subscribe',
      analysis_id: analysisId,
      session_id: 'default' // 必要に応じて変更
    }))
  }, [])

  // 分析結果の購読解除
  const unsubscribeFromAnalysis = useCallback((analysisId: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return
    }

    subscribedAnalyses.current.delete(analysisId)
    
    wsRef.current.send(JSON.stringify({
      type: 'ai_analysis_unsubscribe',
      analysis_id: analysisId,
      session_id: 'default' // 必要に応じて変更
    }))
  }, [])

  // 分析リクエスト
  const requestAnalysis = useCallback((text: string, analysisTypes: string[]) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return
    }

    const analysisId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // 分析状態を初期化
    setAnalysisStates(prev => ({
      ...prev,
      [analysisId]: {
        status: 'pending',
        progress: 0,
        lastUpdate: new Date()
      }
    }))
    
    pendingAnalyses.current.add(analysisId)
    
    wsRef.current.send(JSON.stringify({
      type: 'ai_analysis_request',
      text_content: text,
      analysis_types: analysisTypes,
      session_id: 'default' // 必要に応じて変更
    }))
  }, [])

  // 分析進行状況の取得
  const getAnalysisProgress = useCallback((analysisId: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return
    }

    wsRef.current.send(JSON.stringify({
      type: 'ai_analysis_progress_request',
      analysis_id: analysisId,
      session_id: 'default' // 必要に応じて変更
    }))
  }, [])

  // 分析のキャンセル
  const cancelAnalysis = useCallback((analysisId: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return
    }

    wsRef.current.send(JSON.stringify({
      type: 'ai_analysis_cancel',
      analysis_id: analysisId,
      session_id: 'default' // 必要に応じて変更
    }))
  }, [])

  // メッセージハンドラー
  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'analysis_update':
        console.log('分析結果が更新されました:', message.analysis_id, message.data)
        // 分析状態を更新
        setAnalysisStates(prev => ({
          ...prev,
          [message.analysis_id]: {
            ...prev[message.analysis_id],
            status: 'processing',
            lastUpdate: new Date(message.timestamp)
          }
        }))
        
        // イベントハンドラーを呼び出し
        if (onAnalysisUpdate) {
          onAnalysisUpdate(message.data)
        }
        break
        
      case 'analysis_completed':
        console.log('分析が完了しました:', message.analysis_id, message.data)
        // 分析状態を完了に更新
        setAnalysisStates(prev => ({
          ...prev,
          [message.analysis_id]: {
            status: 'completed',
            progress: 100,
            title: message.data.title,
            summary: message.data.summary,
            lastUpdate: new Date(message.timestamp)
          }
        }))
        
        pendingAnalyses.current.delete(message.analysis_id)
        
        // イベントハンドラーを呼び出し
        if (onAnalysisComplete) {
          onAnalysisComplete(message.data)
        }
        break
        
      case 'analysis_progress':
        console.log('分析進行状況:', message.analysis_id, message.progress)
        // 分析状態を更新
        setAnalysisStates(prev => ({
          ...prev,
          [message.analysis_id]: {
            ...prev[message.analysis_id],
            status: message.status === 'completed' ? 'completed' : 'processing',
            progress: message.progress,
            title: message.title,
            summary: message.summary,
            lastUpdate: new Date(message.timestamp)
          }
        }))
        break
        
      case 'analysis_failed':
        console.log('分析が失敗しました:', message.analysis_id, message.error)
        // 分析状態を失敗に更新
        setAnalysisStates(prev => ({
          ...prev,
          [message.analysis_id]: {
            status: 'failed',
            progress: 0,
            error: message.error,
            lastUpdate: new Date(message.timestamp)
          }
        }))
        
        pendingAnalyses.current.delete(message.analysis_id)
        
        // イベントハンドラーを呼び出し
        if (onAnalysisFailed) {
          onAnalysisFailed(message.error)
        }
        break
        
      case 'analysis_cancelled':
        console.log('分析がキャンセルされました:', message.analysis_id)
        // 分析状態をキャンセルに更新
        setAnalysisStates(prev => ({
          ...prev,
          [message.analysis_id]: {
            ...prev[message.analysis_id],
            status: 'cancelled',
            progress: 0,
            lastUpdate: new Date(message.timestamp)
          }
        }))
        
        pendingAnalyses.current.delete(message.analysis_id)
        break
        
      default:
        console.warn('未知のメッセージタイプ:', message)
    }
  }, [onAnalysisUpdate, onAnalysisComplete, onAnalysisFailed])

  // 自動再接続のスケジュール
  const scheduleReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      return
    }

    const delay = Math.min(1000 * Math.pow(2, Math.min(subscribedAnalyses.current.size, 5)), 30000)
    
    reconnectTimeoutRef.current = setTimeout(() => {
      console.log('WebSocket再接続を試行中...')
      connect()
      reconnectTimeoutRef.current = null
    }, delay)
  }, [connect])

  // コンポーネントマウント時に接続
  useEffect(() => {
    if (backendToken) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [backendToken, connect, disconnect])

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [])

  return {
    isConnected,
    lastUpdate,
    connectionStatus,
    connect,
    disconnect,
    subscribeToAnalysis,
    unsubscribeFromAnalysis,
    requestAnalysis,
    getAnalysisProgress,
    cancelAnalysis,
    analysisStates,
    onAnalysisUpdate,
    onAnalysisComplete,
    onAnalysisFailed
  }
}
