import { PlanService, PLANS } from '../planService'

describe('PlanService', () => {
  describe('getPlan', () => {
    it('should return plan for valid plan ID', () => {
      const basicPlan = PlanService.getPlan('basic')
      expect(basicPlan).toBeDefined()
      expect(basicPlan?.id).toBe('basic')
      expect(basicPlan?.name).toBe('Basic Plan')
      expect(basicPlan?.monthly_price).toBe(980)
    })

    it('should return null for invalid plan ID', () => {
      const invalidPlan = PlanService.getPlan('invalid')
      expect(invalidPlan).toBeNull()
    })

    it('should return all plan types', () => {
      const basicPlan = PlanService.getPlan('basic')
      const premiumPlan = PlanService.getPlan('premium')
      const enterprisePlan = PlanService.getPlan('enterprise')

      expect(basicPlan).toBeDefined()
      expect(premiumPlan).toBeDefined()
      expect(enterprisePlan).toBeDefined()
    })
  })

  describe('getAllPlans', () => {
    it('should return all available plans', () => {
      const allPlans = PlanService.getAllPlans()
      expect(allPlans).toHaveLength(3)
      expect(allPlans.map(p => p.id)).toEqual(['basic', 'premium', 'enterprise'])
    })

    it('should return plans with correct structure', () => {
      const allPlans = PlanService.getAllPlans()
      const firstPlan = allPlans[0]
      
      expect(firstPlan).toHaveProperty('id')
      expect(firstPlan).toHaveProperty('name')
      expect(firstPlan).toHaveProperty('monthly_price')
      expect(firstPlan).toHaveProperty('yearly_price')
      expect(firstPlan).toHaveProperty('features')
      expect(firstPlan).toHaveProperty('trial_days')
    })
  })

  describe('getCurrentPlanByUserCount', () => {
    it('should return basic plan for 10 users or less', () => {
      expect(PlanService.getCurrentPlanByUserCount(1)).toBe('basic')
      expect(PlanService.getCurrentPlanByUserCount(5)).toBe('basic')
      expect(PlanService.getCurrentPlanByUserCount(10)).toBe('basic')
    })

    it('should return premium plan for 11-50 users', () => {
      expect(PlanService.getCurrentPlanByUserCount(11)).toBe('premium')
      expect(PlanService.getCurrentPlanByUserCount(25)).toBe('premium')
      expect(PlanService.getCurrentPlanByUserCount(50)).toBe('premium')
    })

    it('should return enterprise plan for 51+ users', () => {
      expect(PlanService.getCurrentPlanByUserCount(51)).toBe('enterprise')
      expect(PlanService.getCurrentPlanByUserCount(100)).toBe('enterprise')
      expect(PlanService.getCurrentPlanByUserCount(1000)).toBe('enterprise')
    })
  })

  describe('calculateYearlyPrice', () => {
    it('should calculate yearly price with default discount', () => {
      const monthlyPrice = 1000
      const yearlyPrice = PlanService.calculateYearlyPrice(monthlyPrice)
      const expectedPrice = Math.round(1000 * 12 * 0.8) // 20% discount
      expect(yearlyPrice).toBe(expectedPrice)
    })

    it('should calculate yearly price with custom discount', () => {
      const monthlyPrice = 1000
      const discountRate = 0.15
      const yearlyPrice = PlanService.calculateYearlyPrice(monthlyPrice, discountRate)
      const expectedPrice = Math.round(1000 * 12 * 0.85) // 15% discount
      expect(yearlyPrice).toBe(expectedPrice)
    })

    it('should handle zero discount', () => {
      const monthlyPrice = 1000
      const discountRate = 0
      const yearlyPrice = PlanService.calculateYearlyPrice(monthlyPrice, discountRate)
      const expectedPrice = 1000 * 12
      expect(yearlyPrice).toBe(expectedPrice)
    })
  })

  describe('calculateMonthlyEquivalent', () => {
    it('should calculate monthly equivalent from yearly price', () => {
      const yearlyPrice = 12000
      const monthlyEquivalent = PlanService.calculateMonthlyEquivalent(yearlyPrice)
      expect(monthlyEquivalent).toBe(1000)
    })

    it('should round monthly equivalent correctly', () => {
      const yearlyPrice = 11999
      const monthlyEquivalent = PlanService.calculateMonthlyEquivalent(yearlyPrice)
      expect(monthlyEquivalent).toBe(1000) // 11999 / 12 = 999.92... → 1000
    })
  })

  describe('checkPlanUsage', () => {
    it('should return correct usage for basic plan', () => {
      const result = PlanService.checkPlanUsage(5, 'basic')
      expect(result.isOverLimit).toBe(false)
      expect(result.excessUsers).toBe(0)
      expect(result.maxUsers).toBe(10)
    })

    it('should detect over limit for basic plan', () => {
      const result = PlanService.checkPlanUsage(15, 'basic')
      expect(result.isOverLimit).toBe(true)
      expect(result.excessUsers).toBe(5)
      expect(result.maxUsers).toBe(10)
    })

    it('should handle unlimited users in enterprise plan', () => {
      const result = PlanService.checkPlanUsage(1000, 'enterprise')
      expect(result.isOverLimit).toBe(false)
      expect(result.excessUsers).toBe(0)
      expect(result.maxUsers).toBe(Number.MAX_SAFE_INTEGER)
    })

    it('should handle invalid plan ID', () => {
      const result = PlanService.checkPlanUsage(10, 'invalid')
      expect(result.isOverLimit).toBe(false)
      expect(result.excessUsers).toBe(0)
      expect(result.maxUsers).toBe(0)
    })
  })

  describe('getPlanPrice', () => {
    it('should return monthly price for monthly billing', () => {
      const price = PlanService.getPlanPrice('basic', 'monthly')
      expect(price).toBe(980)
    })

    it('should return calculated yearly price for yearly billing', () => {
      const price = PlanService.getPlanPrice('basic', 'yearly')
      const expectedYearlyPrice = PlanService.calculateYearlyPrice(980)
      expect(price).toBe(expectedYearlyPrice)
    })

    it('should return 0 for invalid plan ID', () => {
      const price = PlanService.getPlanPrice('invalid', 'monthly')
      expect(price).toBe(0)
    })
  })

  describe('getPlanDisplayInfo', () => {
    it('should return display info for basic plan', () => {
      const displayInfo = PlanService.getPlanDisplayInfo('basic')
      
      expect(displayInfo.name).toBe('Basic Plan')
      expect(displayInfo.monthlyPrice).toBe(980)
      expect(displayInfo.maxUsers).toBe('10名')
      expect(displayInfo.maxSessions).toBe('50セッション/月')
      expect(displayInfo.features).toContain('文字起こし機能')
      expect(displayInfo.features).toContain('基本AI分析')
      expect(displayInfo.features).not.toContain('高度AI分析')
    })

    it('should return display info for enterprise plan', () => {
      const displayInfo = PlanService.getPlanDisplayInfo('enterprise')
      
      expect(displayInfo.name).toBe('Enterprise Plan')
      expect(displayInfo.maxUsers).toBe('無制限')
      expect(displayInfo.maxSessions).toBe('無制限')
      expect(displayInfo.features).toContain('SSO連携')
      expect(displayInfo.features).toContain('API アクセス')
    })

    it('should return default values for invalid plan ID', () => {
      const displayInfo = PlanService.getPlanDisplayInfo('invalid')
      
      expect(displayInfo.name).toBe('Unknown Plan')
      expect(displayInfo.monthlyPrice).toBe(0)
      expect(displayInfo.maxUsers).toBe('0')
      expect(displayInfo.maxSessions).toBe('0')
      expect(displayInfo.features).toEqual([])
    })

    it('should calculate yearly price correctly in display info', () => {
      const displayInfo = PlanService.getPlanDisplayInfo('basic')
      const expectedYearlyPrice = PlanService.calculateYearlyPrice(980)
      
      expect(displayInfo.yearlyPrice).toBe(expectedYearlyPrice)
    })
  })

  describe('PLANS constant', () => {
    it('should have correct plan structure', () => {
      expect(PLANS.basic).toBeDefined()
      expect(PLANS.premium).toBeDefined()
      expect(PLANS.enterprise).toBeDefined()
    })

    it('should have correct feature structure', () => {
      const basicFeatures = PLANS.basic.features
      
      expect(basicFeatures).toHaveProperty('max_team_members')
      expect(basicFeatures).toHaveProperty('max_sessions_per_month')
      expect(basicFeatures).toHaveProperty('transcription_included')
      expect(basicFeatures).toHaveProperty('support_level')
    })

    it('should have correct pricing structure', () => {
      expect(PLANS.basic.monthly_price).toBe(980)
      expect(PLANS.basic.yearly_price).toBe(9800)
      expect(PLANS.premium.monthly_price).toBe(2980)
      expect(PLANS.enterprise.monthly_price).toBe(9800)
    })
  })
})


