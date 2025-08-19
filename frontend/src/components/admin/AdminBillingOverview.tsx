// 管理者用決済詳細情報コンポーネント
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Users, Calendar, CreditCard, TrendingUp } from "lucide-react"

interface AdminBillingOverviewProps {
  userCount: number
  isFreeTier: boolean
  additionalUsers: number
  additionalCost: number
}

export function AdminBillingOverview({
  userCount,
  isFreeTier,
  additionalUsers,
  additionalCost
}: AdminBillingOverviewProps) {
  const freeLimit = 10
  const remainingFreeSlots = Math.max(0, freeLimit - userCount)
  const nextBillingDate = new Date()
  nextBillingDate.setDate(nextBillingDate.getDate() + 30) // 30日後

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">詳細情報</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 利用状況詳細 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-600" />
              <span>利用状況詳細</span>
            </CardTitle>
            <CardDescription>現在のシステム利用状況</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">総利用者数</span>
              <Badge variant="outline" className="text-lg px-3 py-1">
                {userCount}人
              </Badge>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">無料枠</span>
              <div className="text-right">
                <div className="font-medium">{freeLimit}人まで</div>
                <div className="text-sm text-gray-500">
                  {remainingFreeSlots > 0 
                    ? `${remainingFreeSlots}人分の余裕`
                    : '上限に達しています'
                  }
                </div>
        </div>
      </div>
            
            {additionalUsers > 0 && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600">超過人数</span>
                <Badge variant="destructive" className="text-lg px-3 py-1">
                  +{additionalUsers}人
                </Badge>
              </div>
            )}
            
            <div className="pt-2 border-t">
              <div className="flex justify-between items-center">
                <span className="font-medium">利用率</span>
                <span className="font-bold text-blue-600">
                  {Math.round((userCount / freeLimit) * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${
                    userCount <= freeLimit ? 'bg-blue-600' : 'bg-orange-500'
                  }`}
                  style={{ width: `${Math.min(100, (userCount / freeLimit) * 100)}%` }}
                ></div>
          </div>
        </div>
            

          </CardContent>
        </Card>

        {/* 料金・決済情報 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CreditCard className="h-5 w-5 text-green-600" />
              <span>料金・決済情報</span>
            </CardTitle>
            <CardDescription>現在の料金体系と決済状況</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">基本料金</span>
              <Badge variant="secondary" className="text-lg px-3 py-1">
                無料
              </Badge>
      </div>

      <div className="flex justify-between items-center">
              <span className="text-gray-600">追加料金</span>
              <div className="text-right">
                {additionalUsers > 0 ? (
                  <>
                    <div className="font-bold text-orange-600">
                      ¥{additionalCost.toLocaleString()}/月
                    </div>
        <div className="text-sm text-gray-500">
                      {additionalUsers}人 × ¥500
                    </div>
                  </>
                ) : (
                  <Badge variant="outline" className="text-lg px-3 py-1">
                    なし
                  </Badge>
                )}
        </div>
      </div>

            <div className="flex justify-between items-center">
              <span className="text-gray-600">次回請求日</span>
              <div className="text-right">
                <div className="font-medium">
                  {nextBillingDate.toLocaleDateString('ja-JP')}
                </div>
                <div className="text-sm text-gray-500">
                  {Math.ceil((nextBillingDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24))}日後
            </div>
          </div>
        </div>
            
            <div className="pt-2 border-t">
              <div className="flex justify-between items-center">
                <span className="font-medium">月額合計</span>
                <span className={`text-xl font-bold ${
                  additionalCost > 0 ? 'text-orange-600' : 'text-green-600'
                }`}>
                  {additionalCost > 0 ? `¥${additionalCost.toLocaleString()}` : '無料'}
                </span>
            </div>
          </div>
          </CardContent>
        </Card>
        </div>

      {/* 料金体系の詳細説明 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-purple-600" />
            <span>料金体系について</span>
          </CardTitle>
          <CardDescription>システムの料金プラン詳細</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600 mb-2">10人まで</div>
                <div className="text-sm text-gray-600">無料で利用可能</div>
                <div className="text-xs text-gray-500 mt-1">基本機能すべて利用</div>
      </div>

              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600 mb-2">11人以降</div>
                <div className="text-sm text-gray-600">1人500円/月</div>
                <div className="text-xs text-gray-500 mt-1">追加料金が発生</div>
              </div>
              
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600 mb-2">柔軟な拡張</div>
                <div className="text-sm text-gray-600">必要に応じて追加</div>
                <div className="text-xs text-gray-500 mt-1">月単位で調整可能</div>
          </div>
        </div>
            
            <div className="text-sm text-gray-600 bg-gray-50 p-4 rounded-lg">
              <strong>注意事項:</strong> 料金は月額で計算され、月初に請求されます。
              利用者数の変更は即座に反映され、次回請求時に調整されます。
      </div>
    </div>
        </CardContent>
      </Card>
    </div>
  )
}
