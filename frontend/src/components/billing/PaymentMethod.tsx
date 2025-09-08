'use client';

import React, { useState, useEffect } from 'react';

interface PaymentMethodData {
  id: string;
  type: 'card';
  card: {
    brand: string;
    last4: string;
    exp_month: number;
    exp_year: number;
  };
  is_default: boolean;
  created_at: string;
}

interface PaymentMethodProps {
  organizationId: number;
  onPaymentMethodChange?: () => void;
}

export default function PaymentMethod({ organizationId, onPaymentMethodChange }: PaymentMethodProps) {
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethodData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchPaymentMethods();
  }, [organizationId]);

  const fetchPaymentMethods = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/admin/billing/payment-methods/${organizationId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('支払い方法の取得に失敗しました');
      }

      const data = await response.json();
      setPaymentMethods(data.payment_methods || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : '不明なエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const handleSetDefault = async (paymentMethodId: string) => {
    try {
      const response = await fetch(`/api/admin/billing/payment-methods/${organizationId}/set-default`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          payment_method_id: paymentMethodId
        }),
      });

      if (!response.ok) {
        throw new Error('デフォルト支払い方法の設定に失敗しました');
      }

      await fetchPaymentMethods();
      onPaymentMethodChange?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : '不明なエラーが発生しました');
    }
  };

  const handleDelete = async (paymentMethodId: string) => {
    if (!confirm('この支払い方法を削除しますか？')) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/billing/payment-methods/${organizationId}/${paymentMethodId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('支払い方法の削除に失敗しました');
      }

      await fetchPaymentMethods();
      onPaymentMethodChange?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : '不明なエラーが発生しました');
    }
  };

  const getCardBrandIcon = (brand: string) => {
    const brandIcons: { [key: string]: string } = {
      visa: '💳',
      mastercard: '💳',
      amex: '💳',
      jcb: '💳',
      diners: '💳',
      discover: '💳',
      unknown: '💳'
    };
    return brandIcons[brand.toLowerCase()] || brandIcons.unknown;
  };

  const formatCardBrand = (brand: string) => {
    const brandNames: { [key: string]: string } = {
      visa: 'Visa',
      mastercard: 'Mastercard',
      amex: 'American Express',
      jcb: 'JCB',
      diners: 'Diners Club',
      discover: 'Discover',
      unknown: 'Unknown'
    };
    return brandNames[brand.toLowerCase()] || brand.toUpperCase();
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">支払い方法</h3>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">読み込み中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">支払い方法</h3>
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            <svg className="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            カードを追加
          </button>
        </div>
      </div>

      {error && (
        <div className="mx-6 mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
          <button
            onClick={() => setError('')}
            className="mt-2 text-red-600 hover:text-red-800 text-sm"
          >
            閉じる
          </button>
        </div>
      )}

      <div className="p-6">
        {paymentMethods.length === 0 ? (
          <div className="text-center py-8">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            <p className="text-gray-600 mb-2">登録された支払い方法がありません</p>
            <p className="text-sm text-gray-500 mb-4">クレジットカードを登録して決済を行ってください</p>
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
            >
              最初のカードを追加
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {paymentMethods.map((method) => (
              <div key={method.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-2xl mr-3">
                      {getCardBrandIcon(method.card.brand)}
                    </span>
                    <div>
                      <div className="font-medium text-gray-900">
                        {formatCardBrand(method.card.brand)} •••• {method.card.last4}
                      </div>
                      <div className="text-sm text-gray-600">
                        有効期限: {method.card.exp_month.toString().padStart(2, '0')}/{method.card.exp_year}
                      </div>
                      {method.is_default && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 mt-1">
                          デフォルト
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {!method.is_default && (
                      <button
                        onClick={() => handleSetDefault(method.id)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        デフォルトに設定
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(method.id)}
                      className="text-red-600 hover:text-red-800 p-1"
                      title="削除"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* カード追加フォーム */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-lg font-semibold">新しいカードを追加</h4>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">
                  カード情報の追加は決済時に行われます
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  決済手続きの際に新しいカード情報を入力することで、自動的に支払い方法として保存されます
                </p>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
                >
                  了解
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 注意事項 */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <svg className="w-5 h-5 text-blue-400 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="text-sm font-medium text-blue-800 mb-1">
                支払い方法について
              </h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• デフォルトの支払い方法が自動決済に使用されます</li>
                <li>• カード情報はStripeによって安全に管理されます</li>
                <li>• 期限切れのカードは自動的に無効になります</li>
                <li>• 決済時に新しいカードを追加することができます</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}