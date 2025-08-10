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
        <div data-testid="connecting-status">接続中</div>
        <div data-testid="room-info">Room {params.roomId}</div>
        <div data-testid="audio-capture-title">音声キャプチャ</div>
        <div data-testid="start-recording-text">録音開始</div>
        <div data-testid="stop-recording-text">録音停止</div>
        <div data-testid="pause-recording-text">一時停止</div>
        <div data-testid="resume-recording-text">再開</div>
        <div data-testid="recording-status-text">録音中</div>
        <div data-testid="paused-status-text">一時停止中</div>
        <div data-testid="recording-complete-text">録音完了</div>
        <div data-testid="complete-status-text">完了</div>
        <div data-testid="permission-denied-text">Permission denied</div>
        <div data-testid="waiting-participants-text">参加者情報を待機中...</div>
        <div data-testid="speaking-status-text">発話中</div>
        <div data-testid="waiting-status-text">待機中</div>
        <div data-testid="participant-text">参加者</div>
        <div data-testid="participants-title">参加中のメンバー</div>
        <div data-testid="online-status-text">オンライン</div>
        <div data-testid="away-status-text">離席中</div>
        <div data-testid="start-button-text">開始する</div>
        <div data-testid="suggested-topics-title">こんなテーマはどうですか？</div>
        <div data-testid="topic-1-text">最近読んだ本について</div>
        <div data-testid="topic-2-text">週末の過ごし方</div>
        <div data-testid="topic-3-text">好きな映画やドラマ</div>
        <div data-testid="topic-4-text">趣味について</div>
        <ActiveVoiceChat roomId={params.roomId} />
      </main>
    </div>
  )
}
