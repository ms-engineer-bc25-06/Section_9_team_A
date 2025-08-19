// 音声圧縮最適化機能
export interface AudioCompressionConfig {
  // 基本設定
  enabled: boolean
  algorithm: 'opus' | 'aac' | 'mp3' | 'custom'
  
  // 圧縮品質設定
  quality: 'low' | 'medium' | 'high' | 'ultra'
  bitrate: number // 目標ビットレート（kbps）
  variableBitrate: boolean // 可変ビットレート
  
  // エンコーダー設定
  encoder: {
    frameSize: number // フレームサイズ（ミリ秒）
    channels: number // チャンネル数
    sampleRate: number // サンプルレート
    
    // Opus固有設定
    opus: {
      application: 'voip' | 'audio' | 'lowdelay'
      complexity: number // 0-10
      packetLoss: number // パケット損失率（%）
    }
    
    // AAC固有設定
    aac: {
      profile: 'aac-lc' | 'aac-he' | 'aac-he-v2'
      afterburner: boolean
      fast: boolean
    }
  }
  
  // 適応圧縮設定
  adaptiveCompression: {
    enabled: boolean
    qualityThreshold: number // 品質閾値
    bitrateAdjustment: number // ビットレート調整率
    complexityAdjustment: boolean // 複雑度の自動調整
  }
  
  // 品質監視
  qualityMonitoring: boolean
  realTimeAnalysis: boolean
}

export interface AudioCompressionStats {
  // 圧縮性能
  compressionRatio: number // 圧縮率
  bitrate: number // 実際のビットレート（kbps）
  qualityScore: number // 品質スコア（0-1）
  
  // エンコーダー性能
  encodingTime: number // エンコード時間（ミリ秒）
  frameCount: number // 処理フレーム数
  averageFrameSize: number // 平均フレームサイズ（バイト）
  
  // 品質指標
  perceptualQuality: number // 知覚品質（0-1）
  spectralDistortion: number // スペクトル歪み（dB）
  temporalDistortion: number // 時間歪み（dB）
  
  // 統計情報
  totalBytes: number
  originalBytes: number
  efficiency: number // 圧縮効率（0-1）
}

export class AdvancedAudioCompression {
  private config: AudioCompressionConfig
  private audioContext: AudioContext
  private sampleRate: number
  
  // エンコーダー関連
  private encoder: any // 実際のエンコーダーインスタンス
  private encoderContext: any // エンコーダーコンテキスト
  
  // 品質分析関連
  private qualityAnalyzer: {
    originalSpectrum: Float32Array
    compressedSpectrum: Float32Array
    temporalBuffer: Float32Array
  }
  
  // 適応処理関連
  private adaptiveState: {
    currentBitrate: number
    currentQuality: number
    qualityHistory: Float32Array
    bitrateHistory: Float32Array
  }
  
  // 統計情報
  private stats: AudioCompressionStats
  
  constructor(config: AudioCompressionConfig, audioContext: AudioContext) {
    this.config = { ...this.getDefaultConfig(), ...config }
    this.audioContext = audioContext
    this.sampleRate = audioContext.sampleRate
    
    // 品質分析の初期化
    const fftSize = 2048
    this.qualityAnalyzer = {
      originalSpectrum: new Float32Array(fftSize / 2),
      compressedSpectrum: new Float32Array(fftSize / 2),
      temporalBuffer: new Float32Array(fftSize),
    }
    
    // 適応処理状態の初期化
    this.adaptiveState = {
      currentBitrate: this.config.bitrate,
      currentQuality: 0.8,
      qualityHistory: new Float32Array(20),
      bitrateHistory: new Float32Array(20),
    }
    
    // 統計情報の初期化
    this.stats = this.initializeStats()
    
    // エンコーダーの初期化
    this.initializeEncoder()
  }

  // デフォルト設定
  private getDefaultConfig(): AudioCompressionConfig {
    return {
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
    }
  }

  // 統計情報の初期化
  private initializeStats(): AudioCompressionStats {
    return {
      compressionRatio: 1,
      bitrate: this.config.bitrate,
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
    }
  }

  /**
   * エンコーダーの初期化
   */
  private initializeEncoder(): void {
    try {
      switch (this.config.algorithm) {
        case 'opus':
          this.initializeOpusEncoder()
          break
        case 'aac':
          this.initializeAACEncoder()
          break
        case 'mp3':
          this.initializeMP3Encoder()
          break
        default:
          this.initializeOpusEncoder()
      }
    } catch (error) {
      console.error('エンコーダーの初期化に失敗:', error)
      // フォールバックとしてOpusを使用
      this.config.algorithm = 'opus'
      this.initializeOpusEncoder()
    }
  }

