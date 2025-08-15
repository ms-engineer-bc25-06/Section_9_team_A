// AI分析APIクライアント
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export type AnalysisType = 
  | 'personality' 
  | 'communication' 
  | 'behavior' 
  | 'sentiment' 
  | 'topic' 
  | 'summary'

export interface AnalysisRequest {
  text_content: string
  analysis_types: string[]
  user_context?: Record<string, any>
}

export interface AnalysisResponse {
  id: string
  analysis_type: string
  title: string
  content: string
  summary: string
  keywords: string[]
  topics: string[]
  sentiment_score: number
  sentiment_label: string
  word_count?: number
  sentence_count?: number
  speaking_time?: number
  confidence_score: number
  created_at: string
  personality_traits?: PersonalityTrait[]
  communication_patterns?: CommunicationPattern[]
  behavior_scores?: BehaviorScore[]
  status: string
}

export interface PersonalityTrait {
  trait: string
  score: number
  description: string
}

export interface CommunicationPattern {
  pattern: string
  frequency: number
  strength: string
  improvement: string
}

export interface BehaviorScore {
  category: string
  score: number
  max_score: number
  trend: "up" | "down" | "stable"
}

export interface AnalysisListResponse {
  analyses: AnalysisResponse[]
  total_count: number
  page: number
  page_size: number
}

class AnalyticsAPI {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    authToken?: string
  ): Promise<T> {
    const url = `${API_BASE_URL}/api/v1/analytics${endpoint}`
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    // 既存のヘッダーを追加
    if (options.headers) {
      if (options.headers instanceof Headers) {
        options.headers.forEach((value, key) => {
          headers[key] = value
        })
      } else if (typeof options.headers === 'object') {
        Object.entries(options.headers).forEach(([key, value]) => {
          if (typeof value === 'string') {
            headers[key] = value
          }
        })
      }
    }

    // 認証トークンがある場合はAuthorizationヘッダーを追加
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }
    
    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `API request failed: ${response.status}`)
    }

    return response.json()
  }

  // 分析結果一覧を取得
  async getAnalyses(
    page: number = 1,
    pageSize: number = 20,
    analysisType?: string,
    status?: string,
    authToken?: string
  ): Promise<AnalysisListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })

    if (analysisType) {
      params.append('analysis_type', analysisType)
    }

    if (status) {
      params.append('status', status)
    }

    return this.request<AnalysisListResponse>(`/?${params.toString()}`, {}, authToken)
  }

  // 特定の分析結果を取得
  async getAnalysis(analysisId: string, authToken?: string): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>(`/${analysisId}`, {}, authToken)
  }

  // 新しい分析を作成
  async createAnalysis(request: AnalysisRequest, authToken?: string): Promise<AnalysisResponse[]> {
    return this.request<AnalysisResponse[]>('/', {
      method: 'POST',
      body: JSON.stringify(request),
    }, authToken)
  }

  // 分析結果を更新
  async updateAnalysis(
    analysisId: string,
    updates: Partial<AnalysisResponse>,
    authToken?: string
  ): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>(`/${analysisId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }, authToken)
  }

  // 分析結果を削除
  async deleteAnalysis(analysisId: string, authToken?: string): Promise<void> {
    await this.request(`/${analysisId}`, {
      method: 'DELETE',
    }, authToken)
  }
}

export const analyticsAPI = new AnalyticsAPI()
