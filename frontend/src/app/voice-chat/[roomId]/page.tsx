// 音声チャットルーム画面
"use client"

import { ActiveVoiceChat } from "@/components/voice-chat/ActiveVoiceChat"
import { Button } from "@/components/ui/Button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

interface Props {
  params: {
    roomId: string
  }
}

export default function VoiceChatRoomPage({ params }: Props) {
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
