// FIXME （メンバー詳細表示）
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Separator } from "@/components/ui/Separator"
import { User,Briefcase,CalendarDays,Cake, MapPin, Home, Heart, Trophy, Sun, Utensils, BookOpen, Music, PawPrint, Star, Quote, Target, MessageSquare } from "lucide-react"

interface Props {
  memberId: string
}

const mockMemberDetail = {
  id: 1,
  name: "田中太郎",
  department: "開発部",
  nickname: "太郎",
  join_date: "2023-04-01",
  birth_date: "1990-05-15",
  hometown: "東京都",
  residence: "神奈川県横浜市",
  hobbies: "プログラミング、読書、映画鑑賞",
  student_activities: "テニス部",
  holiday_activities: "カフェ巡り、散歩",
  favorite_food: "ラーメン、寿司",
  favorite_media: "映画、漫画、ドラマ",
  favorite_music: "カラオケの18番",
  pets_oshi: "犬、猫",
  respected_person: "父親",
  motto: "努力は報われる",
  future_goals: "エンジニアとしての成長",
  feedback: [
    "いつも丁寧に教えてくれてありがとうございます！",
    "チームワークを大切にしてくれる素晴らしい方です",
    "技術力が高く、頼りになる存在です",
  ],
}

export function MemberDetail({ memberId }: Props) {
  const member = mockMemberDetail // 実際はAPIから取得

  const profileItems = [
    { icon: User, label: "名前", value: member.name },
    { icon: Briefcase, label: "部署", value: member.department },
    { icon: User, label: "ニックネーム", value: member.nickname },
    { icon: CalendarDays, label: "入社年月", value: member.join_date },
    { icon: Cake, label: "生年月日", value: member.birth_date },
    { icon: MapPin, label: "出身地", value: member.hometown },
    { icon: Home, label: "居住地", value: member.residence },
    { icon: Heart, label: "趣味／特技", value: member.hobbies },
    { icon: Trophy, label: "学生時代の部活／サークル", value: member.student_activities },
    { icon: Sun, label: "休日の過ごし方", value: member.holiday_activities },
    { icon: Utensils, label: "好きな食べ物", value: member.favorite_food },
    { icon: BookOpen, label: "好きな本・漫画・映画・ドラマ", value: member.favorite_media },
    { icon: Music, label: "好きな音楽・カラオケの18番", value: member.favorite_music },
    { icon: PawPrint, label: "ペット・推し", value: member.pets_oshi },
    { icon: Star, label: "尊敬する人", value: member.respected_person },
    { icon: Quote, label: "座右の銘", value: member.motto },
    { icon: Target, label: "将来の目標・生きてるうちにやってみたいこと ", value: member.future_goals },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-6">
            <Avatar className="h-24 w-24">
              <AvatarImage src={`/placeholder.svg?height=96&width=96&query=${member.name}`} />
              <AvatarFallback className="text-2xl">{member.name.slice(0, 2)}</AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-3xl mb-2">{member.name}</CardTitle>
              <Badge variant="secondary" className="text-lg px-3 py-1">
                {member.department}
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
              {member.feedback.map((feedback, index) => (
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
