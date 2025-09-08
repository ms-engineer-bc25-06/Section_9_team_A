"use client"
import { ProfileEditForm } from "@/components/profile/ProfileEditForm"
import { Button } from "@/components/ui/Button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function ProfileEditPage() {

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
        <ProfileEditForm />
      </main>
    </div>
  )
}

