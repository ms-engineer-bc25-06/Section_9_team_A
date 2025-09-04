import Stripe from 'stripe'
import { apiClient } from '../lib/apiClient'

// Stripeインスタンスの初期化
const stripe = new Stripe(process.env.NEXT_PUBLIC_STRIPE_SECRET_KEY || '', {
  apiVersion: '2024-04-10'
})

// 型定義
interface CheckoutSessionParams {
  planId: string
  successUrl: string
  cancelUrl: string
}

interface PaymentIntentParams {
  amount: number
  currency: string
  description: string
}

interface PaymentMethodData {
  type: 'card'
  card: {
    number: string
    expMonth: number
    expYear: number
    cvc: string
  }
}

interface BillingHistoryParams {
  limit?: number
  startingAfter?: string
}

interface SubscriptionPlan {
  id: string
  name: string
  price: number
  features: string[]
}

interface Subscription {
  id: string
  planId: string
  status: string
  currentPeriodEnd: string
}

interface BillingHistoryItem {
  id: string
  amount: number
  status: string
  created: string
}

interface UsageData {
  currentPeriod: {
    sessionsCount: number
    totalMinutes: number
    aiAnalysesCount: number
    storageUsedMB: number
  }
  planLimits: {
    maxSessionsPerMonth: number
    maxMinutesPerMonth: number
    maxAiAnalyses: number
    maxStorageGB: number
  }
  warnings?: string[]
}

interface PaymentMethod {
  id: string
  type: string
  card: {
    brand: string
    last4: string
    expMonth: number
    expYear: number
  }
}

// バリデーション関数
const validatePlanId = (planId: string): void => {
  if (!planId || planId.trim() === '') {
    throw new Error('Plan ID is required')
  }
  if (!/^[a-z0-9_-]+$/i.test(planId)) {
    throw new Error('Invalid plan ID format')
  }
}

const validateUrl = (url: string, fieldName: string): void => {
  try {
    new URL(url)
  } catch {
    throw new Error(`Invalid ${fieldName}`)
  }
}

const validateAmount = (amount: number): void => {
  if (amount < 0) {
    throw new Error('Amount must be positive')
  }
  if (amount === 0) {
    throw new Error('Amount must be greater than 0')
  }
}

// サブスクリプション管理
export const createCheckoutSession = async (params: CheckoutSessionParams) => {
  const { planId, successUrl, cancelUrl } = params

  validatePlanId(planId)
  validateUrl(successUrl, 'success URL')
  validateUrl(cancelUrl, 'cancel URL')

  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [{
        price: planId,
        quantity: 1
      }],
      mode: 'subscription',
      success_url: successUrl,
      cancel_url: cancelUrl
    })

    return session
  } catch (error: any) {
    throw new Error(error.message || 'Failed to create checkout session')
  }
}

export const getSubscriptionPlans = async (): Promise<SubscriptionPlan[]> => {
  try {
    const response = await apiClient.get('/subscriptions/plans')
    return response.data
  } catch (error: any) {
    throw new Error(error.message || 'Failed to fetch subscription plans')
  }
}

export const getCurrentSubscription = async (): Promise<Subscription> => {
  try {
    const response = await apiClient.get('/subscriptions/current')
    return response.data
  } catch (error: any) {
    throw new Error(error.message || 'Failed to fetch current subscription')
  }
}

export const cancelSubscription = async (subscriptionId: string) => {
  try {
    const response = await apiClient.post(`/subscriptions/${subscriptionId}/cancel`)
    return response.data
  } catch (error: any) {
    throw new Error(error.message || 'Failed to cancel subscription')
  }
}

// 決済処理
export const createPaymentIntent = async (params: PaymentIntentParams) => {
  const { amount, currency, description } = params

  validateAmount(amount)

  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency,
      description,
      automatic_payment_methods: {
        enabled: true
      }
    })

    return paymentIntent
  } catch (error: any) {
    throw new Error(error.message || 'Failed to create payment intent')
  }
}

export const confirmPayment = async (paymentIntentId: string, paymentMethodId: string) => {
  try {
    const paymentIntent = await stripe.paymentIntents.confirm(paymentIntentId, {
      payment_method: paymentMethodId
    })

    return paymentIntent
  } catch (error: any) {
    throw new Error(error.message || 'Failed to confirm payment')
  }
}

// 請求履歴
export const getBillingHistory = async (params?: BillingHistoryParams): Promise<BillingHistoryItem[]> => {
  try {
    const queryParams = new URLSearchParams()
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.startingAfter) queryParams.append('startingAfter', params.startingAfter)

    const url = `/billing/history${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    const response = await apiClient.get(url)
    return response.data
  } catch (error: any) {
    throw new Error(error.message || 'Failed to fetch billing history')
  }
}

export const getInvoice = async (invoiceId: string) => {
  try {
    const response = await apiClient.get(`/billing/invoices/${invoiceId}`)
    return response.data
  } catch (error: any) {
    throw new Error(error.message || 'Failed to fetch invoice')
  }
}

// 使用量追跡
export const getCurrentUsage = async (): Promise<UsageData> => {
  try {
    const response = await apiClient.get('/billing/usage')
    return response.data
  } catch (error: any) {
    throw new Error(error.message || 'Failed to fetch usage data')
  }
}

// 支払い方法管理
export const addPaymentMethod = async (data: PaymentMethodData): Promise<PaymentMethod> => {
  try {
    const response = await apiClient.post('/billing/payment-methods', data)
    return response.data
  } catch (error: any) {
    throw new Error(error.message || 'Failed to add payment method')
  }
}

export const getPaymentMethods = async (): Promise<PaymentMethod[]> => {
  try {
    const response = await apiClient.get('/billing/payment-methods')
    return response.data
  } catch (error: any) {
    throw new Error(error.message || 'Failed to fetch payment methods')
  }
}

export const removePaymentMethod = async (paymentMethodId: string) => {
  try {
    const response = await apiClient.delete(`/billing/payment-methods/${paymentMethodId}`)
    return response.data
  } catch (error: any) {
    throw new Error(error.message || 'Failed to remove payment method')
  }
}

// サービスオブジェクトとしてエクスポート
export const billingService = {
  createCheckoutSession,
  getSubscriptionPlans,
  getCurrentSubscription,
  cancelSubscription,
  createPaymentIntent,
  confirmPayment,
  getBillingHistory,
  getInvoice,
  getCurrentUsage,
  addPaymentMethod,
  getPaymentMethods,
  removePaymentMethod
}
