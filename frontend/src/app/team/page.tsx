"use client";
import { useState, useEffect } from "react";
import DepartmentMemberList from "@/components/team/DepartmentMemberList";
import { Button } from "@/components/ui/Button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getTeamMembers, DepartmentMember } from "@/lib/api/teamMembers";

export default function TeamPage() {
  const [members, setMembers] = useState<DepartmentMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchMembers();
  }, []);

  const fetchMembers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const apiMembers = await getTeamMembers();
      setMembers(apiMembers);
      
    } catch (err: any) {
      console.error("Failed to fetch members:", err);
      
      // エラーの種類に応じて適切なメッセージを表示
      if (err.message?.includes('403') || err.message?.includes('管理者権限')) {
        setError("アクセス権限がありません。管理者に連絡してください。");
      } else if (err.message?.includes('401') || err.message?.includes('認証')) {
        setError("ログインが必要です。再度ログインしてください。");
      } else {
        setError("メンバー一覧の取得に失敗しました");
      }
      
      setMembers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewProfile = (memberId: string) => {
    router.push(`/profile/${memberId}`);
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

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-br from-blue-50 to-indigo-50 shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                ダッシュボードへ戻る
              </Button>
            </Link>
            
            <h1 className="text-2xl font-bold text-gray-900 absolute left-1/2 transform -translate-x-1/2">
              メンバー一覧
            </h1>
            <div className="w-32">
              {/* 右側のスペースを確保して中央配置を維持 */}
            </div>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <p className="text-red-800 text-sm font-medium">{error}</p>
            </div>
            {error.includes('アクセス権限') && (
              <p className="text-red-700 text-sm mt-2">
                チームメンバー一覧を表示するには、プロフィール（名前・部署）を設定する必要があります。
              </p>
            )}
          </div>
        )}
        
        {!error && members.length === 0 && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <p className="text-yellow-800 text-sm font-medium">メンバーが見つかりません</p>
            </div>
            <p className="text-yellow-700 text-sm mt-2">
              現在、表示できるメンバーがいません。プロフィール情報が設定されているメンバーのみ表示されます。
            </p>
          </div>
        )}
        
        <DepartmentMemberList 
          members={members}
          onViewProfile={handleViewProfile}
        />
      </main>
    </div>
  )
}
