// 高度なノイズ除去機能
export interface NoiseReductionConfig {
  // 基本設定
  enabled: boolean
  algorithm: 'spectral-subtraction' | 'wiener-filter' | 'kalman-filter' | 'deep-learning'
  
  // スペクトル減算設定
  spectralSubtraction: {
    alpha: number // 減算係数
    beta: number // フロア係数
    smoothingFactor: number // 平滑化係数
  }
  
  // ウィーナーフィルター設定
  wienerFilter: {
    noiseEstimationMethod: 'vad' | 'spectral-tracking' | 'statistical'
    smoothingWindow: number // 平滑化窓サイズ
    adaptationRate: number // 適応率
  }
  
  // 音声活動検出（VAD）
  voiceActivityDetection: {
    enabled: boolean
    threshold: number // 検出閾値
    hangoverTime: number // ハンゴーバー時間（ミリ秒）
    noiseFloor: number // 雑音フロア
  }
  
  // 適応処理
  adaptiveProcessing: {
    enabled: boolean
    learningRate: number // 学習率
    forgettingFactor: number // 忘却係数
    minimumNoiseLevel: number // 最小雑音レベル
  }
  
  // 品質監視
  qualityMonitoring: boolean
  realTimeAnalysis: boolean
}

export interface NoiseReductionStats {
  // 処理性能
  noiseReduction: number // 雑音除去量（dB）
  signalDistortion: number // 信号歪み（dB）
  snrImprovement: number // SNR改善量（dB）
  
  // 適応状況
  adaptationActive: boolean
  noiseLevel: number // 現在の雑音レベル（dB）
  noiseSpectrum: Float32Array // 雑音スペクトル
  
  // 品質指標
  overallQuality: number // 全体的な品質（0-1）
  speechPreservation: number // 音声保持率（0-1）
  
  // 統計情報
  totalFrames: number
  voiceFrames: number
  noiseFrames: number
}

export class AdvancedNoiseReduction {
  private config: NoiseReductionConfig
  private audioContext: AudioContext
  private sampleRate: number
  
  // フィルター関連
  private noiseSpectrum: Float32Array
  private signalSpectrum: Float32Array
  private previousSpectrum: Float32Array
  
  // VAD関連
  private vadState: {
    isVoice: boolean
    hangoverCounter: number
    energyHistory: Float32Array
    spectralHistory: Float32Array
  }
  
  // 適応処理関連
  private adaptiveState: {
    noiseEstimate: Float32Array
    signalEstimate: Float32Array
    adaptationFactor: Float32Array
  }
  
  // 統計情報
  private stats: NoiseReductionStats
  
  constructor(config: NoiseReductionConfig, audioContext: AudioContext) {
    this.config = { ...this.getDefaultConfig(), ...config }
    this.audioContext = audioContext
    this.sampleRate = audioContext.sampleRate
    
    // スペクトル関連の初期化
    const fftSize = 2048
    this.noiseSpectrum = new Float32Array(fftSize / 2)
    this.signalSpectrum = new Float32Array(fftSize / 2)
    this.previousSpectrum = new Float32Array(fftSize / 2)
    
    // VAD状態の初期化
    this.vadState = {
      isVoice: false,
      hangoverCounter: 0,
      energyHistory: new Float32Array(10),
      spectralHistory: new Float32Array(10),
    }
    
    // 適応処理状態の初期化
    this.adaptiveState = {
      noiseEstimate: new Float32Array(fftSize / 2),
      signalEstimate: new Float32Array(fftSize / 2),
      adaptationFactor: new Float32Array(fftSize / 2),
    }
    
    // 統計情報の初期化
    this.stats = this.initializeStats()
  }

  // デフォルト設定
  private getDefaultConfig(): NoiseReductionConfig {
    return {
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
    }
  }

  // 統計情報の初期化
  private initializeStats(): NoiseReductionStats {
    return {
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
    }
  }

  /**
   * ノイズ除去処理
   * @param input 入力音声データ
   * @returns ノイズ除去後の音声データ
   */
  process(input: Float32Array): Float32Array {
    if (!this.config.enabled) {
      return input
    }

    const output = new Float32Array(input.length)
    
    // フレーム分割処理（オーバーラップ処理）
    const frameSize = 512
    const hopSize = frameSize / 2
    
    for (let i = 0; i < input.length - frameSize; i += hopSize) {
      const frame = input.slice(i, i + frameSize)
      const processedFrame = this.processFrame(frame)
      
      // オーバーラップ加算
      for (let j = 0; j < frameSize; j++) {
        if (i + j < output.length) {
          output[i + j] += processedFrame[j] * 0.5 // ハニング窓の重み
        }
      }
    }
    
    // 統計情報の更新
    this.updateStats(input, output)
    
    return output
  }

