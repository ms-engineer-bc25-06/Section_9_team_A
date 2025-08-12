"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Badge } from "@/components/ui/Badge"
import { Separator } from "@/components/ui/Separator"
import { 
  Lightbulb, 
  Clock, 
  Users, 
  Target, 
  MessageSquare,
  Sparkles,
  Loader2
} from "lucide-react"

interface TopicSuggestion {
  title: string
  description: string
  category: string
  difficulty: string
  estimated_duration: number
  conversation_starters: string[]
  related_keywords: string[]
  confidence_score: number
}

interface TopicGenerationResult {
  generation_id: string
  user_id: number
  participant_ids: number[]
  generated_at: string
  topics: TopicSuggestion[]
  generation_reason: string
  analysis_summary: string
  total_score: number
}

interface TopicGeneratorProps {
  onTopicSelect?: (topic: TopicSuggestion) => void
  className?: string
}

export function TopicGenerator({ onTopicSelect, className }: TopicGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedTopics, setGeneratedTopics] = useState<TopicGenerationResult | null>(null)
  const [textContent, setTextContent] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("")
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("")
  const [maxDuration, setMaxDuration] = useState<number>(30)

  const categories = [
    "work", "personal", "hobby", "current_events", 
    "technology", "culture", "sports", "food", "travel", "other"
  ]

  const difficulties = ["easy", "medium", "hard"]

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "work": return "💼"
      case "personal": return "👤"
      case "hobby": return "🎯"
      case "current_events": return "📰"
      case "technology": return "💻"
      case "culture": return "🎭"
      case "sports": return "⚽"
      case "food": return "🍕"
      case "travel": return "✈️"
      default: return "💡"
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy": return "bg-green-100 text-green-800"
      case "medium": return "bg-yellow-100 text-yellow-800"
      case "hard": return "bg-red-100 text-red-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "work": return "bg-blue-100 text-blue-800"
      case "personal": return "bg-purple-100 text-purple-800"
      case "hobby": return "bg-green-100 text-green-800"
      case "current_events": return "bg-orange-100 text-orange-800"
      case "technology": return "bg-indigo-100 text-indigo-800"
      case "culture": return "bg-pink-100 text-pink-800"
      case "sports": return "bg-emerald-100 text-emerald-800"
      case "food": return "bg-amber-100 text-amber-800"
      case "travel": return "bg-cyan-100 text-cyan-800"
      default: return "bg-gray-100 text-gray-800"
    }
  }

  const handleGenerateTopics = async () => {
    if (!textContent.trim()) {
      alert("会話内容を入力してください")
      return
    }

    setIsGenerating(true)
    try {
      // 実際のAPI呼び出し（現在はモックデータ）
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const mockResult: TopicGenerationResult = {
        generation_id: "mock-123",
        user_id: 1,
        participant_ids: [1, 2, 3],
        generated_at: new Date().toISOString(),
        topics: [
          {
            title: "最近の出来事について",
            description: "最近あった楽しかったことや印象に残った出来事を共有しましょう",
            category: "personal",
            difficulty: "easy",
            estimated_duration: 15,
            conversation_starters: ["今週あった楽しいことは？", "最近印象に残った出来事は？"],
            related_keywords: ["日常", "出来事", "体験"],
            confidence_score: 0.85
          },
          {
            title: "趣味・特技の話",
            description: "それぞれの趣味や特技について話し合いましょう",
            category: "hobby",
            difficulty: "easy",
            estimated_duration: 20,
            conversation_starters: ["最近ハマっていることは？", "得意なことは？"],
            related_keywords: ["趣味", "特技", "興味"],
            confidence_score: 0.8
          },
          {
            title: "仕事の話",
            description: "現在の仕事やプロジェクトについて話し合いましょう",
            category: "work",
            difficulty: "medium",
            estimated_duration: 25,
            conversation_starters: ["今取り組んでいる仕事は？", "仕事で困っていることは？"],
            related_keywords: ["仕事", "プロジェクト", "課題"],
            confidence_score: 0.75
          }
        ],
        generation_reason: "会話内容と参加者の興味・関心に基づく提案",
        analysis_summary: "コミュニケーションパターン分析と個性分析の結果を考慮",
        total_score: 0.8
      }
      
      setGeneratedTopics(mockResult)
    } catch (error) {
      console.error("トークテーマ生成エラー:", error)
      alert("トークテーマの生成に失敗しました")
    } finally {
      setIsGenerating(false)
    }
  }

  const handleTopicSelect = (topic: TopicSuggestion) => {
    if (onTopicSelect) {
      onTopicSelect(topic)
    }
  }

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            <span>トークテーマ生成</span>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* 入力フォーム */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="textContent">会話内容</Label>
              <Input
                id="textContent"
                placeholder="分析したい会話内容を入力してください..."
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                className="mt-1"
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="category">カテゴリ</Label>
                <select
                  id="category"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">すべて</option>
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {getCategoryIcon(category)} {category}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <Label htmlFor="difficulty">難易度</Label>
                <select
                  id="difficulty"
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">すべて</option>
                  {difficulties.map((difficulty) => (
                    <option key={difficulty} value={difficulty}>
                      {difficulty}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <Label htmlFor="maxDuration">最大時間（分）</Label>
                <Input
                  id="maxDuration"
                  type="number"
                  min="5"
                  max="120"
                  value={maxDuration}
                  onChange={(e) => setMaxDuration(Number(e.target.value))}
                  className="mt-1"
                />
              </div>
            </div>
            
            <Button
              onClick={handleGenerateTopics}
              disabled={isGenerating || !textContent.trim()}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  生成中...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  トークテーマを生成
                </>
              )}
            </Button>
          </div>

          {/* 生成結果 */}
          {generatedTopics && (
            <div className="space-y-4">
              <Separator />
              
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">生成されたトピック</h3>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">
                    総合スコア: {generatedTopics.total_score}
                  </Badge>
                  <Badge variant="outline">
                    {generatedTopics.topics.length}件
                  </Badge>
                </div>
              </div>
              
              <div className="text-sm text-gray-600">
                <p><strong>生成理由:</strong> {generatedTopics.generation_reason}</p>
                <p><strong>分析要約:</strong> {generatedTopics.analysis_summary}</p>
              </div>
              
              <div className="grid grid-cols-1 gap-4">
                {generatedTopics.topics.map((topic, index) => (
                  <Card key={index} className="border-l-4 border-l-blue-500">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-semibold text-lg mb-2">{topic.title}</h4>
                          <p className="text-gray-600 mb-3">{topic.description}</p>
                          
                          <div className="flex flex-wrap gap-2 mb-3">
                            <Badge className={getCategoryColor(topic.category)}>
                              {getCategoryIcon(topic.category)} {topic.category}
                            </Badge>
                            <Badge className={getDifficultyColor(topic.difficulty)}>
                              {topic.difficulty}
                            </Badge>
                            <Badge variant="outline">
                              <Clock className="h-3 w-3 mr-1" />
                              {topic.estimated_duration}分
                            </Badge>
                            <Badge variant="outline">
                              <Target className="h-3 w-3 mr-1" />
                              {Math.round(topic.confidence_score * 100)}%
                            </Badge>
                          </div>
                        </div>
                        
                        <Button
                          size="sm"
                          onClick={() => handleTopicSelect(topic)}
                          className="ml-4"
                        >
                          <MessageSquare className="h-4 w-4 mr-1" />
                          選択
                        </Button>
                      </div>
                      
                      <div className="space-y-3">
                        <div>
                          <h5 className="font-medium text-sm text-gray-700 mb-2">
                            会話のきっかけ
                          </h5>
                          <div className="space-y-1">
                            {topic.conversation_starters.map((starter, idx) => (
                              <div key={idx} className="flex items-center space-x-2 text-sm text-gray-600">
                                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                                <span>{starter}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                        
                        <div>
                          <h5 className="font-medium text-sm text-gray-700 mb-2">
                            関連キーワード
                          </h5>
                          <div className="flex flex-wrap gap-1">
                            {topic.related_keywords.map((keyword, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {keyword}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
