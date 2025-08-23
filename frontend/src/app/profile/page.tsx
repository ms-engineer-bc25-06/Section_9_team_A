// プロフィール表示ページ
import { ProfileView } from "@/components/profile/ProfileView"
import { Button } from "@/components/ui/Button"
import { ArrowLeft, Edit } from "lucide-react"
import Link from "next/link"

export default function ProfilePage() {
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
              マイプロフィール
            </h1>
            <Link href="/profile/edit">
              <Button>
                <Edit className="h-4 w-4 mr-2" />
                編集画面へ
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <ProfileView />
      </main>
    </div>
  )
}