  /**
   * フレーム単位の処理
   */
  private processFrame(frame: Float32Array): Float32Array {
    // FFT変換
    const spectrum = this.computeSpectrum(frame)
    
    // 音声活動検出
    const isVoice = this.detectVoiceActivity(spectrum)
    
    // 雑音スペクトルの更新
    this.updateNoiseSpectrum(spectrum, isVoice)
    
    // ノイズ除去フィルターの適用
    const filteredSpectrum = this.applyNoiseReduction(spectrum)
    
    // IFFT変換
    return this.computeInverseSpectrum(filteredSpectrum)
  }

  /**
   * FFTスペクトルの計算
   */
  private computeSpectrum(frame: Float32Array): Float32Array {
    // 簡易的なFFT計算（実際の実装ではWeb Audio APIのAnalyserNodeを使用）
    const fftSize = frame.length
    const spectrum = new Float32Array(fftSize / 2)
    
    // ハニング窓の適用
    const windowedFrame = new Float32Array(fftSize)
    for (let i = 0; i < fftSize; i++) {
      const window = 0.5 * (1 - Math.cos(2 * Math.PI * i / (fftSize - 1)))
      windowedFrame[i] = frame[i] * window
    }
    
    // 簡易的なパワースペクトル計算
    for (let k = 0; k < fftSize / 2; k++) {
      let real = 0
      let imag = 0
      
      for (let n = 0; n < fftSize; n++) {
        const angle = -2 * Math.PI * k * n / fftSize
        real += windowedFrame[n] * Math.cos(angle)
        imag += windowedFrame[n] * Math.sin(angle)
      }
      
      spectrum[k] = Math.sqrt(real * real + imag * imag)
    }
    
    return spectrum
  }

  /**
   * 音声活動検出
   */
  private detectVoiceActivity(spectrum: Float32Array): boolean {
    if (!this.config.voiceActivityDetection.enabled) {
      return true
    }

    // エネルギー計算
    const energy = this.computeSpectralEnergy(spectrum)
    
    // スペクトル重心計算
    const spectralCentroid = this.computeSpectralCentroid(spectrum)
    
    // 履歴の更新
    this.updateVADHistory(energy, spectralCentroid)
    
    // 閾値判定
    const energyThreshold = this.config.voiceActivityDetection.threshold
    const isVoice = energy > energyThreshold
    
    // ハンゴーバー処理
    if (isVoice) {
      this.vadState.hangoverCounter = Math.ceil(
        this.config.voiceActivityDetection.hangoverTime * this.sampleRate / 1000
      )
    } else if (this.vadState.hangoverCounter > 0) {
      this.vadState.hangoverCounter--
      isVoice = true
    }
    
    this.vadState.isVoice = isVoice
    return isVoice
  }

  /**
   * スペクトルエネルギーの計算
   */
  private computeSpectralEnergy(spectrum: Float32Array): number {
    let energy = 0
    for (let i = 0; i < spectrum.length; i++) {
      energy += spectrum[i] * spectrum[i]
    }
    return energy / spectrum.length
  }

  /**
   * スペクトル重心の計算
   */
  private computeSpectralCentroid(spectrum: Float32Array): number {
    let weightedSum = 0
    let totalPower = 0
    
    for (let i = 0; i < spectrum.length; i++) {
      const frequency = i * this.sampleRate / spectrum.length
      weightedSum += frequency * spectrum[i]
      totalPower += spectrum[i]
    }
    
    return totalPower > 0 ? weightedSum / totalPower : 0
  }

  /**
   * VAD履歴の更新
   */
  private updateVADHistory(energy: number, spectralCentroid: number): void {
    // エネルギー履歴の更新
    for (let i = this.vadState.energyHistory.length - 1; i > 0; i--) {
      this.vadState.energyHistory[i] = this.vadState.energyHistory[i - 1]
    }
    this.vadState.energyHistory[0] = energy
    
    // スペクトル履歴の更新
    for (let i = this.vadState.spectralHistory.length - 1; i > 0; i--) {
      this.vadState.spectralHistory[i] = this.vadState.spectralHistory[i - 1]
    }
    this.vadState.spectralHistory[0] = spectralCentroid
  }

