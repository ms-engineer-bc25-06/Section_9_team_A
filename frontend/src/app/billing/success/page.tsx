// 課金成功後の確認ページ
'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

interface PaymentResult {
  payment_intent_id: string;
  amount: number;
  organization_name: string;
  member_count: number;
  payment_date: string;
  receipt_url?: string;
}

export default function BillingSuccessPage() {
  const [paymentResult, setPaymentResult] = useState<PaymentResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const paymentIntentId = searchParams.get('payment_intent');
    const paymentIntentClientSecret = searchParams.get('payment_intent_client_secret');

    if (paymentIntentId) {
      verifyPayment(paymentIntentId);
    } else {
      setError('決済情報が見つかりません');
      setLoading(false);
    }
  }, [searchParams]);

  const verifyPayment = async (paymentIntentId: string) => {
    try {
      const response = await fetch(`/api/billing/verify-payment/${paymentIntentId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('決済確認に失敗しました');
      }

      const data = await response.json();
      setPaymentResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '決済確認でエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReceipt = () => {
    if (paymentResult?.receipt_url) {
      window.open(paymentResult.receipt_url, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">決済結果を確認中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6 text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">エラーが発生しました</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Link
            href="/billing"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            決済ページに戻る
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-2xl mx-auto px-4">
        {/* 成功メッセージ */}
        <div className="bg-white rounded-lg shadow-lg p-8 text-center mb-8">
          <div className="text-green-600 mb-6">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            決済が完了しました！
          </h1>
          
          <p className="text-gray-600 mb-6">
            ご利用ありがとうございます。決済が正常に処理されました。
          </p>

          {/* 決済詳細 */}
          {paymentResult && (
            <div className="bg-gray-50 rounded-lg p-6 text-left">
              <h2 className="text-lg font-semibold mb-4 text-center">決済詳細</h2>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">組織名</span>
                  <span className="font-medium">{paymentResult.organization_name}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">メンバー数</span>
                  <span className="font-medium">{paymentResult.member_count}人</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">決済金額</span>
                  <span className="font-medium text-green-600">
                    ¥{paymentResult.amount.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">決済日時</span>
                  <span className="font-medium">
                    {new Date(paymentResult.payment_date).toLocaleString('ja-JP')}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">決済ID</span>
                  <span className="font-mono text-sm text-gray-500">
                    {paymentResult.payment_intent_id}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* アクションボタン */}
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {paymentResult?.receipt_url && (
              <button
                onClick={handleDownloadReceipt}
                className="flex items-center justify-center px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                領収書をダウンロード
              </button>
            )}
            
            <Link
              href="/billing/subscription"
              className="flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              サブスクリプション管理
            </Link>
          </div>
          
          <div className="text-center">
            <Link
              href="/dashboard"
              className="inline-flex items-center px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors text-lg font-medium"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v1H8V5z" />
              </svg>
              ダッシュボードに戻る
            </Link>
          </div>
        </div>

        {/* 注意事項 */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                お知らせ
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <ul className="pl-5 space-y-1">
                  <li>• 決済完了の確認メールを送信いたします</li>
                  <li>• 領収書は決済から24時間以内に利用可能になります</li>
                  <li>• ご不明な点がございましたらサポートまでお問い合わせください</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}