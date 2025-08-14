import { useState, useEffect } from 'react'
import { analyticsAPI, AnalysisRequest, AnalysisResponse, AnalysisListResponse } from '@/lib/api/analytics'

interface UseAIAnalysisReturn {
  analyses: AnalysisResponse[]
  isLoading: boolean
  error: string | null
  fetchAnalyses: () => Promise<void>
  createAnalysis: (text: string, analysisTypes: string[]) => Promise<AnalysisResponse[] | null>
  getAnalysisById: (id: string) => AnalysisResponse | undefined
  getAnalysesByType: (type: string) => AnalysisResponse[]
  updateAnalysis: (id: string, updates: Partial<AnalysisResponse>) => Promise<AnalysisResponse | null>
  deleteAnalysis: (id: string) => Promise<boolean>
  refreshAnalyses: () => Promise<void>
}

export function useAIAnalysis(): UseAIAnalysisReturn {
  const [analyses, setAnalyses] = useState<AnalysisResponse[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 分析結果を取得
  const fetchAnalyses = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await analyticsAPI.getAnalyses()
      setAnalyses(response.analyses)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '分析結果の取得に失敗しました'
      setError(errorMessage)
      console.error('Failed to fetch analyses:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // 新しい分析を作成
  const createAnalysis = async (text: string, analysisTypes: string[]): Promise<AnalysisResponse[] | null> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const request: AnalysisRequest = {
        text_content: text,
        analysis_types: analysisTypes,
      }
      
      const newAnalyses = await analyticsAPI.createAnalysis(request)
      setAnalyses(prev => [...newAnalyses, ...prev])
      return newAnalyses
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '分析の作成に失敗しました'
      setError(errorMessage)
      console.error('Failed to create analysis:', err)
      return null
    } finally {
      setIsLoading(false)
    }
  }

  // 分析結果を更新
  const updateAnalysis = async (id: string, updates: Partial<AnalysisResponse>): Promise<AnalysisResponse | null> => {
    try {
      const updatedAnalysis = await analyticsAPI.updateAnalysis(id, updates)
      setAnalyses(prev => prev.map(analysis => 
        analysis.id === id ? updatedAnalysis : analysis
      ))
      return updatedAnalysis
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '分析の更新に失敗しました'
      setError(errorMessage)
      console.error('Failed to update analysis:', err)
      return null
    }
  }

  // 分析結果を削除
  const deleteAnalysis = async (id: string): Promise<boolean> => {
    try {
      await analyticsAPI.deleteAnalysis(id)
      setAnalyses(prev => prev.filter(analysis => analysis.id !== id))
      return true
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '分析の削除に失敗しました'
      setError(errorMessage)
      console.error('Failed to delete analysis:', err)
      return false
    }
  }

  // IDによる分析結果の取得
  const getAnalysisById = (id: string): AnalysisResponse | undefined => {
    return analyses.find(analysis => analysis.id === id)
  }

  // タイプによる分析結果のフィルタリング
  const getAnalysesByType = (type: string): AnalysisResponse[] => {
    return analyses.filter(analysis => analysis.analysis_type === type)
  }

  // 分析結果を再取得
  const refreshAnalyses = async () => {
    await fetchAnalyses()
  }

  // 初回読み込み時に分析結果を取得
  useEffect(() => {
    fetchAnalyses()
  }, [])

  return {
    analyses,
    isLoading,
    error,
    fetchAnalyses,
    createAnalysis,
    getAnalysisById,
    getAnalysesByType,
    updateAnalysis,
    deleteAnalysis,
    refreshAnalyses
  }
}
