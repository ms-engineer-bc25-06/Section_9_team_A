//FIXME（プロフィール編集）
"use client"

import { useState, useEffect } from "react"
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
import { useAuth } from "@/components/auth/AuthProvider"
import { fetchWithAuth } from "@/lib/auth"

interface ProfileData {
  nickname: string
  department: string
  join_date: string
  birth_date: string
  hometown: string
  residence: string
  hobbies: string
  student_activities: string
  holiday_activities: string
  favorite_food: string
  favorite_media: string
  favorite_music: string
  pets_oshi: string
  respected_person: string
  motto: string
  future_goals: string
}

const defaultProfile: ProfileData = {
  nickname: "",
  department: "",
  join_date: "",
  birth_date: "",
  hometown: "",
  residence: "",
  hobbies: "",
  student_activities: "",
  holiday_activities: "",
  favorite_food: "",
  favorite_media: "",
  favorite_music: "",
  pets_oshi: "",
  respected_person: "",
  motto: "",
  future_goals: "",
}

export function ProfileEditForm() {
  const [profile, setProfile] = useState<ProfileData>(defaultProfile)
  const [isLoading, setIsLoading] = useState(false)
  const [isInitializing, setIsInitializing] = useState(true)
  const router = useRouter()
  const { user } = useAuth()

  // 初期データの取得
  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) return
      
      try {
        const response = await fetchWithAuth(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/users/profile`)
        if (response.ok) {
          const data = await response.json()
          setProfile(data)
        } else {
          console.warn("プロフィール取得に失敗しました")
        }
      } catch (error) {
        console.error("プロフィール取得エラー:", error)
      } finally {
        setIsInitializing(false)
      }
    }

    fetchProfile()
  }, [user])

  const handleInputChange = (field: string, value: string) => {
    setProfile((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    if (!user) {
      alert("ログインが必要です")
      return
    }

    setIsLoading(true)
    
    try {
      const response = await fetchWithAuth(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/users/profile`,
        {
          method: "PUT",
          body: JSON.stringify(profile)
        }
      )

      if (response.ok) {
        alert("プロフィールを更新しました")
        router.push("/profile")
      } else {
        const errorData = await response.json()
        alert(`更新に失敗しました: ${errorData.detail || "エラーが発生しました"}`)
      }
    } catch (error) {
      console.error("保存エラー:", error)
      alert("保存中にエラーが発生しました")
    } finally {
      setIsLoading(false)
    }
  }

  const handleViewFeedback = () => {
    router.push("/profile/feedback")
  }

  if (isInitializing) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="p-8">
            <div className="text-center">読み込み中...</div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-6">
            <div className="relative">
              <Avatar className="h-24 w-24">
                <AvatarImage src={`/placeholder.svg?height=96&width=96&query=${profile.nickname}`} />
                <AvatarFallback className="text-2xl">{profile.nickname.slice(0, 2) || "ユ"}</AvatarFallback>
              </Avatar>
              <Button size="sm" className="absolute -bottom-2 -right-2 rounded-full w-8 h-8 p-0">
                <Camera className="h-4 w-4" />
              </Button>
            </div>
            <div>
              <CardTitle className="text-3xl mb-2">{profile.nickname || "ニックネーム未設定"}</CardTitle>
              <Badge variant="secondary" className="text-lg px-3 py-1">
                {profile.department || "部署未設定"}
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="nickname">ニックネーム</Label>
              <Input id="nickname" value={profile.nickname} onChange={(e) => handleInputChange("nickname", e.target.value)} />
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
              <Label htmlFor="join_date">入社年月</Label>
              <Input
                id="join_date"
                type="date"
                value={profile.join_date}
                onChange={(e) => handleInputChange("join_date", e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="birth_date">生年月日</Label>
              <Input
                id="birth_date"
                type="date"
                value={profile.birth_date}
                onChange={(e) => handleInputChange("birth_date", e.target.value)}
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
              <Label htmlFor="hobbies">趣味・特技</Label>
              <Textarea
                id="hobbies"
                value={profile.hobbies}
                onChange={(e) => handleInputChange("hobbies", e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="student_activities">学生時代の部活・サークル・力を入れていたこと</Label>
              <Textarea
                id="student_activities"
                value={profile.student_activities}
                onChange={(e) => handleInputChange("student_activities", e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="holiday_activities">休日の過ごし方</Label>
              <Textarea
                id="holiday_activities"
                value={profile.holiday_activities}
                onChange={(e) => handleInputChange("holiday_activities", e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="favorite_food">好きな食べ物</Label>
              <Textarea
                id="favorite_food"
                value={profile.favorite_food}
                onChange={(e) => handleInputChange("favorite_food", e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="favorite_media">好きな本・漫画・映画・ドラマ</Label>
              <Textarea
                id="favorite_media"
                value={profile.favorite_media}
                onChange={(e) => handleInputChange("favorite_media", e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="favorite_music">好きな音楽・カラオケの18番</Label>
              <Textarea
                id="favorite_music"
                value={profile.favorite_music}
                onChange={(e) => handleInputChange("favorite_music", e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="pets_oshi">ペット・推し</Label>
              <Textarea
                id="pets_oshi"
                value={profile.pets_oshi}
                onChange={(e) => handleInputChange("pets_oshi", e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="respected_person">尊敬する人</Label>
              <Textarea
                id="respected_person"
                value={profile.respected_person}
                onChange={(e) => handleInputChange("respected_person", e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="motto">座右の銘</Label>
              <Textarea
                id="motto"
                value={profile.motto}
                onChange={(e) => handleInputChange("motto", e.target.value)}
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="future_goals">将来の目標・生きてるうちにやってみたいこと</Label>
              <Textarea
                id="future_goals"
                value={profile.future_goals}
                onChange={(e) => handleInputChange("future_goals", e.target.value)}
                rows={3}
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