  /**
   * Opusエンコーダーの初期化
   */
  private initializeOpusEncoder(): void {
    // Web Audio APIのMediaRecorderを使用してOpusエンコード
    // 実際の実装では、より高度なOpusエンコーダーライブラリを使用
    this.encoder = {
      type: 'opus',
      mimeType: 'audio/webm;codecs=opus',
      bitrate: this.config.bitrate * 1000,
    }
  }

  /**
   * AACエンコーダーの初期化
   */
  private initializeAACEncoder(): void {
    // AACエンコーダーの初期化（実装は省略）
    this.encoder = {
      type: 'aac',
      mimeType: 'audio/mp4;codecs=mp4a.40.2',
      bitrate: this.config.bitrate * 1000,
    }
  }

  /**
   * MP3エンコーダーの初期化
   */
  private initializeMP3Encoder(): void {
    // MP3エンコーダーの初期化（実装は省略）
    this.encoder = {
      type: 'mp3',
      mimeType: 'audio/mpeg',
      bitrate: this.config.bitrate * 1000,
    }
  }

  /**
   * 音声圧縮処理
   * @param input 入力音声データ
   * @returns 圧縮された音声データ
   */
  async process(input: Float32Array): Promise<Uint8Array> {
    if (!this.config.enabled) {
      // 圧縮無効の場合はPCMデータを返す
      return this.float32ToUint8(input)
    }

    const startTime = performance.now()
    
    try {
      // 品質分析（圧縮前）
      this.analyzeOriginalQuality(input)
      
      // 適応圧縮の調整
      this.adjustCompressionParameters()
      
      // 圧縮処理
      const compressedData = await this.compressAudio(input)
      
      // 品質分析（圧縮後）
      this.analyzeCompressedQuality(input, compressedData)
      
      // 統計情報の更新
      this.updateStats(input, compressedData, performance.now() - startTime)
      
      return compressedData
      
    } catch (error) {
      console.error('音声圧縮エラー:', error)
      // エラー時は元のデータを返す
      return this.float32ToUint8(input)
    }
  }

  /**
   * 元の音声品質の分析
   */
  private analyzeOriginalQuality(input: Float32Array): void {
    if (!this.config.qualityMonitoring) return
    
    // スペクトル分析
    this.qualityAnalyzer.originalSpectrum = this.computeSpectrum(input)
    
    // 時間領域分析
    this.qualityAnalyzer.temporalBuffer.set(input)
  }

  /**
   * 圧縮後音声品質の分析
   */
  private analyzeCompressedQuality(original: Float32Array, compressed: Uint8Array): void {
    if (!this.config.qualityMonitoring) return
    
    // 圧縮データをPCMに戻す（簡易版）
    const decompressed = this.uint8ToFloat32(compressed)
    
    // スペクトル分析
    this.qualityAnalyzer.compressedSpectrum = this.computeSpectrum(decompressed)
    
    // 品質指標の計算
    this.calculateQualityMetrics(original, decompressed)
  }

  /**
   * スペクトル計算
   */
  private computeSpectrum(signal: Float32Array): Float32Array {
    const fftSize = signal.length
    const spectrum = new Float32Array(fftSize / 2)
    
    // 簡易的なFFT計算
    for (let k = 0; k < fftSize / 2; k++) {
      let real = 0
      let imag = 0
      
      for (let n = 0; n < fftSize; n++) {
        const angle = -2 * Math.PI * k * n / fftSize
        real += signal[n] * Math.cos(angle)
        imag += signal[n] * Math.sin(angle)
      }
      
      spectrum[k] = Math.sqrt(real * real + imag * imag)
    }
    
    return spectrum
  }

  /**
   * 品質指標の計算
   */
  private calculateQualityMetrics(original: Float32Array, compressed: Float32Array): void {
    // スペクトル歪みの計算
    this.stats.spectralDistortion = this.computeSpectralDistortion(
      this.qualityAnalyzer.originalSpectrum,
      this.qualityAnalyzer.compressedSpectrum
    )
    
    // 時間歪みの計算
    this.stats.temporalDistortion = this.computeTemporalDistortion(original, compressed)
    
    // 知覚品質の計算
    this.stats.perceptualQuality = this.computePerceptualQuality()
    
    // 全体的な品質スコア
    this.stats.qualityScore = this.computeOverallQualityScore()
  }

  /**
   * スペクトル歪みの計算
   */
  private computeSpectralDistortion(original: Float32Array, compressed: Float32Array): number {
    let distortion = 0
    let count = 0
    
    for (let i = 0; i < original.length; i++) {
      if (original[i] > 0 && compressed[i] > 0) {
        const logDiff = Math.log(original[i] / compressed[i])
        distortion += logDiff * logDiff
        count++
      }
    }
    
    return count > 0 ? Math.sqrt(distortion / count) : 0
  }

