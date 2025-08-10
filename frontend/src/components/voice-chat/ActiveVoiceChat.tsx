"use client"

import { useEffect, useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Mic, MicOff, Volume2, VolumeX, Phone, Users } from "lucide-react"
import { useRouter } from "next/navigation"
import { useVoiceChat } from "@/hooks/useVoiceChat"
import { AudioCapture } from "./AudioCapture"

interface Props {
  roomId: string
}

export function ActiveVoiceChat({ roomId }: Props) {
  const [isMuted, setIsMuted] = useState(false)
  const [isSpeakerOn, setIsSpeakerOn] = useState(true)
  const [duration, setDuration] = useState(0)
  const router = useRouter()
  const sessionId = useMemo(() => roomId, [roomId])
  const { isConnected, participants, join, leave } = useVoiceChat(sessionId)

  // 音声データの処理
  const handleAudioData = (audioBlob: Blob) => {
    console.log('音声データ受信:', audioBlob);
    // TODO: WebSocket経由で音声データを送信
    // TODO: 音声品質の確認
  };

  // 録音状態の変更
  const handleRecordingStateChange = (isRecording: boolean) => {
    console.log('録音状態変更:', isRecording);
    // TODO: 参加者に録音状態を通知
  };

  useEffect(() => {
    if (isConnected) {
      join()
    }
  }, [isConnected, join])

  useEffect(() => {
    const timer = setInterval(() => setDuration((prev) => prev + 1), 1000)
    return () => clearInterval(timer)
  }, [])

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const handleEndCall = () => {
    try {
      leave()
    } finally {
      router.push("/voice-chat")
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <div className="text-4xl font-bold mb-2">{formatDuration(duration)}</div>
        <Badge variant="secondary" className="text-lg px-4 py-2">
          {isConnected ? "接続中" : "接続中..."} - Room {roomId}
        </Badge>
      </div>

      <Card className="bg-gray-800 border-gray-700 mb-8">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-white">
            <Users className="h-5 w-5" />
            <span>参加中のメンバー</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {participants.map((p: any) => (
              <div key={p.user_id ?? p.id} className="text-center">
                <div className="relative mb-3">
                  <Avatar className="h-20 w-20 mx-auto">
                    <AvatarImage src={p.avatar_url || "/placeholder.svg?height=80&width=80"} />
                    <AvatarFallback className="text-xl">
                      {(p.display_name || p.username || "U").slice(0, 2)}
                    </AvatarFallback>
                  </Avatar>
                  {p.is_active && (
                    <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-gray-800 flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                    </div>
                  )}
                  {p.is_muted && (
                    <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full border-2 border-gray-800 flex items-center justify-center">
                      <MicOff className="h-3 w-3 text-white" />
                    </div>
                  )}
                </div>
                <p className="text-white font-medium">{p.display_name || p.username || "参加者"}</p>
                <div className="flex items-center justify-center gap-2 mt-1">
                  {typeof p.is_active === "boolean" && (
                    <Badge variant={p.is_active ? "default" : "secondary"} className="text-xs">
                      {p.is_active ? "発話中" : "待機中"}
                    </Badge>
                  )}
                  {p.role && (
                    <Badge variant="secondary" className="text-xs">{p.role}</Badge>
                  )}
                </div>
              </div>
            ))}
            {participants.length === 0 && (
              <div className="text-sm text-gray-300">参加者情報を待機中...</div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 音声キャプチャ機能 */}
      <Card className="bg-gray-800 border-gray-700 mb-8">
        <CardHeader>
          <CardTitle className="text-white">音声キャプチャ</CardTitle>
        </CardHeader>
        <CardContent>
          <AudioCapture
            onAudioData={handleAudioData}
            onRecordingStateChange={handleRecordingStateChange}
          />
        </CardContent>
      </Card>

      <div className="flex justify-center space-x-4">
        <Button
          variant={isMuted ? "destructive" : "secondary"}
          size="lg"
          className="rounded-full w-16 h-16"
          onClick={() => setIsMuted(!isMuted)}
          type="button"
        >
          {isMuted ? <MicOff className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
        </Button>

        <Button
          variant={isSpeakerOn ? "secondary" : "outline"}
          size="lg"
          className="rounded-full w-16 h-16"
          onClick={() => setIsSpeakerOn(!isSpeakerOn)}
          type="button"
        >
          {isSpeakerOn ? <Volume2 className="h-6 w-6" /> : <VolumeX className="h-6 w-6" />}
        </Button>

        <Button
          variant="destructive"
          size="lg"
          className="rounded-full w-16 h-16"
          onClick={handleEndCall}
          type="button"
        >
          <Phone className="h-6 w-6" />
        </Button>
      </div>
    </div>
  )
}
