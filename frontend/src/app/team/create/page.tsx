// REVIEW: チーム作成ページ仮実装（るい）
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Textarea } from "@/components/ui/Textarea"
import { ArrowLeft, Plus, Users } from "lucide-react"
import Link from "next/link"

export default function CreateTeamPage() {
  const [teamData, setTeamData] = useState({
    name: "",
    description: "",
    maxMembers: 10
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("チーム作成:", teamData)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/team">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                チーム一覧へ戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">新しいチームを作成</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Plus className="h-5 w-5" />
                チーム情報
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <Label htmlFor="name">チーム名 *</Label>
                  <Input
                    id="name"
                    value={teamData.name}
                    onChange={(e) => setTeamData({ ...teamData, name: e.target.value })}
                    placeholder="チーム名を入力"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="description">説明</Label>
                  <Textarea
                    id="description"
                    value={teamData.description}
                    onChange={(e) => setTeamData({ ...teamData, description: e.target.value })}
                    placeholder="チームの説明を入力"
                    rows={4}
                  />
                </div>

                <div>
                  <Label htmlFor="maxMembers">最大メンバー数</Label>
                  <Input
                    id="maxMembers"
                    type="number"
                    value={teamData.maxMembers}
                    onChange={(e) => setTeamData({ ...teamData, maxMembers: parseInt(e.target.value) })}
                    min="1"
                    max="100"
                  />
                </div>

                <div className="flex justify-end space-x-4">
                  <Link href="/team">
                    <Button variant="outline" type="button">
                      キャンセル
                    </Button>
                  </Link>
                  <Button type="submit">
                    <Plus className="h-4 w-4 mr-2" />
                    チームを作成
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}