  /**
   * 雑音スペクトルの更新
   */
  private updateNoiseSpectrum(spectrum: Float32Array, isVoice: boolean): void {
    if (!isVoice) {
      // 音声がない場合のみ雑音スペクトルを更新
      const alpha = this.config.adaptiveProcessing.learningRate
      const beta = this.config.adaptiveProcessing.forgettingFactor
      
      for (let i = 0; i < spectrum.length; i++) {
        this.adaptiveState.noiseEstimate[i] = 
          beta * this.adaptiveState.noiseEstimate[i] + 
          alpha * spectrum[i]
      }
    }
    
    // 雑音スペクトルの平滑化
    const smoothingFactor = this.config.spectralSubtraction.smoothingFactor
    for (let i = 0; i < spectrum.length; i++) {
      this.noiseSpectrum[i] = 
        smoothingFactor * this.noiseSpectrum[i] + 
        (1 - smoothingFactor) * this.adaptiveState.noiseEstimate[i]
    }
  }

  /**
   * ノイズ除去フィルターの適用
   */
  private applyNoiseReduction(spectrum: Float32Array): Float32Array {
    const filteredSpectrum = new Float32Array(spectrum.length)
    
    switch (this.config.algorithm) {
      case 'spectral-subtraction':
        return this.applySpectralSubtraction(spectrum)
      case 'wiener-filter':
        return this.applyWienerFilter(spectrum)
      case 'kalman-filter':
        return this.applyKalmanFilter(spectrum)
      default:
        return this.applySpectralSubtraction(spectrum)
    }
  }

  /**
   * スペクトル減算法
   */
  private applySpectralSubtraction(spectrum: Float32Array): Float32Array {
    const filteredSpectrum = new Float32Array(spectrum.length)
    const alpha = this.config.spectralSubtraction.alpha
    const beta = this.config.spectralSubtraction.beta
    
    for (let i = 0; i < spectrum.length; i++) {
      const noisePower = this.noiseSpectrum[i] * this.noiseSpectrum[i]
      const signalPower = spectrum[i] * spectrum[i]
      
      // スペクトル減算
      let filteredPower = signalPower - alpha * noisePower
      
      // フロア処理
      filteredPower = Math.max(filteredPower, beta * signalPower)
      
      // 平方根で振幅に戻す
      filteredSpectrum[i] = Math.sqrt(filteredPower)
    }
    
    return filteredSpectrum
  }

  /**
   * ウィーナーフィルター法
   */
  private applyWienerFilter(spectrum: Float32Array): Float32Array {
    const filteredSpectrum = new Float32Array(spectrum.length)
    
    for (let i = 0; i < spectrum.length; i++) {
      const noisePower = this.noiseSpectrum[i] * this.noiseSpectrum[i]
      const signalPower = spectrum[i] * spectrum[i]
      
      // ウィーナーフィルター係数
      const snr = signalPower / (noisePower + 1e-10)
      const filterCoeff = snr / (snr + 1)
      
      filteredSpectrum[i] = spectrum[i] * filterCoeff
    }
    
    return filteredSpectrum
  }

  /**
   * カルマンフィルター法（簡易版）
   */
  private applyKalmanFilter(spectrum: Float32Array): Float32Array {
    const filteredSpectrum = new Float32Array(spectrum.length)
    
    for (let i = 0; i < spectrum.length; i++) {
      const noisePower = this.noiseSpectrum[i] * this.noiseSpectrum[i]
      const signalPower = spectrum[i] * spectrum[i]
      
      // カルマンゲインの計算
      const kalmanGain = signalPower / (signalPower + noisePower)
      
      // フィルタリング
      filteredSpectrum[i] = spectrum[i] * kalmanGain
    }
    
    return filteredSpectrum
  }

  /**
   * IFFT逆変換
   */
  private computeInverseSpectrum(spectrum: Float32Array): Float32Array {
    const fftSize = spectrum.length * 2
    const output = new Float32Array(fftSize)
    
    // 簡易的なIFFT計算
    for (let n = 0; n < fftSize; n++) {
      let real = 0
      
      for (let k = 0; k < spectrum.length; k++) {
        const angle = 2 * Math.PI * k * n / fftSize
        real += spectrum[k] * Math.cos(angle)
      }
      
      output[n] = real / fftSize
    }
    
    return output
  }

