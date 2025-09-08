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
import { apiGet, apiPut, uploadAvatar } from "@/lib/apiClient"
import { getAvatarSrc } from "@/lib/utils/avatarUtils"

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
  avatar_url?: string
  is_first_login?: boolean
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
  avatar_url: "",
}

export function ProfileEditForm() {
  const [profile, setProfile] = useState<ProfileData>(defaultProfile)
  const [isLoading, setIsLoading] = useState(false)
  const [isInitializing, setIsInitializing] = useState(true)
  const [isFirstLogin, setIsFirstLogin] = useState(false)
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [avatarPreview, setAvatarPreview] = useState<string>("")
  const router = useRouter()
  const { user } = useAuth()

  // 実際のAPIからプロフィールデータを取得
  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) return
      
      try {
        console.log("🔍 プロフィール情報を取得中...")
        const data = await apiGet<ProfileData>("/users/profile")
        console.log("📊 取得したプロフィール情報:", data)
        
        setProfile({
          full_name: data.full_name || "",
          nickname: data.nickname || "",
          department: data.department || "",
          join_date: data.join_date ? data.join_date.split('T')[0] : "", // ISO形式から日付部分のみ抽出
          birth_date: data.birth_date ? data.birth_date.split('T')[0] : "", // ISO形式から日付部分のみ抽出
          hometown: data.hometown || "",
          residence: data.residence || "",
          hobbies: data.hobbies || "",
          student_activities: data.student_activities || "",
          holiday_activities: data.holiday_activities || "",
          favorite_food: data.favorite_food || "",
          favorite_media: data.favorite_media || "",
          favorite_music: data.favorite_music || "",
          pets_oshi: data.pets_oshi || "",
          respected_person: data.respected_person || "",
          motto: data.motto || "",
          future_goals: data.future_goals || "",
          avatar_url: data.avatar_url || "",
        })
        setIsFirstLogin(data.is_first_login || false)
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

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setAvatarFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setAvatarPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleAvatarRemove = () => {
    setAvatarFile(null)
    setAvatarPreview("")
    setProfile((prev) => ({ ...prev, avatar_url: "" }))
  }

  const handleSave = async () => {
    if (!user) return

    setIsLoading(true)
    
    try {
      console.log("💾 プロフィール保存中...", profile)
      
      // アバターファイルがある場合は、まずアップロード処理を行う
      let avatarUrl = profile.avatar_url
      if (avatarFile) {
        console.log("📤 アバター画像をアップロード中...")
        try {
          const uploadResult = await uploadAvatar(avatarFile)
          avatarUrl = uploadResult.avatar_url
          console.log("✅ アバターアップロード完了:", avatarUrl)
        } catch (uploadError) {
          console.error("❌ アバターアップロードエラー:", uploadError)
          throw new Error(`アバターのアップロードに失敗しました: ${uploadError instanceof Error ? uploadError.message : '不明なエラー'}`)
        }
      }
      
      // プロフィールデータにアバターURLを設定し、日付形式を適切に処理
      const profileData = {
        ...profile,
        avatar_url: avatarUrl,
        // 日付が空文字列の場合はnullに変換
        join_date: profile.join_date || null,
        birth_date: profile.birth_date || null
      }
      
      // 実際のAPIを呼び出してプロフィールを保存
      await apiPut('/users/profile', profileData)
      
      console.log("✅ プロフィール保存完了")
      alert("プロフィールが保存されました！")
      
      // アバターファイルの状態をリセット
      setAvatarFile(null)
      setAvatarPreview("")
      
    } catch (error) {
      console.error("プロフィール保存エラー:", error)
      const errorMessage = error instanceof Error ? error.message : "プロフィールの保存に失敗しました"
      alert(`プロフィールの保存に失敗しました: ${errorMessage}`)
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
            <div className="relative group">
                          <Avatar className="h-24 w-24">
              <AvatarImage 
                src={getAvatarSrc(avatarPreview, profile.avatar_url, profile.full_name || profile.nickname, 96)} 
              />
              <AvatarFallback className="text-2xl">
                {(profile.full_name || profile.nickname || "ユ").slice(0, 2)}
              </AvatarFallback>
            </Avatar>
              <div className="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <label htmlFor="avatar-upload" className="cursor-pointer">
                  <Camera className="h-6 w-6 text-white" />
                </label>
                <input
                  id="avatar-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarChange}
                  className="hidden"
                />
              </div>
              {(avatarPreview || profile.avatar_url) && (
                <Button 
                  size="sm" 
                  variant="destructive"
                  className="absolute -bottom-2 -right-2 rounded-full w-8 h-8 p-0"
                  onClick={handleAvatarRemove}
                >
                  ×
                </Button>
              )}
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
