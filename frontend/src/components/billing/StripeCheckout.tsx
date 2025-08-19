// Stripe決済処理コンポーネント
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { CreditCard, Loader2 } from "lucide-react"

interface StripeCheckoutProps {
  amount: number
  currency: string
  description: string
  onSuccess: (paymentIntentId: string) => void
  onError: (error: string) => void
  disabled?: boolean
}

export function StripeCheckout({
  amount,
  currency,
  description,
  onSuccess,
  onError,
  disabled = false
}: StripeCheckoutProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handlePayment = async () => {
    setLoading(true)
    setError(null)

    try {
      // Step 1: バックエンドでStripe Checkoutセッションを作成
      const response = await fetch('/api/admin/billing/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          amount,
          currency,
          description,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create checkout session')
      }

      const { checkout_url, session_id } = await response.json()

      // Step 2: Stripe Checkoutページにリダイレクト
      window.location.href = checkout_url

      // NOTE: 実際の決済完了はwebhookとsuccess pageで処理
      
    } catch (err) {
      console.error('Payment error:', err)
      const errorMessage = err instanceof Error ? err.message : '決済処理でエラーが発生しました'
      setError(errorMessage)
      onError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* エラー表示 */}
      {error && (
        <Alert>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 決済内容の表示 */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-2">
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">サービス</span>
          <span className="text-sm">{description}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">金額</span>
          <span className="text-sm font-semibold">
            ¥{amount.toLocaleString()} {currency.toUpperCase()}
          </span>
        </div>
      </div>

      {/* 決済ボタン */}
      <Button
        onClick={handlePayment}
        disabled={disabled || loading}
        className="w-full"
        size="lg"
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            処理中...
          </>
        ) : (
          <>
            <CreditCard className="mr-2 h-4 w-4" />
            Stripeで決済する
          </>
        )}
      </Button>

      {/* 注意事項 */}
      <div className="text-xs text-gray-500 text-center">
        <p>• 決済はStripeの安全なサーバーで処理されます</p>
        <p>• クレジットカード情報は当サイトに保存されません</p>
        <p>• 決済完了後、すぐにサービスが利用可能になります</p>
      </div>
    </div>
  )
}

// 'use client';

// import React, { useState } from 'react';
// import { loadStripe } from '@stripe/stripe-js';
// import {
//   Elements,
//   CardElement,
//   useStripe,
//   useElements
// } from '@stripe/react-stripe-js';

// const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

// interface StripeCheckoutProps {
//   organizationId: number;
//   memberCount: number;
//   amount: number;
//   onSuccess: (paymentIntentId: string) => void;
//   onError: (error: string) => void;
//   onCancel?: () => void;
// }

// interface CheckoutFormProps {
//   organizationId: number;
//   memberCount: number;
//   amount: number;
//   onSuccess: (paymentIntentId: string) => void;
//   onError: (error: string) => void;
//   onCancel?: () => void;
// }

// const CheckoutForm: React.FC<CheckoutFormProps> = ({
//   organizationId,
//   memberCount,
//   amount,
//   onSuccess,
//   onError,
//   onCancel
// }) => {
//   const stripe = useStripe();
//   const elements = useElements();
//   const [isProcessing, setIsProcessing] = useState(false);
//   const [clientSecret, setClientSecret] = useState<string>('');

//   // Payment Intent作成
//   const createPaymentIntent = async () => {
//     try {
//       const response = await fetch('/api/admin/billing/create-payment-intent', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${localStorage.getItem('token')}`,
//         },
//         body: JSON.stringify({
//           organization_id: organizationId,
//           member_count: memberCount,
//           amount: amount
//         }),
//       });

//       if (!response.ok) {
//         throw new Error('決済準備に失敗しました');
//       }

//       const data = await response.json();
//       return data.client_secret;
//     } catch (error) {
//       throw error;
//     }
//   };

//   const handleSubmit = async (event: React.FormEvent) => {
//     event.preventDefault();

//     if (!stripe || !elements) {
//       onError('Stripeの初期化に失敗しました');
//       return;
//     }

//     setIsProcessing(true);

//     try {
//       // Payment Intent作成
//       const secret = await createPaymentIntent();
//       setClientSecret(secret);

//       const cardElement = elements.getElement(CardElement);
//       if (!cardElement) {
//         throw new Error('カード情報の取得に失敗しました');
//       }