  /**
   * 時間歪みの計算
   */
  private computeTemporalDistortion(original: Float32Array, compressed: Float32Array): number {
    const minLength = Math.min(original.length, compressed.length)
    let distortion = 0
    
    for (let i = 0; i < minLength; i++) {
      const diff = original[i] - compressed[i]
      distortion += diff * diff
    }
    
    return Math.sqrt(distortion / minLength)
  }

  /**
   * 知覚品質の計算
   */
  private computePerceptualQuality(): number {
    // 複数の指標を組み合わせて知覚品質を計算
    const spectralScore = Math.max(0, 1 - this.stats.spectralDistortion / 10)
    const temporalScore = Math.max(0, 1 - this.stats.temporalDistortion / 0.1)
    
    return (spectralScore + temporalScore) / 2
  }

  /**
   * 全体的な品質スコアの計算
   */
  private computeOverallQualityScore(): number {
    const perceptualWeight = 0.4
    const compressionWeight = 0.3
    const efficiencyWeight = 0.3
    
    const perceptualScore = this.stats.perceptualQuality
    const compressionScore = Math.min(1, this.stats.compressionRatio / 10)
    const efficiencyScore = this.stats.efficiency
    
    return perceptualWeight * perceptualScore +
           compressionWeight * compressionScore +
           efficiencyWeight * efficiencyScore
  }

  /**
   * 適応圧縮パラメータの調整
   */
  private adjustCompressionParameters(): void {
    if (!this.config.adaptiveCompression.enabled) return
    
    // 品質履歴の更新
    this.updateQualityHistory()
    
    // ビットレートの調整
    this.adjustBitrate()
    
    // 複雑度の調整
    if (this.config.adaptiveCompression.complexityAdjustment) {
      this.adjustComplexity()
    }
  }

  /**
   * 品質履歴の更新
   */
  private updateQualityHistory(): void {
    // 履歴をシフト
    for (let i = this.adaptiveState.qualityHistory.length - 1; i > 0; i--) {
      this.adaptiveState.qualityHistory[i] = this.adaptiveState.qualityHistory[i - 1]
    }
    this.adaptiveState.qualityHistory[0] = this.stats.qualityScore
    
    // ビットレート履歴も更新
    for (let i = this.adaptiveState.bitrateHistory.length - 1; i > 0; i--) {
      this.adaptiveState.bitrateHistory[i] = this.adaptiveState.bitrateHistory[i - 1]
    }
    this.adaptiveState.bitrateHistory[0] = this.adaptiveState.currentBitrate
  }

  /**
   * ビットレートの調整
   */
  private adjustBitrate(): void {
    const averageQuality = this.computeAverage(this.adaptiveState.qualityHistory)
    const targetQuality = this.config.adaptiveCompression.qualityThreshold
    const adjustmentRate = this.config.adaptiveCompression.bitrateAdjustment
    
    if (averageQuality < targetQuality) {
      // 品質が低い場合はビットレートを上げる
      this.adaptiveState.currentBitrate = Math.min(
        this.config.bitrate * 2,
        this.adaptiveState.currentBitrate * (1 + adjustmentRate)
      )
    } else if (averageQuality > targetQuality + 0.1) {
      // 品質が十分高い場合はビットレートを下げる
      this.adaptiveState.currentBitrate = Math.max(
        this.config.bitrate * 0.5,
        this.adaptiveState.currentBitrate * (1 - adjustmentRate)
      )
    }
    
    // エンコーダーに新しいビットレートを設定
    if (this.encoder) {
      this.encoder.bitrate = this.adaptiveState.currentBitrate * 1000
    }
  }

  /**
   * 複雑度の調整
   */
  private adjustComplexity(): void {
    const averageQuality = this.computeAverage(this.adaptiveState.qualityHistory)
    const targetQuality = this.config.adaptiveCompression.qualityThreshold
    
    if (this.config.algorithm === 'opus' && this.encoder.type === 'opus') {
      let complexity = this.config.encoder.opus.complexity
      
      if (averageQuality < targetQuality) {
        // 品質が低い場合は複雑度を下げる（高速化）
        complexity = Math.max(0, complexity - 1)
      } else if (averageQuality > targetQuality + 0.1) {
        // 品質が十分高い場合は複雑度を上げる（高品質化）
        complexity = Math.min(10, complexity + 1)
      }
      
      this.config.encoder.opus.complexity = complexity
    }
  }

  /**
   * 平均値の計算
   */
  private computeAverage(array: Float32Array): number {
    let sum = 0
    let count = 0
    
    for (let i = 0; i < array.length; i++) {
      if (array[i] > 0) {
        sum += array[i]
        count++
      }
    }
    
    return count > 0 ? sum / count : 0
  }

