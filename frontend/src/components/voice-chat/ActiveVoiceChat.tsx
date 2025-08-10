"use client"

import { useEffect, useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Mic, MicOff, Volume2, VolumeX, Phone, Users, MessageCircle } from "lucide-react"
import { useRouter } from "next/navigation"
import { useVoiceChat } from "@/hooks/useVoiceChat"
import { AudioCapture } from "./AudioCapture"

interface Props {
  roomId: string
}

// トークテーマの定義
const TALK_TOPICS = [
  {
    text: "最近読んだ本について",
    category: "読書",
    description: "お気に入りの一冊を共有しましょう"
  },
  {
    text: "週末の過ごし方",
    category: "ライフスタイル", 
    description: "リフレッシュ方法を教えてください"
  },
  {
    text: "好きな映画やドラマ",
    category: "エンターテイメント",
    description: "感動した作品の話を聞かせて"
  },
  {
    text: "趣味について",
    category: "趣味",
    description: "熱中していることを教えてください"
  },
  {
    text: "旅行の思い出",
    category: "旅行",
    description: "印象に残った旅のエピソードを"
  },
  {
    text: "おすすめのレストラン",
    category: "グルメ",
    description: "隠れた名店の情報を交換しましょう"
  },
  {
    text: "最近ハマっていること",
    category: "トレンド",
    description: "新しい発見や興味を共有"
  },
  {
    text: "将来の夢や目標",
    category: "キャリア",
    description: "それぞれの展望を聞かせてください"
  }
]

// モック参加者データ（実際の実装ではAPIから取得）
const MOCK_PARTICIPANTS = [
  {
    id: "1",
    display_name: "田中太郎",
    username: "tanaka_taro",
    avatar_url: "/api/avatars/1",
    is_active: true,
    is_muted: false,
    role: "ホスト",
    status: "online"
  },
  {
    id: "2", 
    display_name: "佐藤花子",
    username: "sato_hanako",
    avatar_url: "/api/avatars/2",
    is_active: false,
    is_muted: true,
    role: "参加者",
    status: "online"
  },
  {
    id: "3",
    display_name: "鈴木一郎",
    username: "suzuki_ichiro", 
    avatar_url: "/api/avatars/3",
    is_active: false,
    is_muted: false,
    role: "参加者",
    status: "away"
  }
]

