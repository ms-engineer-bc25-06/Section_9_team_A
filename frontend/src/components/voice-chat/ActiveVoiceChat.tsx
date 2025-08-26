"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Phone, Users, Lightbulb, TrendingUp } from "lucide-react"
import { useRouter } from "next/navigation"
import { mockTopics, mockVoiceSession } from "@/data/mockVoiceChatData"

interface Props {
  roomId: string
}

export function ActiveVoiceChat({ roomId }: Props) {
  const [duration, setDuration] = useState(0)
  const [currentTopic, setCurrentTopic] = useState<{ text: string; category: string; description: string }>({ text: '', category: '', description: '' })
  const router = useRouter()
  
  // プレゼンテーション用：モックデータから初期トピックを設定
  useEffect(() => {
    setCurrentTopic(mockTopics[1]) // 週末の過ごし方
  }, [])
  
  // プレゼンテーション用：モックデータで参加者情報を取得
  const mockParticipants = mockVoiceSession.participants

  // プレゼンテーション用：モックデータでトークテーマを取得
  const availableTopics = mockTopics

  // プレゼンテーション用：モックデータで現在のトピックを設定
  const currentTopicData = currentTopic || availableTopics[1]

  // プレゼンテーション用：モックデータでセッション時間をシミュレート
  useEffect(() => {
    const interval = setInterval(() => {
      setDuration(prev => prev + 1)
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const handleLeaveRoom = () => {
    // プレゼンテーション用：ルーム退出をシミュレート
    if (confirm("雑談ルームを退出しますか？")) {
      alert("雑談ルームを退出しました！")
      router.push("/voice-chat")
    }
  }

  const handleTopicChange = (topic: { text: string; category: string; description: string }) => {
    // プレゼンテーション用：トピック変更をシミュレート
    setCurrentTopic(topic)
    alert(`トピックを「${topic.text}」に変更しました！`)
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
    <div className="space-y-6">
      {/* ヘッダー情報 */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">雑談ルーム #{roomId}</h2>
          <p className="text-gray-300">現在のトピック: {currentTopicData.text}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{formatDuration(duration)}</div>
            <div className="text-sm text-gray-400">通話時間</div>
          </div>
          <Button variant="outline" onClick={handleLeaveRoom} className="text-white border-white hover:bg-white hover:text-gray-900">
            <Phone className="h-4 w-4 mr-2" />
            退出
          </Button>
        </div>
      </div>

      {/* 接続状態表示 */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Users className="h-5 w-5" />
            接続状態
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Badge variant="default" className="bg-green-600">WebSocket: 接続済み</Badge>
            <Badge variant="default" className="bg-green-600">WebRTC: 接続済み</Badge>
            <Badge variant="default" className="bg-green-600">音声: アクティブ</Badge>
            <Badge variant="outline" className="text-white">参加者: {mockParticipants.length}人</Badge>
          </div>
        </CardContent>
      </Card>

      {/* メインコンテンツ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 参加者リスト */}
        <div className="lg:col-span-1">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Users className="h-5 w-5" />
                参加者 ({mockParticipants.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockParticipants.map((participant) => (
                  <div key={participant.id} className="flex items-center gap-3 p-3 bg-gray-700 rounded-lg">
                    <div className="relative">
                      <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center text-white font-medium">
                        {participant.name.slice(0, 2)}
                      </div>
                      <div
                        className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-gray-800 ${getStatusColor(participant.status)}`}
                      />
                      {participant.isSpeaking && (
                        <div className="absolute -top-1 -right-1 w-4 h-4 bg-blue-500 rounded-full animate-pulse" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-white truncate">{participant.name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="secondary" className="text-xs">
                          {getStatusText(participant.status)}
                        </Badge>
                        {participant.department && (
                          <Badge variant="outline" className="text-xs text-gray-300">
                            {participant.department}
                          </Badge>
                        )}
                      </div>
                      {participant.isSpeaking && (
                        <div className="flex items-center gap-1 mt-1">
                          <span className="text-xs text-blue-400">話し中</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* トピック選択（大きく目立たせる） */}
        <div className="lg:col-span-2">
          <Card className="bg-gradient-to-br from-blue-900 to-indigo-900 border-blue-600 shadow-lg">
            <CardHeader className="text-center pb-6">
              <CardTitle className="text-white text-2xl flex items-center justify-center gap-3">
                <Lightbulb className="h-8 w-8 text-yellow-400" />
                トピック選択
              </CardTitle>
              <p className="text-blue-200 text-lg">現在のトピック: <span className="font-bold text-white">{currentTopicData.text}</span></p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {availableTopics.map((topic, index) => (
                  <Button
                    key={index}
                    variant={currentTopic?.text === topic.text ? "default" : "outline"}
                    onClick={() => handleTopicChange(topic)}
                    className={`justify-start text-left h-auto py-4 px-6 text-lg transition-all duration-200 ${
                      currentTopic?.text === topic.text 
                        ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg scale-105' 
                        : 'bg-gray-800 hover:bg-gray-700 text-white border-gray-600 hover:border-gray-500'
                    }`}
                  >
                    <div className="text-left w-full">
                      <div className="font-semibold text-lg mb-2">{topic.text}</div>
                      <div className="text-sm text-gray-300">{topic.description}</div>
                      {topic.popularity && (
                        <div className="flex items-center gap-2 mt-2">
                          <TrendingUp className="h-4 w-4 text-blue-400" />
                          <span className="text-xs text-blue-400">人気度: {topic.popularity}%</span>
                        </div>
                      )}
                    </div>
                  </Button>
                ))}
              </div>
              
              {/* 現在選択されているトピックの詳細表示 */}
              {currentTopic && (
                <div className="bg-blue-800/50 border border-blue-600 rounded-lg p-6 text-center">
                  <h3 className="text-xl font-bold text-white mb-3">現在のトピック</h3>
                  <div className="bg-blue-700 rounded-lg p-4">
                    <h4 className="text-lg font-semibold text-white mb-2">{currentTopic.text}</h4>
                    <p className="text-blue-200 mb-3">{currentTopic.description}</p>
                                          <div className="flex items-center justify-center gap-4">
                        <Badge variant="outline" className="text-blue-300 border-blue-400">
                          カテゴリ: {currentTopic.category}
                        </Badge>
                        {(currentTopic as any).popularity && (
                          <Badge variant="default" className="bg-yellow-600">
                            人気度: {(currentTopic as any).popularity}%
                          </Badge>
                        )}
                      </div>
                  </div>
                  <p className="text-blue-200 text-sm mt-3">
                    このトピックで雑談を始めましょう！
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
