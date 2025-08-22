// REVIEW: 音声チャット履歴ページ仮実装（るい）
"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Input } from "@/components/ui/Input"
import { ArrowLeft, Search, Play, Download, Trash2, Calendar } from "lucide-react"
import Link from "next/link"

interface VoiceSession {
  id: string
  title: string
  date: string
  duration: string
  participants: number
  status: "completed" | "processing" | "failed"
}

export default function VoiceChatHistoryPage() {
  const [sessions, setSessions] = useState<VoiceSession[]>([
    {
      id: "1",
      title: "チーム定例会議",
      date: "2024-01-15",
      duration: "45分",
      participants: 8,
      status: "completed"
    },
    {
      id: "2",
      title: "プロジェクト振り返り",
      date: "2024-01-14",
      duration: "30分",
      participants: 5,
      status: "completed"
    }
  ])
  const [searchTerm, setSearchTerm] = useState("")

  const filteredSessions = sessions.filter(session =>
    session.title.toLowerCase().includes(searchTerm.toLowerCase())
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

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/voice-chat">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                音声チャットへ戻る
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
              placeholder="セッションを検索..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* 履歴一覧 */}
          <div className="grid gap-4">
            {filteredSessions.map((session) => (
              <Card key={session.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{session.title}</CardTitle>
                    {getStatusBadge(session.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span className="flex items-center space-x-1">
                          <Calendar className="h-4 w-4" />
                          {session.date}
                        </span>
                        <span>時間: {session.duration}</span>
                        <span>参加者: {session.participants}人</span>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm">
                        <Play className="h-4 w-4 mr-1" />
                        再生
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-1" />
                        ダウンロード
                      </Button>
                      <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
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
              <p className="text-gray-500">履歴が見つかりません</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}