export function ActiveVoiceChat({ roomId }: Props) {
  const [isMuted, setIsMuted] = useState(false)
  const [isSpeakerOn, setIsSpeakerOn] = useState(true)
  const [duration, setDuration] = useState(0)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'error'>('connecting')
  const [currentTopic, setCurrentTopic] = useState<{ text: string; category: string; description: string }>({ text: '', category: '', description: '' })
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

  // 接続状態の管理
  useEffect(() => {
    if (isConnected) {
      setConnectionStatus('connected')
      join()
    } else {
      setConnectionStatus('connecting')
    }
  }, [isConnected, join])

  // 接続タイムアウト処理
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (connectionStatus === 'connecting') {
        setConnectionStatus('error')
      }
    }, 10000) // 10秒でタイムアウト

    return () => clearTimeout(timeout)
  }, [connectionStatus])

  // トークテーマのランダム選択
  useEffect(() => {
    const randomTopic = TALK_TOPICS[Math.floor(Math.random() * TALK_TOPICS.length)]
    setCurrentTopic(randomTopic)
  }, [])

  // 新しいトークテーマを選択
  const selectNewTopic = () => {
    const currentIndex = TALK_TOPICS.findIndex(topic => topic.text === currentTopic.text)
    let newIndex
    do {
      newIndex = Math.floor(Math.random() * TALK_TOPICS.length)
    } while (newIndex === currentIndex && TALK_TOPICS.length > 1)
    
    setCurrentTopic(TALK_TOPICS[newIndex])
  }

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

  // 接続状態に応じたステータス表示
  const renderConnectionStatus = () => {
    switch (connectionStatus) {
      case 'connecting':
        return (
          <div className="text-center mb-8">
            <div className="text-4xl font-bold mb-2">{formatDuration(duration)}</div>
            <Badge variant="secondary" className="text-lg px-4 py-2 animate-pulse">
              接続中... - Room {roomId}
            </Badge>
          </div>
        )
      case 'connected':
        return (
          <div className="text-center mb-8">
            <div className="text-4xl font-bold mb-2">{formatDuration(duration)}</div>
            <Badge variant="default" className="text-lg px-4 py-2 bg-green-600">
              接続完了 - Room {roomId}
            </Badge>
          </div>
        )
      case 'error':
        return (
          <div className="text-center mb-8">
            <div className="text-4xl font-bold mb-2">{formatDuration(duration)}</div>
            <Badge variant="destructive" className="text-lg px-4 py-2">
              接続エラー - Room {roomId}
            </Badge>
          </div>
        )
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {renderConnectionStatus()}

      {/* トークテーマ表示 */}
      {connectionStatus === 'connected' && currentTopic && (
        <Card className="bg-gradient-to-r from-blue-900 to-purple-900 border-blue-700 mb-8">
          <CardHeader>
            <CardTitle className="flex items-center justify-between text-white">
              <div className="flex items-center space-x-2">
                <MessageCircle className="h-5 w-5 text-blue-300" />
                <span>今日のトークテーマ</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={selectNewTopic}
                className="border-blue-300 text-blue-300 hover:bg-blue-800"
              >
                別のテーマ
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="mb-3">
                <Badge variant="outline" className="border-blue-300 text-blue-300 mb-2">
                  {currentTopic.category}
                </Badge>
              </div>
              <p className="text-2xl font-bold text-blue-100 mb-3">
                「{currentTopic.text}」
              </p>
              <p className="text-sm text-blue-300 mb-4">
                {currentTopic.description}
              </p>
              <div className="flex justify-center space-x-4 text-xs text-blue-400">
                <span>💡 話しやすい話題</span>
                <span>🎯 共通の興味を見つけよう</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 参加者リスト */}
      <Card className="bg-gray-800 border-gray-700 mb-8">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-white">
            <Users className="h-5 w-5" />
            <span>参加中のメンバー</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6" data-testid="participants-list">
            {MOCK_PARTICIPANTS.map((p) => (
              <div key={p.id} className="text-center">
                <div className="relative mb-3">
                  <Avatar className="h-20 w-20 mx-auto">
                    <AvatarImage src={p.avatar_url} />
                    <AvatarFallback className="text-xl bg-gray-600">
                      {(p.display_name || p.username || "U").slice(0, 2)}
                    </AvatarFallback>
                  </Avatar>
                  {/* オンライン/オフライン状態 */}
                  <div className={`absolute -bottom-1 -right-1 w-6 h-6 rounded-full border-2 border-gray-800 flex items-center justify-center ${
                    p.status === 'online' ? 'bg-green-500' : 'bg-gray-400'
                  }`}>
                    <div className={`w-2 h-2 rounded-full ${
                      p.status === 'online' ? 'bg-white animate-pulse' : 'bg-gray-200'
                    }`} />
                  </div>
                  {/* ミュート状態 */}
                  {p.is_muted && (
                    <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full border-2 border-gray-800 flex items-center justify-center">
                      <MicOff className="h-3 w-3 text-white" />
                    </div>
                  )}
                </div>
                <p className="text-white font-medium">{p.display_name}</p>
                <div className="flex items-center justify-center gap-2 mt-1">
                  <Badge variant={p.is_active ? "default" : "secondary"} className="text-xs">
                    {p.is_active ? "発話中" : "待機中"}
                  </Badge>
                  <Badge variant="outline" className="text-xs border-blue-500 text-blue-300">
                    {p.role}
                  </Badge>
                </div>
                <div className="mt-1">
                  <Badge variant="secondary" className="text-xs">
                    {p.status === 'online' ? 'オンライン' : '離席中'}
                  </Badge>
                </div>
              </div>
            ))}
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

      {/* 音声コントロール */}
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
