// 管理者用決済詳細情報コンポーネント
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Users, Calendar, CreditCard, TrendingUp } from "lucide-react"
import { PlanService } from "@/services/planService"

interface AdminBillingOverviewProps {
  userCount: number
  isFreeTier: boolean
  additionalUsers: number
  additionalCost: number
  currentPlan?: string 
}

export function AdminBillingOverview({
  userCount,
  isFreeTier,
  additionalUsers,
  additionalCost,
  currentPlan = 'premium'
}: AdminBillingOverviewProps) {
  const planInfo = PlanService.getPlanDisplayInfo(currentPlan)
  const planUsage = PlanService.checkPlanUsage(userCount, currentPlan)
  const remainingSlots = Math.max(0, planUsage.maxUsers - userCount)
  
  // 請求日を毎月10日に設定
  const nextBillingDate = new Date()
  nextBillingDate.setDate(10)
  if (nextBillingDate <= new Date()) {
    nextBillingDate.setMonth(nextBillingDate.getMonth() + 1)
  }

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
              <span className="text-gray-600">プラン上限</span>
              <div className="text-right">
                <div className="font-medium">{planInfo.maxUsers}</div>
                <div className="text-sm text-gray-500">
                  {remainingSlots > 0 
                    ? `${remainingSlots}人分の余裕`
                    : '上限に達しています'
                  }
                </div>
        </div>
      </div>
            

            
            <div className="pt-2 border-t">
                          <div className="flex justify-between items-center">
              <span className="font-medium">利用率</span>
              <span className="font-bold text-blue-600">
                {planUsage.maxUsers === Number.MAX_SAFE_INTEGER 
                  ? '無制限' 
                  : `${Math.round((userCount / planUsage.maxUsers) * 100)}%`
                }
              </span>
            </div>
            {planUsage.maxUsers !== Number.MAX_SAFE_INTEGER && (
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${
                    userCount <= planUsage.maxUsers ? 'bg-blue-600' : 'bg-orange-500'
                  }`}
                  style={{ width: `${Math.min(100, (userCount / planUsage.maxUsers) * 100)}%` }}
                ></div>
              </div>
            )}
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
              <span className="text-gray-600">プラン料金</span>
              <Badge variant="secondary" className="text-lg px-3 py-1">
                ¥{planInfo.monthlyPrice.toLocaleString()}/月
              </Badge>
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
                <span className="text-xl font-bold text-green-600">
                  ¥{planInfo.monthlyPrice.toLocaleString()}
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
              {PlanService.getAllPlans().map((plan) => {
                const displayInfo = PlanService.getPlanDisplayInfo(plan.id)
                const isCurrentPlan = plan.id === currentPlan
                return (
                  <div 
                    key={plan.id}
                    className={`text-center p-4 rounded-lg border-2 ${
                      isCurrentPlan 
                        ? 'bg-blue-100 border-blue-500' 
                        : plan.id === 'basic' 
                          ? 'bg-blue-50 border-blue-200'
                          : plan.id === 'premium'
                            ? 'bg-orange-50 border-orange-200'
                            : 'bg-green-50 border-green-200'
                    }`}
                  >
                    <div className={`text-2xl font-bold mb-2 ${
                      isCurrentPlan 
                        ? 'text-blue-700' 
                        : plan.id === 'basic' 
                          ? 'text-blue-600'
                          : plan.id === 'premium'
                            ? 'text-orange-600'
                            : 'text-green-600'
                    }`}>
                      {displayInfo.name}
                      {isCurrentPlan && <span className="text-sm ml-2">(現在)</span>}
                    </div>
                    <div className="text-sm text-gray-600">月額{displayInfo.monthlyPrice.toLocaleString()}円</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {displayInfo.maxUsers}、{displayInfo.maxSessions}
                    </div>
                  </div>
                )
              })}
        </div>
            
            <div className="text-sm text-gray-600 bg-gray-50 p-4 rounded-lg">
              <strong>支払いについて:</strong> 料金は月額で計算され、毎月10日に請求されます。
              プラン変更は即座に反映され、次回請求時に調整されます。
              決済はStripeを通じて安全に処理されます。
      </div>
    </div>
        </CardContent>
      </Card>
    </div>
  )
}
