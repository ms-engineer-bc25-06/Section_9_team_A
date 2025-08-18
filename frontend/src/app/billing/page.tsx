// メイン決済ページ(決済は管理者のみのため、コメントアウト)
// 'use client';

// import React, { useState, useEffect } from 'react';
// import { loadStripe } from '@stripe/stripe-js';
// import {
//   Elements,
//   CardElement,
//   useStripe,
//   useElements
// } from '@stripe/react-stripe-js';
// import { useRouter } from 'next/navigation';

// // Stripe の初期化
// const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

// interface BillingInfo {
//   organization_id: number;
//   organization_name: string;
//   current_members: number;
//   required_payment: number;
//   free_limit: number;
//   per_user_cost: number;
//   is_payment_required: boolean;
// }

// // 決済フォームコンポーネント
// const CheckoutForm = ({ 
//   billingInfo, 
//   clientSecret, 
//   onSuccess 
// }: {
//   billingInfo: BillingInfo;
//   clientSecret: string;
//   onSuccess: () => void;
// }) => {
//   const stripe = useStripe();
//   const elements = useElements();
//   const [isProcessing, setIsProcessing] = useState(false);
//   const [errorMessage, setErrorMessage] = useState('');

//   const handleSubmit = async (event: React.FormEvent) => {
//     event.preventDefault();

//     if (!stripe || !elements) {
//       return;
//     }

//     setIsProcessing(true);
//     setErrorMessage('');

//     const cardElement = elements.getElement(CardElement);

//     if (!cardElement) {
//       setIsProcessing(false);
//       return;
//     }

//     const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
//       payment_method: {
//         card: cardElement,
//         billing_details: {
//           name: billingInfo.organization_name,
//         },
//       }
//     });

//     setIsProcessing(false);

//     if (error) {
//       setErrorMessage(error.message || '決済処理中にエラーが発生しました');
//     } else if (paymentIntent && paymentIntent.status === 'succeeded') {
//       onSuccess();
//     }
//   };

//   return (
//     <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
//       <h2 className="text-2xl font-bold mb-6 text-center">決済情報</h2>
      
//       {/* 請求詳細 */}
//       <div className="bg-gray-50 rounded-lg p-4 mb-6">
//         <div className="flex justify-between items-center mb-2">
//           <span className="text-gray-600">組織名</span>
//           <span className="font-medium">{billingInfo.organization_name}</span>
//         </div>
//         <div className="flex justify-between items-center mb-2">
//           <span className="text-gray-600">現在のメンバー数</span>
//           <span className="font-medium">{billingInfo.current_members}人</span>
//         </div>
//         <div className="flex justify-between items-center mb-2">
//           <span className="text-gray-600">無料枠</span>
//           <span className="font-medium">{billingInfo.free_limit}人まで</span>
//         </div>
//         <div className="flex justify-between items-center mb-2">
//           <span className="text-gray-600">超過人数</span>
//           <span className="font-medium text-orange-600">
//             {Math.max(0, billingInfo.current_members - billingInfo.free_limit)}人
//           </span>
//         </div>
//         <hr className="my-3" />
//         <div className="flex justify-between items-center">
//           <span className="text-lg font-semibold">合計金額</span>
//           <span className="text-xl font-bold text-blue-600">
//             ¥{billingInfo.required_payment.toLocaleString()}
//           </span>
//         </div>
//       </div>

//       {/* 決済フォーム */}
//       <form onSubmit={handleSubmit}>
//         <div className="mb-4">
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
//               }}
//             />
//           </div>
//         </div>

//         {errorMessage && (
//           <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
//             {errorMessage}
//           </div>
//         )}

//         <button
//           type="submit"
//           disabled={!stripe || isProcessing}
//           className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-colors ${
//             !stripe || isProcessing
//               ? 'bg-gray-400 cursor-not-allowed'
//               : 'bg-blue-600 hover:bg-blue-700'
//           }`}
//         >
//           {isProcessing ? (
//             <div className="flex items-center justify-center">
//               <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
//               処理中...
//             </div>
//           ) : (
//             `¥${billingInfo.required_payment.toLocaleString()}を決済する`
//           )}
//         </button>
//       </form>

