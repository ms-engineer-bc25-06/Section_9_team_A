"use client";

// チームメンバー一覧
import OrganizationMemberList from "@/components/team/OrganizationMemberList"
import { Button } from "@/components/ui/Button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function TeamPage() {
  // ダミーデータ（実際の実装ではAPIから取得）
  const mockMembers = [
    {
      id: "1",
      user_id: "user1",
      organization_id: "org1",
      role: "admin",
      status: "active",
      joined_at: "2024-01-01T00:00:00Z",
      user: {
        display_name: "管理者ユーザー",
        email: "admin@example.com",
        avatar_url: undefined
      }
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          {/* 戻るボタンを左寄せに配置 */}
          <div className="flex justify-start mb-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                ダッシュボードへ戻る
              </Button>
            </Link>
          </div>
          {/* タイトルを中央に配置 */}
          <div className="flex justify-center">
            <h1 className="text-2xl font-bold text-gray-900">チームメンバー 一覧</h1>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-8">
        <OrganizationMemberList 
          members={mockMembers}
          onAddMember={() => console.log("メンバー追加")}
          onEditMember={(id) => console.log("メンバー編集:", id)}
          onRemoveMember={(id) => console.log("メンバー削除:", id)}
          onViewProfile={(id) => console.log("プロフィール表示:", id)}
          currentUserRole="admin"
        />
      </main>
    </div>
  )
}
