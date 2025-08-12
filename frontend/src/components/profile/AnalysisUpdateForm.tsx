"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Textarea } from "@/components/ui/Textarea"
import { Badge } from "@/components/ui/Badge"
import { Separator } from "@/components/ui/Separator"
import { 
  Brain, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle,
  Loader2
} from "lucide-react"

interface AnalysisUpdateFormProps {
  onAnalysisUpdate: (text: string, analysisTypes: string[]) => Promise<void>
  isLoading?: boolean
}

const analysisTypes = [
  { id: "personality", label: "個性分析", description: "性格・思考・趣向の推定" },
  { id: "communication", label: "コミュニケーション", description: "コミュニケーションパターン分析" },
  { id: "behavior", label: "行動特性", description: "行動特性スコアの算出" },
  { id: "sentiment", label: "感情分析", description: "発言の感情傾向分析" },
  { id: "topic", label: "トピック分析", description: "会話のトピック・キーワード抽出" },
  { id: "summary", label: "要約", description: "会話内容の要約" }
]

export function AnalysisUpdateForm({ onAnalysisUpdate, isLoading = false }: AnalysisUpdateFormProps) {
  const [text, setText] = useState("")
  const [selectedTypes, setSelectedTypes] = useState<string[]>(["personality", "communication", "behavior"])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<string | null>(null)

  const handleTypeToggle = (typeId: string) => {
    setSelectedTypes(prev => 
      prev.includes(typeId) 
        ? prev.filter(id => id !== typeId)
        : [...prev, typeId]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim() || selectedTypes.length === 0) return

    setIsSubmitting(true)
    try {
      await onAnalysisUpdate(text, selectedTypes)
      setLastUpdate(new Date().toLocaleString('ja-JP'))
      setText("")
    } catch (error) {
      console.error('Analysis update failed:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const isFormValid = text.trim().length > 0 && selectedTypes.length > 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <RefreshCw className="h-5 w-5" />
          <span>AI分析の更新</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 分析対象テキスト */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              分析対象のテキスト
            </label>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="音声チャットの内容や、分析したいテキストを入力してください..."
              rows={4}
              className="w-full"
              disabled={isSubmitting}
            />
            <p className="text-xs text-gray-500 mt-1">
              {text.length}文字
            </p>
          </div>

          {/* 分析タイプの選択 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              分析タイプ（複数選択可）
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {analysisTypes.map((type) => (
                <div
                  key={type.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedTypes.includes(type.id)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleTypeToggle(type.id)}
                >
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={selectedTypes.includes(type.id)}
                      onChange={() => handleTypeToggle(type.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-sm">{type.label}</div>
                      <div className="text-xs text-gray-500">{type.description}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 分析タイプの説明 */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-sm mb-2 flex items-center space-x-2">
              <Brain className="h-4 w-4 text-blue-500" />
              <span>分析タイプの説明</span>
            </h4>
            <div className="text-xs text-gray-600 space-y-1">
              <p>• <strong>個性分析:</strong> 性格特性、思考パターン、興味・関心を分析</p>
              <p>• <strong>コミュニケーション:</strong> 発言パターン、会話スタイル、改善点を分析</p>
              <p>• <strong>行動特性:</strong> チーム貢献度、問題解決能力などを数値化</p>
              <p>• <strong>感情分析:</strong> 発言の感情傾向（ポジティブ/ネガティブ）を分析</p>
              <p>• <strong>トピック分析:</strong> 会話の主要トピックとキーワードを抽出</p>
              <p>• <strong>要約:</strong> 会話内容を簡潔にまとめる</p>
            </div>
          </div>

          {/* 送信ボタン */}
          <div className="flex items-center justify-between">
            <Button
              type="submit"
              disabled={!isFormValid || isSubmitting}
              className="flex items-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>分析中...</span>
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4" />
                  <span>分析を実行</span>
                </>
              )}
            </Button>

            {lastUpdate && (
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span>最終更新: {lastUpdate}</span>
              </div>
            )}
          </div>

          {/* 注意事項 */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <div className="flex items-start space-x-2">
              <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-yellow-800">
                <p className="font-medium">注意事項</p>
                <ul className="mt-1 space-y-1 text-xs">
                  <li>• 分析には数分かかる場合があります</li>
                  <li>• 長いテキストの場合は、重要な部分を抽出してから分析することをお勧めします</li>
                  <li>• 分析結果は自動的にプロフィールに反映されます</li>
                </ul>
              </div>
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