//       <p className="text-xs text-gray-500 text-center mt-4">
//         決済はStripeによって安全に処理されます
//       </p>
//     </div>
//   );
// };

// // メイン決済ページコンポーネント
// export default function BillingPage() {
//   const [billingInfo, setBillingInfo] = useState<BillingInfo | null>(null);
//   const [clientSecret, setClientSecret] = useState('');
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState('');
//   const router = useRouter();

//   useEffect(() => {
//     fetchBillingInfo();
//   }, []);

//   const fetchBillingInfo = async () => {
//     try {
//       setLoading(true);
//       const response = await fetch('/api/billing/info', {
//         headers: {
//           'Authorization': `Bearer ${localStorage.getItem('token')}`,
//         },
//       });

//       if (!response.ok) {
//         throw new Error('請求情報の取得に失敗しました');
//       }

//       const data = await response.json();
//       setBillingInfo(data);

//       // 決済が必要な場合は Payment Intent を作成
//       if (data.is_payment_required) {
//         await createPaymentIntent(data.organization_id);
//       }
//     } catch (err) {
//       setError(err instanceof Error ? err.message : '不明なエラーが発生しました');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const createPaymentIntent = async (organizationId: number) => {
//     try {
//       const response = await fetch('/api/billing/create-payment-intent', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${localStorage.getItem('token')}`,
//         },
//         body: JSON.stringify({
//           organization_id: organizationId,
//         }),
//       });

//       if (!response.ok) {
//         throw new Error('決済準備に失敗しました');
//       }

//       const data = await response.json();
//       setClientSecret(data.client_secret);
//     } catch (err) {
//       setError(err instanceof Error ? err.message : '決済準備でエラーが発生しました');
//     }
//   };

//   const handlePaymentSuccess = () => {
//     router.push('/billing/success');
//   };

//   if (loading) {
//     return (
//       <div className="min-h-screen bg-gray-50 flex items-center justify-center">
//         <div className="text-center">
//           <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
//           <p className="text-gray-600">請求情報を読み込み中...</p>
//         </div>
//       </div>
//     );
//   }

//   if (error) {
//     return (
//       <div className="min-h-screen bg-gray-50 flex items-center justify-center">
//         <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6 text-center">
//           <div className="text-red-600 mb-4">
//             <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
//             </svg>
//           </div>
//           <h2 className="text-xl font-bold text-gray-900 mb-2">エラーが発生しました</h2>
//           <p className="text-gray-600 mb-4">{error}</p>
//           <button
//             onClick={() => window.location.reload()}
//             className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
//           >
//             再試行
//           </button>
//         </div>
//       </div>
//     );
//   }

//   if (!billingInfo) {
//     return null;
//   }

//   return (
//     <div className="min-h-screen bg-gray-50 py-12">
//       <div className="max-w-4xl mx-auto px-4">
//         <div className="text-center mb-8">
//           <h1 className="text-3xl font-bold text-gray-900 mb-2">決済ページ</h1>
//           <p className="text-gray-600">
//             メンバー数が無料枠を超過しているため、追加料金の決済が必要です
//           </p>
//         </div>

//         {!billingInfo.is_payment_required ? (
//           // 決済不要の場合
//           <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6 text-center">
//             <div className="text-green-600 mb-4">
//               <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
//               </svg>
//             </div>
//             <h2 className="text-xl font-bold text-gray-900 mb-2">決済は不要です</h2>
//             <p className="text-gray-600 mb-4">
//               現在のメンバー数（{billingInfo.current_members}人）は無料枠内です
//             </p>
//             <button
//               onClick={() => router.push('/dashboard')}
//               className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
//             >
//               ダッシュボードに戻る
//             </button>
//           </div>
//         ) : (
//           // 決済が必要な場合
//           clientSecret && (
//             <Elements stripe={stripePromise}>
//               <CheckoutForm
//                 billingInfo={billingInfo}
//                 clientSecret={clientSecret}
//                 onSuccess={handlePaymentSuccess}
//               />
//             </Elements>
//           )
//         )}
//       </div>
//     </div>
//   );
// }