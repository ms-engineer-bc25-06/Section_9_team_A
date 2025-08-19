"use client"

import { useCallback, useEffect, useRef, useState, useMemo } from 'react'
import { AdvancedEchoCancellation, EchoCancellationConfig, EchoCancellationStats } from '@/lib/audio-processing/echo-cancellation'
import { AdvancedNoiseReduction, NoiseReductionConfig, NoiseReductionStats } from '@/lib/audio-processing/noise-reduction'
import { AdvancedAudioCompression, AudioCompressionConfig, AudioCompressionStats } from '@/lib/audio-processing/audio-compression'

interface AudioOptimizationConfig {
  // エコーキャンセル設定
  echoCancellation: EchoCancellationConfig
  // ノイズ除去設定
  noiseReduction: NoiseReductionConfig
  // 音声圧縮設定
  audioCompression: AudioCompressionConfig
}

interface AudioOptimizationStats {
  // 各処理の統計情報
  echoCancellation: EchoCancellationStats
  noiseReduction: NoiseReductionStats
  audioCompression: AudioCompressionStats
  
  // 統合された統計情報
  overallQuality: number // 全体的な品質（0-1）
  processingLatency: number // 処理遅延（ミリ秒）
  cpuUsage: number // CPU使用率（0-1）
  memoryUsage: number // メモリ使用量（MB）
}

interface UseAdvancedAudioOptimizationReturn {
  // 状態管理
  isEnabled: boolean
  isProcessing: boolean
  
  // 設定管理
  config: AudioOptimizationConfig
  updateConfig: (newConfig: Partial<AudioOptimizationConfig>) => void
  
  // 処理制御
  enableOptimization: () => void
  disableOptimization: () => void
  resetOptimization: () => void
  
  // 音声処理
  processAudio: (input: Float32Array, reference?: Float32Array) => Promise<Float32Array>
  
  // 統計情報
  stats: AudioOptimizationStats
  
  // エラーハンドリング
  error: string | null
  clearError: () => void
}

