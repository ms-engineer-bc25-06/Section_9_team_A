// 管理者が新規ユーザーを追加できる画面
import { AddUsersForm } from "@/components/admin/AddUsersForm"
import { Button } from "@/components/ui/Button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function AddUsersPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/admin/billing">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                決済管理へ戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">使用人数追加</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <AddUsersForm />
      </main>
    </div>
  )
}
