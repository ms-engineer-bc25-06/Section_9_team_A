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
import { Camera, Save, List, AlertCircle } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/AuthProvider"
import { mockUserProfile } from "@/data/mockProfileData"

interface ProfileData {
  full_name?: string
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
  full_name: "",
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
  const [isFirstLogin, setIsFirstLogin] = useState(false)
  const router = useRouter()
  const { user } = useAuth()

  // プレゼンテーション用：モックデータを初期値として使用
  useEffect(() => {
    const fetchMockProfile = async () => {
      if (!user) return
      
      try {
        // シミュレーション用の遅延（実際のAPI呼び出しを模擬）
        await new Promise(resolve => setTimeout(resolve, 300))
        
        // モックデータを設定
        setProfile({
          full_name: mockUserProfile.full_name,
          nickname: mockUserProfile.nickname,
          department: mockUserProfile.department,
          join_date: mockUserProfile.join_date,
          birth_date: mockUserProfile.birth_date,
          hometown: mockUserProfile.hometown,
          residence: mockUserProfile.residence,
          hobbies: mockUserProfile.hobbies,
          student_activities: mockUserProfile.student_activities,
          holiday_activities: mockUserProfile.holiday_activities,
          favorite_food: mockUserProfile.favorite_food,
          favorite_media: mockUserProfile.favorite_media,
          favorite_music: mockUserProfile.favorite_music,
          pets_oshi: mockUserProfile.pets_oshi,
          respected_person: mockUserProfile.respected_person,
          motto: mockUserProfile.motto,
          future_goals: mockUserProfile.future_goals,
        })
        setIsFirstLogin(false)
      } catch (error) {
        console.error("プロフィール取得エラー:", error)
      } finally {
        setIsInitializing(false)
      }
    }

    fetchMockProfile()
  }, [user])

  const handleInputChange = (field: string, value: string) => {
    setProfile((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    if (!user) return

    setIsLoading(true)
    
    try {
      // プレゼンテーション用：シミュレーション用の遅延
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // プレゼンテーション用：成功メッセージを表示
      alert("プロフィールが保存されました！")
      
      // 実際の実装ではここでAPIを呼び出す
      // await apiClient.put('/users/profile', profile)
      
    } catch (error) {
      console.error("プロフィール保存エラー:", error)
      alert("プロフィールの保存に失敗しました")
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
                <AvatarImage src={`/placeholder.svg?height=96&width=96&query=${profile.full_name || profile.nickname}`} />
                <AvatarFallback className="text-2xl">
                  {(profile.full_name || profile.nickname || "ユ").slice(0, 2)}
                </AvatarFallback>
              </Avatar>
              <Button size="sm" className="absolute -bottom-2 -right-2 rounded-full w-8 h-8 p-0">
                <Camera className="h-4 w-4" />
              </Button>
            </div>
            <div>
              <CardTitle className="text-3xl mb-2">
                {profile.full_name || profile.nickname || "名前未設定"}
              </CardTitle>
              {profile.nickname && profile.nickname !== profile.full_name && (
                <p className="text-lg text-gray-600 mb-2">({profile.nickname})</p>
              )}
              <Badge variant="secondary" className="text-lg px-3 py-1">
                {profile.department || "部署未設定"}
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="full_name" className="flex items-center gap-2">
                お名前
                {isFirstLogin && <span className="text-red-500 text-sm">*</span>}
              </Label>
              <Input 
                id="full_name" 
                value={profile.full_name || ""} 
                onChange={(e) => handleInputChange("full_name", e.target.value)}
                placeholder="田中太郎"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="nickname">
                ニックネーム
              </Label>
              <Input 
                id="nickname" 
                value={profile.nickname || ""} 
                onChange={(e) => handleInputChange("nickname", e.target.value)}
                placeholder="たなちゃん"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="department" className="flex items-center gap-2">
                部署
                {isFirstLogin && <span className="text-red-500 text-sm">*</span>}
              </Label>
              <Input
                id="department"
                value={profile.department}
                onChange={(e) => handleInputChange("department", e.target.value)}
                placeholder="開発部"
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

            <Button 
              onClick={handleSave} 
              disabled={isLoading || (isFirstLogin && (!profile.full_name?.trim() || !profile.department?.trim()))}
              className={isFirstLogin ? "bg-blue-600 hover:bg-blue-700" : ""}
            >
              {isLoading ? "保存中..." : "プロフィールを更新"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
