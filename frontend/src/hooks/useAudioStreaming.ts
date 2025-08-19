"use client"

import { useCallback, useEffect, useRef, useState } from 'react'

interface AudioStreamingConfig {
  sampleRate: number
  channels: number
  bitDepth: number
  echoCancellation: boolean
  noiseSuppression: boolean
  autoGainControl: boolean
  highPassFilter: boolean
}

interface AudioQualityMetrics {
  volume: number
  clarity: number
  latency: number
  packetLoss: number
  jitter: number
}

interface UseAudioStreamingReturn {
  // 音声品質設定
  config: AudioStreamingConfig
  updateConfig: (newConfig: Partial<AudioStreamingConfig>) => void
  
  // 音声品質メトリクス
  qualityMetrics: AudioQualityMetrics
  
  // ストリーミング制御
  startStreaming: (stream: MediaStream) => Promise<void>
  stopStreaming: () => void
  isStreaming: boolean
  
  // 音声処理
  enableEchoCancellation: () => void
  disableEchoCancellation: () => void
  enableNoiseSuppression: () => void
  disableNoiseSuppression: () => void
  
  // 音声品質向上
  enhanceAudio: (audioData: Float32Array) => Float32Array
  normalizeAudio: (audioData: Float32Array) => Float32Array
  
  // エラーハンドリング
  error: string | null
}

