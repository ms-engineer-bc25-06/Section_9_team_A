// TODO:最近のアクティビティ一覧モックデータの解除
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { MessageCircle, Users, BarChart3, Clock } from "lucide-react"

const mockActivities = [
  {
    id: 1,
    type: "voice_chat",
    user: "佐藤花子",
    action: "雑談ルームに参加しました",
    time: "5分前",
    icon: MessageCircle,
  },
  {
    id: 2,
    type: "team",
    user: "鈴木一郎",
    action: "プロフィールを更新しました",
    time: "15分前",
    icon: Users,
  },
  {
    id: 3,
    type: "analytics",
    user: "システム",
    action: "週次レポートが生成されました",
    time: "1時間前",
    icon: BarChart3,
  },
  {
    id: 4,
    type: "voice_chat",
    user: "高橋美咲",
    action: "音声セッションを終了しました",
    time: "2時間前",
    icon: MessageCircle,
  },
]

export function RecentActivity() {
  const getActivityColor = (type: string) => {
    switch (type) {
      case "voice_chat":
        return "text-green-600"
      case "team":
        return "text-blue-600"
      case "analytics":
        return "text-orange-600"
      default:
        return "text-gray-600"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Clock className="h-5 w-5" />
          <span>最近のアクティビティ</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockActivities.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-3">
              <div className={`p-2 rounded-full bg-gray-100 ${getActivityColor(activity.type)}`}>
                <activity.icon className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-sm">{activity.user}</span>
                  <Badge variant="secondary" className="text-xs">
                    {activity.time}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 mt-1">{activity.action}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
