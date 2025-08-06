//FIXME（プロフィール編集）
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Textarea } from "@/components/ui/Textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Separator } from "@/components/ui/Separator"
import { Camera, Save, List } from "lucide-react"
import { useRouter } from "next/navigation"

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
}

export function ProfileEditForm() {
  const [profile, setProfile] = useState(mockProfile)
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleInputChange = (field: string, value: string) => {
    setProfile((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    setIsLoading(true)
    // 保存処理のシミュレーション
    setTimeout(() => {
      setIsLoading(false)
      router.push("/profile")
    }, 1000)
  }

  const handleViewFeedback = () => {
    router.push("/profile/feedback")
  }

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-6">
            <div className="relative">
              <Avatar className="h-24 w-24">
                <AvatarImage src={`/placeholder.svg?height=96&width=96&query=${profile.name}`} />
                <AvatarFallback className="text-2xl">{profile.name.slice(0, 2)}</AvatarFallback>
              </Avatar>
              <Button size="sm" className="absolute -bottom-2 -right-2 rounded-full w-8 h-8 p-0">
                <Camera className="h-4 w-4" />
              </Button>
            </div>
            <div>
              <CardTitle className="text-3xl mb-2">{profile.name}</CardTitle>
              <Badge variant="secondary" className="text-lg px-3 py-1">
                {profile.department}
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="name">名前</Label>
              <Input id="name" value={profile.name} onChange={(e) => handleInputChange("name", e.target.value)} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="department">部署</Label>
              <Input
                id="department"
                value={profile.department}
                onChange={(e) => handleInputChange("department", e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="joinDate">入社年月</Label>
              <Input
                id="joinDate"
                type="date"
                value={profile.joinDate}
                onChange={(e) => handleInputChange("joinDate", e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="birthDate">生年月日</Label>
              <Input
                id="birthDate"
                type="date"
                value={profile.birthDate}
                onChange={(e) => handleInputChange("birthDate", e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="hometown">出身地</Label>
              <Input
                id="hometown"
                value={profile.hometown}
                onChange={(e) => handleInputChange("hometown", e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="residence">居住地</Label>
              <Input
                id="residence"
                value={profile.residence}
                onChange={(e) => handleInputChange("residence", e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="hobbies">趣味／特技</Label>
              <Textarea
                id="hobbies"
                value={profile.hobbies}
                onChange={(e) => handleInputChange("hobbies", e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="club">学生時代の部活／サークル</Label>
              <Input id="club" value={profile.club} onChange={(e) => handleInputChange("club", e.target.value)} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="favoriteFood">好きな食べ物</Label>
              <Input
                id="favoriteFood"
                value={profile.favoriteFood}
                onChange={(e) => handleInputChange("favoriteFood", e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="weekendActivity">休日の過ごし方</Label>
              <Textarea
                id="weekendActivity"
                value={profile.weekendActivity}
                onChange={(e) => handleInputChange("weekendActivity", e.target.value)}
                rows={2}
              />
            </div>
          </div>

          <Separator />

          <div className="flex justify-between">
            <Button variant="outline" onClick={handleViewFeedback}>
              <List className="h-4 w-4 mr-2" />
              フィードバック一覧
            </Button>

            <Button onClick={handleSave} disabled={isLoading}>
              <Save className="h-4 w-4 mr-2" />
              {isLoading ? "保存中..." : "保存"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
