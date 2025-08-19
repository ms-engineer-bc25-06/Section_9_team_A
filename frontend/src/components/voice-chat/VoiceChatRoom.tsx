// FIXME （雑談ルームUI）
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Play, Users, Lightbulb, Mic, Settings } from "lucide-react"
import { useRouter } from "next/navigation"
import { AudioEnhancement } from "./AudioEnhancement"

const mockParticipants = [
  { id: 1, name: "田中太郎", status: "online" },
  { id: 2, name: "佐藤花子", status: "online" },
  { id: 3, name: "鈴木一郎", status: "away" },
]

const suggestedTopics = [
  "最近読んだ本について",
  "週末の過ごし方",
  "好きな映画やドラマ",
  "趣味について",
  "おすすめのレストラン",
]

export function VoiceChatRoom() {
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null)
  const [showAudioEnhancement, setShowAudioEnhancement] = useState(false)
  const router = useRouter()

  const startVoiceChat = () => {
    console.log("Starting voice chat...") // デバッグ用
    try {
      router.push("/voice-chat/room-1")
    } catch (error) {
      console.error("Navigation error:", error)
    }
  }

  const handleEnhancedAudio = (audioBlob: Blob) => {
    console.log("Enhanced audio received:", audioBlob)
    // ここで音声チャットに処理済み音声を送信する処理を追加
  }

  return (
    <div className="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>現在参加中のメンバー</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockParticipants.map((participant) => (
              <div key={participant.id} className="flex items-center space-x-3">
                <div className="relative">
                  <Avatar>
                    <AvatarImage src={`/placeholder.svg?height=40&width=40&query=${participant.name}`} />
                    <AvatarFallback>{participant.name.slice(0, 2)}</AvatarFallback>
                  </Avatar>
                  <div
                    className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
                      participant.status === "online" ? "bg-green-500" : "bg-yellow-500"
                    }`}
                  />
                </div>
                <div className="flex-1">
                  <p className="font-medium">{participant.name}</p>
                  <Badge variant="secondary" className="text-xs">
                    {participant.status === "online" ? "オンライン" : "離席中"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>

          <div className="space-y-3 mt-6">
            <Button onClick={startVoiceChat} className="w-full" size="lg" type="button">
              <Play className="h-5 w-5 mr-2" />
              開始する
            </Button>
            
            <Button 
              onClick={() => setShowAudioEnhancement(!showAudioEnhancement)} 
              variant="outline" 
              className="w-full" 
              type="button"
            >
              <Settings className="h-5 w-5 mr-2" />
              {showAudioEnhancement ? '音声品質向上を隠す' : '音声品質向上を表示'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Lightbulb className="h-5 w-5" />
            <span>こんなテーマはどうですか？</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {suggestedTopics.map((topic, index) => (
              <Button
                key={index}
                variant={selectedTopic === topic ? "default" : "outline"}
                className="w-full justify-start text-left h-auto py-3 px-4"
                onClick={() => setSelectedTopic(topic)}
                type="button"
              >
                {topic}
              </Button>
            ))}
          </div>

          {selectedTopic && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-700">
                選択されたテーマ: <strong>{selectedTopic}</strong>
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 音声品質向上セクション */}
      {showAudioEnhancement && (
        <div className="lg:col-span-2">
          <AudioEnhancement 
            onEnhancedAudio={handleEnhancedAudio}
            className="mt-6"
          />
        </div>
      )}
    </div>
  )
}
