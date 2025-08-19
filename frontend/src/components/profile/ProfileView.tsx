//FIXME（プロフィール閲覧）
"use client"


import { AIAnalysisSection } from "./AIAnalysisSection"
import { AnalysisUpdateForm } from "./AnalysisUpdateForm"
import { ProfileTabs } from "./ProfileTabs"
import { useAIAnalysis } from "@/hooks/useAIAnalysis"

const mockProfile = {
  name: "田中太郎",
  nickname: "タロウ",
  department: "開発部",
  joinDate: "2023-04-01",
  birthDate: "1990-05-15",
  hometown: "東京都",
  residence: "神奈川県横浜市",
  hobbies: "プログラミング、読書、映画鑑賞",
  studentActivities: "テニス部、プログラミングサークル",
  holidayActivities: "カフェ巡り、散歩、映画鑑賞",
  favoriteFood: "ラーメン、寿司、カレー",
  favoriteMedia: "ハリーポッター、スターウォーズ、進撃の巨人",
  favoriteMusic: "J-POP、ロック、カラオケでは「乾杯」",
  petsOshi: "猫を飼っています、推しは初音ミク",
  respectedPerson: "スティーブ・ジョブズ",
  motto: "継続は力なり",
  futureGoals: "AI技術で社会に貢献するプロダクトを作りたい",
  feedback: [
    "チームワークを大切にする素晴らしいメンバーです",
    "技術力が高く、いつも頼りになります",
    "コミュニケーション能力が高く、話しやすいです",
  ],
}

export function ProfileView() {
  const { analyses, isLoading, error, createAnalysis } = useAIAnalysis()
  
  const handleAnalysisUpdate = async (text: string, analysisTypes: string[]) => {
    try {
      await createAnalysis(text, analysisTypes)
    } catch (error) {
      console.error('Analysis update failed:', error)
      throw error
    }
  }

  return (
    <ProfileTabs profile={mockProfile}>
      <div className="space-y-6">
        {/* AI分析結果セクション */}
        <AIAnalysisSection analyses={analyses} isLoading={isLoading} />
        
        {/* AI分析更新フォーム */}
        <AnalysisUpdateForm onAnalysisUpdate={handleAnalysisUpdate} isLoading={isLoading} />
      </div>
    </ProfileTabs>
  )
}
