'use client';

import React from 'react';

interface SubscriptionStatusProps {
  status: 'free' | 'paid' | 'overdue';
  memberCount: number;
  freeLimit: number;
  lastPaymentDate?: string;
  nextBillingDate?: string;
}

export default function SubscriptionStatus({
  status,
  memberCount,
  freeLimit,
  lastPaymentDate,
  nextBillingDate
}: SubscriptionStatusProps) {
  
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'free':
        return {
          color: 'bg-green-100 text-green-800 border-green-200',
          icon: '✓',
          title: '無料プラン',
          description: '現在のメンバー数は無料枠内です'
        };
      case 'paid':
        return {
          color: 'bg-blue-100 text-blue-800 border-blue-200',
          icon: '💳',
          title: '有料プラン',
          description: '決済が完了しています'
        };
      case 'overdue':
        return {
          color: 'bg-red-100 text-red-800 border-red-200',
          icon: '⚠️',
          title: '支払い遅延',
          description: '決済が必要です'
        };
      default:
        return {
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '?',
          title: '不明',
          description: 'ステータスを確認してください'
        };
    }
  };

  const statusConfig = getStatusConfig(status);
  const isOverLimit = memberCount > freeLimit;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">サブスクリプション状況</h3>
      
      {/* ステータスバッジ */}
      <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border ${statusConfig.color} mb-4`}>
        <span className="mr-2">{statusConfig.icon}</span>
        {statusConfig.title}
      </div>

      <p className="text-gray-600 mb-6">{statusConfig.description}</p>

      {/* メンバー数表示 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span className="text-sm text-gray-600">メンバー数</span>
          </div>
          <div className="text-right">
            <div className="font-bold text-gray-900">{memberCount}人</div>
            <div className="text-xs text-gray-500">/ {freeLimit}人無料</div>
          </div>
        </div>

        {/* プログレスバー */}
        <div>
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>使用状況</span>
            <span>{Math.round((memberCount / Math.max(memberCount, freeLimit)) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                isOverLimit 
                  ? 'bg-gradient-to-r from-orange-400 to-red-500' 
                  : 'bg-gradient-to-r from-green-400 to-blue-500'
              }`}
              style={{
                width: `${Math.min((memberCount / Math.max(memberCount, freeLimit)) * 100, 100)}%`
              }}
            ></div>
          </div>
          {isOverLimit && (
            <p className="text-xs text-orange-600 mt-1">
              無料枠を{memberCount - freeLimit}人超過
            </p>
          )}
        </div>

        {/* 日付情報 */}
        <div className="space-y-2 pt-4 border-t border-gray-200">
          {lastPaymentDate && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">最終決済日</span>
              <span className="font-medium">{formatDate(lastPaymentDate)}</span>
            </div>
          )}
          
          {nextBillingDate && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">次回請求日</span>
              <span className="font-medium">{formatDate(nextBillingDate)}</span>
            </div>
          )}
          
          {!lastPaymentDate && !nextBillingDate && status === 'free' && (
            <div className="text-center text-sm text-gray-500 py-2">
              無料プランをご利用中です
            </div>
          )}
        </div>

        {/* アラート表示 */}
        {status === 'overdue' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="text-sm font-medium text-red-800">決済が必要です</p>
                <p className="text-xs text-red-600">サービスの継続利用のため決済を完了してください</p>
              </div>
            </div>
          </div>
        )}

        {isOverLimit && status === 'free' && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-yellow-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="text-sm font-medium text-yellow-800">無料枠超過</p>
                <p className="text-xs text-yellow-600">有料プランへのアップグレードが必要です</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}