export const useAdvancedAudioOptimization = (
  audioContext: AudioContext | null
): UseAdvancedAudioOptimizationReturn => {
  const [isEnabled, setIsEnabled] = useState(true)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // 設定の状態管理
  const [config, setConfig] = useState<AudioOptimizationConfig>({
    echoCancellation: {
      enabled: true,
      delayCompensation: 50,
      filterLength: 2048,
      adaptationRate: 0.01,
      leakageFactor: 0.999,
      doubleTalkDetection: true,
      doubleTalkThreshold: 0.1,
      nonlinearProcessing: true,
      clippingThreshold: 0.95,
      qualityMonitoring: true,
      convergenceThreshold: 0.8,
    },
    noiseReduction: {
      enabled: true,
      algorithm: 'spectral-subtraction',
      spectralSubtraction: {
        alpha: 2.0,
        beta: 0.01,
        smoothingFactor: 0.9,
      },
      wienerFilter: {
        noiseEstimationMethod: 'vad',
        smoothingWindow: 5,
        adaptationRate: 0.1,
      },
      voiceActivityDetection: {
        enabled: true,
        threshold: 0.15,
        hangoverTime: 200,
        noiseFloor: -40,
      },
      adaptiveProcessing: {
        enabled: true,
        learningRate: 0.01,
        forgettingFactor: 0.99,
        minimumNoiseLevel: -60,
      },
      qualityMonitoring: true,
      realTimeAnalysis: true,
    },
    audioCompression: {
      enabled: true,
      algorithm: 'opus',
      quality: 'high',
      bitrate: 64,
      variableBitrate: true,
      encoder: {
        frameSize: 20,
        channels: 1,
        sampleRate: 48000,
        opus: {
          application: 'voip',
          complexity: 5,
          packetLoss: 1,
        },
        aac: {
          profile: 'aac-lc',
          afterburner: false,
          fast: true,
        },
      },
      adaptiveCompression: {
        enabled: true,
        qualityThreshold: 0.7,
        bitrateAdjustment: 0.1,
        complexityAdjustment: true,
      },
      qualityMonitoring: true,
      realTimeAnalysis: true,
    },
  })

  // 処理エンジンのref
  const echoCancellationRef = useRef<AdvancedEchoCancellation | null>(null)
  const noiseReductionRef = useRef<AdvancedNoiseReduction | null>(null)
  const audioCompressionRef = useRef<AdvancedAudioCompression | null>(null)
  
  // 統計情報の状態管理
  const [stats, setStats] = useState<AudioOptimizationStats>({
    echoCancellation: {
      filterConvergence: 0,
      residualEcho: 0,
      adaptationActive: false,
      adaptationRate: 0.01,
      echoSuppression: 0,
      signalQuality: 0,
      totalSamples: 0,
      convergenceTime: 0,
    },
    noiseReduction: {
      noiseReduction: 0,
      signalDistortion: 0,
      snrImprovement: 0,
      adaptationActive: false,
      noiseLevel: -60,
      noiseSpectrum: new Float32Array(),
      overallQuality: 0,
      speechPreservation: 0,
      totalFrames: 0,
      voiceFrames: 0,
      noiseFrames: 0,
    },
    audioCompression: {
      compressionRatio: 1,
      bitrate: 64,
      qualityScore: 0,
      encodingTime: 0,
      frameCount: 0,
      averageFrameSize: 0,
      perceptualQuality: 0,
      spectralDistortion: 0,
      temporalDistortion: 0,
      totalBytes: 0,
      originalBytes: 0,
      efficiency: 0,
    },
    overallQuality: 0,
    processingLatency: 0,
    cpuUsage: 0,
    memoryUsage: 0,
  })

  // 処理エンジンの初期化
  const initializeProcessingEngines = useCallback(() => {
    if (!audioContext) return

    try {
      // エコーキャンセルエンジンの初期化
      echoCancellationRef.current = new AdvancedEchoCancellation(
        config.echoCancellation,
        audioContext
      )

      // ノイズ除去エンジンの初期化
      noiseReductionRef.current = new AdvancedNoiseReduction(
        config.noiseReduction,
        audioContext
      )

      // 音声圧縮エンジンの初期化
      audioCompressionRef.current = new AdvancedAudioCompression(
        config.audioCompression,
        audioContext
      )

      setError(null)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`音声処理エンジンの初期化エラー: ${errorMessage}`)
      console.error('音声処理エンジンの初期化エラー:', err)
    }
  }, [audioContext, config])

  // 設定の更新
  const updateConfig = useCallback((newConfig: Partial<AudioOptimizationConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }))
    
    // 各エンジンに設定を反映
    if (echoCancellationRef.current && newConfig.echoCancellation) {
      echoCancellationRef.current.updateConfig(newConfig.echoCancellation)
    }
    if (noiseReductionRef.current && newConfig.noiseReduction) {
      noiseReductionRef.current.updateConfig(newConfig.noiseReduction)
    }
    if (audioCompressionRef.current && newConfig.audioCompression) {
      audioCompressionRef.current.updateConfig(newConfig.audioCompression)
    }
  }, [])

  // 最適化の有効化
  const enableOptimization = useCallback(() => {
    setIsEnabled(true)
    initializeProcessingEngines()
  }, [initializeProcessingEngines])

  // 最適化の無効化
  const disableOptimization = useCallback(() => {
    setIsEnabled(false)
    // エンジンのクリーンアップ
    if (echoCancellationRef.current) {
      echoCancellationRef.current.destroy()
      echoCancellationRef.current = null
    }
    if (noiseReductionRef.current) {
      noiseReductionRef.current.destroy()
      noiseReductionRef.current = null
    }
    if (audioCompressionRef.current) {
      audioCompressionRef.current.destroy()
      audioCompressionRef.current = null
    }
  }, [])

  // 最適化のリセット
  const resetOptimization = useCallback(() => {
    if (echoCancellationRef.current) {
      echoCancellationRef.current.reset()
    }
    if (noiseReductionRef.current) {
      noiseReductionRef.current.reset()
    }
    if (audioCompressionRef.current) {
      audioCompressionRef.current.reset()
    }
    
    // 統計情報のリセット
    setStats(prev => ({
      ...prev,
      overallQuality: 0,
      processingLatency: 0,
      cpuUsage: 0,
      memoryUsage: 0,
    }))
  }, [])

  // 音声処理の実行
  const processAudio = useCallback(async (
    input: Float32Array,
    reference?: Float32Array
  ): Promise<Float32Array> => {
    if (!isEnabled || !audioContext) {
      return input
    }

    setIsProcessing(true)
    const startTime = performance.now()
    
    try {
      let processedAudio = input

      // 1. エコーキャンセル処理
      if (config.echoCancellation.enabled && echoCancellationRef.current && reference) {
        processedAudio = echoCancellationRef.current.process(processedAudio, reference)
      }

      // 2. ノイズ除去処理
      if (config.noiseReduction.enabled && noiseReductionRef.current) {
        processedAudio = noiseReductionRef.current.process(processedAudio)
      }

      // 3. 音声圧縮処理
      if (config.audioCompression.enabled && audioCompressionRef.current) {
        const compressedData = await audioCompressionRef.current.process(processedAudio)
        // 圧縮データをPCMに戻す（実際の実装では適切なデコード処理が必要）
        processedAudio = new Float32Array(compressedData.buffer)
      }

      // 処理遅延の計算
      const processingLatency = performance.now() - startTime
      
      // 統計情報の更新
      updateStats(processingLatency)
      
      return processedAudio

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`音声処理エラー: ${errorMessage}`)
      console.error('音声処理エラー:', err)
      return input
    } finally {
      setIsProcessing(false)
    }
  }, [isEnabled, audioContext, config])

  // 統計情報の更新
  const updateStats = useCallback((processingLatency: number) => {
    if (!echoCancellationRef.current || !noiseReductionRef.current || !audioCompressionRef.current) {
      return
    }

    const echoStats = echoCancellationRef.current.getStats()
    const noiseStats = noiseReductionRef.current.getStats()
    const compressionStats = audioCompressionRef.current.getStats()

    // 全体的な品質の計算
    const overallQuality = (
      echoStats.signalQuality * 0.4 +
      noiseStats.overallQuality * 0.4 +
      compressionStats.qualityScore * 0.2
    )

    // CPU使用率の推定（簡易版）
    const cpuUsage = Math.min(1, processingLatency / 16.67) // 60fpsを基準

    // メモリ使用量の推定（簡易版）
    const memoryUsage = (
      (echoStats.totalSamples * 4) + // Float32
      (noiseStats.totalFrames * 1024) + // フレームバッファ
      (compressionStats.totalBytes)
    ) / (1024 * 1024) // MB単位

    setStats({
      echoCancellation: echoStats,
      noiseReduction: noiseStats,
      audioCompression: compressionStats,
      overallQuality,
      processingLatency,
      cpuUsage,
      memoryUsage,
    })
  }, [])

  // エラーのクリア
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  // 初期化処理
  useEffect(() => {
    if (audioContext && isEnabled) {
      initializeProcessingEngines()
    }
  }, [audioContext, isEnabled, initializeProcessingEngines])

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (echoCancellationRef.current) {
        echoCancellationRef.current.destroy()
      }
      if (noiseReductionRef.current) {
        noiseReductionRef.current.destroy()
      }
      if (audioCompressionRef.current) {
        audioCompressionRef.current.destroy()
      }
    }
  }, [])

  // 統計情報の定期更新
  useEffect(() => {
    if (!isEnabled || !isProcessing) return

    const interval = setInterval(() => {
      if (echoCancellationRef.current && noiseReductionRef.current && audioCompressionRef.current) {
        updateStats(0) // 処理遅延は0として更新
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [isEnabled, isProcessing, updateStats])

  return {
    isEnabled,
    isProcessing,
    config,
    updateConfig,
    enableOptimization,
    disableOptimization,
    resetOptimization,
    processAudio,
    stats,
    error,
    clearError,
  }
}
