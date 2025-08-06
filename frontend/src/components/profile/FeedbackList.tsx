"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { MessageSquare, Calendar } from "lucide-react"

const mockFeedbacks = [
  {
    id: 1,
    from: "佐藤花子",
    department: "デザイン部",
    message: "いつも丁寧に教えてくれてありがとうございます！技術的な質問にも親切に答えてくれて、とても助かっています。",
    date: "2024-01-15",
    type: "positive",
  },
  {
    id: 2,
    from: "鈴木一郎",
    department: "営業部",
    message: "チームワークを大切にしてくれる素晴らしい方です。プロジェクトでの協力姿勢がとても印象的でした。",
    date: "2024-01-10",
    type: "positive",
  },
  {
    id: 3,
    from: "高橋美咲",
    department: "マーケティング部",
    message: "技術力が高く、頼りになる存在です。複雑な問題も冷静に解決してくれるので安心して相談できます。",
    date: "2024-01-08",
    type: "positive",
  },
  {
    id: 4,
    from: "山田次郎",
    department: "開発部",
    message: "コミュニケーション能力が高く、話しやすいです。チーム内の雰囲気作りにも貢献してくれています。",
    date: "2024-01-05",
    type: "positive",
  },
  {
    id: 5,
    from: "伊藤三郎",
    department: "企画部",
    message: "新しいアイデアを積極的に提案してくれて、プロジェクトが活性化されました。創造性豊かな方だと思います。",
    date: "2024-01-03",
    type: "positive",
  },
]

export function FeedbackList() {
  const getTypeColor = (type: string) => {
    switch (type) {
      case "positive":
        return "bg-green-50 border-green-200"
      case "neutral":
        return "bg-blue-50 border-blue-200"
      case "improvement":
        return "bg-yellow-50 border-yellow-200"
      default:
        return "bg-gray-50 border-gray-200"
    }
  }

  const getTypeBadge = (type: string) => {
    switch (type) {
      case "positive":
        return { text: "ポジティブ", variant: "default" as const }
      case "neutral":
        return { text: "中立", variant: "secondary" as const }
      case "improvement":
        return { text: "改善提案", variant: "outline" as const }
      default:
        return { text: "その他", variant: "secondary" as const }
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-2">
          <MessageSquare className="h-5 w-5 text-gray-500" />
          <h2 className="text-xl font-semibold">受け取ったフィードバック</h2>
        </div>
        <p className="text-gray-600">チームメンバーからのフィードバックを確認できます。</p>
      </div>

      <div className="space-y-4">
        {mockFeedbacks.map((feedback) => {
          const badge = getTypeBadge(feedback.type)
          return (
            <Card key={feedback.id} className={getTypeColor(feedback.type)}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Avatar>
                      <AvatarImage src={`/placeholder.svg?height=40&width=40&query=${feedback.from}`} />
                      <AvatarFallback>{feedback.from.slice(0, 2)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle className="text-lg">{feedback.from}</CardTitle>
                      <p className="text-sm text-gray-600">{feedback.department}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={badge.variant}>{badge.text}</Badge>
                    <div className="flex items-center space-x-1 text-sm text-gray-500">
                      <Calendar className="h-4 w-4" />
                      <span>{feedback.date}</span>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 leading-relaxed">{feedback.message}</p>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
