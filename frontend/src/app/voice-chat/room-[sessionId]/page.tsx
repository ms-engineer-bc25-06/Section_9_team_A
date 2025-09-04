/**
 * 動的音声通話ルームページ
 */
"use client"

import { VoiceCallRoom } from "@/components/voice-chat/VoiceCallRoom"
import { Button } from "@/components/ui/Button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useParams } from "next/navigation"

export default function DynamicVoiceCallRoomPage() {
  const params = useParams()
  const sessionId = params.sessionId as string

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-br from-blue-50 to-indigo-50 shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/voice-chat">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                雑談ルームに戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900 absolute left-1/2 transform -translate-x-1/2">
              音声通話ルーム: {sessionId}
            </h1>
            <div className="w-32">
              {/* 右側のスペースを確保して中央配置を維持 */}
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <VoiceCallRoom roomId={sessionId} />
      </main>
    </div>
  )
}
