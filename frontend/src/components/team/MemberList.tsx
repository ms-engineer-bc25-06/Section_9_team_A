"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Input } from "@/components/ui/Input"
import { Search, Users, Calendar, MapPin, Heart, Trophy, Coffee, Utensils, BookOpen, Music, Star, Target, Quote } from "lucide-react"
import { fetchWithAuth } from "@/lib/apiClient"

interface MemberProfile {
  department?: string
  position?: string
  nickname?: string
  join_date?: string
  birth_date?: string
  hometown?: string
  residence?: string
  hobbies?: string
  student_activities?: string
  holiday_activities?: string
  favorite_food?: string
  favorite_media?: string
  favorite_music?: string
  pets_oshi?: string
  respected_person?: string
  motto?: string
  future_goals?: string
}

interface Member {
  id: string
  display_name: string
  avatar_url?: string
  profile?: MemberProfile
}

export function MemberList() {
  const router = useRouter()
  const [members, setMembers] = useState<Member[]>([])
  const [filteredMembers, setFilteredMembers] = useState<Member[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    fetchMembers()
  }, [])

  useEffect(() => {
    filterMembers()
  }, [members, searchTerm])

  const fetchMembers = async () => {
    try {
      setIsLoading(true)
      const response = await fetchWithAuth(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/users/members`
      )
      
      if (response.ok) {
        const data = await response.json()
        console.log('Fetched members data:', data)
        setMembers(data)
      } else {
        console.error("メンバー取得に失敗しました")
      }
    } catch (error) {
      console.error("メンバー取得エラー:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const filterMembers = () => {
    if (!searchTerm.trim()) {
      setFilteredMembers(members)
      return
    }

    const filtered = members.filter(member => 
      member.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.profile?.department?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.profile?.nickname?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.profile?.hobbies?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    setFilteredMembers(filtered)
  }

  const handleMemberClick = (memberId: string) => {
    router.push(`/profile/${memberId}`)
  }

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <Card>
          <CardContent className="p-8">
            <div className="text-center">メンバー情報を読み込み中...</div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* 検索バー */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center space-x-2">
            <Search className="h-5 w-5 text-gray-400" />
            <Input
              placeholder="名前、部署、趣味などで検索..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
          </div>
        </CardContent>
      </Card>

      {/* メンバー一覧 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredMembers.map((member) => (
          <Card 
            key={member.id} 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => handleMemberClick(member.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-3">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={member.avatar_url} />
                  <AvatarFallback className="text-lg">
                    {member.display_name.slice(0, 2)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <CardTitle className="text-lg truncate">{member.display_name}</CardTitle>
                  {member.profile?.department && (
                    <Badge variant="secondary" className="text-sm">
                      {member.profile.department}
                    </Badge>
                  )}
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="pt-0">
              <div className="space-y-2">
                {member.profile?.nickname && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">ニックネーム:</span> {member.profile.nickname}
                  </div>
                )}
                
                {member.profile?.hobbies && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">趣味:</span> {member.profile.hobbies}
                  </div>
                )}
                
                {member.profile?.favorite_food && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">好きな食べ物:</span> {member.profile.favorite_food}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredMembers.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center text-gray-500">
            {searchTerm ? "検索条件に一致するメンバーが見つかりません" : "メンバーが登録されていません"}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
