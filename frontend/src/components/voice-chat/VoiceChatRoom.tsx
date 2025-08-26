// プレゼンテーション用：雑談ルームUI（モックデータ使用）
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Play, Users, Lightbulb, Mic, Settings, TrendingUp } from "lucide-react"
import { useRouter } from "next/navigation"
import { AudioEnhancement } from "./AudioEnhancement"
import { mockParticipants, mockTopics } from "@/data/mockVoiceChatData"

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
    // プレゼンテーション用：モックデータで音声処理をシミュレート
    alert("音声品質向上処理が完了しました！")
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "bg-green-500"
      case "away":
        return "bg-yellow-500"
      case "offline":
        return "bg-gray-400"
      default:
        return "bg-gray-400"
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "online":
        return "オンライン"
      case "away":
        return "離席中"
      case "offline":
        return "オフライン"
      default:
        return "不明"
    }
  }

  return (
    <div className="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>現在参加中のメンバー ({mockParticipants.length}人)</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockParticipants.map((participant) => (
              <div key={participant.id} className="flex items-center space-x-3">
                <div className="relative">
                  <Avatar>
                    <AvatarImage src={participant.avatar_url} />
                    <AvatarFallback>{participant.name.slice(0, 2)}</AvatarFallback>
                  </Avatar>
                  <div
                    className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${getStatusColor(participant.status)}`}
                  />
                  {participant.isSpeaking && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-blue-500 rounded-full animate-pulse" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="font-medium">{participant.name}</p>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="text-xs">
                      {getStatusText(participant.status)}
                    </Badge>
                    {participant.department && (
                      <Badge variant="outline" className="text-xs">
                        {participant.department}
                      </Badge>
                    )}
                  </div>
                  {participant.isSpeaking && (
                    <div className="flex items-center gap-1 mt-1">
                      <Mic className="h-3 w-3 text-blue-600" />
                      <span className="text-xs text-blue-600">話し中</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="space-y-3 mt-6">
            <Button onClick={startVoiceChat} className="w-full" size="lg" type="button">
              <Play className="h-5 w-5 mr-2" />
              雑談ルームを開始する
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
            <span>AI提案トピック</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockTopics.slice(0, 6).map((topic, index) => (
              <Button
                key={index}
                variant={selectedTopic === topic.text ? "default" : "outline"}
                className="w-full justify-start text-left h-auto py-3 px-4"
                onClick={() => setSelectedTopic(topic.text)}
                type="button"
              >
                <div className="flex-1 text-left">
                  <div className="font-medium">{topic.text}</div>
                  <div className="text-xs text-gray-500 mt-1">{topic.description}</div>
                </div>
                {topic.popularity && (
                  <div className="flex items-center gap-1 text-xs text-gray-600">
                    <TrendingUp className="h-3 w-3" />
                    {topic.popularity}%
                  </div>
                )}
              </Button>
            ))}
          </div>

          {selectedTopic && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-700">
                選択されたテーマ: <strong>{selectedTopic}</strong>
              </p>
              <p className="text-xs text-blue-600 mt-1">
                このテーマで雑談を始めましょう！
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
