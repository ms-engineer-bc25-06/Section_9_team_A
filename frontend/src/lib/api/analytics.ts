// AI分析APIクライアント
import { apiClient } from '@/lib/apiClient'

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
  total: number
  page: number
  size: number
}

class AnalyticsAPI {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await apiClient.get(`/analytics${endpoint}`, options)
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to fetch analyses: ${errorText}`)
    }
    
    return response.json()
  }

  // 分析履歴を取得
  async getAnalyses(
    page: number = 1,
    page_size: number = 20,
    analysis_type?: string
  ): Promise<AnalysisListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: page_size.toString(),
    })
    
    if (analysis_type) {
      params.append('analysis_type', analysis_type)
    }
    
    return this.request<AnalysisListResponse>(`?${params.toString()}`)
  }

  // 特定の分析を取得
  async getAnalysis(analysisId: string): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>(`/${analysisId}`)
  }

  // 新しい分析を作成
  async createAnalysis(request: AnalysisRequest): Promise<AnalysisResponse[]> {
    const response = await apiClient.post('/analytics', request)
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to create analysis: ${errorText}`)
    }
    
    return response.json()
  }

  // 分析を更新
  async updateAnalysis(
    analysisId: string,
    updates: Partial<AnalysisRequest>
  ): Promise<AnalysisResponse> {
    const response = await apiClient.put(`/api/v1/analytics/${analysisId}`, updates)
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to update analysis: ${errorText}`)
    }
    
    return response.json()
  }

  // 分析を削除
  async deleteAnalysis(analysisId: string): Promise<void> {
    const response = await apiClient.delete(`/api/v1/analytics/${analysisId}`)
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to delete analysis: ${errorText}`)
    }
  }

  // 分析結果をエクスポート
  async exportAnalysis(
    analysisId: string,
    format: 'pdf' | 'csv' | 'json' = 'json'
  ): Promise<Blob> {
    const response = await apiClient.get(`/api/v1/analytics/${analysisId}/export?format=${format}`)
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to export analysis: ${errorText}`)
    }
    
    return response.blob()
  }

  // 分析統計を取得
  async getAnalyticsStats(): Promise<{
    total_analyses: number
    analyses_this_month: number
    average_confidence: number
    most_common_type: string
  }> {
    return this.request('/stats')
  }

  // 分析タイプ別の統計を取得
  async getAnalyticsByType(analysisType: string): Promise<{
    type: string
    count: number
    average_score: number
    trends: Array<{ date: string; count: number }>
  }> {
    return this.request(`/type/${analysisType}/stats`)
  }
}

// シングルトンインスタンスをエクスポート
export const analyticsAPI = new AnalyticsAPI()
export default analyticsAPI
