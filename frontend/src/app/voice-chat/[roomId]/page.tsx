// 音声チャットルーム画面
"use client"

import { ActiveVoiceChat } from "@/components/voice-chat/ActiveVoiceChat"
import { Button } from "@/components/ui/Button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useAuth } from "@/components/auth/AuthProvider"
import { useEffect } from "react"

interface Props {
  params: {
    roomId: string
  }
}

export default function VoiceChatRoomPage({ params }: Props) {
  const { isAuthenticated, isLoading, redirectToLogin } = useAuth()

  // 認証状態の確認
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      console.log("認証されていません。ログインページにリダイレクトします。")
      redirectToLogin()
    }
  }, [isAuthenticated, isLoading, redirectToLogin])

  // 認証状態の読み込み中
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-4"></div>
          <p>認証状態を確認中...</p>
        </div>
      </div>
    )
  }

  // 認証されていない場合は何も表示しない（リダイレクト中）
  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/voice-chat">
              <Button variant="ghost" size="sm" className="text-white hover:bg-gray-700">
                <ArrowLeft className="h-4 w-4 mr-2" />
                雑談ルームへ戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold">音声通話中... (Room: {params.roomId})</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-4">
        <ActiveVoiceChat roomId={params.roomId} />
      </main>
    </div>
  )
}
