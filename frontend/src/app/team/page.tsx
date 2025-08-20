// チームメンバー一覧
import { OrganizationMemberList } from "@/components/team/OrganizationMemberList"
import { Button } from "@/components/ui/Button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function TeamPage() {
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
        <OrganizationMemberList />
      </main>
    </div>
  )
}