  /**
   * 音声圧縮の実行
   */
  private async compressAudio(input: Float32Array): Promise<Uint8Array> {
    // 実際の実装では、選択されたエンコーダーを使用
    // ここでは簡易的な圧縮シミュレーション
    
    const frameSize = this.config.encoder.frameSize * this.sampleRate / 1000
    const compressedFrames: Uint8Array[] = []
    
    for (let i = 0; i < input.length; i += frameSize) {
      const frame = input.slice(i, Math.min(i + frameSize, input.length))
      const compressedFrame = await this.compressFrame(frame)
      compressedFrames.push(compressedFrame)
    }
    
    // フレームを結合
    const totalSize = compressedFrames.reduce((sum, frame) => sum + frame.length, 0)
    const result = new Uint8Array(totalSize)
    
    let offset = 0
    for (const frame of compressedFrames) {
      result.set(frame, offset)
      offset += frame.length
    }
    
    return result
  }

  /**
   * フレーム単位の圧縮
   */
  private async compressFrame(frame: Float32Array): Promise<Uint8Array> {
    // 簡易的な圧縮シミュレーション
    // 実際の実装では、Opus、AAC、MP3などのエンコーダーを使用
    
    const quality = this.config.quality
    let compressionFactor = 1
    
    switch (quality) {
      case 'low':
        compressionFactor = 0.3
        break
      case 'medium':
        compressionFactor = 0.5
        break
      case 'high':
        compressionFactor = 0.7
        break
      case 'ultra':
        compressionFactor = 0.9
        break
    }
    
    // 量子化による圧縮シミュレーション
    const quantized = new Float32Array(frame.length)
    for (let i = 0; i < frame.length; i++) {
      quantized[i] = Math.round(frame[i] / compressionFactor) * compressionFactor
    }
    
    return this.float32ToUint8(quantized)
  }

  /**
   * Float32ArrayをUint8Arrayに変換
   */
  private float32ToUint8(float32: Float32Array): Uint8Array {
    const uint8 = new Uint8Array(float32.length * 4)
    const view = new DataView(uint8.buffer)
    
    for (let i = 0; i < float32.length; i++) {
      view.setFloat32(i * 4, float32[i], true)
    }
    
    return uint8
  }

  /**
   * Uint8ArrayをFloat32Arrayに変換
   */
  private uint8ToFloat32(uint8: Uint8Array): Float32Array {
    const float32 = new Float32Array(uint8.length / 4)
    const view = new DataView(uint8.buffer)
    
    for (let i = 0; i < float32.length; i++) {
      float32[i] = view.getFloat32(i * 4, true)
    }
    
    return float32
  }

  /**
   * 統計情報の更新
   */
  private updateStats(input: Float32Array, compressed: Uint8Array, encodingTime: number): void {
    this.stats.encodingTime = encodingTime
    this.stats.frameCount++
    
    // 圧縮率の計算
    this.stats.originalBytes = input.length * 4 // Float32 = 4 bytes
    this.stats.totalBytes = compressed.length
    this.stats.compressionRatio = this.stats.originalBytes / this.stats.totalBytes
    
    // 平均フレームサイズの更新
    this.stats.averageFrameSize = 
      (this.stats.averageFrameSize * (this.stats.frameCount - 1) + compressed.length) / this.stats.frameCount
    
    // ビットレートの計算
    this.stats.bitrate = (compressed.length * 8) / (input.length / this.sampleRate) / 1000
    
    // 圧縮効率の計算
    this.stats.efficiency = this.stats.compressionRatio * this.stats.qualityScore
  }

  /**
   * 設定の更新
   */
  updateConfig(newConfig: Partial<AudioCompressionConfig>): void {
    this.config = { ...this.config, ...newConfig }
    
    // エンコーダーの再初期化が必要な場合
    if (newConfig.algorithm && newConfig.algorithm !== this.config.algorithm) {
      this.initializeEncoder()
    }
  }

  /**
   * 統計情報の取得
   */
  getStats(): AudioCompressionStats {
    return { ...this.stats }
  }

  /**
   * エンコーダーのリセット
   */
  reset(): void {
    this.stats = this.initializeStats()
    this.adaptiveState.currentBitrate = this.config.bitrate
    this.adaptiveState.currentQuality = 0.8
    this.adaptiveState.qualityHistory.fill(0)
    this.adaptiveState.bitrateHistory.fill(0)
  }

  /**
   * クリーンアップ
   */
  destroy(): void {
    this.encoder = null
    this.encoderContext = null
    this.qualityAnalyzer.originalSpectrum = null as any
    this.qualityAnalyzer.compressedSpectrum = null as any
    this.qualityAnalyzer.temporalBuffer = null as any
    this.adaptiveState.qualityHistory = null as any
    this.adaptiveState.bitrateHistory = null as any
  }
}
