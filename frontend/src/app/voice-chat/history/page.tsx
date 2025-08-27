// プレゼンテーション用：音声チャット履歴ページ（モックデータ使用）
"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Input } from "@/components/ui/Input"
import { ArrowLeft, Search, Play, Download, Trash2, Calendar, Users, Clock, MessageSquare } from "lucide-react"
import Link from "next/link"
import { mockVoiceChatHistory } from "@/data/mockVoiceChatData"

interface VoiceSession {
  id: string
  title: string
  date: string
  duration: string
  participants: number
  status: "completed" | "processing" | "failed"
  topic: string
}

export default function VoiceChatHistoryPage() {
  const [sessions, setSessions] = useState<VoiceSession[]>([])
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    // プレゼンテーション用：モックデータを設定
    const formattedSessions: VoiceSession[] = mockVoiceChatHistory.map(session => ({
      ...session,
      status: session.status as "completed" | "processing" | "failed"
    }))
    setSessions(formattedSessions)
  }, [])

  const filteredSessions = sessions.filter(session =>
    session.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    session.topic.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge variant="default">完了</Badge>
      case "processing":
        return <Badge variant="secondary">処理中</Badge>
      case "failed":
        return <Badge variant="destructive">失敗</Badge>
      default:
        return <Badge variant="outline">不明</Badge>
    }
  }

  const handlePlaySession = (sessionId: string) => {
    // プレゼンテーション用：セッション再生をシミュレート
    alert(`セッション「${sessions.find(s => s.id === sessionId)?.title}」を再生します！`)
  }

  const handleDownloadSession = (sessionId: string) => {
    // プレゼンテーション用：ダウンロードをシミュレート
    alert(`セッション「${sessions.find(s => s.id === sessionId)?.title}」をダウンロードします！`)
  }

  const handleDeleteSession = (sessionId: string) => {
    // プレゼンテーション用：削除をシミュレート
    if (confirm(`セッション「${sessions.find(s => s.id === sessionId)?.title}」を削除しますか？`)) {
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      alert("セッションが削除されました！")
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/voice-chat">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                雑談ルームへ戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">音声チャット履歴</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* 検索バー */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="セッションタイトルやトピックで検索..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* 履歴一覧 */}
          <div className="grid gap-4">
            {filteredSessions.map((session) => (
              <Card key={session.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{session.title}</CardTitle>
                    {getStatusBadge(session.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="space-y-3">
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span className="flex items-center space-x-1">
                          <Calendar className="h-4 w-4" />
                          {session.date}
                        </span>
                        <span className="flex items-center space-x-1">
                          <Clock className="h-4 w-4" />
                          {session.duration}
                        </span>
                        <span className="flex items-center space-x-1">
                          <Users className="h-4 w-4" />
                          {session.participants}人
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <MessageSquare className="h-4 w-4 text-blue-500" />
                        <span className="text-sm text-gray-700">トピック: {session.topic}</span>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handlePlaySession(session.id)}
                      >
                        <Play className="h-4 w-4 mr-1" />
                        再生
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDownloadSession(session.id)}
                      >
                        <Download className="h-4 w-4 mr-1" />
                        ダウンロード
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="text-red-600 hover:text-red-700"
                        onClick={() => handleDeleteSession(session.id)}
                      >
                        <Trash2 className="h-4 w-4 mr-1" />
                        削除
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredSessions.length === 0 && (
            <div className="text-center py-12">
              <MessageSquare className="h-12 w-12 mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500">履歴が見つかりません</p>
              <p className="text-sm text-gray-400 mt-1">検索条件を変更するか、新しい雑談ルームを開始してください</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}