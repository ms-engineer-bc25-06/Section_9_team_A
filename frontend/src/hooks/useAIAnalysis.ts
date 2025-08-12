import { useState, useEffect } from 'react'

// AI分析結果の型定義
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
  maxScore: number
  trend: "up" | "down" | "stable"
}

export interface AnalysisResult {
  id: string
  analysisType: "personality" | "communication" | "behavior" | "sentiment" | "topic" | "summary"
  title: string
  content: string
  summary: string
  keywords: string[]
  topics: string[]
  sentimentScore: number
  sentimentLabel: string
  confidenceScore: number
  createdAt: string
  personalityTraits?: PersonalityTrait[]
  communicationPatterns?: CommunicationPattern[]
  behaviorScores?: BehaviorScore[]
}

interface UseAIAnalysisReturn {
  analyses: AnalysisResult[]
  isLoading: boolean
  error: string | null
  fetchAnalyses: () => Promise<void>
  createAnalysis: (text: string, analysisTypes: string[]) => Promise<AnalysisResult | null>
  getAnalysisById: (id: string) => AnalysisResult | undefined
  getAnalysesByType: (type: string) => AnalysisResult[]
}

// モックデータ（実際のAPIが実装されるまでの仮実装）
const mockAnalyses: AnalysisResult[] = [
  {
    id: "1",
    analysisType: "personality",
    title: "個性分析結果",
    content: "田中太郎さんの個性分析を行いました。",
    summary: "リーダーシップがあり、論理的思考が得意で、チームワークを重視する性格です。",
    keywords: ["リーダーシップ", "論理的思考", "チームワーク"],
    topics: ["性格", "リーダーシップ", "コミュニケーション"],
    sentimentScore: 0.8,
    sentimentLabel: "ポジティブ",
    confidenceScore: 0.9,
    createdAt: "2024-01-15T10:00:00Z",
    personalityTraits: [
      {
        trait: "リーダーシップ",
        score: 8,
        description: "チームをまとめる能力が高く、メンバーから信頼されています。"
      },
      {
        trait: "論理的思考",
        score: 9,
        description: "問題を体系的に分析し、効率的な解決策を見つけることができます。"
      },
      {
        trait: "共感力",
        score: 7,
        description: "他者の感情を理解し、適切なサポートを提供できます。"
      }
    ]
  },
  {
    id: "2",
    analysisType: "communication",
    title: "コミュニケーションパターン分析",
    content: "田中太郎さんのコミュニケーションパターンを分析しました。",
    summary: "積極的な発言が多く、他者の意見を尊重し、建設的な議論を促進します。",
    keywords: ["積極性", "尊重", "建設的"],
    topics: ["コミュニケーション", "チームワーク", "議論"],
    sentimentScore: 0.7,
    sentimentLabel: "ポジティブ",
    confidenceScore: 0.85,
    createdAt: "2024-01-15T11:00:00Z",
    communicationPatterns: [
      {
        pattern: "積極的な発言",
        frequency: 8,
        strength: "会議での発言が多く、アイデアを積極的に提案する",
        improvement: "時々話しすぎることがあるので、他の人の発言機会も確保する"
      },
      {
        pattern: "他者への配慮",
        frequency: 9,
        strength: "チームメンバーの意見をよく聞き、尊重する",
        improvement: "より多くのメンバーに発言を促す"
      },
      {
        pattern: "建設的な議論",
        frequency: 7,
        strength: "問題解決に向けた建設的な議論を促進する",
        improvement: "感情的な議論になりそうな時は冷静さを保つ"
      }
    ]
  },
  {
    id: "3",
    analysisType: "behavior",
    title: "行動特性スコア",
    content: "田中太郎さんの行動特性を数値化しました。",
    summary: "チーム貢献度が高く、問題解決能力に優れています。",
    keywords: ["チーム貢献", "問題解決", "学習意欲"],
    topics: ["行動", "能力", "成長"],
    sentimentScore: 0.6,
    sentimentLabel: "ポジティブ",
    confidenceScore: 0.8,
    createdAt: "2024-01-15T12:00:00Z",
    behaviorScores: [
      {
        category: "チーム貢献度",
        score: 85,
        maxScore: 100,
        trend: "up"
      },
      {
        category: "問題解決能力",
        score: 90,
        maxScore: 100,
        trend: "up"
      },
      {
        category: "学習意欲",
        score: 78,
        maxScore: 100,
        trend: "stable"
      },
      {
        category: "コミュニケーション能力",
        score: 82,
        maxScore: 100,
        trend: "up"
      }
    ]
  }
]

export function useAIAnalysis(): UseAIAnalysisReturn {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 分析結果を取得
  const fetchAnalyses = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      // 実際のAPIが実装されるまではモックデータを使用
      // const response = await fetch('/api/analytics')
      // const data = await response.json()
      // setAnalyses(data.analyses)
      
      // モックデータを設定
      await new Promise(resolve => setTimeout(resolve, 1000)) // ローディング効果のため
      setAnalyses(mockAnalyses)
    } catch (err) {
      setError('分析結果の取得に失敗しました')
      console.error('Failed to fetch analyses:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // 新しい分析を作成
  const createAnalysis = async (text: string, analysisTypes: string[]): Promise<AnalysisResult | null> => {
    setIsLoading(true)
    setError(null)
    
    try {
      // 実際のAPIが実装されるまではモックデータを返す
      // const response = await fetch('/api/analytics', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ text, analysis_types: analysisTypes })
      // })
      // const data = await response.json()
      // return data.analysis
      
      // モックデータを返す
      await new Promise(resolve => setTimeout(resolve, 2000)) // 分析処理のシミュレーション
      
      const newAnalysis: AnalysisResult = {
        id: Date.now().toString(),
        analysisType: "summary",
        title: "新しい分析結果",
        content: text,
        summary: `「${text.substring(0, 50)}...」の分析が完了しました。`,
        keywords: ["新規", "分析"],
        topics: ["分析"],
        sentimentScore: 0.5,
        sentimentLabel: "ニュートラル",
        confidenceScore: 0.8,
        createdAt: new Date().toISOString()
      }
      
      setAnalyses(prev => [newAnalysis, ...prev])
      return newAnalysis
    } catch (err) {
      setError('分析の作成に失敗しました')
      console.error('Failed to create analysis:', err)
      return null
    } finally {
      setIsLoading(false)
    }
  }

  // IDによる分析結果の取得
  const getAnalysisById = (id: string): AnalysisResult | undefined => {
    return analyses.find(analysis => analysis.id === id)
  }

  // タイプによる分析結果のフィルタリング
  const getAnalysesByType = (type: string): AnalysisResult[] => {
    return analyses.filter(analysis => analysis.analysisType === type)
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
    getAnalysesByType
  }
}
