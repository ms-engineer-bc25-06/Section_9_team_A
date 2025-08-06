// FIXME (メンバー一覧)
"use client"

import { Card, CardContent } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Eye } from "lucide-react"
import { useRouter } from "next/navigation"

const mockMembers = [
  {
    id: 1,
    name: "田中太郎",
    department: "開発部",
    joinDate: "2023-04-01",
    status: "online",
  },
  {
    id: 2,
    name: "佐藤花子",
    department: "デザイン部",
    joinDate: "2023-03-15",
    status: "offline",
  },
  {
    id: 3,
    name: "鈴木一郎",
    department: "営業部",
    joinDate: "2023-02-01",
    status: "online",
  },
  {
    id: 4,
    name: "高橋美咲",
    department: "マーケティング部",
    joinDate: "2023-01-10",
    status: "away",
  },
]

export function TeamMemberList() {
  const router = useRouter()

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "bg-green-500"
      case "away":
        return "bg-yellow-500"
      case "offline":
        return "bg-gray-400"
      default:
        return "bg-gray-400"
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "online":
        return "オンライン"
      case "away":
        return "離席中"
      case "offline":
        return "オフライン"
      default:
        return "不明"
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {mockMembers.map((member) => (
        <Card key={member.id} className="hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4 mb-4">
              <div className="relative">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={`/placeholder.svg?height=48&width=48&query=${member.name}`} />
                  <AvatarFallback>{member.name.slice(0, 2)}</AvatarFallback>
                </Avatar>
                <div
                  className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${getStatusColor(member.status)}`}
                />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-lg">{member.name}</h3>
                <p className="text-gray-600">{member.department}</p>
              </div>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">入社日:</span>
                <span>{member.joinDate}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500 text-sm">ステータス:</span>
                <Badge variant="secondary" className="text-xs">
                  {getStatusText(member.status)}
                </Badge>
              </div>
            </div>

            <Button onClick={() => router.push(`/team/${member.id}`)} className="w-full" variant="outline">
              <Eye className="h-4 w-4 mr-2" />
              詳細
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