  /**
   * 統計情報の更新
   */
  private updateStats(input: Float32Array, output: Float32Array): void {
    this.stats.totalFrames++
    
    if (this.vadState.isVoice) {
      this.stats.voiceFrames++
    } else {
      this.stats.noiseFrames++
    }
    
    // 雑音除去量の計算
    const inputPower = this.computeSignalPower(input)
    const outputPower = this.computeSignalPower(output)
    
    if (inputPower > 0) {
      this.stats.noiseReduction = 10 * Math.log10(inputPower / outputPower)
    }
    
    // SNR改善量の計算
    const inputSNR = this.computeSNR(input)
    const outputSNR = this.computeSNR(output)
    this.stats.snrImprovement = outputSNR - inputSNR
    
    // 全体的な品質の計算
    this.stats.overallQuality = this.computeOverallQuality()
    
    // 音声保持率の計算
    this.stats.speechPreservation = this.computeSpeechPreservation(input, output)
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
   * SNRの計算
   */
  private computeSNR(signal: Float32Array): number {
    const signalPower = this.computeSignalPower(signal)
    const noisePower = this.computeAverageNoisePower()
    
    if (noisePower === 0) return 0
    
    return 10 * Math.log10(signalPower / noisePower)
  }

  /**
   * 平均雑音電力の計算
   */
  private computeAverageNoisePower(): number {
    let totalPower = 0
    for (let i = 0; i < this.noiseSpectrum.length; i++) {
      totalPower += this.noiseSpectrum[i] * this.noiseSpectrum[i]
    }
    return totalPower / this.noiseSpectrum.length
  }

  /**
   * 全体的な品質の計算
   */
  private computeOverallQuality(): number {
    // 複数の指標を組み合わせて品質を計算
    const noiseReductionScore = Math.min(1, this.stats.noiseReduction / 20) // 20dB以上で満点
    const snrScore = Math.min(1, (this.stats.snrImprovement + 10) / 30) // -10dB〜20dBを0〜1に正規化
    const speechScore = this.stats.speechPreservation
    
    return (noiseReductionScore + snrScore + speechScore) / 3
  }

  /**
   * 音声保持率の計算
   */
  private computeSpeechPreservation(input: Float32Array, output: Float32Array): number {
    // 相関係数による音声保持率の計算
    const correlation = this.computeCorrelation(input, output)
    return Math.max(0, correlation)
  }

  /**
   * 相関係数の計算
   */
  private computeCorrelation(signal1: Float32Array, signal2: Float32Array): number {
    const mean1 = this.computeMean(signal1)
    const mean2 = this.computeMean(signal2)
    
    let numerator = 0
    let denominator1 = 0
    let denominator2 = 0
    
    for (let i = 0; i < signal1.length; i++) {
      const diff1 = signal1[i] - mean1
      const diff2 = signal2[i] - mean2
      
      numerator += diff1 * diff2
      denominator1 += diff1 * diff1
      denominator2 += diff2 * diff2
    }
    
    const denominator = Math.sqrt(denominator1 * denominator2)
    return denominator > 0 ? numerator / denominator : 0
  }

  /**
   * 平均値の計算
   */
  private computeMean(signal: Float32Array): number {
    let sum = 0
    for (let i = 0; i < signal.length; i++) {
      sum += signal[i]
    }
    return sum / signal.length
  }

  /**
   * 設定の更新
   */
  updateConfig(newConfig: Partial<NoiseReductionConfig>): void {
    this.config = { ...this.config, ...newConfig }
  }

  /**
   * 統計情報の取得
   */
  getStats(): NoiseReductionStats {
    return { ...this.stats }
  }

  /**
   * フィルターのリセット
   */
  reset(): void {
    this.noiseSpectrum.fill(0)
    this.signalSpectrum.fill(0)
    this.previousSpectrum.fill(0)
    
    this.adaptiveState.noiseEstimate.fill(0)
    this.adaptiveState.signalEstimate.fill(0)
    this.adaptiveState.adaptationFactor.fill(1)
    
    this.stats = this.initializeStats()
  }

  /**
   * クリーンアップ
   */
  destroy(): void {
    this.noiseSpectrum = null as any
    this.signalSpectrum = null as any
    this.previousSpectrum = null as any
    this.adaptiveState.noiseEstimate = null as any
    this.adaptiveState.signalEstimate = null as any
    this.adaptiveState.adaptationFactor = null as any
  }
}
