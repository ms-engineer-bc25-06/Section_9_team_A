"use client"

import { useCallback, useEffect, useRef, useState, useMemo } from 'react'
import { getWhisperClient, WhisperTranscriptionOptions } from '@/lib/openai-whisper'

interface TranscriptionSegment {
  id: string
  text: string
  startTime: number
  endTime: number
  confidence: number
  isComplete: boolean
  timestamp: Date
}

interface UseRealTimeTranscriptionReturn {
  // 状態管理
  isTranscribing: boolean
  isPaused: boolean
  currentText: string
  segments: TranscriptionSegment[]
  
  // 制御関数
  startTranscription: () => Promise<void>
  stopTranscription: () => void
  pauseTranscription: () => void
  resumeTranscription: () => void
  clearTranscription: () => void
  
  // 設定
  updateTranscriptionOptions: (options: Partial<WhisperTranscriptionOptions>) => void
  
  // 統計情報
  stats: {
    totalSegments: number
    averageConfidence: number
    totalDuration: number
    wordsPerMinute: number
  }
  
  // エラーハンドリング
  error: string | null
  clearError: () => void
}

export const useRealTimeTranscription = (
  audioStream: MediaStream | null,
  options: WhisperTranscriptionOptions = {}
): UseRealTimeTranscriptionReturn => {
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [currentText, setCurrentText] = useState('')
  const [segments, setSegments] = useState<TranscriptionSegment[]>([])
  const [error, setError] = useState<string | null>(null)
  const [transcriptionOptions, setTranscriptionOptions] = useState<WhisperTranscriptionOptions>(options)

  // 音声処理用のref
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const transcriptionQueueRef = useRef<Blob[]>([])
  const isProcessingRef = useRef(false)
  const startTimeRef = useRef<number>(0)
  const segmentIdCounterRef = useRef(0)

  // 音声チャンクの処理間隔（ミリ秒）
  const CHUNK_INTERVAL = 3000 // 3秒ごと
  const MIN_CHUNK_SIZE = 1000 // 1秒以上

  // エラーのクリア
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  // 文字起こしオプションの更新
  const updateTranscriptionOptions = useCallback((newOptions: Partial<WhisperTranscriptionOptions>) => {
    setTranscriptionOptions(prev => ({ ...prev, ...newOptions }))
  }, [])

  // 音声チャンクの処理
  const processAudioChunk = useCallback(async (audioChunk: Blob) => {
    if (!isTranscribing || isPaused || isProcessingRef.current) {
      return
    }

    try {
      isProcessingRef.current = true
      
      const whisperClient = getWhisperClient()
      const previousText = currentText
      
      const result = await whisperClient.transcribeAudioChunk(
        audioChunk,
        previousText,
        transcriptionOptions
      )

      // 新しいセグメントを作成
      const newSegment: TranscriptionSegment = {
        id: `segment-${++segmentIdCounterRef.current}`,
        text: result.text,
        startTime: Date.now() - startTimeRef.current,
        endTime: Date.now() - startTimeRef.current,
        confidence: result.confidence,
        isComplete: result.isComplete,
        timestamp: new Date(),
      }

      // セグメントを追加
      setSegments(prev => [...prev, newSegment])
      
      // 現在のテキストを更新
      if (result.isComplete) {
        setCurrentText(prev => prev + (prev ? ' ' : '') + result.text)
      } else {
        // 不完全な文の場合は一時的に表示
        setCurrentText(prev => {
          const baseText = prev.endsWith('...') ? prev.slice(0, -3) : prev
          return baseText + (baseText ? ' ' : '') + result.text + '...'
        })
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`文字起こしエラー: ${errorMessage}`)
      console.error('音声チャンク処理エラー:', err)
    } finally {
      isProcessingRef.current = false
    }
  }, [isTranscribing, isPaused, currentText, transcriptionOptions])

  // 音声チャンクのキュー処理
  const processTranscriptionQueue = useCallback(async () => {
    if (transcriptionQueueRef.current.length === 0 || isProcessingRef.current) {
      return
    }

    const chunk = transcriptionQueueRef.current.shift()
    if (chunk) {
      await processAudioChunk(chunk)
    }
  }, [processAudioChunk])

  // 音声データの受信処理
  const handleDataAvailable = useCallback((event: BlobEvent) => {
    if (event.data.size > 0) {
      audioChunksRef.current.push(event.data)
      
      // 十分なサイズになったら文字起こしキューに追加
      const totalSize = audioChunksRef.current.reduce((sum, chunk) => sum + chunk.size, 0)
      if (totalSize >= MIN_CHUNK_SIZE) {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        transcriptionQueueRef.current.push(audioBlob)
        audioChunksRef.current = []
        
        // キュー処理を開始
        processTranscriptionQueue()
      }
    }
  }, [processTranscriptionQueue])

  // 文字起こしの開始
  const startTranscription = useCallback(async () => {
    if (!audioStream || isTranscribing) {
      return
    }

    try {
      setError(null)
      setIsTranscribing(true)
      setIsPaused(false)
      startTimeRef.current = Date.now()
      
      // MediaRecorderの設定
      const mediaRecorder = new MediaRecorder(audioStream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 16000,
      })

      mediaRecorderRef.current = mediaRecorder
      
      // 音声データの受信処理
      mediaRecorder.ondataavailable = handleDataAvailable
      
      // 録音開始
      mediaRecorder.start(CHUNK_INTERVAL)
      
      console.log('リアルタイム文字起こし開始')
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`文字起こし開始エラー: ${errorMessage}`)
      console.error('文字起こし開始エラー:', err)
    }
  }, [audioStream, isTranscribing, handleDataAvailable])

  // 文字起こしの停止
  const stopTranscription = useCallback(() => {
    if (mediaRecorderRef.current && isTranscribing) {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current = null
      setIsTranscribing(false)
      setIsPaused(false)
      
      // 残りのキューを処理
      if (transcriptionQueueRef.current.length > 0) {
        transcriptionQueueRef.current.forEach(chunk => {
          processAudioChunk(chunk)
        })
        transcriptionQueueRef.current = []
      }
      
      console.log('リアルタイム文字起こし停止')
    }
  }, [isTranscribing, processAudioChunk])

  // 文字起こしの一時停止
  const pauseTranscription = useCallback(() => {
    if (isTranscribing && !isPaused) {
      setIsPaused(true)
      console.log('文字起こし一時停止')
    }
  }, [isTranscribing, isPaused])

  // 文字起こしの再開
  const resumeTranscription = useCallback(() => {
    if (isTranscribing && isPaused) {
      setIsPaused(false)
      console.log('文字起こし再開')
    }
  }, [isTranscribing, isPaused])

  // 文字起こしのクリア
  const clearTranscription = useCallback(() => {
    setCurrentText('')
    setSegments([])
    segmentIdCounterRef.current = 0
    setError(null)
    console.log('文字起こしクリア')
  }, [])

  // 統計情報の計算
  const stats = useMemo(() => {
    const totalSegments = segments.length
    const averageConfidence = totalSegments > 0 
      ? segments.reduce((sum, seg) => sum + seg.confidence, 0) / totalSegments 
      : 0
    
    const totalDuration = totalSegments > 0 
      ? Math.max(...segments.map(seg => seg.endTime)) / 1000 
      : 0
    
    const totalWords = segments.reduce((sum, seg) => {
      return sum + seg.text.split(/\s+/).length
    }, 0)
    
    const wordsPerMinute = totalDuration > 0 
      ? (totalWords / totalDuration) * 60 
      : 0

    return {
      totalSegments,
      averageConfidence: Math.round(averageConfidence * 100) / 100,
      totalDuration: Math.round(totalDuration * 100) / 100,
      wordsPerMinute: Math.round(wordsPerMinute * 100) / 100,
    }
  }, [segments])

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])

  // 定期的なキュー処理
  useEffect(() => {
    if (!isTranscribing || isPaused) return

    const interval = setInterval(() => {
      processTranscriptionQueue()
    }, 1000)

    return () => clearInterval(interval)
  }, [isTranscribing, isPaused, processTranscriptionQueue])

  return {
    isTranscribing,
    isPaused,
    currentText,
    segments,
    startTranscription,
    stopTranscription,
    pauseTranscription,
    resumeTranscription,
    clearTranscription,
    updateTranscriptionOptions,
    stats,
    error,
    clearError,
  }
}