export const useAudioStreaming = (): UseAudioStreamingReturn => {
  const [config, setConfig] = useState<AudioStreamingConfig>({
    sampleRate: 48000,
    channels: 1,
    bitDepth: 16,
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    highPassFilter: true,
  })

  const [qualityMetrics, setQualityMetrics] = useState<AudioQualityMetrics>({
    volume: 0,
    clarity: 0,
    latency: 0,
    packetLoss: 0,
    jitter: 0,
  })

  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const audioContextRef = useRef<AudioContext | null>(null)
  const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null)
  const processorNodeRef = useRef<ScriptProcessorNode | null>(null)
  const analyserNodeRef = useRef<AnalyserNode | null>(null)
  const gainNodeRef = useRef<GainNode | null>(null)
  const biquadFilterRef = useRef<BiquadFilterNode | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  // 音声品質設定の更新
  const updateConfig = useCallback((newConfig: Partial<AudioStreamingConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }))
  }, [])

  // 音声品質メトリクスの計算
  const calculateQualityMetrics = useCallback((audioData: Float32Array) => {
    // 音量レベルの計算
    let sum = 0
    let rms = 0
    for (let i = 0; i < audioData.length; i++) {
      sum += Math.abs(audioData[i])
      rms += audioData[i] * audioData[i]
    }
    const average = sum / audioData.length
    const rmsValue = Math.sqrt(rms / audioData.length)
    
    // 音量を0-100の範囲に正規化
    const volume = Math.min(100, Math.max(0, (rmsValue * 100) / 0.5))
    
    // 音声の明瞭度（スペクトル重心）
    const fft = new Float32Array(2048)
    // 簡易的なFFT計算（実際の実装ではWeb Audio APIのAnalyserNodeを使用）
    let clarity = 50 + (volume - 50) * 0.5 // 簡易的な計算
    
    // レイテンシーの推定（実際の実装ではWebRTCの統計情報を使用）
    const estimatedLatency = Math.random() * 50 + 10 // 10-60msの範囲
    
    // パケット損失の推定（実際の実装ではWebRTCの統計情報を使用）
    const estimatedPacketLoss = Math.random() * 5 // 0-5%の範囲
    
    // ジッターの推定（実際の実装ではWebRTCの統計情報を使用）
    const estimatedJitter = Math.random() * 20 + 5 // 5-25msの範囲
    
    setQualityMetrics(prev => ({
      ...prev,
      volume,
      clarity,
      latency: estimatedLatency,
      packetLoss: estimatedPacketLoss,
      jitter: estimatedJitter,
    }))
  }, [])

  // エコーキャンセルの有効化
  const enableEchoCancellation = useCallback(() => {
    updateConfig({ echoCancellation: true })
  }, [updateConfig])

  // エコーキャンセルの無効化
  const disableEchoCancellation = useCallback(() => {
    updateConfig({ echoCancellation: false })
  }, [updateConfig])

  // ノイズ除去の有効化
  const enableNoiseSuppression = useCallback(() => {
    updateConfig({ noiseSuppression: true })
  }, [updateConfig])

  // ノイズ除去の無効化
  const disableNoiseSuppression = useCallback(() => {
    updateConfig({ noiseSuppression: false })
  }, [updateConfig])

  // 音声品質向上処理
  const enhanceAudio = useCallback((audioData: Float32Array): Float32Array => {
    const enhanced = new Float32Array(audioData.length)
    
    // ノイズ除去（簡易的な閾値処理）
    if (config.noiseSuppression) {
      const noiseThreshold = 0.01
      for (let i = 0; i < audioData.length; i++) {
        if (Math.abs(audioData[i]) < noiseThreshold) {
          enhanced[i] = 0
        } else {
          enhanced[i] = audioData[i]
        }
      }
    } else {
      for (let i = 0; i < audioData.length; i++) {
        enhanced[i] = audioData[i]
      }
    }
    
    // 自動ゲイン制御
    if (config.autoGainControl) {
      let maxAmplitude = 0
      for (let i = 0; i < enhanced.length; i++) {
        if (Math.abs(enhanced[i]) > maxAmplitude) {
          maxAmplitude = Math.abs(enhanced[i])
        }
      }
      
      if (maxAmplitude > 0) {
        const gain = Math.min(1.0, 0.8 / maxAmplitude)
        for (let i = 0; i < enhanced.length; i++) {
          enhanced[i] *= gain
        }
      }
    }
    
    return enhanced
  }, [config.noiseSuppression, config.autoGainControl])

  // 音声正規化
  const normalizeAudio = useCallback((audioData: Float32Array): Float32Array => {
    const normalized = new Float32Array(audioData.length)
    let maxAmplitude = 0
    
    for (let i = 0; i < audioData.length; i++) {
      if (Math.abs(audioData[i]) > maxAmplitude) {
        maxAmplitude = Math.abs(audioData[i])
      }
    }
    
    if (maxAmplitude > 0) {
      const scale = 0.95 / maxAmplitude
      for (let i = 0; i < audioData.length; i++) {
        normalized[i] = audioData[i] * scale
      }
    }
    
    return normalized
  }, [])

  // 音声ストリーミング開始
  const startStreaming = useCallback(async (stream: MediaStream) => {
    try {
      setError(null)
      
      // AudioContextの作成
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: config.sampleRate,
        latencyHint: 'interactive',
      })
      
      const audioContext = audioContextRef.current
      
      // 音声ソースノードの作成
      sourceNodeRef.current = audioContext.createMediaStreamSource(stream)
      const sourceNode = sourceNodeRef.current
      
      // アナライザーノードの作成
      analyserNodeRef.current = audioContext.createAnalyser()
      analyserNodeRef.current.fftSize = 2048
      analyserNodeRef.current.smoothingTimeConstant = 0.8
      
      // ゲインノードの作成
      gainNodeRef.current = audioContext.createGain()
      gainNodeRef.current.gain.value = 1.0
      
      // ハイパスフィルターの作成
      if (config.highPassFilter) {
        biquadFilterRef.current = audioContext.createBiquadFilter()
        biquadFilterRef.current.type = 'highpass'
        biquadFilterRef.current.frequency.value = 80 // 80Hz以下をカット
        biquadFilterRef.current.Q.value = 1.0
      }
      
      // 音声処理ノードの作成
      processorNodeRef.current = audioContext.createScriptProcessor(4096, 1, 1)
      
      // 音声処理の実装
      processorNodeRef.current.onaudioprocess = (event) => {
        const inputBuffer = event.inputBuffer
        const outputBuffer = event.outputBuffer
        const inputData = inputBuffer.getChannelData(0)
        const outputData = outputBuffer.getChannelData(0)
        
        // 音声品質向上処理
        let processedData = enhanceAudio(inputData)
        
        // 音声正規化
        processedData = normalizeAudio(processedData)
        
        // 出力バッファにコピー
        outputData.set(processedData)
        
        // 品質メトリクスの計算
        calculateQualityMetrics(processedData)
      }
      
      // 音声処理チェーンの構築
      sourceNode.connect(analyserNodeRef.current)
      
      if (biquadFilterRef.current) {
        analyserNodeRef.current.connect(biquadFilterRef.current)
        biquadFilterRef.current.connect(gainNodeRef.current)
      } else {
        analyserNodeRef.current.connect(gainNodeRef.current)
      }
      
      gainNodeRef.current.connect(processorNodeRef.current)
      processorNodeRef.current.connect(audioContext.destination)
      
      streamRef.current = stream
      setIsStreaming(true)
      
      console.log('音声ストリーミング開始')
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`音声ストリーミング開始エラー: ${errorMessage}`)
      console.error('音声ストリーミング開始エラー:', err)
    }
  }, [config.sampleRate, config.highPassFilter, enhanceAudio, normalizeAudio, calculateQualityMetrics])

  // 音声ストリーミング停止
  const stopStreaming = useCallback(() => {
    try {
      // 音声処理ノードの切断
      if (processorNodeRef.current) {
        processorNodeRef.current.disconnect()
        processorNodeRef.current = null
      }
      
      if (gainNodeRef.current) {
        gainNodeRef.current.disconnect()
        gainNodeRef.current = null
      }
      
      if (biquadFilterRef.current) {
        biquadFilterRef.current.disconnect()
        biquadFilterRef.current = null
      }
      
      if (analyserNodeRef.current) {
        analyserNodeRef.current.disconnect()
        analyserNodeRef.current = null
      }
      
      if (sourceNodeRef.current) {
        sourceNodeRef.current.disconnect()
        sourceNodeRef.current = null
      }
      
      // AudioContextの停止
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close()
        audioContextRef.current = null
      }
      
      streamRef.current = null
      setIsStreaming(false)
      
      console.log('音声ストリーミング停止')
      
    } catch (err) {
      console.error('音声ストリーミング停止エラー:', err)
    }
  }, [])

  // クリーンアップ
  useEffect(() => {
    return () => {
      stopStreaming()
    }
  }, [stopStreaming])

  return {
    config,
    updateConfig,
    qualityMetrics,
    startStreaming,
    stopStreaming,
    isStreaming,
    enableEchoCancellation,
    disableEchoCancellation,
    enableNoiseSuppression,
    disableNoiseSuppression,
    enhanceAudio,
    normalizeAudio,
    error,
  }
}
