"use client"

import { useState } from "react"
import { TopicGenerator } from "@/components/topic-generation/TopicGenerator"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Separator } from "@/components/ui/Separator"
import { 
  ArrowLeft, 
  Lightbulb, 
  Users, 
  Clock, 
  Target,
  MessageSquare,
  Share2
} from "lucide-react"
import Link from "next/link"

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

export default function TopicGenerationPage() {
  const [selectedTopic, setSelectedTopic] = useState<TopicSuggestion | null>(null)
  const [recentTopics, setRecentTopics] = useState<TopicSuggestion[]>([
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
    }
  ])

  const handleTopicSelect = (topic: TopicSuggestion) => {
    setSelectedTopic(topic)
  }

  const handleShareTopic = (topic: TopicSuggestion) => {
    // 実際の実装では、チームメンバーやチャットルームに共有する処理
    alert(`${topic.title}を共有しました！`)
  }

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

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  ダッシュボードへ戻る
                </Button>
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">トークテーマ生成</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* メインコンテンツ */}
          <div className="lg:col-span-2">
            <TopicGenerator onTopicSelect={handleTopicSelect} />
          </div>

          {/* サイドバー */}
          <div className="space-y-6">
            {/* 選択されたトピック */}
            {selectedTopic && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <MessageSquare className="h-5 w-5 text-blue-500" />
                    <span>選択されたトピック</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-lg mb-2">{selectedTopic.title}</h4>
                    <p className="text-gray-600 text-sm mb-3">{selectedTopic.description}</p>
                    
                    <div className="flex flex-wrap gap-2 mb-3">
                      <Badge className={getCategoryColor(selectedTopic.category)}>
                        {getCategoryIcon(selectedTopic.category)} {selectedTopic.category}
                      </Badge>
                      <Badge className={getDifficultyColor(selectedTopic.difficulty)}>
                        {selectedTopic.difficulty}
                      </Badge>
                      <Badge variant="outline">
                        <Clock className="h-3 w-3 mr-1" />
                        {selectedTopic.estimated_duration}分
                      </Badge>
                    </div>
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-3">
                    <Button 
                      className="w-full" 
                      onClick={() => handleShareTopic(selectedTopic)}
                    >
                      <Share2 className="h-4 w-4 mr-2" />
                      チームに共有
                    </Button>
                    
                    <Button variant="outline" className="w-full">
                      <MessageSquare className="h-4 w-4 mr-2" />
                      チャットルームで使用
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 最近のトピック */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Lightbulb className="h-5 w-5 text-yellow-500" />
                  <span>最近のトピック</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {recentTopics.map((topic, index) => (
                  <div key={index} className="p-3 border border-gray-200 rounded-lg">
                    <h5 className="font-medium text-sm mb-2">{topic.title}</h5>
                    <div className="flex flex-wrap gap-1 mb-2">
                      <Badge className={getCategoryColor(topic.category)} size="sm">
                        {getCategoryIcon(topic.category)}
                      </Badge>
                      <Badge className={getDifficultyColor(topic.difficulty)} size="sm">
                        {topic.difficulty}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{topic.estimated_duration}分</span>
                      <span>{Math.round(topic.confidence_score * 100)}%</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* 統計情報 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">統計情報</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">生成されたトピック</span>
                  <Badge variant="secondary">24件</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">使用されたトピック</span>
                  <Badge variant="secondary">18件</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">平均評価</span>
                  <Badge variant="secondary">4.2/5.0</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
