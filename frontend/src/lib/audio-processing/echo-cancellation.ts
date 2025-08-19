// 高度なエコーキャンセル機能
export interface EchoCancellationConfig {
  // 基本設定
  enabled: boolean
  delayCompensation: number // 遅延補償（ミリ秒）
  filterLength: number // フィルター長
  
  // 適応フィルター設定
  adaptationRate: number // 適応率
  leakageFactor: number // 漏れ係数
  
  // ダブルトーク検出
  doubleTalkDetection: boolean
  doubleTalkThreshold: number
  
  // 非線形処理
  nonlinearProcessing: boolean
  clippingThreshold: number
  
  // 品質監視
  qualityMonitoring: boolean
  convergenceThreshold: number
}

export interface EchoCancellationStats {
  // フィルター性能
  filterConvergence: number // 収束度（0-1）
  residualEcho: number // 残存エコー（dB）
  
  // 適応状況
  adaptationActive: boolean
  adaptationRate: number
  
  // 品質指標
  echoSuppression: number // エコー抑制量（dB）
  signalQuality: number // 信号品質（0-1）
  
  // 統計情報
  totalSamples: number
  convergenceTime: number // 収束時間（ミリ秒）
}

export class AdvancedEchoCancellation {
  private config: EchoCancellationConfig
  private audioContext: AudioContext
  private sampleRate: number
  
  // フィルター関連
  private adaptiveFilter: Float32Array
  private filterBuffer: Float32Array
  private referenceBuffer: Float32Array
  
  // 状態管理
  private isInitialized: boolean = false
  private convergenceCounter: number = 0
  private startTime: number = 0
  
  // 統計情報
  private stats: EchoCancellationStats
  
  constructor(config: EchoCancellationConfig, audioContext: AudioContext) {
    this.config = { ...this.getDefaultConfig(), ...config }
    this.audioContext = audioContext
    this.sampleRate = audioContext.sampleRate
    
    // フィルターの初期化
    this.adaptiveFilter = new Float32Array(this.config.filterLength)
    this.filterBuffer = new Float32Array(this.config.filterLength)
    this.referenceBuffer = new Float32Array(this.config.filterLength)
    
    // 統計情報の初期化
    this.stats = this.initializeStats()
    
    this.isInitialized = true
    this.startTime = Date.now()
  }

  // デフォルト設定
  private getDefaultConfig(): EchoCancellationConfig {
    return {
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
    }
  }

  // 統計情報の初期化
  private initializeStats(): EchoCancellationStats {
    return {
      filterConvergence: 0,
      residualEcho: 0,
      adaptationActive: false,
      adaptationRate: this.config.adaptationRate,
      echoSuppression: 0,
      signalQuality: 0,
      totalSamples: 0,
      convergenceTime: 0,
    }
  }

  /**
   * エコーキャンセル処理
   * @param input 入力音声データ
   * @param reference 参照信号（スピーカー出力）
   * @returns エコーキャンセル後の音声データ
   */
  process(input: Float32Array, reference: Float32Array): Float32Array {
    if (!this.config.enabled || !this.isInitialized) {
      return input
    }

    const output = new Float32Array(input.length)
    
    // 遅延補償の適用
    const compensatedReference = this.applyDelayCompensation(reference)
    
    // 適応フィルターの更新
    this.updateAdaptiveFilter(input, compensatedReference)
    
    // エコー除去
    for (let i = 0; i < input.length; i++) {
      const echoEstimate = this.computeEchoEstimate(i)
      output[i] = input[i] - echoEstimate
      
      // 非線形処理
      if (this.config.nonlinearProcessing) {
        output[i] = this.applyNonlinearProcessing(output[i])
      }
    }
    
    // 統計情報の更新
    this.updateStats(input, output, compensatedReference)
    
    return output
  }

  /**
   * 遅延補償の適用
   */
  private applyDelayCompensation(reference: Float32Array): Float32Array {
    const delaySamples = Math.floor(this.config.delayCompensation * this.sampleRate / 1000)
    const compensated = new Float32Array(reference.length)
    
    for (let i = 0; i < reference.length; i++) {
      const delayedIndex = i - delaySamples
      compensated[i] = delayedIndex >= 0 ? reference[delayedIndex] : 0
    }
    
    return compensated
  }

  /**
   * 適応フィルターの更新
   */
  private updateAdaptiveFilter(input: Float32Array, reference: Float32Array): void {
    // ダブルトーク検出
    if (this.config.doubleTalkDetection && this.isDoubleTalk(input, reference)) {
      // ダブルトーク時は適応を停止
      this.stats.adaptationActive = false
      return
    }

    this.stats.adaptationActive = true
    
    // NLMS（Normalized Least Mean Square）アルゴリズム
    for (let i = 0; i < input.length; i++) {
      // フィルターバッファの更新
      this.updateFilterBuffer(reference[i])
      
      // エラー信号の計算
      const echoEstimate = this.computeEchoEstimate(0)
      const error = input[i] - echoEstimate
      
      // 適応フィルターの更新
      this.updateFilterCoefficients(error)
    }
  }

  /**
   * フィルターバッファの更新
   */
  private updateFilterBuffer(newSample: number): void {
    // バッファをシフト
    for (let i = this.filterBuffer.length - 1; i > 0; i--) {
      this.filterBuffer[i] = this.filterBuffer[i - 1]
    }
    this.filterBuffer[0] = newSample
  }

  /**
   * エコー推定値の計算
   */
  private computeEchoEstimate(offset: number): number {
    let estimate = 0
    for (let i = 0; i < this.adaptiveFilter.length; i++) {
      if (offset + i < this.filterBuffer.length) {
        estimate += this.adaptiveFilter[i] * this.filterBuffer[offset + i]
      }
    }
    return estimate
  }