//       // 決済確認
//       const { error, paymentIntent } = await stripe.confirmCardPayment(secret, {
//         payment_method: {
//           card: cardElement,
//           billing_details: {
//             name: `Organization ${organizationId}`,
//           },
//         }
//       });

//       if (error) {
//         throw new Error(error.message || '決済処理に失敗しました');
//       }

//       if (paymentIntent && paymentIntent.status === 'succeeded') {
//         onSuccess(paymentIntent.id);
//       } else {
//         throw new Error('決済が完了しませんでした');
//       }
//     } catch (err) {
//       onError(err instanceof Error ? err.message : '不明なエラーが発生しました');
//     } finally {
//       setIsProcessing(false);
//     }
//   };

//   const freeLimit = 10;
//   const excessMembers = Math.max(0, memberCount - freeLimit);
//   const costPerUser = 500;

//   return (
//     <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
//       <h3 className="text-xl font-bold mb-6 text-center">決済手続き</h3>
      
//       {/* 決済詳細 */}
//       <div className="bg-gray-50 rounded-lg p-4 mb-6 space-y-2">
//         <div className="flex justify-between">
//           <span className="text-gray-600">現在のメンバー数</span>
//           <span className="font-medium">{memberCount}人</span>
//         </div>
//         <div className="flex justify-between">
//           <span className="text-gray-600">無料枠</span>
//           <span className="font-medium">{freeLimit}人</span>
//         </div>
//         <div className="flex justify-between">
//           <span className="text-gray-600">超過人数</span>
//           <span className={`font-medium ${excessMembers > 0 ? 'text-orange-600' : 'text-green-600'}`}>
//             {excessMembers}人
//           </span>
//         </div>
//         <div className="flex justify-between">
//           <span className="text-gray-600">単価</span>
//           <span className="font-medium">¥{costPerUser}/人</span>
//         </div>
//         <hr className="my-2" />
//         <div className="flex justify-between text-lg font-bold">
//           <span>合計金額</span>
//           <span className="text-blue-600">¥{amount.toLocaleString()}</span>
//         </div>
//       </div>

//       {/* 決済フォーム */}
//       <form onSubmit={handleSubmit} className="space-y-4">
//         <div>
//           <label className="block text-sm font-medium text-gray-700 mb-2">
//             カード情報
//           </label>
//           <div className="border border-gray-300 rounded-lg p-3 bg-white">
//             <CardElement
//               options={{
//                 style: {
//                   base: {
//                     fontSize: '16px',
//                     color: '#424770',
//                     '::placeholder': {
//                       color: '#aab7c4',
//                     },
//                   },
//                   invalid: {
//                     color: '#9e2146',
//                   },
//                 },
//                 hidePostalCode: true,
//               }}
//             />
//           </div>
//         </div>

//         <div className="flex space-x-3">
//           {onCancel && (
//             <button
//               type="button"
//               onClick={onCancel}
//               disabled={isProcessing}
//               className="flex-1 py-3 px-4 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
//             >
//               キャンセル
//             </button>
//           )}
          
//           <button
//             type="submit"
//             disabled={!stripe || isProcessing || amount === 0}
//             className={`flex-1 py-3 px-4 rounded-lg font-medium text-white transition-colors ${
//               !stripe || isProcessing || amount === 0
//                 ? 'bg-gray-400 cursor-not-allowed'
//                 : 'bg-blue-600 hover:bg-blue-700'
//             }`}
//           >
//             {isProcessing ? (
//               <div className="flex items-center justify-center">
//                 <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
//                 処理中...
//               </div>
//             ) : amount === 0 ? (
//               '決済不要'
//             ) : (
//               `¥${amount.toLocaleString()}を決済`
//             )}
//           </button>
//         </div>
//       </form>

//       {/* セキュリティ情報 */}
//       <div className="mt-4 text-center">
//         <p className="text-xs text-gray-500">
//           🔒 決済情報はStripeによって安全に暗号化されます
//         </p>
//       </div>
//     </div>
//   );
// };

// const StripeCheckout: React.FC<StripeCheckoutProps> = (props) => {
//   return (
//     <Elements stripe={stripePromise}>
//       <CheckoutForm {...props} />
//     </Elements>
//   );
// };

// export default StripeCheckout;