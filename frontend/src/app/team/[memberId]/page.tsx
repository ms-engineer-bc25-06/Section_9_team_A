// チームメンバー詳細画面
import { MemberDetail } from "@/components/team/MemberDetail"
import { Button } from "@/components/ui/Button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

interface Props {
  params: {
    memberId: string
  }
}

export default function MemberDetailPage({ params }: Props) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          {/* 戻るボタンを左寄せに配置 */}
          <div className="flex justify-start mb-4">
            <Link href="/team">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                一覧画面へ戻る
              </Button>
            </Link>
            </div>
          {/* タイトルを中央に配置 */}
          <div className="flex justify-center">
            <h1 className="text-2xl font-bold text-gray-900">メンバー詳細</h1>
          </div>
        </div>
      </header>
            
      <main className="container mx-auto px-4 py-8">
        <MemberDetail memberId={params.memberId} />
      </main>
    </div>
  )
}
