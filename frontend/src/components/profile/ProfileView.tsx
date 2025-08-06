//FIXME（プロフィール閲覧）
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Separator } from "@/components/ui/Separator"
import { Calendar, MapPin, Home, Heart, Trophy, Utensils, Coffee, MessageSquare } from "lucide-react"

const mockProfile = {
  name: "田中太郎",
  department: "開発部",
  joinDate: "2023-04-01",
  birthDate: "1990-05-15",
  hometown: "東京都",
  residence: "神奈川県横浜市",
  hobbies: "プログラミング、読書、映画鑑賞",
  club: "テニス部",
  favoriteFood: "ラーメン、寿司",
  weekendActivity: "カフェ巡り、散歩",
  feedback: [
    "チームワークを大切にする素晴らしいメンバーです",
    "技術力が高く、いつも頼りになります",
    "コミュニケーション能力が高く、話しやすいです",
  ],
}

export function ProfileView() {
  const profileItems = [
    { icon: Calendar, label: "入社年月", value: mockProfile.joinDate },
    { icon: Calendar, label: "生年月日", value: mockProfile.birthDate },
    { icon: MapPin, label: "出身地", value: mockProfile.hometown },
    { icon: Home, label: "居住地", value: mockProfile.residence },
    { icon: Heart, label: "趣味／特技", value: mockProfile.hobbies },
    { icon: Trophy, label: "学生時代の部活／サークル", value: mockProfile.club },
    { icon: Utensils, label: "好きな食べ物", value: mockProfile.favoriteFood },
    { icon: Coffee, label: "休日の過ごし方", value: mockProfile.weekendActivity },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-6">
            <Avatar className="h-24 w-24">
              <AvatarImage src={`/placeholder.svg?height=96&width=96&query=${mockProfile.name}`} />
              <AvatarFallback className="text-2xl">{mockProfile.name.slice(0, 2)}</AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-3xl mb-2">{mockProfile.name}</CardTitle>
              <Badge variant="secondary" className="text-lg px-3 py-1">
                {mockProfile.department}
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {profileItems.map((item, index) => (
              <div key={index} className="flex items-start space-x-3">
                <item.icon className="h-5 w-5 text-gray-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <dt className="text-sm font-medium text-gray-500 mb-1">{item.label}</dt>
                  <dd className="text-gray-900">{item.value}</dd>
                </div>
              </div>
            ))}
          </div>

          <Separator />

          <div>
            <div className="flex items-center space-x-2 mb-4">
              <MessageSquare className="h-5 w-5 text-gray-500" />
              <h3 className="text-lg font-semibold">フィードバック</h3>
            </div>
            <div className="space-y-3">
              {mockProfile.feedback.map((feedback, index) => (
                <Card key={index} className="bg-blue-50 border-blue-200">
                  <CardContent className="p-4">
                    <p className="text-gray-700">{feedback}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