  /**
   * フィルター係数の更新
   */
  private updateFilterCoefficients(error: number): void {
    // 正規化係数の計算
    const power = this.computeReferencePower()
    const normalizedStepSize = this.config.adaptationRate / (power + 1e-10)
    
    // フィルター係数の更新
    for (let i = 0; i < this.adaptiveFilter.length; i++) {
      this.adaptiveFilter[i] += normalizedStepSize * error * this.filterBuffer[i]
      
      // 漏れ係数の適用
      this.adaptiveFilter[i] *= this.config.leakageFactor
    }
  }

  /**
   * 参照信号の電力計算
   */
  private computeReferencePower(): number {
    let power = 0
    for (let i = 0; i < this.filterBuffer.length; i++) {
      power += this.filterBuffer[i] * this.filterBuffer[i]
    }
    return power / this.filterBuffer.length
  }

  /**
   * ダブルトーク検出
   */
  private isDoubleTalk(input: Float32Array, reference: Float32Array): boolean {
    const inputPower = this.computeSignalPower(input)
    const referencePower = this.computeSignalPower(reference)
    
    const ratio = inputPower / (referencePower + 1e-10)
    return ratio > this.config.doubleTalkThreshold
  }

  /**
   * 信号電力の計算
   */
  private computeSignalPower(signal: Float32Array): number {
    let power = 0
    for (let i = 0; i < signal.length; i++) {
      power += signal[i] * signal[i]
    }
    return power / signal.length
  }

  /**
   * 非線形処理の適用
   */
  private applyNonlinearProcessing(sample: number): number {
    // クリッピング処理
    if (Math.abs(sample) > this.config.clippingThreshold) {
      sample = Math.sign(sample) * this.config.clippingThreshold
    }
    
    // ソフトクリッピング
    const threshold = this.config.clippingThreshold * 0.8
    if (Math.abs(sample) > threshold) {
      const excess = Math.abs(sample) - threshold
      const softClip = threshold + excess * (1 - Math.exp(-excess * 2))
      sample = Math.sign(sample) * softClip
    }
    
    return sample
  }

  /**
   * 統計情報の更新
   */
  private updateStats(input: Float32Array, output: Float32Array, reference: Float32Array): void {
    this.stats.totalSamples += input.length
    
    // 収束度の計算
    this.stats.filterConvergence = this.computeConvergence()
    
    // 残存エコーの計算
    this.stats.residualEcho = this.computeResidualEcho(input, output)
    
    // エコー抑制量の計算
    this.stats.echoSuppression = this.computeEchoSuppression(input, output)
    
    // 信号品質の計算
    this.stats.signalQuality = this.computeSignalQuality(output)
    
    // 収束時間の計算
    if (this.stats.filterConvergence >= this.config.convergenceThreshold && this.stats.convergenceTime === 0) {
      this.stats.convergenceTime = Date.now() - this.startTime
    }
  }

  /**
   * 収束度の計算
   */
  private computeConvergence(): number {
    // フィルター係数の変化量から収束度を推定
    let totalChange = 0
    for (let i = 0; i < this.adaptiveFilter.length; i++) {
      totalChange += Math.abs(this.adaptiveFilter[i])
    }
    
    const averageChange = totalChange / this.adaptiveFilter.length
    return Math.max(0, Math.min(1, 1 - averageChange))
  }

  /**
   * 残存エコーの計算
   */
  private computeResidualEcho(input: Float32Array, output: Float32Array): number {
    const inputPower = this.computeSignalPower(input)
    const outputPower = this.computeSignalPower(output)
    
    if (inputPower === 0) return 0
    
    const suppression = 10 * Math.log10(outputPower / inputPower)
    return Math.max(-60, suppression) // -60dB以下は-60dBとして扱う
  }

  /**
   * エコー抑制量の計算
   */
  private computeEchoSuppression(input: Float32Array, output: Float32Array): number {
    const inputPower = this.computeSignalPower(input)
    const outputPower = this.computeSignalPower(output)
    
    if (inputPower === 0) return 0
    
    return 10 * Math.log10(inputPower / outputPower)
  }

  /**
   * 信号品質の計算
   */
  private computeSignalQuality(signal: Float32Array): number {
    // 信号対雑音比（SNR）の簡易計算
    const signalPower = this.computeSignalPower(signal)
    const noiseFloor = 1e-6 // 雑音フロア
    
    const snr = 10 * Math.log10(signalPower / noiseFloor)
    return Math.max(0, Math.min(1, (snr + 20) / 60)) // -20dB〜40dBを0〜1に正規化
  }

  /**
   * 設定の更新
   */
  updateConfig(newConfig: Partial<EchoCancellationConfig>): void {
    this.config = { ...this.config, ...newConfig }
    
    // フィルター長が変更された場合の再初期化
    if (newConfig.filterLength && newConfig.filterLength !== this.config.filterLength) {
      this.adaptiveFilter = new Float32Array(newConfig.filterLength)
      this.filterBuffer = new Float32Array(newConfig.filterLength)
      this.referenceBuffer = new Float32Array(newConfig.filterLength)
    }
  }

  /**
   * 統計情報の取得
   */
  getStats(): EchoCancellationStats {
    return { ...this.stats }
  }

  /**
   * フィルターのリセット
   */
  reset(): void {
    this.adaptiveFilter.fill(0)
    this.filterBuffer.fill(0)
    this.referenceBuffer.fill(0)
    this.stats = this.initializeStats()
    this.convergenceCounter = 0
    this.startTime = Date.now()
  }

  /**
   * クリーンアップ
   */
  destroy(): void {
    this.isInitialized = false
    this.adaptiveFilter = null as any
    this.filterBuffer = null as any
    this.referenceBuffer = null as any
  }
}
