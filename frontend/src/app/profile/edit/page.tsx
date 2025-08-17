// プロフィール編集ページ
import { ProfileEditForm } from "@/components/profile/ProfileEditForm"
import { FeedbackApprovalManager } from "@/components/profile/FeedbackApprovalManager"
import { Button } from "@/components/ui/Button"
import { ArrowLeft, User, FileText } from "lucide-react"
import Link from "next/link"
import { useState } from "react"

export default function ProfileEditPage() {
  const [activeTab, setActiveTab] = useState<'profile' | 'feedback'>('profile')

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/profile">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                閲覧画面へ
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">マイプロフィール管理</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* タブナビゲーション */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('profile')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'profile'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <User className="h-4 w-4 inline mr-2" />
                プロフィール編集
              </button>
              <button
                onClick={() => setActiveTab('feedback')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'feedback'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <FileText className="h-4 w-4 inline mr-2" />
                フィードバック承認管理
              </button>
            </nav>
          </div>
        </div>

        {/* タブコンテンツ */}
        {activeTab === 'profile' && <ProfileEditForm />}
        {activeTab === 'feedback' && <FeedbackApprovalManager />}
      </main>
    </div>
  )
}

