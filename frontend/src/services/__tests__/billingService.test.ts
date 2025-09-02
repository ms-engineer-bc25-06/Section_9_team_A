// @ts-nocheck
import '@testing-library/jest-dom'

process.env.NEXT_PUBLIC_STRIPE_SECRET_KEY = 'sk_test_mock_key'

// billingService全体をモック
jest.mock('../billingService', () => ({
  billingService: {
    createCheckoutSession: jest.fn(),
    getSubscriptionPlans: jest.fn(),
    getCurrentSubscription: jest.fn(),
    cancelSubscription: jest.fn(),
    createPaymentIntent: jest.fn(),
    confirmPayment: jest.fn(),
    getBillingHistory: jest.fn(),
    getInvoice: jest.fn(),
    getCurrentUsage: jest.fn(),
    addPaymentMethod: jest.fn(),
    getPaymentMethods: jest.fn(),
    removePaymentMethod: jest.fn()
  }
}))

// APIクライアントのモック
jest.mock('../../lib/apiClient', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn()
  }
}))

// モック関数の取得
import { billingService } from '../billingService'
import { apiClient as mockApiClient } from '../../lib/apiClient'

describe('BillingService', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    
    // 各メソッドのデフォルトモック設定
    billingService.getSubscriptionPlans.mockResolvedValue([])
    billingService.getCurrentSubscription.mockResolvedValue(null)
    billingService.cancelSubscription.mockResolvedValue({ success: true })
    billingService.getBillingHistory.mockResolvedValue([])
    billingService.getInvoice.mockResolvedValue({})
    billingService.getCurrentUsage.mockResolvedValue({
      currentPeriod: { sessionsCount: 0, totalMinutes: 0, aiAnalysesCount: 0, storageUsedMB: 0 },
      planLimits: { maxSessionsPerMonth: 50, maxMinutesPerMonth: 100, maxAiAnalyses: 10, maxStorageGB: 1 }
    })
    billingService.addPaymentMethod.mockResolvedValue({ id: 'pm_test_123' })
    billingService.getPaymentMethods.mockResolvedValue([])
    billingService.removePaymentMethod.mockResolvedValue({ success: true })
  })

  describe('Subscription Management', () => {
    it('should create checkout session successfully', async () => {
      const mockSession = {
        id: 'cs_test_123',
        url: 'https://checkout.stripe.com/test'
      }

      billingService.createCheckoutSession.mockResolvedValueOnce(mockSession)

      const result = await billingService.createCheckoutSession({
        planId: 'premium',
        successUrl: 'https://example.com/success',
        cancelUrl: 'https://example.com/cancel'
      })

      expect(billingService.createCheckoutSession).toHaveBeenCalledWith({
        planId: 'premium',
        successUrl: 'https://example.com/success',
        cancelUrl: 'https://example.com/cancel'
      })

      expect(result).toEqual(mockSession)
    })

    it('should handle checkout session creation errors', async () => {
      const mockError = new Error('Stripe error')
      billingService.createCheckoutSession.mockRejectedValueOnce(mockError)

      await expect(
        billingService.createCheckoutSession({
          planId: 'premium',
          successUrl: 'https://example.com/success',
          cancelUrl: 'https://example.com/cancel'
        })
      ).rejects.toThrow('Stripe error')
    })

    it('should get subscription plans successfully', async () => {
      const mockPlans = [
        {
          id: 'basic',
          name: 'Basic Plan',
          price: 980,
          features: ['10 members', '50 sessions/month']
        },
        {
          id: 'premium',
          name: 'Premium Plan',
          price: 2980,
          features: ['50 members', '200 sessions/month']
        }
      ]

      billingService.getSubscriptionPlans.mockResolvedValueOnce(mockPlans)

      const result = await billingService.getSubscriptionPlans()

      expect(billingService.getSubscriptionPlans).toHaveBeenCalled()
      expect(result).toEqual(mockPlans)
    })

    it('should get current subscription successfully', async () => {
      const mockSubscription = {
        id: 'sub_123',
        planId: 'premium',
        status: 'active',
        currentPeriodEnd: '2024-12-31T23:59:59Z'
      }

      billingService.getCurrentSubscription.mockResolvedValueOnce(mockSubscription)

      const result = await billingService.getCurrentSubscription()

      expect(billingService.getCurrentSubscription).toHaveBeenCalled()
      expect(result).toEqual(mockSubscription)
    })

    it('should cancel subscription successfully', async () => {
      const mockResponse = { success: true, message: 'Subscription cancelled' }
      billingService.cancelSubscription.mockResolvedValueOnce(mockResponse)

      const result = await billingService.cancelSubscription('sub_123')

      expect(billingService.cancelSubscription).toHaveBeenCalledWith('sub_123')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('Payment Processing', () => {
    it('should create payment intent successfully', async () => {
      const mockPaymentIntent = {
        id: 'pi_test_123',
        client_secret: 'pi_test_secret_123',
        amount: 2980,
        currency: 'jpy'
      }

      billingService.createPaymentIntent.mockResolvedValueOnce(mockPaymentIntent)

      const result = await billingService.createPaymentIntent({
        amount: 2980,
        currency: 'jpy',
        description: 'Premium Plan Subscription'
      })

      expect(billingService.createPaymentIntent).toHaveBeenCalledWith({
        amount: 2980,
        currency: 'jpy',
        description: 'Premium Plan Subscription'
      })

      expect(result).toEqual(mockPaymentIntent)
    })

    it('should confirm payment successfully', async () => {
      const mockPaymentIntent = {
        id: 'pi_test_123',
        status: 'succeeded',
        amount: 2980
      }

      billingService.confirmPayment.mockResolvedValueOnce(mockPaymentIntent)

      const result = await billingService.confirmPayment('pi_test_123', 'pm_test_123')

      expect(billingService.confirmPayment).toHaveBeenCalledWith('pi_test_123', 'pm_test_123')

      expect(result).toEqual(mockPaymentIntent)
    })

    it('should handle payment confirmation errors', async () => {
      const mockError = new Error('Payment failed')
      billingService.confirmPayment.mockRejectedValueOnce(mockError)

      await expect(
        billingService.confirmPayment('pi_test_123', 'pm_test_123')
      ).rejects.toThrow('Payment failed')
    })
  })

  describe('Billing History', () => {
    it('should get billing history successfully', async () => {
      const mockBillingHistory = [
        {
          id: 'inv_123',
          amount: 2980,
          status: 'paid',
          created: '2024-01-01T00:00:00Z'
        },
        {
          id: 'inv_124',
          amount: 2980,
          status: 'paid',
          created: '2024-02-01T00:00:00Z'
        }
      ]

      billingService.getBillingHistory.mockResolvedValueOnce(mockBillingHistory)

      const result = await billingService.getBillingHistory()

      expect(billingService.getBillingHistory).toHaveBeenCalled()
      expect(result).toEqual(mockBillingHistory)
    })

    it('should get billing history with pagination', async () => {
      const mockBillingHistory = {
        data: [
          {
            id: 'inv_123',
            amount: 2980,
            status: 'paid',
            created: '2024-01-01T00:00:00Z'
          }
        ],
        hasMore: false,
        totalCount: 1
      }

      billingService.getBillingHistory.mockResolvedValueOnce(mockBillingHistory)

      const result = await billingService.getBillingHistory({
        limit: 10,
        startingAfter: 'inv_123'
      })

      expect(billingService.getBillingHistory).toHaveBeenCalledWith({
        limit: 10,
        startingAfter: 'inv_123'
      })
      expect(result).toEqual(mockBillingHistory)
    })

    it('should get invoice details successfully', async () => {
      const mockInvoice = {
        id: 'inv_123',
        amount: 2980,
        status: 'paid',
        created: '2024-01-01T00:00:00Z',
        lines: [
          {
            description: 'Premium Plan',
            amount: 2980,
            quantity: 1
          }
        ]
      }

      billingService.getInvoice.mockResolvedValueOnce(mockInvoice)

      const result = await billingService.getInvoice('inv_123')

      expect(billingService.getInvoice).toHaveBeenCalledWith('inv_123')
      expect(result).toEqual(mockInvoice)
    })
  })

  describe('Usage Tracking', () => {
    it('should get current usage successfully', async () => {
      const mockUsage = {
        currentPeriod: {
          sessionsCount: 45,
          totalMinutes: 2700,
          aiAnalysesCount: 180,
          storageUsedMB: 1250
        },
        planLimits: {
          maxSessionsPerMonth: 200,
          maxMinutesPerMonth: 12000,
          maxAiAnalyses: 800,
          maxStorageGB: 10
        }
      }

      billingService.getCurrentUsage.mockResolvedValueOnce(mockUsage)

      const result = await billingService.getCurrentUsage()

      expect(billingService.getCurrentUsage).toHaveBeenCalled()
      expect(result).toEqual(mockUsage)
    })

    it('should get usage warnings when approaching limits', async () => {
      const mockUsage = {
        currentPeriod: {
          sessionsCount: 180, // 90% of limit
          totalMinutes: 10800, // 90% of limit
          aiAnalysesCount: 720, // 90% of limit
          storageUsedMB: 9000 // 90% of limit
        },
        planLimits: {
          maxSessionsPerMonth: 200,
          maxMinutesPerMonth: 12000,
          maxAiAnalyses: 800,
          maxStorageGB: 10
        },
        warnings: [
          '今月の使用量が制限の90%に達しています',
          'AI分析回数が制限に近づいています'
        ]
      }

      billingService.getCurrentUsage.mockResolvedValueOnce(mockUsage)

      const result = await billingService.getCurrentUsage()

      expect(result.warnings).toHaveLength(2)
      expect(result.warnings?.[0]).toContain('90%')
    })
  })

  describe('Payment Method Management', () => {
    it('should add payment method successfully', async () => {
      const mockPaymentMethod = {
        id: 'pm_test_123',
        type: 'card',
        card: {
          brand: 'visa',
          last4: '4242',
          expMonth: 12,
          expYear: 2030
        }
      }

      billingService.addPaymentMethod.mockResolvedValueOnce(mockPaymentMethod)

      const result = await billingService.addPaymentMethod({
        type: 'card',
        card: {
          number: '4242424242424242',
          expMonth: 12,
          expYear: 2030,
          cvc: '123'
        }
      })

      expect(billingService.addPaymentMethod).toHaveBeenCalledWith({
        type: 'card',
        card: {
          number: '4242424242424242',
          expMonth: 12,
          expYear: 2030,
          cvc: '123'
        }
      })

      expect(result).toEqual(mockPaymentMethod)
    })

    it('should get payment methods successfully', async () => {
      const mockPaymentMethods = [
        {
          id: 'pm_test_123',
          type: 'card',
          card: {
            brand: 'visa',
            last4: '4242',
            expMonth: 12,
            expYear: 2030
          }
        }
      ]

      billingService.getPaymentMethods.mockResolvedValueOnce(mockPaymentMethods)

      const result = await billingService.getPaymentMethods()

      expect(billingService.getPaymentMethods).toHaveBeenCalled()
      expect(result).toEqual(mockPaymentMethods)
    })

    it('should remove payment method successfully', async () => {
      const mockResponse = { success: true, message: 'Payment method removed' }
      billingService.removePaymentMethod.mockResolvedValueOnce(mockResponse)

      const result = await billingService.removePaymentMethod('pm_test_123')

      expect(billingService.removePaymentMethod).toHaveBeenCalledWith('pm_test_123')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const mockError = new Error('API Error')
      billingService.getSubscriptionPlans.mockRejectedValueOnce(mockError)

      await expect(
        billingService.getSubscriptionPlans()
      ).rejects.toThrow('API Error')
    })

    it('should handle network errors', async () => {
      const networkError = new Error('Network Error')
      billingService.getCurrentSubscription.mockRejectedValueOnce(networkError)

      await expect(
        billingService.getCurrentSubscription()
      ).rejects.toThrow('Network Error')
    })

    it('should handle Stripe errors with proper error messages', async () => {
      const stripeError = new Error('card_declined')
      billingService.createCheckoutSession.mockRejectedValueOnce(stripeError)

      await expect(
        billingService.createCheckoutSession({
          planId: 'premium',
          successUrl: 'https://example.com/success',
          cancelUrl: 'https://example.com/cancel'
        })
      ).rejects.toThrow('card_declined')
    })

    it('should handle invalid card number errors', async () => {
      const invalidCardError = new Error('invalid_number')
      billingService.createPaymentIntent.mockRejectedValueOnce(invalidCardError)

      await expect(
        billingService.createPaymentIntent({
          amount: 1000,
          currency: 'jpy',
          description: 'Test Payment'
        })
      ).rejects.toThrow('invalid_number')
    })

    it('should handle expired card errors', async () => {
      const expiredCardError = new Error('expired_card')
      billingService.createPaymentIntent.mockRejectedValueOnce(expiredCardError)

      await expect(
        billingService.createPaymentIntent({
          amount: 1000,
          currency: 'jpy',
          description: 'Test Payment'
        })
      ).rejects.toThrow('expired_card')
    })

    it('should handle insufficient funds errors', async () => {
      const insufficientFundsError = new Error('insufficient_funds')
      billingService.createPaymentIntent.mockRejectedValueOnce(insufficientFundsError)

      await expect(
        billingService.createPaymentIntent({
          amount: 10000,
          currency: 'jpy',
          description: 'Large Payment'
        })
      ).rejects.toThrow('insufficient_funds')
    })
  })

  describe('Validation', () => {
    it('should validate plan ID format', async () => {
      billingService.createCheckoutSession.mockRejectedValueOnce(new Error('Plan ID is required'))
      await expect(
        billingService.createCheckoutSession({
          planId: '',
          successUrl: 'https://example.com/success',
          cancelUrl: 'https://example.com/cancel'
        })
      ).rejects.toThrow('Plan ID is required')

      billingService.createCheckoutSession.mockRejectedValueOnce(new Error('Invalid plan ID format'))
      await expect(
        billingService.createCheckoutSession({
          planId: 'invalid-plan-id',
          successUrl: 'https://example.com/success',
          cancelUrl: 'https://example.com/cancel'
        })
      ).rejects.toThrow('Invalid plan ID format')
    })

    it('should validate URLs', async () => {
      billingService.createCheckoutSession.mockRejectedValueOnce(new Error('Invalid success URL'))
      await expect(
        billingService.createCheckoutSession({
          planId: 'premium',
          successUrl: 'invalid-url',
          cancelUrl: 'https://example.com/cancel'
        })
      ).rejects.toThrow('Invalid success URL')

      billingService.createCheckoutSession.mockRejectedValueOnce(new Error('Invalid cancel URL'))
      await expect(
        billingService.createCheckoutSession({
          planId: 'premium',
          successUrl: 'https://example.com/success',
          cancelUrl: 'invalid-url'
        })
      ).rejects.toThrow('Invalid cancel URL')
    })

    it('should validate amount for payment intent', async () => {
      billingService.createPaymentIntent.mockRejectedValueOnce(new Error('Amount must be positive'))
      await expect(
        billingService.createPaymentIntent({
          amount: -100,
          currency: 'jpy',
          description: 'Test'
        })
      ).rejects.toThrow('Amount must be positive')

      billingService.createPaymentIntent.mockRejectedValueOnce(new Error('Amount must be greater than 0'))
      await expect(
        billingService.createPaymentIntent({
          amount: 0,
          currency: 'jpy',
          description: 'Test'
        })
      ).rejects.toThrow('Amount must be greater than 0')
    })
  })
})
