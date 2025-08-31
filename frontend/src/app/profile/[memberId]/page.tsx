"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { ArrowLeft, Building2, Calendar, MapPin, Heart, Music, BookOpen, Target } from "lucide-react";
import Link from "next/link";
import { getMemberProfile, MemberProfile } from "@/lib/api/teamMembers";
import { MemberFeedbackList } from "@/components/team/MemberFeedbackList";
import { getDepartmentColor } from "@/lib/utils/departmentColors";
import { getAvatarUrl } from "@/lib/utils/avatarUtils";

export default function MemberProfilePage() {
  const params = useParams();
  const router = useRouter();
  const memberId = params.memberId as string;
  
  const [profile, setProfile] = useState<MemberProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (memberId) {
      fetchMemberProfile(memberId);
    }
  }, [memberId]);

  const fetchMemberProfile = async (id: string) => {
    try {
      setLoading(true);
      console.log('Fetching profile for member ID:', id);
      
      // 実際のAPIからデータを取得
      const apiProfile = await getMemberProfile(id);
      console.log('Received profile data:', apiProfile);
      setProfile(apiProfile);
      
    } catch (err) {
      console.error("Failed to fetch profile:", err);
      setError("プロフィールの取得に失敗しました");
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">プロフィールが見つかりません</p>
          <Button onClick={() => router.back()}>戻る</Button>
        </div>
      </div>
    );
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return "未設定";
    try {
      return new Date(dateString).toLocaleDateString('ja-JP');
    } catch {
      return dateString;
    }
  };

  // AI分析フィードバックのモックデータ（コメントアウト）
  // const feedbackData = [
  //   {
  //     icon: <MessageSquare className="h-5 w-5 text-green-600" />,
  //     title: "過去の実績",
  //     content: "家電量販店に勤務しているとき、月間売上日本一に輝いた",
  //     category: "AI分析結果"
  //   },
  //   {
  //     icon: <Star className="h-5 w-5 text-yellow-600" />,
  //     title: "コミュニケーション",
  //     content: "常に様々な話題を提供している",
  //     category: "AI分析結果"
  //   },
  //   {
  //     icon: <TrendingUp className="h-5 w-5 text-blue-600" />,
  //     title: "最近の活動",
  //     content: "先週サッカー野球観戦で東京ドームに行った",
  //     category: "AI分析結果"
  //   }
  // ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-br from-blue-50 to-indigo-50 shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button variant="ghost" size="sm" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              戻る
            </Button>
            
            <h1 className="text-2xl font-bold text-gray-900 absolute left-1/2 transform -translate-x-1/2">
              メンバープロフィール
            </h1>
            <div className="w-32">
              {/* 右側のスペースを確保して中央配置を維持 */}
            </div>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {error && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-yellow-800 text-sm">{error}</p>
            </div>
          )}
          
          {/* プロフィールヘッダー */}
          <Card className="mb-8">
            <CardContent className="p-8">
              <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
                <Avatar className="h-24 w-24">
                  <AvatarImage 
                    src={getAvatarUrl(profile.avatar_url, profile.display_name, 96)} 
                    alt={profile.display_name} 
                  />
                  <AvatarFallback className="text-2xl">
                    {profile.display_name.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                
                <div className="flex-1 text-center md:text-left">
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    {profile.display_name}
                  </h2>
                  <p className="text-gray-600 mb-4">{profile.email}</p>
                  
                  <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                    {profile.department && (
                      <Badge variant="outline" className={`flex items-center gap-1 ${getDepartmentColor(profile.department)}`}>
                        <Building2 className="h-4 w-4" />
                        {profile.department}
                      </Badge>
                    )}
                    {profile.join_date && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        入社: {formatDate(profile.join_date)}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 基本情報 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  基本情報
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">出身地</label>
                  <p className="text-gray-900">{profile.hometown || "未設定"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">現在の居住地</label>
                  <p className="text-gray-900">{profile.residence || "未設定"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">誕生日</label>
                  <p className="text-gray-900">{formatDate(profile.birth_date)}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="h-5 w-5" />
                  趣味・活動
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">趣味</label>
                  <p className="text-gray-900">{profile.hobbies || "未設定"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">学生時代の活動</label>
                  <p className="text-gray-900">{profile.student_activities || "未設定"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">休日の過ごし方</label>
                  <p className="text-gray-900">{profile.holiday_activities || "未設定"}</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 好み・価値観 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Music className="h-5 w-5" />
                  好み
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">好きな食べ物</label>
                  <p className="text-gray-900">{profile.favorite_food || "未設定"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">好きなメディア</label>
                  <p className="text-gray-900">{profile.favorite_media || "未設定"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">好きな音楽</label>
                  <p className="text-gray-900">{profile.favorite_music || "未設定"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">ペット・推し</label>
                  <p className="text-gray-900">{profile.pets_oshi || "未設定"}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  価値観・目標
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">尊敬する人</label>
                  <p className="text-gray-900">{profile.respected_person || "未設定"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">座右の銘</label>
                  <p className="text-gray-900">{profile.motto || "未設定"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">将来の目標</label>
                  <p className="text-gray-900">{profile.future_goals || "未設定"}</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* AI分析フィードバック欄（コメントアウト） */}
          {/* <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">AI分析フィードバック</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {feedbackData.map((feedback, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-2">
                      {feedback.icon}
                      <CardTitle className="text-sm">{feedback.title}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm text-gray-700 mb-3">{feedback.content}</p>
                    <div className="text-xs text-blue-600 font-medium">
                      {feedback.category}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div> */}

          {/* 承認されたフィードバック一覧 */}
          <div className="mb-8">
            <MemberFeedbackList 
              memberId={memberId} 
              memberName={profile.display_name}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
