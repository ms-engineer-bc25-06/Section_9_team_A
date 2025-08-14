"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Separator } from "@/components/ui/Separator"
import { Button } from "@/components/ui/Button"
import Link from "next/link"
import { PersonalGrowthEmbed } from "./PersonalGrowthEmbed"
import { 
  User, 
  Brain, 
  TrendingUp, 
  Settings,
  Calendar, 
  MapPin, 
  Home, 
  Heart, 
  Trophy, 
  Utensils, 
  Coffee, 
  MessageSquare,
  BookOpen,
  Music,
  PawPrint,
  Star,
  Quote,
  Target,
  BarChart3
} from "lucide-react"

interface ProfileTabsProps {
  profile: {
    name: string
    nickname: string
    department: string
    joinDate: string
    birthDate: string
    hometown: string
    residence: string
    hobbies: string
    studentActivities: string
    holidayActivities: string
    favoriteFood: string
    favoriteMedia: string
    favoriteMusic: string
    petsOshi: string
    respectedPerson: string
    motto: string
    futureGoals: string
    feedback: string[]
  }
  children: React.ReactNode
}

const tabs = [
  { id: "basic", label: "基本情報", icon: User },
  { id: "ai-analysis", label: "AI分析結果", icon: Brain },
  { id: "growth", label: "成長・変化", icon: TrendingUp },
  { id: "settings", label: "設定", icon: Settings }
]

export function ProfileTabs({ profile, children }: ProfileTabsProps) {
  const [activeTab, setActiveTab] = useState("basic")

  const profileItems = [
    { icon: User, label: "ニックネーム", value: profile.nickname },
    { icon: Calendar, label: "入社年月", value: profile.joinDate },
    { icon: Calendar, label: "生年月日", value: profile.birthDate },
    { icon: MapPin, label: "出身地", value: profile.hometown },
    { icon: Home, label: "居住地", value: profile.residence },
    { icon: Heart, label: "趣味・特技", value: profile.hobbies },
    { icon: Trophy, label: "学生時代の部活・サークル・力を入れていたこと", value: profile.studentActivities },
    { icon: Coffee, label: "休日の過ごし方", value: profile.holidayActivities },
    { icon: Utensils, label: "好きな食べ物", value: profile.favoriteFood },
    { icon: BookOpen, label: "好きな本・漫画・映画・ドラマ", value: profile.favoriteMedia },
    { icon: Music, label: "好きな音楽・カラオケの18番", value: profile.favoriteMusic },
    { icon: PawPrint, label: "ペット・推し", value: profile.petsOshi },
    { icon: Star, label: "尊敬する人", value: profile.respectedPerson },
    { icon: Quote, label: "座右の銘", value: profile.motto },
    { icon: Target, label: "将来の目標・生きてるうちにやってみたいこと", value: profile.futureGoals },
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case "basic":
        return (
          <div className="space-y-6">
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
                {profile.feedback.map((feedback, index) => (
                  <Card key={index} className="bg-blue-50 border-blue-200">
                    <CardContent className="p-4">
                      <p className="text-gray-700">{feedback}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        )
      
      case "ai-analysis":
        return (
          <div className="space-y-6">
            {children}
            
            {/* 分析結果一覧へのリンク */}
            <Card>
              <CardContent className="p-6">
                <div className="text-center">
                  <BarChart3 className="h-12 w-12 text-blue-500 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">より詳細な分析結果を確認</h3>
                  <p className="text-gray-600 mb-4">
                    すべての分析結果を一覧で確認し、詳細なレポートや統計情報を閲覧できます。
                  </p>
                  <Link href="/analytics">
                    <Button className="bg-blue-600 hover:bg-blue-700">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      分析結果一覧へ
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        )
      
      case "growth":
        return <PersonalGrowthEmbed />
      
      case "settings":
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>プロフィール設定</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">プロフィールの編集機能は現在開発中です。</p>
              </CardContent>
            </Card>
          </div>
        )
      
      default:
        return null
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* プロフィールヘッダー */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center space-x-6">
            <div className="h-24 w-24 rounded-full bg-gray-200 flex items-center justify-center">
              <span className="text-2xl text-gray-600">{profile.name.slice(0, 2)}</span>
            </div>
            <div>
              <CardTitle className="text-3xl mb-2">{profile.name}</CardTitle>
              <Badge variant="secondary" className="text-lg px-3 py-1">
                {profile.department}
              </Badge>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* タブナビゲーション */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* タブコンテンツ */}
      <div className="min-h-[400px]">
        {renderTabContent()}
      </div>
    </div>
  )
}
