// 料金プラン表示
'use client';

import React from 'react';
import { PlanService } from '@/services/planService';

interface PricingCardProps {
  memberCount: number;
  freeLimit: number;
  costPerUser: number;
  currentAmount: number;
  excessMembers: number;
  isPaymentRequired: boolean;
  onPaymentClick: () => void;
  currentPlan?: string;
}

export default function PricingCard({
  memberCount,
  freeLimit,
  costPerUser,
  currentAmount,
  excessMembers,
  isPaymentRequired,
  onPaymentClick,
  currentPlan = 'premium'
}: PricingCardProps) {
  
  const planInfo = PlanService.getPlanDisplayInfo(currentPlan)
  const planUsage = PlanService.checkPlanUsage(memberCount, currentPlan)
  const isOverLimit = planUsage.isOverLimit;

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
      {/* ヘッダー */}
      <div className={`px-6 py-4 ${isOverLimit ? 'bg-gradient-to-r from-orange-500 to-red-500' : 'bg-gradient-to-r from-green-500 to-blue-500'} text-white`}>
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-bold">
            {isOverLimit ? '有料プラン' : '無料プラン'}
          </h3>
          <div className="text-right">
            <div className="text-2xl font-bold">
              ¥{currentAmount.toLocaleString()}
            </div>
            <div className="text-sm opacity-90">
              /月
            </div>
          </div>
        </div>
      </div>

      {/* 詳細情報 */}
      <div className="p-6">
        <div className="space-y-4">
          {/* メンバー数情報 */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <svg className="w-6 h-6 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <div>
                <div className="font-medium text-gray-900">現在のメンバー数</div>
                <div className="text-sm text-gray-600">アクティブユーザー</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">{memberCount}</div>
              <div className="text-sm text-gray-600">人</div>
            </div>
          </div>

          {/* 料金詳細 */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">現在のプラン</span>
              <span className="font-medium">{planInfo.name}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">利用者数</span>
              <span className="font-medium">{memberCount}人</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">プラン上限</span>
              <span className="font-medium">最大{planInfo.maxUsers}</span>
            </div>
            

            
            <hr className="my-3" />
            
            <div className="flex justify-between items-center text-lg font-bold">
              <span>月額料金</span>
              <span className="text-green-600">
                ¥{planInfo.monthlyPrice.toLocaleString()}
              </span>
            </div>
          </div>

          {/* プラン説明 */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">プラン詳細</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li className="flex items-center">
                <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                {planInfo.maxUsers}まで利用可能
              </li>
              <li className="flex items-center">
                <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                {planInfo.maxSessions}
              </li>
              <li className="flex items-center">
                <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                月次課金制
              </li>
              <li className="flex items-center">
                <svg className="w-4 h-4 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                いつでもメンバー数変更可能
              </li>
            </ul>
          </div>

          {/* アクションボタン */}
          <div className="pt-4">
            {isPaymentRequired ? (
              <button
                onClick={onPaymentClick}
                className="w-full bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105"
              >
                <div className="flex items-center justify-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                  ¥{planInfo.monthlyPrice.toLocaleString()}を決済する
                </div>
              </button>
            ) : (
              <div className="text-center py-3">
                <div className="flex items-center justify-center text-green-600">
                  <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="font-medium">決済不要（プラン上限内）</span>
                </div>
              </div>
            )}
          </div>

          {/* 注意事項 */}
          {isOverLimit && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-yellow-600 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm text-yellow-800 font-medium">プラン上限を超過しています</p>
                  <p className="text-xs text-yellow-700 mt-1">
                    メンバー数がプラン上限を超過しているため、上位プランへの変更が必要です。
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}