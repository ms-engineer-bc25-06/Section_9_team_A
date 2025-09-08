// REVIEW: チームメンバー設定ページ仮実装（るい）
"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Switch } from "@/components/ui/Switch"
import { ArrowLeft, Save, User, Shield, Bell } from "lucide-react"
import Link from "next/link"

export default function OrganizationMemberSettingsPage() {
  const params = useParams()
  const memberId = params.memberId as string
  
  const [settings, setSettings] = useState({
    notifications: true,
    privacy: "team",
    role: "member"
  })

  const handleSave = () => {
    console.log("設定を保存:", settings)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link href={`/team/${memberId}`}>
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                メンバー詳細へ戻る
              </Button>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">メンバー設定</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="h-5 w-5" />
                基本設定
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="role">役割</Label>
                <Input
                  id="role"
                  value={settings.role}
                  onChange={(e) => setSettings({ ...settings, role: e.target.value })}
                  placeholder="役割を入力"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                通知設定
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="notifications">通知を有効にする</Label>
                <Switch
                  id="notifications"
                  checked={settings.notifications}
                  onCheckedChange={(checked) => 
                    setSettings({ ...settings, notifications: checked })
                  }
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                プライバシー設定
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="privacy">情報の公開範囲</Label>
                <select
                  id="privacy"
                  value={settings.privacy}
                  onChange={(e) => setSettings({ ...settings, privacy: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="private">プライベート</option>
                  <option value="team">チーム内のみ</option>
                  <option value="organization">組織内</option>
                </select>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end space-x-4">
            <Link href={`/team/${memberId}`}>
              <Button variant="outline">キャンセル</Button>
            </Link>
            <Button onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              保存
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}