// OpenAI Whisper API クライアント
export interface WhisperTranscriptionOptions {
  model?: 'whisper-1'
  language?: string
  prompt?: string
  response_format?: 'json' | 'text' | 'srt' | 'verbose_json' | 'vtt'
  temperature?: number
}

export interface WhisperTranscriptionResponse {
  text: string
  language?: string
  duration?: number
  segments?: Array<{
    id: number
    start: number
    end: number
    text: string
    tokens: number[]
    temperature: number
    avg_logprob: number
    compression_ratio: number
    no_speech_prob: number
  }>
}

export class WhisperAPIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message)
    this.name = 'WhisperAPIError'
  }
}

export class WhisperAPIClient {
  private apiKey: string
  private baseURL: string

  constructor(apiKey: string, baseURL: string = 'https://api.openai.com/v1') {
    this.apiKey = apiKey
    this.baseURL = baseURL
  }

  /**
   * 音声ファイルを文字起こし
   */
  async transcribeAudio(
    audioBlob: Blob,
    options: WhisperTranscriptionOptions = {}
  ): Promise<WhisperTranscriptionResponse> {
    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'audio.webm')
      formData.append('model', options.model || 'whisper-1')
      
      if (options.language) {
        formData.append('language', options.language)
      }
      if (options.prompt) {
        formData.append('prompt', options.prompt)
      }
      if (options.response_format) {
        formData.append('response_format', options.response_format)
      }
      if (options.temperature !== undefined) {
        formData.append('temperature', options.temperature.toString())
      }

      const response = await fetch(`${this.baseURL}/audio/transcriptions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new WhisperAPIError(
          errorData.error?.message || `HTTP ${response.status}`,
          response.status,
          errorData.error?.code
        )
      }

      const result = await response.json()
      return result
    } catch (error) {
      if (error instanceof WhisperAPIError) {
        throw error
      }
      throw new WhisperAPIError(
        error instanceof Error ? error.message : 'Unknown error occurred'
      )
    }
  }

  /**
   * 音声データをBase64エンコードして送信（ストリーミング用）
   */
  async transcribeAudioBase64(
    audioData: string, // Base64エンコードされた音声データ
    options: WhisperTranscriptionOptions = {}
  ): Promise<WhisperTranscriptionResponse> {
    try {
      const response = await fetch(`${this.baseURL}/audio/transcriptions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file: `data:audio/webm;base64,${audioData}`,
          model: options.model || 'whisper-1',
          language: options.language,
          prompt: options.prompt,
          response_format: options.response_format || 'json',
          temperature: options.temperature,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new WhisperAPIError(
          errorData.error?.message || `HTTP ${response.status}`,
          response.status,
          errorData.error?.code
        )
      }

      const result = await response.json()
      return result
    } catch (error) {
      if (error instanceof WhisperAPIError) {
        throw error
      }
      throw new WhisperAPIError(
        error instanceof Error ? error.message : 'Unknown error occurred'
      )
    }
  }

  /**
   * 音声チャンクの連続処理（リアルタイム文字起こし用）
   */
  async transcribeAudioChunk(
    audioChunk: Blob,
    previousText: string = '',
    options: WhisperTranscriptionOptions = {}
  ): Promise<{
    text: string
    isComplete: boolean
    confidence: number
  }> {
    try {
      // 前のテキストをプロンプトとして使用（文脈の継続性を保つ）
      const enhancedOptions = {
        ...options,
        prompt: previousText ? `Previous text: ${previousText}` : undefined,
        temperature: 0.3, // より一貫性のある結果のため
      }

      const result = await this.transcribeAudio(audioChunk, enhancedOptions)
      
      // 信頼度の計算（簡易版）
      const confidence = this.calculateConfidence(result)
      
      return {
        text: result.text,
        isComplete: this.isCompleteSentence(result.text),
        confidence,
      }
    } catch (error) {
      throw new WhisperAPIError(
        `Chunk transcription failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      )
    }
  }

  /**
   * 信頼度の計算
   */
  private calculateConfidence(result: WhisperTranscriptionResponse): number {
    if (!result.segments || result.segments.length === 0) {
      return 0.5 // デフォルト値
    }

    // セグメントの平均信頼度を計算
    const avgLogProb = result.segments.reduce((sum, segment) => {
      return sum + segment.avg_logprob
    }, 0) / result.segments.length

    // logprobを0-1の範囲に正規化
    const confidence = Math.max(0, Math.min(1, (avgLogProb + 10) / 10))
    return confidence
  }

  /**
   * 文が完了しているかの判定
   */
  private isCompleteSentence(text: string): boolean {
    const trimmedText = text.trim()
    if (trimmedText.length === 0) return false

    // 句読点で終わるかチェック
    const sentenceEndings = ['.', '!', '?', '。', '！', '？']
    return sentenceEndings.some(ending => trimmedText.endsWith(ending))
  }

  /**
   * 音声データの品質チェック
   */
  validateAudioData(audioBlob: Blob): {
    isValid: boolean
    issues: string[]
    recommendations: string[]
  } {
    const issues: string[] = []
    const recommendations: string[] = []

    // ファイルサイズチェック
    const maxSize = 25 * 1024 * 1024 // 25MB
    if (audioBlob.size > maxSize) {
      issues.push('ファイルサイズが大きすぎます')
      recommendations.push('音声を短くするか、品質を下げてください')
    }

    // ファイル形式チェック
    const supportedFormats = ['audio/webm', 'audio/mp4', 'audio/mpeg', 'audio/wav']
    if (!supportedFormats.includes(audioBlob.type)) {
      issues.push('サポートされていない音声形式です')
      recommendations.push('WebM、MP4、MP3、WAV形式を使用してください')
    }

    // 音声の長さチェック（推定）
    const estimatedDuration = audioBlob.size / (16000 * 2) // 16kHz, 16bit
    if (estimatedDuration > 300) { // 5分以上
      issues.push('音声が長すぎます')
      recommendations.push('5分以内の音声に分割してください')
    }

    return {
      isValid: issues.length === 0,
      issues,
      recommendations,
    }
  }
}

// シングルトンインスタンス
let whisperClient: WhisperAPIClient | null = null

export const getWhisperClient = (): WhisperAPIClient => {
  if (!whisperClient) {
    const apiKey = process.env.NEXT_PUBLIC_OPENAI_API_KEY
    if (!apiKey) {
      throw new Error('OpenAI API key is not configured')
    }
    whisperClient = new WhisperAPIClient(apiKey)
  }
  return whisperClient
}

export const setWhisperClient = (client: WhisperAPIClient) => {
  whisperClient = client
}
